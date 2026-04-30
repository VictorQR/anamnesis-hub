# 🧠 OpenClaw Memory Hub

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![ClawHub](https://img.shields.io/badge/ClawHub-openclaw--memory--hub-blue)](https://clawhub.ai/skills/openclaw-memory-hub)

**Three-tier memory architecture for OpenClaw AI agents.**  
Persistent, automated, cross-device memory that never forgets who you are.

---

## One-Command Setup

```bash
# Clone and run
git clone https://github.com/VictorQR/openclaw-memory-hub.git
cd openclaw-memory-hub
bash scripts/auto-setup.sh
```

The interactive script handles everything:

| Step | What it does | Toggle |
|------|-------------|--------|
| ✅ | Install **Ollama** (standard or Intel) | `--skip-ollama` |
| ✅ | Download **bge-m3** embedding model | — |
| ✅ | **Plugin conflict check** (auto-detect subconscious-personality-guardian) | — |
| ✅ | Install **memory-core** plugin | — |
| ✅ | Configure **openclaw.json** | Auto-insert on confirm |
| ✅ | Install **MemOS Cloud** (*optional*) | `--skip-memos` |
| ✅ | Create `memory/` directory | — |
| ✅ | Set up **Dreaming cron** (03:00 UTC) | — |

```bash
# Preview mode
bash scripts/auto-setup.sh --dry-run

# Skip Ollama (already installed)
bash scripts/auto-setup.sh --skip-ollama

# Skip MemOS Cloud
bash scripts/auto-setup.sh --skip-memos
```

---

## Architecture

| Tier | Layer | Technology | Purpose |
|------|-------|-----------|---------|
| **L0** | Runtime Retrieval | memory-core + Ollama bge-m3 + SQLite-vec | Real-time semantic + BM25 hybrid search |
| **L0** | Cloud Recall | MemOS Cloud plugin (*optional*) | Cross-device memory capture & recall |
| **L1** | Working Memory | `memory/YYYY-MM-DD.md` | Daily summaries, notes, decisions |
| **L2** | Long-term Memory | `MEMORY.md` | Key facts, user profile, permanent truths |

### Automated Pipelines

| Pipeline | Schedule | Job |
|----------|----------|-----|
| **Dreaming** | 03:00 UTC daily | Scan logs → DeepSeek analysis → promote to L2 |
| **Three-Way Sync** | 18:00 / 20:00 / 22:00 CST (*optional*) | Cloud ↔ Markdown ↔ Vector alignment |
| **Wiki Compilation** | 04:00 UTC daily (*optional*) | Entity extraction → wiki vault pages |

---

## Installation via ClawHub

```bash
openclaw skills install openclaw-memory-hub
```

This loads the SKILL.md into your agent's context so it knows how to set up and maintain the memory system.

---

## Prerequisites

- [OpenClaw](https://openclaw.ai) >= 3.x
- Node.js >= 18
- Internet connection (for Ollama download and bge-m3 model)

---

## Skill Structure

```
openclaw-memory-hub/
├── SKILL.md                          # Main skill entry (loaded into agent context)
├── openclaw-memory-hub.skill         # Packaged .skill distribution file
├── scripts/
│   └── auto-setup.sh                 # One-command interactive setup script
├── references/
│   ├── architecture.md               # Full architecture documentation
│   ├── setup-guide.md                # Step-by-step manual guide
│   └── sync-api.md                   # MemOS Cloud API reference
└── README.md                         # This file
```

---

## How It Works

1. **Every conversation** is automatically indexed into the vector database
2. **Each session** retrieves relevant context via semantic + BM25 hybrid search
3. **Daily** the Dreaming pipeline analyzes logs and promotes insights to long-term memory
4. **Tri-hourly** (*optional*) the three-way sync keeps cloud, local files, and vector store aligned
5. **The Agent** never starts from scratch — it remembers you across sessions

---

## License

MIT — free to use, modify, and redistribute.

---

## Author

**VictorQR** — Open source OpenClaw memory infrastructure
