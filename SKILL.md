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
| **L0** | Cloud Recall | MemOS Cloud plugin (*optional*) | Cross-device memory capture and recall |
| **L1** | Working Memory | `memory/YYYY-MM-DD.md` files | Daily summaries, todos, technical notes (30–90 day retention) |
| **L2** | Long-term Memory | `MEMORY.md` (read-only base) | Key facts, user profile, permanent decisions |

### Automated Pipelines

- **Dreaming (03:00 UTC daily)**: Scans conversation logs, evaluates candidates via DeepSeek analysis, promotes high-scoring insights to L2
- **Three-way Sync (18:00 / 20:00 / 22:00 CST)**: Keeps Cloud ↔ Markdown ↔ Vector stores in sync
- **Wiki Compilation (04:00 UTC daily, *optional*)**: Extracts entities and concepts, writes structured wiki vault pages

## Setup

### One-command auto-setup

```bash
bash scripts/auto-setup.sh
```

This script handles everything interactively:

| Step | What it does | Optional? |
|------|-------------|-----------|
| 1 | Install **Ollama** (standard or Intel edition) | Choose on-the-fly |
| 2 | Download **bge-m3** embedding model | — |
| 3 | Install **memory-core** plugin | — |
| 4 | Insert `memory-core` config into **openclaw.json** | Auto-insert with confirmation |
| 5 | Install and configure **MemOS Cloud** plugin with recommended settings | Skip if unwanted |
| 6 | Create `memory/` directory, check AGENTS.md | — |
| 7 | Set up Dreaming **cron job** (03:00 UTC daily) | — |

### Options

```bash
bash scripts/auto-setup.sh --skip-ollama   # Skip Ollama install (use your existing one)
bash scripts/auto-setup.sh --skip-memos    # Skip MemOS Cloud plugin entirely
bash scripts/auto-setup.sh --dry-run       # Preview without making changes
```

### Manual setup

See `references/setup-guide.md` for step-by-step manual configuration.

## When to Use

- Setting up OpenClaw memory for the first time
- Configuring memory-core plugin with local Ollama embedding
- Installing MemOS Cloud plugin for cross-device sync
- Setting up automatic Dreaming and promotion pipelines
- Configuring three-way sync between cloud, files, and vector DB

## Components

### 1. Memory Plugins (L0)

Configured via `openclaw.json`:

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
│   ├── YYYY-MM-DD.md          # Daily working memory (auto-indexed)
│   ├── MEMORY_INDEX.md        # Vector BM25 cluster summaries
│   ├── memos-cloud-*.md       # Cloud-pulled memory entries
│   ├── .sync-cloud-state.json # Cloud pull cursor
│   └── .sync-push-state.json  # Push state (SHA256 tracking)
├── MEMORY.md                  # Long-term memory base (read-only)
├── AGENTS.md                  # Runtime context + memory rules
└── SOUL.md                    # Agent persona
```

### 3. Sync Scripts (*optional*)

Located at `user_workspace/scripts/`:
- `sync-cloud-pull.py` — Pull from MemOS Cloud → Markdown files
- `sync-cloud-push.py` — Push local markdown changes → Cloud (SHA256 diff)
- `sync-vector-index.py` — Vector DB → MEMORY_INDEX.md (FTS5 BM25 clustering)
- `sync-all.sh` — Orchestrator that runs all three

See `references/sync-api.md` for MemOS Cloud API details.

## File Reference

- `references/architecture.md` — Detailed architecture documentation
- `references/setup-guide.md` — Complete manual setup guide with templates
- `references/sync-api.md` — MemOS Cloud API reference
- `scripts/auto-setup.sh` — One-command interactive setup (recommended)
