# 🧠 OpenClaw Memory Hub

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-3.x-blue)](https://openclaw.ai)

**Three-tier memory architecture for OpenClaw AI agents.**  
Persistent, automated, cross-device memory that never forgets who you are.

---

## Architecture

| Tier | Layer | Technology | Purpose |
|------|-------|-----------|---------|
| **L0** | Runtime Retrieval | memory-core + Ollama bge-m3 + SQLite-vec | Real-time semantic + BM25 hybrid search |
| **L0** | Cloud Recall | MemOS Cloud plugin | Cross-device memory capture & recall |
| **L1** | Working Memory | `memory/YYYY-MM-DD.md` | Daily summaries, notes, decisions |
| **L2** | Long-term Memory | `MEMORY.md` | Key facts, user profile, permanent truths |

### Automated Pipelines

| Pipeline | Schedule | Job |
|----------|----------|-----|
| **Dreaming** | 03:00 UTC daily | Scan logs → extract insights → promote to L2 |
| **Three-Way Sync** | 18/20/22 CST | Cloud ↔ Markdown ↔ Vector alignment |
| **Wiki Compilation** | 04:00 UTC daily | Entity extraction → wiki vault pages |

---

## Installation

### Option 1: ClawHub (recommended)

```bash
openclaw skills install openclaw-memory-hub
```

### Option 2: From this repo

```bash
git clone https://github.com/VictorQR/openclaw-memory-hub.git
cd openclaw-memory-hub
openclaw skills install ./openclaw-memory-hub.skill
```

### Option 3: Manual copy

Copy `openclaw-memory-hub` folder to your OpenClaw skills directory:

```bash
cp -r openclaw-memory-hub ~/.openclaw/workspace/skills/
```

---

## Quick Start

```bash
# 1. Run the memory-core setup script
bash scripts/setup-memory-core.sh

# 2. Set up cron jobs for Dreaming + Sync
bash scripts/setup-cron.sh

# 3. Verify everything works
openclaw memory status
openclaw memory index --force
```

See `references/setup-guide.md` for full configuration guide.

---

## Prerequisites

- [OpenClaw](https://openclaw.ai) >= 3.x
- [Ollama](https://ollama.ai) with [bge-m3](https://ollama.com/library/bge-m3) model pulled
- Node.js >= 18

---

## Skill Structure

```
openclaw-memory-hub/
├── SKILL.md                          # Main skill entry point (loaded into context)
├── openclaw-memory-hub.skill         # Packaged distribution file
├── references/
│   ├── architecture.md              # Full architecture documentation
│   ├── setup-guide.md               # Step-by-step installation guide
│   └── sync-api.md                  # MemOS Cloud API reference
└── scripts/
    ├── setup-memory-core.sh         # One-click memory-core + Ollama setup
    └── setup-cron.sh                # Cron configuration for pipelines
```

---

## How It Works

1. **Every conversation** is automatically indexed into the vector database
2. **Each session** retrieves relevant context via semantic + BM25 hybrid search
3. **Daily** the Dreaming pipeline analyzes logs and promotes insights to long-term memory
4. **Tri-hourly** the three-way sync keeps cloud, local files, and vector store aligned
5. **The Agent** never starts from scratch — it remembers you across sessions

---

## License

MIT — free to use, modify, and redistribute.

---

## Author

**VictorQR** — Open source OpenClaw memory infrastructure
