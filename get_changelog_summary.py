#!/usr/bin/env python3
"""
OpenStack OpenDev Changelog Summary Script

This script fetches merged changelog information from OpenStack repositories
via Gerrit REST API and outputs the changes data as JSON.

Environment Variables:
- OPENDEV_REPO_NAME: Repository name (default: openstack/barbican)
- OPENDEV_STATUS: Status filter (default: merged)
- OPENDEV_AFTER: After date in YYYY-MM-DD format (default: calculated from age)
- OPENDEV_AGE: Age filter (default: 1d) - converted to after date
- OPENDEV_DRY_RUN: If set to 'true', only show query without making API calls
- OPENDEV_LOG: If set to 'true', show debug and info messages (default: false)
"""

import requests
import json
import urllib.parse
import os
import sys
from datetime import datetime, timedelta
import re

def log_message(message, file=sys.stderr):
    """
    Print log message only if OPENDEV_LOG environment variable is set to 'true'.
    
    Args:
        message (str): Message to log
        file: Output file (default: sys.stderr)
    """
    if os.getenv('OPENDEV_LOG', '').lower() == 'true':
        print(message, file=file)

def parse_age_to_date(age_str):
    """
    Parse age string (like '1d', '7d', '30d') to a date string in YYYY-MM-DD format.
    
    Args:
        age_str (str): Age string like '1d', '7d', '30d'
        
    Returns:
        str: Date string in YYYY-MM-DD format
    """
    if not age_str:
        age_str = '1d'
    
    # Parse the age string using regex
    match = re.match(r'^(\d+)([dhm])$', age_str.lower())
    if not match:
        # If parsing fails, default to 1 day
        days = 1
    else:
        number = int(match.group(1))
        unit = match.group(2)
        
        if unit == 'd':
            days = number
        elif unit == 'h':
            days = max(1, number // 24)  # Convert hours to days, minimum 1 day
        elif unit == 'm':
            days = max(1, number // (24 * 60))  # Convert minutes to days, minimum 1 day
        else:
            days = 1
    
    # Calculate the date
    target_date = datetime.now() - timedelta(days=days)
    return target_date.strftime('%Y-%m-%d')

def get_changelog_summary():
    """
    Gerrit REST APIを使用して、指定された条件でマージされた
    リポジトリの変更のchangelog情報を取得し、JSON形式で出力します。
    """
    # 環境変数から設定を取得（デフォルト値付き）
    repo_name = os.getenv('OPENDEV_REPO_NAME', 'openstack/barbican')
    status = os.getenv('OPENDEV_STATUS', 'merged')
    after = os.getenv('OPENDEV_AFTER')
    age = os.getenv('OPENDEV_AGE', '1d')
    dry_run = os.getenv('OPENDEV_DRY_RUN', '').lower() == 'true'
    
    # afterが指定されていない場合は、ageから変換
    if not after:
        after = parse_age_to_date(age)
    
    gerrit_url = 'https://review.opendev.org'
    
    # 検索クエリを構築 (mergedafter -> after に変更)
    query = f'status:{status} repo:{repo_name} after:{after}'
    
    log_message(f"Searching for changes: {query}")
    
    if dry_run:
        log_message("DRY_RUN mode: Skipping API calls")
        return {
            'query': query,
            'count': 0,
            'repository': repo_name,
            'status': status,
            'after': after,
            'timestamp': datetime.now().isoformat(),
            'changes': [],
            'dry_run': True
        }
    
    # Gerrit APIのエンドポイント
    changes_endpoint = f'{gerrit_url}/changes/'
    
    try:
        # 変更リストをクエリするAPIリクエスト
        # 応答の不正なプレフィックス `)]}'` を処理します。
        response = requests.get(
            changes_endpoint, 
            params={'q': query, 'o': ['ALL_REVISIONS', 'DETAILED_ACCOUNTS', 'MESSAGES']},
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        
        # JSONレスポンスからプレフィックスを削除
        changes = json.loads(response.text[4:])
        
    except requests.exceptions.RequestException as e:
        print(f"APIリクエスト中にエラーが発生しました: {e}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"JSONデコード中にエラーが発生しました: {e}", file=sys.stderr)
        return None

    if not changes:
        log_message(f"指定された条件 ({query}) でマージされた変更は見つかりませんでした。")
        return {"changes": [], "query": query, "count": 0}

    log_message(f"条件に一致する変更を {len(changes)} 件見つけました。")
    
    result_changes = []
    
    for change in changes:
        change_id = change['id']
        change_subject = change['subject']
        
        log_message(f"\n--- 変更を処理中: {change_subject} ({change_id}) ---")

        # 最新のリビジョンIDを取得します
        revision_id = change['current_revision']
        
        # changelog情報を構築
        change_data = {
            'id': change_id,
            'change_id': change.get('change_id'),  # Change-Id
            'subject': change_subject,
            'status': change.get('status'),
            'owner': change.get('owner', {}),
            'created': change.get('created'),
            'updated': change.get('updated'),
            'submitted': change.get('submitted'),
            'revision_id': revision_id,
            'project': change.get('project'),
            'branch': change.get('branch'),
            'topic': change.get('topic'),
            'hashtags': change.get('hashtags', []),
            'messages': change.get('messages', []),
            'changelog': {}
        }
        
        try:
            # changelog情報として、コミットメッセージと関連情報を取得
            revision_endpoint = f'{changes_endpoint}{change_id}/revisions/{revision_id}'
            revision_response = requests.get(revision_endpoint)
            revision_response.raise_for_status()
            
            # レスポンスのJSONからプレフィックスを削除
            revision_data = json.loads(revision_response.text[4:])
            
            # changelog情報を追加
            changelog_info = {
                'commit_message': revision_data.get('commit', {}).get('message', ''),
                'author': revision_data.get('commit', {}).get('author', {}),
                'committer': revision_data.get('commit', {}).get('committer', {}),
                'parents': revision_data.get('commit', {}).get('parents', []),
                'web_links': revision_data.get('web_links', []),
                'files': []
            }
            
            # 変更されたファイルのリストを取得
            files_endpoint = f'{changes_endpoint}{change_id}/revisions/{revision_id}/files/'
            files_response = requests.get(files_endpoint)
            
            if files_response.status_code == 200:
                files = json.loads(files_response.text[4:])
                # 差分を取得しない特殊なキーをスキップ（/COMMIT_MSGなど）
                file_paths = [path for path in files.keys() if not path.startswith('/')]
                
                for file_path in file_paths:
                    file_info = files.get(file_path, {})
                    changelog_info['files'].append({
                        'path': file_path,
                        'status': file_info.get('status'),
                        'lines_inserted': file_info.get('lines_inserted'),
                        'lines_deleted': file_info.get('lines_deleted'),
                        'size_delta': file_info.get('size_delta'),
                        'size': file_info.get('size')
                    })
                
                log_message(f"changelog情報を取得しました: {len(file_paths)} ファイル")
            
            change_data['changelog'] = changelog_info

        except requests.exceptions.RequestException as e:
            print(f"changelog情報の取得中にエラーが発生しました: {e}", file=sys.stderr)
            change_data['error'] = str(e)
        
        result_changes.append(change_data)

    # 結果をJSON形式で構造化
    result = {
        'query': query,
        'count': len(result_changes),
        'repository': repo_name,
        'status': status,
        'after': after,
        'timestamp': datetime.now().isoformat(),
        'changes': result_changes
    }
    
    return result

def main():
    """メイン関数"""
    result = get_changelog_summary()
    
    if result is not None:
        # JSON形式で出力（標準エラー出力でログ、標準出力でJSON）
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()