---
name: openclaw-memory-hub
description: "Three-tier memory architecture for OpenClaw AI agents. Provides L0 runtime semantic retrieval (Ollama bge-m3 + SQLite-vec vector store), L1 working memory (daily markdown logs), L2 long-term memory (curated base file), Dreaming pipeline for automatic insight promotion, and three-way sync (Cloud ↔ Markdown ↔ Vector). Use when setting up persistent agent memory, configuring memory plugins, or building multi-layered memory systems for OpenClaw."
---

# OpenClaw Memory Hub

Three-tier memory architecture with automated Dreaming pipeline and three-way synchronization.

## Overview

This architecture solves AI amnesia across sessions by layering memory at three levels:

| Tier | Layer | Technology | Purpose |
|------|-------|-----------|---------|
| **L0** | Runtime Retrieval | memory-core plugin (Ollama bge-m3 → SQLite + sqlite-vec) | Real-time semantic + BM25 hybrid search |
| **L0** | Cloud Recall | MemOS Cloud plugin | Cross-device memory capture and recall |
| **L1** | Working Memory | `memory/YYYY-MM-DD.md` files | Daily summaries, todos, technical notes (30–90 day retention) |
| **L2** | Long-term Memory | `MEMORY.md` (read-only base) | Key facts, user profile, permanent decisions |

### Automated Pipelines

- **Dreaming (03:00 UTC daily)**: Scans conversation logs, evaluates candidates, promotes high-scoring insights to L2
- **Three-way Sync (18:00 / 20:00 / 22:00 CST)**: Keeps Cloud ↔ Markdown ↔ Vector stores in sync
- **Wiki Compilation (04:00 UTC daily)**: Extracts entities and concepts, writes structured wiki vault

## When to Use

- Setting up OpenClaw memory for the first time
- Configuring memory-core plugin with local embedding
- Installing MemOS Cloud plugin for cross-device sync
- Setting up automatic Dreaming and promotion pipelines
- Configuring three-way sync between cloud, files, and vector DB

## Components

### 1. Memory Plugins (L0)

Configured in `openclaw.json`:

```json
{
  "plugins": {
    "entries": {
      "memory-core": {
        "config": {
          "embeddingUrl": "http://127.0.0.1:11434/api/embed",
          "embeddingModel": "bge-m3",
          "dimension": 1024
        }
      },
      "memos-cloud-openclaw-plugin": {
        "config": {
          "url": "https://your-memos-server",
          "token": "your-token"
        }
      }
    }
  }
}
```

### 2. Memory Files (L1 + L2)

```
~/.openclaw/workspace/
├── memory/
│   ├── YYYY-MM-DD.md          # Daily working memory
│   ├── MEMORY_INDEX.md        # Vector BM25 cluster summaries
│   ├── memos-cloud-*.md       # Cloud-pulled memory entries
│   ├── .sync-cloud-state.json # Sync state tracking
│   └── .sync-push-state.json  # Push state tracking
├── MEMORY.md                  # Long-term memory base (read-only)
├── AGENTS.md                  # Runtime context + memory rules
├── TOOLS.md                   # Environment-specific configuration
└── SOUL.md                    # Agent persona
```

### 3. Sync Scripts

Located at `user_workspace/scripts/`:
- `sync-cloud-pull.py` — Pull from MemOS Cloud → markdown files
- `sync-cloud-push.py` — Push local markdown → MemOS Cloud (SHA256 diff)
- `sync-vector-index.py` — Extract vector DB → MEMORY_INDEX.md (FTS5 BM25 clustering)
- `sync-all.sh` — Orchestrator that runs all three

See `references/setup-guide.md` for complete installation and configuration.

## Setup

For new installations, run:

```bash
# 1. Install memory-core plugin
scripts/setup-memory-core.sh

# 2. Install MemOS Cloud plugin (optional, for cross-device sync)
#    Configure URL and token in openclaw.json

# 3. Set up cron jobs for Dreaming and Sync
scripts/setup-cron.sh

# 4. Configure runtime files: AGENTS.md, SOUL.md, TOOLS.md
#    See references/setup-guide.md for templates
```

## File Reference

- `references/architecture.md` — Detailed architecture documentation
- `references/setup-guide.md` — Complete setup guide with templates
- `references/sync-api.md` — MemOS Cloud API reference
- `scripts/setup-memory-core.sh` — One-command memory-core installation
- `scripts/setup-cron.sh` — Cron job setup for Dreaming + Sync
