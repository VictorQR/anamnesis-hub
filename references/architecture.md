# OpenClaw Memory Hub — Architecture

## Design Principles

1. **Local-first**: Primary storage is local SQLite + markdown files; cloud is sync target, not source of truth
2. **Progressive disclosure**: L0 catches everything, L1 structures daily context, L2 curates what matters
3. **Zero-latency retrieval**: bge-m3 embedding runs on local Ollama; no API latency
4. **Multi-language**: bge-m3 supports 100+ languages, 1024-dim vectors
5. **DAG-based composition**: memory-core uses DAG for multi-agent memory lineage

## Three-Tier Architecture

```
┌─────────────────────────────────────────────┐
│                L0 — Runtime                  │
│  ┌─────────────────┐  ┌──────────────────┐  │
│  │  memory-core     │  │  MemOS Cloud     │  │
│  │  (Ollama bge-m3) │  │  (Cloud Recall)  │  │
│  │  SQLite + vec    │  │  Lifecycle hooks │  │
│  └────────┬────────┘  └────────┬─────────┘  │
│           │                     │            │
│  ┌────────▼─────────────────────▼─────────┐  │
│  │  Hybrid Search (semantic + BM25)       │  │
│  └────────────────┬───────────────────────┘  │
└───────────────────┼──────────────────────────┘
                    │
┌───────────────────▼──────────────────────────┐
│              L1 — Working Memory              │
│  memory/YYYY-MM-DD.md (30-90 day retention)  │
│  - Daily conversation summaries              │
│  - Technical notes & decisions               │
│  - TODOs & reminders                         │
│  - Hand-editable, human-readable             │
└───────────────────┬──────────────────────────┘
                    │  Dreaming pipeline
                    │  (Daily 03:00 UTC)
                    ▼
┌──────────────────────────────────────────────┐
│           L2 — Long-term Memory               │
│  MEMORY.md (read-only base, auto-curated)     │
│  - Key user facts & profile                   │
│  - Permanent decisions & preferences          │
│  - Encrypted sensitive info (SHA-256)         │
│  - Promoted high-scoring insights             │
└──────────────────────────────────────────────┘
```

## Memory Plugins

### memory-core (Primary)

- **Provider**: OpenClaw Plugin Registry
- **Embedding Backend**: Ollama (`http://127.0.0.1:11434`)
- **Model**: `bge-m3` (BAAI, 1024-dimension, multi-language)
- **Vector Storage**: SQLite + sqlite-vec extension
- **Search**: Semantic vector similarity + BM25 keyword hybrid
- **Database**: `~/.openclaw/memory/main.sqlite`
- **Indexing**: Automatic on file save; manual via `openclaw memory index --force`

### MemOS Cloud Plugin (Supplementary)

- **Lifecycle Hook**: Captures and recalls memory via `POST /api/memo` hooks
- **Recall**: Injects relevant memory context into session at bootstrap
- **Cross-device**: Syncs memory across multiple OpenClaw instances

## Dual-Plugin Collaborative Workflow

This is the core innovation of the architecture — **two plugins working in layers, not competing**:

```
User sends message → Gateway receives
         │
         ▼
┌─────────────────────────────────────────────┐
│ 1. MemOS Cloud Plugin                       │
│    (before_agent_start lifecycle hook)       │
│                                              │
│    → Injects:                                │
│      • Long-term facts ("User rides a 703F") │
│      • User preferences ("Hates sweets")     │
│      • Profile constants ("Name is Victor")  │
│                                              │
│    Layer: Static / low-frequency truths      │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ 2. memory-core                               │
│    (Runtime semantic retrieval)               │
│                                              │
│    → Injects:                                │
│      • Recent conversation snippets          │
│      • Topically relevant past discussions   │
│      • Working memory (today's context)      │
│                                              │
│    Layer: Dynamic / high-frequency context   │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ Agent receives complete memory context:      │
│                                              │
│  "Victor rides a 703F" (fact — MemOS)        │
│  + "Yesterday discussed Zettelkasten"        │
│    (recent — memory-core)                    │
│  + "Today's weather forecast" (today — L1)  │
└─────────────────────────────────────────────┘
```

### Division of Responsibility

| Aspect | MemOS Cloud | memory-core |
|--------|-------------|-------------|
| **Data type** | Facts, preferences, profile | Conversations, working context |
| **Frequency** | Static / rarely changes | Dynamic / every session |
| **Source** | Cloud API (`POST /api/memo`) | Local SQLite-vec index |
| **Trigger** | `before_agent_start` hook | Runtime semantic query |
| **Retention** | Permanent (cloud) | Configurable (last N chunks) |
| **Scope** | Cross-device, long-term | Single device, recent history |
| **Conflict** | None — complementary | None — complementary |

### Why This Works

- **No overlap**: MemOS handles 

## File Anatomy

### Runtime Context Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Memory rules, safe operation protocol, execution guidelines |
| `SOUL.md` | Agent persona, core principles, independent values |
| `USER.md` | User profile, preferences, communication style |
| `TOOLS.md` | Environment-specific configuration, known issues |
| `MEMORY.md` | Long-term facts (L2), read-only base loaded at bootstrap |

### Daily Memory Files

```
memory/
├── YYYY-MM-DD.md          # Day's conversation log, key decisions
├── MEMORY_INDEX.md         # Auto-generated vector BM25 summary
├── memos-cloud-*.md        # Cloud-pulled memory (read-only cache)
├── .sync-cloud-state.json  # Cloud pull cursor (last fetch timestamp)
├── .sync-push-state.json   # Cloud push state (SHA256 per file)
└── DREAMS.md              # Latest Dreaming analysis output
```

## Automated Pipelines

### Dreaming Pipeline

Runs daily at **03:00 UTC** (11:00 CST):

1. **REM Backfill**: Scans recent session logs, extracts structured facts
2. **DeepSeek Analysis**: Runs AI analysis on extracted facts:
   - Preference changes
   - Lessons learned
   - Relationship updates
   - Project criteria
3. **Dreaming Promotion**: Evaluates candidates against threshold (minScore: 0.8, max 10 items) and promotes to MEMORY.md

Output delivered via QQ:
- 📄 REM Backfill: status report
- 🔬 DeepSeek 分析: extracted insights count
- 🌙 Dreaming Promotion: promoted count

### Three-Way Sync

Runs at **18:00 / 20:00 / 22:00 CST** (covering user active hours 19–23):

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│  Cloud   │◄──►│Markdown  │◄──►│  Vector  │
│ (Memos)  │    │ (Files)  │    │ (SQLite) │
└──────────┘    └──────────┘    └──────────┘
     │               │               │
     │  sync-pull    │  sync-push    │  sync-index
     ▼               ▼               ▼
  memos-cloud*.md → Cloud API     MEMORY_INDEX.md
```

**Sync Rules**:
- Cloud → MD: New/changed entries since last pull (cursor-based)
- MD → Cloud: SHA256 hash comparison, push only changed files
- Vector → MD: FTS5 BM25 clustering, score > 0.65, grouped by source_file
- Excluded from push: `memos-cloud-*.md`, `MEMORY_INDEX.md`, `DREAMS.md`, `.sync-*.json`

### Wiki Compilation (Planned)

Runs daily at **04:00 UTC** after Dreaming completes:

- Scan memory-core DB + latest Dreaming output
- Extract new entities, concepts, syntheses
- Deduplicate via fuzzy filename matching
- Write new wiki vault pages
- Report new page count only

## Sensitive Information

SHA-256 hashing with salt `VictorQR_7x9K2mP` for:

- Passwords & verification hashes
- Phone numbers, ID numbers
- Email addresses (all accounts)
- Social media IDs (WeChat, QQ, Douyin)

Stored in `MEMORY.md` hash table, verified by SHA-256 comparison before access.

## Known Conflicts & Compatibility

### ❌ subconscious-personality-guardian ↔ memory-core

**Status: Incompatible**

Both plugins attempt to use the same OpenClaw memory slot. Installing both causes:
- Memory write conflicts (race conditions on save)
- Retrieval logic duplication (both inject into context)
- Context management conflicts (duplicate or conflicting memory context in prompts)

**Fix**: Disable or remove `subconscious-personality-guardian`:
```json
// openclaw.json
{
  "plugins": {
    "disabled": ["subconscious-personality-guardian"],
    "deny": ["subconscious-personality-guardian"]
  }
}
```

### ✅ memory-core + MemOS Cloud Plugin

**Status: Compatible — designed to work in layers**

They are **not competing** memory systems. They operate at different layers with different responsibilities:

| | memory-core | MemOS Cloud |
|--|-------------|-------------|
| Role | Recent/working context | Long-term facts & preferences |
| Data | Conversations, discussions | User profile, habits, decisions |
| Timing | Every session (runtime query) | Session start (lifecycle hook) |
| Storage | Local SQLite-vec | Remote cloud API |

**Execution order**:
1. MemOS Cloud fires `before_agent_start` → injects static facts
2. memory-core queries local vector DB → injects dynamic context
3. Agent receives layered memory: "who the user is" + "what we talked about recently"

**No overlap**: One handles local retrieval, the other handles cloud sync. Both should be enabled simultaneously for best results.

### ⚠️ MemOS Cloud Plugin + ReMe

**Status: Potentially conflicting**

Both provide cloud memory functionality. Installing both may cause:
- File layer overlap (both write to `memory/`)
- Retrieval logic duplication
- API endpoint conflicts (competing memory services)

**Recommendation**: Choose one. MemOS Cloud is recommended if using OpenClaw natively.

## Performance Characteristics

- **Embedding speed**: ~50ms per query on RTX 4070 Super (12GB VRAM)
- **Database size**: ~100MB for 10K+ memory chunks
- **Hybrid search latency**: <100ms for top-10 results
- **Dreaming pipeline**: ~30 seconds per full run
- **Sync run**: ~10 seconds per direction
