# 🧠 OpenClaw Memory Hub

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![ClawHub](https://img.shields.io/badge/ClawHub-openclaw--memory--hub-blue)](https://clawhub.ai/skills/openclaw-memory-hub)

**Three-tier memory architecture for OpenClaw AI agents.**  
Persistent, automated, cross-device memory that never forgets.

---

## 中文简介

OpenClaw Memory Hub 是一套面向 OpenClaw AI Agent 的**三层记忆架构**，解决跨会话的"AI 失忆"问题：

| 层级 | 功能 | 技术栈 |
|------|------|--------|
| **L0** 运行时检索 | 语义 + BM25 混合搜索，实时注入上下文 | memory-core + Ollama bge-m3 + SQLite-vec |
| **L0** 云召回 *可选* | 多设备记忆同步，跨实例共享 | MemOS Cloud 插件 |
| **L1** 工作记忆 | 按日归档的 Markdown 日志，人工可编辑 | `memory/YYYY-MM-DD.md` |
| **L2** 长期记忆 | 持久化事实、用户画像、永久决策 | `MEMORY.md`（只读基底） |

**自动化管线**：Dreaming（每日 UTC 03:00 自动分析会话 → 提炼 → 提升至 L2）、三方同步（Cloud ↔ 文件 ↔ 向量库）、Wiki 编译（实体提取 → 知识库）。

一行命令部署：`bash scripts/auto-setup.sh`

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
| ✅ | Configure **openclaw.json** with optimized defaults | Auto-insert on confirm |
| ✅ | Install **MemOS Cloud** (*optional*) with full recommended config | `--skip-memos` |
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
