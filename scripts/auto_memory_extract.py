#!/usr/bin/env python3
"""
auto-memory-extract — 自动记忆提取 v2

从 MemOS Cloud 已提取的结构化事实中，用本地 qwen3 精加工后写入 MEMORY.md。

流程:
  MemOS agent_end → 云端 LLM 提取 → sync 30min 拉回本地
                                      ↓
                            memos-cloud-YYYY-MM-DD.md
                            （已提取好但含大量噪声）
                                      ↓
                            本脚本：qwen3 过滤+去重+格式化
                                      ↓
                            MEMORY.md（只有高度相关的长期记忆）

用法:
  python3 auto_memory_extract.py [--mode full|status|dry-run] [--days 1]
"""

import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# ── 路径配置 ──────────────────────────────────────────────────────────────────

WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE / "memory"
MEMORY_MD = WORKSPACE / "MEMORY.md"
WRITER_SCRIPT = (
    WORKSPACE
    / "user_workspace"
    / "skills"
    / "cross-platform-writer"
    / "scripts"
    / "write_file.py"
)

# qwen3 本地调用
OLLAMA_BASE = "http://127.0.0.1:11434"
LLM_MODEL = "qwen3:8b"

# ── 噪音过滤关键词（标题中包含这些的条目跳过不处理） ────────────────────────

NOISE_KEYWORDS = [
    "Cron delivery check", "Cron delivery process",
    "OpenClaw doctor", "Dreams of a rack", "Dashboard URL",
    "Wiki同步", "Cron delivery result",
    "无待投递", "已搬运", "heartbeat",
    "HEARTBEAT", "cron-delivery",
    "/get/memory 获取", "sync-cloud",
    "已确认", "确认工作", "确认通知",
    "Home Assistant 版本",
]

# ── Prompt（精简：只需去重+格式化） ──────────────────────────────────────────

EXTRACT_PROMPT = """你是一个记忆整理助手。我已从 MemOS Cloud 中拉回已提取好的事实和偏好，其中有大量系统级噪音（如 cron 检测、重复记录等），也有少量真正值得写入长期记忆（MEMORY.md）的用户信息。

任务：
1. 过滤掉噪音（cron 检测、系统自动任务、重复记录等）
2. 识别出真正有价值的用户记忆：偏好、习惯、配置、项目决策、重要事件
3. 与已有 MEMORY.md 对比去重（完全相同的内容不重复写入）

已有 MEMORY.md 内容：
```
{memory_md}
```

待处理的新记忆（已从 MemOS Cloud 拉取）：
```
{memos_entries}
```

输出格式（只输出 JSON，不要任何其他文字）：
{{"add":[{{"category":"分类","content":"具体事实"}}],"update":[],"remove":[]}}

分类建议：偏好/习惯、兴趣/爱好、项目/工作、技术/配置、设备/环境、社交/关系、计划/目标、重要事件
原则：宁少勿多，不确定的条目不输出；无有价值信息则输出 {{"add":[],"update":[],"remove":[]}}"""


# ── 工具函数 ──────────────────────────────────────────────────────────────────

def call_llm(prompt: str, max_tokens: int = 2000) -> str:
    """通过本地 Ollama 调用 qwen3"""
    payload = json.dumps({
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": max_tokens, "temperature": 0},
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{OLLAMA_BASE}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("response", "").strip()
    except Exception as e:
        print(json.dumps({"status": "error", "step": "llm_call", "message": str(e)}), file=sys.stderr)
        return ""


def parse_extraction_result(text: str) -> dict:
    """解析 JSON 输出"""
    code_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if code_match:
        text = code_match.group(1)
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start:end+1]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"add": [], "update": [], "remove": []}


def read_memos_cloud(days: int = 1) -> str:
    """
    读取最新的 memos-cloud-YYYY-MM-DD.md 文件的最新同步批次。
    只处理最后一次同步拉取的新记忆（避免重复处理历史记忆）。
    """
    today = datetime.now().astimezone()
    entries = []

    for d in range(days):
        date_str = (today - __import__("datetime").timedelta(days=d)).strftime("%Y-%m-%d")
        path = MEMORY_DIR / f"memos-cloud-{date_str}.md"
        if not path.exists():
            continue

        content = path.read_text(encoding="utf-8", errors="replace")

        # 只处理最后一个同步批次（最新拉取的记忆）
        last_sync = content.rfind("# MemOS Cloud 同步 @")
        if last_sync < 0:
            continue
        content = content[last_sync:]

        # 解析该批次内的条目
        lines = content.split("\n")
        current_title = None
        current_time = None
        current_text = None

        for line in lines:
            title_m = re.match(r"^### (.+)", line)
            if title_m:
                if current_title and current_text and current_time:
                    if not any(kw.lower() in current_title.lower() for kw in NOISE_KEYWORDS):
                        entries.append(f"[{current_time}] {current_title} → {current_text[:200]}")
                current_title = title_m.group(1)
                current_time = None
                current_text = None
                continue

            time_m = re.match(r"^- 类型: \S+\s+\|\s+记录时间:\s+(.+)", line)
            if time_m and current_title:
                current_time = time_m.group(1).strip()
                continue

            if current_title and current_time and line.startswith("- ") and "类型:" not in line:
                current_text = line[2:].strip()

        # 最后一条
        if current_title and current_text and current_time:
            if not any(kw.lower() in current_title.lower() for kw in NOISE_KEYWORDS):
                entries.append(f"[{current_time}] {current_title} → {current_text[:200]}")

    seen = set()
    unique = []
    for e in entries:
        if e not in seen:
            seen.add(e)
            unique.append(e)

    return "\n".join(unique) if unique else ""


def read_memory_md() -> str:
    try:
        return MEMORY_MD.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "# 长期记忆\n"


def merge_memory_md(current_md: str, operations: dict) -> str:
    """将提取结果合并到 MEMORY.md"""
    adds = operations.get("add", []) or []
    if not adds:
        return current_md

    today = datetime.now().astimezone().strftime("%Y-%m-%d")
    new_entries = []
    for item in adds:
        if isinstance(item, dict):
            cat = item.get("category", "其他")
            content = item.get("content", "")
            new_entries.append(f"- **{cat}**: {content}")
        else:
            new_entries.append(f"- {item}")

    # 检查 MEMORY.md 是否已有 Auto-Extracted 区块
    section_mark = f"## Auto-Extracted ({today})"
    block = f"\n\n{section_mark}\n<!-- auto-memory:{today} -->\n" + "\n".join(x for x in new_entries)

    if section_mark in current_md:
        # 追加到已有区块
        idx = current_md.find(section_mark)
        after = current_md[idx:]
        # 在 <!-- auto-memory: --> 注释后追加
        insert_point = after.find("-->", after.find("auto-memory"))
        if insert_point >= 0:
            before = current_md[:idx + insert_point + 3]
            existing_entries = after[insert_point + 3:].strip()
            new_lines = "\n".join(x for x in new_entries)
            current_md = before + "\n" + new_lines + "\n" + existing_entries
    else:
        current_md = current_md.rstrip() + block

    return current_md


def write_with_script(path: str, content: str) -> dict:
    import subprocess
    tmp = Path(f"/tmp/_tw_auto_{Path(path).name}.txt")
    tmp.write_text(content, encoding="utf-8")
    cmd = [sys.executable, str(WRITER_SCRIPT), "--path", path, "--content-file", str(tmp)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    tmp.unlink(missing_ok=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"status": "error", "message": result.stderr or result.stdout}


# ── 运行模式 ──────────────────────────────────────────────────────────────────

def run_status(days: int = 1) -> dict:
    """查看状态"""
    memos_files = sorted(MEMORY_DIR.glob("memos-cloud-*.md"), reverse=True)[:days]
    entries_text = read_memos_cloud(days)
    return {
        "status": "ok",
        "memos_files": [f.name for f in memos_files],
        "filtered_entries_count": len([l for l in entries_text.split("\n") if l.strip()]),
        "total_chars": len(entries_text),
    }


def run_extract(days: int = 1, dry_run: bool = False) -> dict:
    """执行记忆提取"""
    entries_text = read_memos_cloud(days)
    if not entries_text:
        return {"status": "ok", "message": "没有找到新的记忆条目", "skipped": True}

    entry_count = len([l for l in entries_text.split("\n") if l.strip()])
    if entry_count < 2:
        return {"status": "ok", "message": "有效条目太少，跳过", "skipped": True}

    current_md = read_memory_md()

    print(json.dumps({"status": "info", "step": "extract", "entries": entry_count, "chars": len(entries_text)}))

    if dry_run:
        return {"status": "dry_run", "entries_preview": entries_text[:500], "total_entries": entry_count}

    # 调用 qwen3
    prompt = EXTRACT_PROMPT.format(memory_md=current_md[:2000], memos_entries=entries_text[:5000])
    result = call_llm(prompt, max_tokens=2000)

    operations = parse_extraction_result(result)
    add_count = len(operations.get("add", []) or [])

    md_result = {"status": "skipped", "message": "无新记忆"}
    if add_count > 0:
        new_md = merge_memory_md(current_md, operations)
        if new_md != current_md:
            md_result = write_with_script(str(MEMORY_MD), new_md)

    return {
        "status": "ok",
        "summary": {
            "add_count": add_count,
            "result_preview": result[:300] if result else "(empty)",
        },
        "memory_md_update": md_result,
    }


def main():
    parser = argparse.ArgumentParser(description="auto-memory v2")
    parser.add_argument("--mode", choices=["status", "dry-run", "full"], default="full")
    parser.add_argument("--days", type=int, default=1)
    args = parser.parse_args()

    if args.mode == "status":
        result = run_status(args.days)
    elif args.mode == "dry-run":
        result = run_extract(args.days, dry_run=True)
    else:
        result = run_extract(args.days)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get("skipped") else 0


if __name__ == "__main__":
    sys.exit(main())
