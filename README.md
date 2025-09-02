# openstack-opendev-changelog-summary

このリポジトリには、OpenStackの開発基盤である [opendev](https://review.opendev.org) からマージされたchangelog情報を取得し、JSON形式で要約を出力するためのPython 3スクリプトが含まれています。Gerrit APIのエンドポイントを使用して、マージされた変更のChange-Id、コミットメッセージ、ファイル変更情報などを取得します。

## 使い方

### 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 基本的な使用方法

```bash
python3 get_changelog_summary.py
```

### 環境変数による設定

以下の環境変数で動作をカスタマイズできます：

- `OPENDEV_REPO_NAME`: 対象リポジトリ（デフォルト: `openstack/barbican`）
- `OPENDEV_STATUS`: ステータスフィルター（デフォルト: `merged`）
- `OPENDEV_AFTER`: 日付の下限をYYYY-MM-DD形式で指定（デフォルト: 昨日の日付）
- `OPENDEV_DRY_RUN`: `true`に設定するとAPIコールを行わずクエリのみ表示
- `OPENDEV_LOG`: `true`に設定するとデバッグ情報とログメッセージを表示（デフォルト: `false`）

### 使用例

```bash
# デフォルト設定（openstack/barbican、過去1日のマージ済み変更）
python3 get_changelog_summary.py

# 異なるリポジトリを指定
OPENDEV_REPO_NAME=openstack/nova python3 get_changelog_summary.py

# 過去のオープンな変更を取得
OPENDEV_STATUS=open OPENDEV_AFTER=2025-01-20 python3 get_changelog_summary.py

# 特定の日付以降のマージ済み変更を取得
OPENDEV_AFTER=2025-01-01 python3 get_changelog_summary.py

# ドライランモード（APIコールなし）
OPENDEV_DRY_RUN=true python3 get_changelog_summary.py

# デバッグ情報とログメッセージを表示
OPENDEV_LOG=true python3 get_changelog_summary.py

# 複数の設定を組み合わせ
OPENDEV_REPO_NAME=openstack/keystone OPENDEV_STATUS=merged OPENDEV_AFTER=2025-01-15 python3 get_changelog_summary.py
```

## 出力形式

スクリプトは以下の形式でJSONを出力します：

```json
{
  "query": "status:merged repo:openstack/barbican after:2025-01-29",
  "count": 2,
  "repository": "openstack/barbican",
  "status": "merged",
  "after": "2025-01-29",
  "timestamp": "2024-01-01T12:00:00.000000",
  "changes": [
    {
      "id": "change-id",
      "change_id": "I1234567890abcdef...",
      "subject": "変更のタイトル",
      "status": "MERGED",
      "owner": {...},
      "created": "...",
      "updated": "...",
      "submitted": "...",
      "revision_id": "...",
      "project": "openstack/barbican",
      "branch": "master",
      "topic": "...",
      "hashtags": [],
      "messages": [...],
      "changelog": {
        "commit_message": "詳細なコミットメッセージ...",
        "author": {...},
        "committer": {...},
        "parents": [...],
        "web_links": [...],
        "files": [
          {
            "path": "path/to/file.py",
            "status": "MODIFIED",
            "lines_inserted": 10,
            "lines_deleted": 5,
            "size_delta": 100,
            "size": 1000
          }
        ]
      }
    }
  ]
}
```

## 主な特徴

- **Change-Id 基盤**: Gerrit Change-Idを使用してマージ情報を追跡
- **Changelog 情報**: ファイル差分ではなく、changelog情報（コミットメッセージ、ファイル変更サマリなど）を取得
- **柔軟なクエリ**: `after:` パラメータを使用した日付フィルタリング
- **JSON 出力**: 構造化されたJSON形式での出力
- **カスタマイズ可能**: 環境変数による設定のカスタマイズ

## 参考実装との違い

このスクリプトは [azkaoru/openstack-opendev-merge-summary](https://github.com/azkaoru/openstack-opendev-merge-summary) を参考にしていますが、以下の変更が加えられています：

1. **クエリパラメータ**: `mergedafter:` → `after:`
2. **データ取得**: ファイル差分 → changelog情報
3. **出力内容**: 差分詳細 → Change-Id、コミットメッセージ、ファイル変更サマリ
