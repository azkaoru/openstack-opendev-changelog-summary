#!/bin/bash
# Test script for OpenStack OpenDev Changelog Summary

echo "=== OpenStack OpenDev Changelog Summary Test Script ==="
echo

# Test 1: Default configuration (dry run)
echo "Test 1: Default configuration (Barbican, 1 day, dry run)"
OPENDEV_DRY_RUN=true OPENDEV_LOG=true python3 get_changelog_summary.py
echo

# Test 2: Different repository (dry run)
echo "Test 2: Different repository (Nova, dry run)"
OPENDEV_REPO_NAME=openstack/nova OPENDEV_DRY_RUN=true OPENDEV_LOG=true python3 get_changelog_summary.py
echo

# Test 3: Different time range (dry run)
echo "Test 3: 7 days ago (dry run)"
OPENDEV_AGE=7d OPENDEV_DRY_RUN=true OPENDEV_LOG=true python3 get_changelog_summary.py
echo

# Test 4: Open status (dry run)
echo "Test 4: Open status (dry run)"
OPENDEV_STATUS=open OPENDEV_DRY_RUN=true OPENDEV_LOG=true python3 get_changelog_summary.py
echo

# Test 5: Specific date (dry run)
echo "Test 5: Specific date (dry run)"
OPENDEV_AFTER=2025-01-01 OPENDEV_DRY_RUN=true OPENDEV_LOG=true python3 get_changelog_summary.py
echo

echo "=== All tests completed ==="
echo "Note: All tests run in dry run mode to avoid network calls in test environment"