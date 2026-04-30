#!/bin/bash
# setup-cron.sh — Set up Dreaming and Sync cron jobs for OpenClaw Memory Hub
# Usage: bash setup-cron.sh
# Requires: openclaw CLI, crontab access

set -euo pipefail

echo "=== OpenClaw Memory Hub — Cron Setup ==="

# 1. Verify openclaw CLI
if ! command -v openclaw &>/dev/null; then
    echo "ERROR: openclaw not found in PATH"
    exit 1
fi

SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="$(cd "$SCRIPTS_DIR/../../.." && pwd)"

echo "Workspace: $WORKSPACE"

# 2. Set up Dreaming cron via openclaw (daily 03:00 UTC)
echo ""
echo "[1/2] Setting up Dreaming pipeline (03:00 UTC daily)..."
openclaw cron add \
    --name "memory-dreaming-pipeline" \
    --schedule "0 3 * * *" \
    --agent-id "default" \
    --message "Run Dreaming pipeline: scan session logs, extract insights via DeepSeek analysis, promote high-scoring candidates to MEMORY.md" \
    --enabled true \
    2>/dev/null || echo "Cron already exists or scheduled via openclaw.json"

# 3. Set up three-way sync via system crontab (18/20/22 CST = 10/12/14 UTC)
echo "[2/2] Setting up three-way sync (18:00, 20:00, 22:00 CST)..."
SYNC_SCRIPT="$WORKSPACE/user_workspace/scripts/sync-all.sh"

if [ -f "$SYNC_SCRIPT" ]; then
    (crontab -l 2>/dev/null; echo "") | sort -u | crontab -

    # Check if sync cron already exists
    if crontab -l 2>/dev/null | grep -q sync-all; then
        echo "Sync cron already configured in system crontab"
    else
        (crontab -l 2>/dev/null; echo "# OpenClaw Memory Hub — Three-way sync (CST 18:00, 20:00, 22:00)") | crontab -
        (crontab -l 2>/dev/null; echo "0 10,12,14 * * * cd $WORKSPACE && bash $SYNC_SCRIPT >> $WORKSPACE/memory/sync-cron.log 2>&1") | crontab -
        echo "Sync cron added"
    fi

    # Show current crontab
    echo ""
    echo "Current crontab:"
    crontab -l 2>/dev/null || echo "(none)"
else
    echo "WARNING: $SYNC_SCRIPT not found"
    echo "Create sync scripts first, then run this script again"
fi

echo ""
echo "=== Cron Setup Complete ==="
echo ""
echo "To verify:"
echo "  openclaw cron list"
echo "  crontab -l"
