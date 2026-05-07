---
name: auto-memory
description: |
  自动对话记忆提取。读取最近会话语料，调用本地 LLM (qwen3:8b) 提取
  结构化记忆并更新 MEMORY.md + 工作日志 (memory/YYYY-MM-DD.md)。

  手动触发：说"提取记忆"、"同步记忆"、"收尾"、"整理记忆"
metadata:
  openclaw:
    emoji: "🧠"
---

# auto-memory — 自动对话记忆提取

## 概述

从最近的会话语料（session-corpus）中自动提取有价值的记忆，更新到：
- **MEMORY.md** — 长期记忆（用户画像、偏好、配置等）  
- **memory/YYYY-MM-DD.md** — 当日工作日志（完成/讨论/待跟进）

脚本每次只处理最近 1 天的会话，截取尾部 ~3.5KB 内容，确保本地 LLM 稳定输出。

## 触发方式

### 自动（Cron）
- 每天 18:30、20:30、22:30 各执行一次
- 挂载在 `memo-three-way-sync` cron 之后 30 分钟执行

### 手动
用户说以下任意命令触发：
- "提取记忆"
- "同步记忆"
- "收尾"
- "整理记忆"
- "auto-memory"
- "提取一下"

## 脚本

```
user_workspace/scripts/auto_memory_extract.py
```

### 模式

```bash
# 查看状态（显示待处理的会话文件）
python3 user_workspace/scripts/auto_memory_extract.py --mode status

# 干跑（执行 LLM 提取但不写入文件）
python3 user_workspace/scripts/auto_memory_extract.py --mode dry-run

# 完整执行（提取 + 写入）
python3 user_workspace/scripts/auto_memory_extract.py [--mode full]

# 指定天数
python3 user_workspace/scripts/auto_memory_extract.py --days 2
```

### 输出示例

```json
// 成功（有记忆变更）
{
  "status": "ok",
  "summary": {
    "add_count": 3,
    "update_count": 0,
    "remove_count": 0,
    "daily_entries": "[完成] ...\n[讨论] ..."
  },
  "memory_md_update": {"status": "ok", ...},
  "daily_log_update": {"status": "ok", ...}
}

// 跳过（无语料或语料过短）
{"status": "ok", "skipped": true, "message": "没有找到最近的会话语料"}
```

## 技术说明

- **LLM 模型**: qwen3:8b（本地 Ollama，免费）
- **API**: `POST /api/generate`（generate API 比 chat API 更适合思考型模型）
- **Prompt 策略**: 对话内容在前，指令在后（Qwen3 输出结构最稳定）
- **语料大小**: 截取至 ~3.5KB（Qwen3-8B 在较小输入 + 显式 JSON 格式时输出最准确）
- **输出过滤**: Prompt B 只提取 `[完成]`、`[讨论]`、`[待跟进]`、`[决策]` 开头的行
- **写入**: 使用 cross-platform-writer 脚本确保编码兼容
