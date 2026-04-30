# OpenClaw Memory Hub — Setup Guide

## Prerequisites

- OpenClaw >= v25.9.0
- Ollama running on `http://127.0.0.1:11434`
- bge-m3 model pulled: `ollama pull bge-m3`
- Node.js >= 18

## Step 1: Install memory-core Plugin

### Via OpenClaw CLI

```bash
openclaw plugins install memory-core
```

### Manual Config

Add to `openclaw.json`:

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
      }
    }
  }
}
```

Restart Gateway:

```bash
openclaw gateway restart
```

Verify status:

```bash
openclaw memory status
```

## Step 2: Install MemOS Cloud Plugin (Optional)

Required for cross-device memory sync.

### In `openclaw.json`:

```json
{
  "plugins": {
    "entries": {
      "memos-cloud-openclaw-plugin": {
        "config": {
          "url": "https://your-memos-server.com",
          "token": "your-memos-api-token"
        }
      }
    }
  }
}
```

## Step 3: Configure Runtime Files

### AGENTS.md — Memory Rules

Add to your `AGENTS.md`:

```markdown
## 🧠 Memory System

- **L0 Runtime Retrieval**: memory-core plugin (Ollama bge-m3 → SQLite-vec), semantic + BM25 hybrid
- **L1 Working Memory**: `memory/YYYY-MM-DD.md` files, 30-90 day retention
- **L2 Long-term Memory**: `MEMORY.md` read-only base
- **Dreaming**: Daily 03:00 UTC — auto-analyze and promote to L2
- **Writing Rules**: Important decisions → L1 log; "记住" → L1 + verify via memory_search
- **Lessons**: Update AGENTS.md / TOOLS.md
- **Errors**: `.learnings/ERRORS.md`

**MEMORY.md is read-only** — agent loads at bootstrap. New memories go to L1 files.
```

### SOUL.md — Core Identity

```markdown
## Continuity

Each session is a fresh start. These files _are_ your memory. Read them. Update them.

## Memory

- Use memory files for persistence, not session recall
- The Dreaming pipeline runs daily — no need to report it
- Trust the system: auto-indexing + daily promotion covers continuity
```

### TOOLS.md — Environment Config

```markdown
## 🧠 Memory System (memory-core)

- **Embedding backend**: Ollama (`http://127.0.0.1:11434`)
- **Embedding model**: `bge-m3` (1024-dim, multi-language)
- **Database**: `~/.openclaw/memory/main.sqlite`
- **Index**: `openclaw memory index --force`
- **Status**: `openclaw memory status`
- **Dreaming**: Daily 03:00 UTC
```

## Step 4: Set Up Cron Jobs

### Dreaming Pipeline (Daily 03:00 UTC)

```bash
# Using openclaw cron
openclaw cron add --name "dreaming-pipeline" \
  --schedule "0 3 * * *" \
  --agent-id "default" \
  --message "Run Dreaming pipeline: scan logs, extract insights, promote to MEMORY.md"
```

### Three-Way Sync (18:00, 20:00, 22:00 CST)

Place sync scripts in `user_workspace/scripts/`:

1. `sync-cloud-pull.py` — Pulls new entries from MemOS Cloud API
2. `sync-cloud-push.py` — Pushes local markdown changes to Cloud
3. `sync-vector-index.py` — Generates MEMORY_INDEX.md from vector DB
4. `sync-all.sh` — Orchestrator

Cron schedule (UTC):

```bash
# 10:00 / 12:00 / 14:00 UTC = 18:00 / 20:00 / 22:00 CST
0 10,12,14 * * * ~/.openclaw/workspace/user_workspace/scripts/sync-all.sh
```

## Step 5: Verify Setup

```bash
# Check memory status
openclaw memory status

# Force index
openclaw memory index --force

# List cron jobs
openclaw cron list

# Check logs
openclaw logs --follow --plain
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Embedding fails | Ollama not running | `ollama serve` |
| bge-m3 not found | Model not pulled | `ollama pull bge-m3` |
| Plugin not loaded | Restart needed | `openclaw gateway restart` |
| Slow search | Index stale | `openclaw memory index --force` |
| Cloud sync fails | Token expired | Refresh MemOS API token |
| Dreaming not running | Cron disabled | `openclaw cron list` → verify |
