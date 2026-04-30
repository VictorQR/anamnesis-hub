#!/bin/bash
# setup-memory-core.sh — Install and configure memory-core plugin for OpenClaw
# Usage: bash setup-memory-core.sh

set -euo pipefail

echo "=== OpenClaw Memory Hub — memory-core Setup ==="

# 1. Check prerequisites
echo "[1/5] Checking prerequisites..."

if ! command -v openclaw &>/dev/null; then
    echo "ERROR: openclaw not found in PATH"
    exit 1
fi

if ! curl -s http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    echo "WARNING: Ollama not detected at http://127.0.0.1:11434"
    echo "Start Ollama with: ollama serve"
fi

# 2. Pull bge-m3 model if needed
echo "[2/5] Checking bge-m3 embedding model..."
if ! ollama list 2>/dev/null | grep -q bge-m3; then
    echo "Pulling bge-m3 model (this may take a minute)..."
    ollama pull bge-m3
fi

# 3. Install memory-core plugin
echo "[3/5] Installing memory-core plugin..."
openclaw plugins install memory-core 2>/dev/null || echo "Plugin already installed or installed via openclaw.json"

# 4. Create memory directory structure
echo "[4/5] Creating memory directory structure..."
WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
mkdir -p "$WORKSPACE/memory"

# 5. Verify status
echo "[5/5] Verifying setup..."
openclaw memory status 2>/dev/null || echo "Run 'openclaw gateway restart' and retry"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Restart Gateway:  openclaw gateway restart"
echo "  2. Check status:     openclaw memory status"
echo "  3. Force index:      openclaw memory index --force"
echo ""
echo "See references/setup-guide.md for full configuration."
