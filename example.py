#!/usr/bin/env python3
"""
Example script demonstrating how to use get_changelog_summary.py
This example shows the expected JSON output structure and usage patterns.
"""

import json
import os
import subprocess
import sys

def run_example():
    """Run examples with different configurations"""
    
    examples = [
        {
            "name": "Default Barbican Configuration",
            "env": {
                "OPENDEV_DRY_RUN": "true",
                "OPENDEV_LOG": "true"
            },
            "description": "Get merged changes from openstack/barbican for the last day"
        },
        {
            "name": "Nova Repository with Specific Date",
            "env": {
                "OPENDEV_REPO_NAME": "openstack/nova",
                "OPENDEV_AFTER": "2025-01-20",
                "OPENDEV_DRY_RUN": "true",
                "OPENDEV_LOG": "true"
            },
            "description": "Get merged changes from openstack/nova since January 20th, 2025"
        },
        {
            "name": "Open Changes Since January 1st",
            "env": {
                "OPENDEV_STATUS": "open",
                "OPENDEV_AFTER": "2025-01-01",
                "OPENDEV_DRY_RUN": "true",
                "OPENDEV_LOG": "true"
            },
            "description": "Get open changes since January 1st, 2025"
        }
    ]
    
    print("=== OpenStack OpenDev Changelog Summary Examples ===\n")
    
    for i, example in enumerate(examples, 1):
        print(f"Example {i}: {example['name']}")
        print(f"Description: {example['description']}")
        print("Environment variables:")
        for key, value in example['env'].items():
            print(f"  {key}={value}")
        print()
        
        # Set environment variables
        env = os.environ.copy()
        env.update(example['env'])
        
        try:
            # Run the script
            result = subprocess.run(
                [sys.executable, 'get_changelog_summary.py'],
                env=env,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Parse and pretty-print the JSON output
                try:
                    output_data = json.loads(result.stdout)
                    print("Output (JSON):")
                    print(json.dumps(output_data, indent=2, ensure_ascii=False))
                except json.JSONDecodeError:
                    print("Output (Raw):")
                    print(result.stdout)
            else:
                print("Error:")
                print(result.stderr)
        
        except subprocess.TimeoutExpired:
            print("Error: Script execution timed out")
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    run_example()