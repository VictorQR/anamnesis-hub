---
name: openclaw-memory-hub
description: "四层记忆架构 (Four-tier memory architecture for OpenClaw AI agents). 提供 L0 运行时语义检索 (Ollama bge-m3 + SQLite-vec 向量库)、L1 工作记忆 (每日 Markdown 日志)、L2 长期记忆 (MEMORY.md 索引 + ARCHIVE.md 档案 + facts.db 结构化知识图谱)、Dreaming 自动化提炼管线、三方同步 (Cloud ↔ Markdown ↔ Vector)、Active Memory 主动召回、auto-memory v3 两阶段提取 (ARCHIVE.md 归档 → MEMORY.md 摘要)、cross-platform-writer 跨平台写入。适用于首次配置持久化记忆、安装 memory-core/MemOS Cloud 插件、搭建多层记忆系统。"
version: 1.11.0
---

# OpenClaw Memory Hub

Four-tier memory architecture with automated Dreaming pipeline, three-way synchronization, Active Memory recall, and two-stage auto-extraction.

## Overview

| Tier | Layer | Technology | Purpose |
|------|-------|-----------|---------|
| **L0** | Runtime Retrieval | memory-core plugin (Ollama bge-m3 → SQLite + sqlite-vec) | Real-time semantic + BM25 hybrid search |
| **L0** | Cloud Recall | MemOS Cloud plugin (*optional*) | Cross-device memory capture and recall |
| **L0** | Active Memory | Built-in OpenClaw plugin | Pre-reply sub-agent memory search + context injection |
| **L1** | Working Memory | `memory/YYYY-MM-DD.md` files | Daily summaries, todos, technical notes |
| **L2a** | Long-term Index | `MEMORY.md` (~90 lines, read-only base) | Bidirectional index → ARCHIVE.md, 0% Auto-Extracted pollution |
| **L2b** | Detailed Archive | `ARCHIVE.md` (~220 lines) | Full records with ← MEMORY.md:XX reverse references |
| **L2c** | Structured KB | `facts.sqlite` (entity/key/value) | Precise lookup for IPs, ports, versions; activation/decay tracking |

### Automated Pipelines

| Pipeline | Schedule | Description |
|----------|----------|-------------|
| **Dreaming** | 03:00 UTC daily | Scan logs → DeepSeek analysis → promote to L2 |
| **Three-way Sync** | 18:00 / 20:00 / 22:00 CST | Cloud ↔ Markdown ↔ Vector alignment |
| **auto-memory v3** | 18:30 / 22:30 CST | Read MemOS Cloud facts → qwen3 filter → **Stage1: ARCHIVE.md (SHA-256 dedup)** → **Stage2: MEMORY.md (one-line summary)** |
| **Workspace Cleaner** | 19:00 CST | Auto-clean working directory |
| **DeepSeek Analysis** | 20:30 CST | Deep historical session analysis → DB |

### Memory Flow (v3: Two-Stage Pipeline)

```
agent_end → MemOS Cloud (real-time capture + cloud LLM extraction)
              ↓
        sync-cloud-pull.py (18/20/22 CST)
              ↓
        user_workspace/memos-cloud-cache/
              ↓
        auto-memory.py → qwen3 filter + memos-extractor-0.6b
              ↓
        ┌─ Stage 1: ARCHIVE.md (完整归档, SHA-256 去重)
        └─ Stage 2: MEMORY.md (一行摘要, 不写入详细内容)

before_agent_start → MemOS Cloud recall
                  + Active Memory sub-agent
                  + memory-core (bge-m3 + BM25)
              ↓
        Layered context injected before reply
```

## Bundled Skills

This package includes two auxiliary skills:

### 1. cross-platform-writer

**Path**: `skills/cross-platform-writer/`
**Script**: `skills/cross-platform-writer/scripts/write_file.py`

Replaces OpenClaw's built-in `write` tool for text file creation. Auto-detects encoding (utf-8/utf-8-sig/gbk), handles BOM, and adapts line endings (CRLF/LF) per platform.

When writing text files: write to temp → run `write_file.py` → cleanup.

### 2. auto-memory

**Path**: `skills/auto-memory/`
**Script**: `scripts/auto_memory_extract.py`

Reads the latest MemOS Cloud synced facts (`memos-cloud-YYYY-MM-DD.md`), filters noise (system crons, duplicates), and uses local qwen3:8b to extract structured long-term memories into `MEMORY.md`.

Manual trigger: "提取记忆" / "同步记忆" / "整理记忆"
Cron: 18:30 / 22:30 CST (`30 18,22 * * *`)

## Setup

### One-command auto-setup

```bash
bash scripts/auto-setup.sh
```

### Options

```bash
bash scripts/auto-setup.sh --skip-ollama   # Skip Ollama install
bash scripts/auto-setup.sh --skip-memos    # Skip MemOS Cloud
bash scripts/auto-setup.sh --dry-run       # Preview only
```

### Manual setup

See `references/setup-guide.md` for step-by-step manual configuration.

## When to Use

- Setting up OpenClaw memory for the first time
- Configuring memory-core plugin with local Ollama embedding
- Installing MemOS Cloud plugin for cross-device sync
- Enabling Active Memory for pre-reply context injection
- Setting up auto-memory pipeline for MEMORY.md curation
- Installing cross-platform-writer for cross-OS file compatibility
- Configuring automatic Dreaming and promotion pipelines
- Setting up three-way sync between cloud, files, and vector DB

## Plugin Conflicts

### ❌ subconscious-personality-guardian ↔ memory-core

**Incompatible.** Both use the same OpenClaw memory slot.

**Fix**: Disable in openclaw.json:
```json
{
  "plugins": {
    "disabled": ["subconscious-personality-guardian"],
    "deny": ["subconscious-personality-guardian"]
  }
}
```

### ✅ memory-core + MemOS Cloud

**Compatible — designed to work in layers.**

```
User message → MemOS Cloud (static facts) → memory-core (recent context)
```

### ✅ Active Memory + MemOS Cloud + memory-core

**Compatible — triple-layer recall.**

```
User message
  → Active Memory sub-agent (searches all memory stores)
  → MemOS Cloud (injects long-term facts & preferences)
  → memory-core (semantic + BM25 hybrid retrieval)
  → Agent receives layered context
```

### ✅ auto-memory + MemOS Cloud + memos-extractor

**Designed to work together.** MemOS captures at `agent_end`, syncs to local files, then auto-memory reads those files for MEMORY.md curation. v1.10 adds a second channel: memos-extractor-0.6b API (MemOS self-developed model) returns structured facts + preferences, cross-validated against qwen3 output.

## Components

### 1. Memory Plugins (L0)

See `references/architecture.md` for full configuration.

### 2. Memory Files (L1 + L2)

```
~/.openclaw/workspace/
├── memory/
│   ├── YYYY-MM-DD.md          # Daily working memory (auto-indexed)
│   ├── MEMORY_INDEX.md        # Vector BM25 cluster summaries
│   └── .sync-*.json           # Sync state files
├── MEMORY.md                  # Long-term memory base
├── AGENTS.md                  # Runtime context + memory rules
└── user_workspace/
    ├── memos-cloud-cache/         # v1.10: Cloud-pulled memory (isolated from index)
    │   └── memos-cloud-*.md       #     Auto-clean >7 days
    ├── scripts/
    │   ├── auto_memory_extract.py  # auto-memory v2 (dual-channel)
    │   └── sync-*.py               # Sync scripts
    └── skills/
        ├── cross-platform-writer/  # Encoding-safe file writer
        └── auto-memory/            # Auto extraction skill
```

### 3. Sync Scripts

Located at `user_workspace/scripts/`:
- `sync-cloud-pull.py` — Pull from MemOS Cloud → memos-cloud-cache/ (v1.10: isolated from memory/)
- `sync-cloud-push.py` — Push local markdown changes → Cloud (SHA256 diff)
- `sync-vector-index.py` — Vector DB → MEMORY_INDEX.md (FTS5 BM25 clustering)
- `sync-all.sh` — Orchestrator: pull → push → vector-index → cache cleanup (>7d) → reindex
- `auto_memory_extract.py` — auto-memory v2 extraction (dual-channel: qwen3 + memos-extractor)

See `references/sync-api.md` for MemOS Cloud API details.

## File Reference

- `references/architecture.md` — Detailed architecture documentation
- `references/setup-guide.md` — Complete manual setup guide with templates
- `references/sync-api.md` — MemOS Cloud API reference
- `scripts/auto-setup.sh` — One-command interactive setup
- `scripts/auto_memory_extract.py` — auto-memory v2 script
- `skills/cross-platform-writer/` — Cross-platform text file writer skill
- `skills/auto-memory/` — Auto memory extraction skill
