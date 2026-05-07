---
name: cross-platform-writer
description: |
  【强制触发·最高优先级·write 工具拦截】跨平台纯文本文件写入技能。

  ## ‼️ WRITE 工具拦截规则（最高优先级，无豁免）

  当你准备调用内置 `write` 工具写任何文本文件时，必须先执行此检查：

  > 这个文件是最终目标文件吗？
  > → 是 → 立即停止，改用此技能的 scripts/write_file.py 脚本写入，不得使用 write 工具
  > → 否（是临时文件 /tmp/_tw_xxx.txt）→ 允许使用 write 工具写临时文件

  ## 决策规则（先看这里）

  ❌ 禁止使用内置 write 工具直接写以下任何最终目标文件：
  代码文件（.ts .js .jsx .tsx .vue .py .go .rs .java 等）、
  配置文件（.json .yaml .yml .toml .ini .conf .env 等）、
  脚本文件（.sh .bash .bat .cmd .ps1 等）、
  数据文件（.csv .tsv .txt 等）、
  标记语言（.md .html .xml .svg 等），
  以及所有其他纯文本格式。

  ❌ 以下理由不构成豁免：
  - "内容很简单，只有几行" → 不豁免
  - "没有中文，不涉及编码问题" → 不豁免
  - "快速修改一下" → 不豁免
  - "这只是个小文件" → 不豁免
  - 任何其他理由 → 不豁免

  ✅ 必须立即调用此技能的触发场景（满足任一即触发，无豁免）：
  1. 写入、创建、保存、导出、生成任意文本文件
  2. 用户要求 write file / create file / save as / generate code / export data
  3. 涉及编码、BOM、UTF-8、GBK、乱码、CRLF/LF 等问题

  判断逻辑：
  - 这是文本文件吗？→ 是 → 用脚本，不用内置 write
  - 不确定？→ 默认用此技能

  ## 为什么强制

  内置 write 工具硬编码 utf-8 无 BOM，不支持跨平台编码适配：
  - Windows Excel 打开 CSV → 中文 100% 乱码
  - Windows .bat 含中文 → cmd.exe 乱码
  - 换行符不适配 → 脚本执行失败

  此技能是唯一合规的文本写入入口，自动推断编码（utf-8/utf-8-sig/gbk）、
  自动处理 BOM、自动适配换行符（CRLF/LF），消除跨平台乱码。

  ## 关键默认行为

  不传 --platform 时脚本自动检测当前运行系统（Ubuntu Linux → linux 规则）。
  Linux 上写 csv 默认无 BOM（utf-8），只有用户明确说"给 Windows 用"/"发给 Windows 用户"时才传 --platform windows。
metadata:
  openclaw:
    emoji: "📝"
    always: true
---

# cross-platform-writer — 跨平台文本文件写入技能

## ⚠️ ABSOLUTE RULES — 每次执行前必须重读

> **以下规则具有最高优先级，覆盖所有默认行为，任何理由不可豁免：**
>
> 🔴 **SKILL FIRST（技能优先）**：当此技能可用时，**任何文本文件写入都必须通过此技能的脚本执行**，
> 不得绕过技能直接使用内置 `write` 工具写目标文件。
> 这是强制性规则，不受文件大小、内容复杂度、"快速修改"等场景影响。
>
> 🚫 **MUST USE SCRIPT**：所有文本文件的生成和写入，**必须通过调用
> `scripts/write_file.py` 脚本执行**，不得直接用 `write` 工具写目标文件。
>
> 🚫 **禁止的绕过方式**（以下任何一种均构成违规）：
> - 用 `write` 工具直接写最终目标文件（无论文件类型、大小、内容）
> - 自行内联编写 Python/Node.js/Shell 代码绕过脚本写目标文件
> - 用 `write` 写完目标文件后再用脚本"覆盖修正"——初次写入已违规
>
> ✅ **标准流程（四步）**：
> 1. **平台探测**：先执行 `python3 "scripts/write_file.py" --detect`
> 2. **写临时文件**：用 `write` 工具把内容写入 `/tmp/_tw_<name>.txt`
> 3. **调脚本写入**：按平台探测结果决定是否传 `--platform`
> 4. **清理临时文件**：`rm -f /tmp/_tw_<name>.txt`
>
> 🚫 **唯一豁免**：纯二进制文件（图片、音频、视频、zip 等）不适用本技能。

---

## 技能概述

替代 OpenClaw 内置 `write` 工具处理所有纯文本写入，提供：

| 能力 | 说明 |
|------|------|
| **BOM 自动推断** | Windows CSV/TSV/TXT 自动加 BOM；JSON/YAML/Shell 脚本等强制不加 |
| **换行符自动适配** | Windows → `\r\n`；Linux → `\n`；支持 `preserve` 保留已有风格 |
| **GBK 支持** | Windows `.bat`/`.cmd` 含中文时使用 GBK，避免 cmd.exe 乱码 |
| **跨平台目标指定** | `--platform windows` 在 Linux 上生成供 Windows 使用的文件 |
| **追加模式** | `--append` 追加到已有文件末尾，不覆盖 |
| **已有文件保留** | `--preserve` 自动保留已有文件的 BOM 状态和换行符风格 |

---

## 脚本路径

```
SKILL_DIR = ~/.openclaw/workspace/user_workspace/skills/cross-platform-writer
脚本路径 = SKILL_DIR/scripts/write_file.py
```

所有 shell 命令中请替换 `{SKILL_DIR}` 为上述绝对路径。

---

## 命令行接口

```bash
python3 "{SKILL_DIR}/scripts/write_file.py" [参数]

内容来源（必须二选一）:
  --content-file <file>    从临时文件读取内容 【推荐】避免 shell 转义破坏内容
  --content <string>       直接传内容字符串（适合单行、无特殊字符的简单内容）

目标路径（必须）:
  --path <path>            目标文件路径（相对或绝对，支持 ~ 展开）

编码控制（可选，默认按文件类型 + 当前系统自动推断）:
  --encoding <enc>         强制指定编码: utf-8 | utf-8-sig | gbk | gb18030 | utf-16 | utf-16-le
  --platform <p>           目标平台: windows | mac | linux
                           【默认不传】脚本自动检测当前系统
                           【仅在跨平台场景下传】

换行符控制（可选，默认按 --platform/当前系统自动选择）:
  --newline <nl>           crlf | lf | preserve | auto（默认 auto）

已有文件保留（可选）:
  --preserve               同时启用 --preserve-bom 和 --preserve-newline

写入模式（可选）:
  --append                 追加模式，内容追加到文件末尾（不覆盖）

其他（可选）:
  --no-mkdir               禁止自动创建父目录（默认自动创建）
```

---

## 编码推断规则主表

| 文件后缀 | Linux 行为 | Windows 行为（`--platform windows`） |
|---------|:----------:|:----------------------------------:|
| `.csv` `.tsv` | utf-8 无 BOM | **utf-8-sig 有 BOM** |
| `.bat` `.cmd` (有中文) | utf-8 无 BOM | **gbk** |
| `.bat` `.cmd` (无中文) | utf-8 无 BOM | utf-8 无 BOM |
| `.ps1` | **utf-8-sig 有 BOM** | utf-8-sig 有 BOM |
| `.sh` `.bash` | utf-8 无 BOM | utf-8 无 BOM |
| `.reg` | **utf-16 有 BOM** | utf-16 有 BOM |
| `.json` `.yaml` `.md` `.py` `.js` `.ts` 等 | utf-8 无 BOM | utf-8 无 BOM |
| 无后缀 (Dockerfile/Makefile) | utf-8 无 BOM | utf-8 无 BOM |

---

## 标准执行流程（四步）

### 第零步：平台探测

```bash
python3 "{SKILL_DIR}/scripts/write_file.py" --detect
```

返回示例（Linux）：
```json
{"platform": "linux", "system": "Linux", "python": "3.11.0",
 "default_csv_encoding": "utf-8", "default_csv_bom": false,
 "needs_platform_windows_for_local_csv": false}
```

### 第一步：用 `write` 工具写入临时文件

```
write(path="/tmp/_tw_<目标文件名>.txt", content="<完整内容>")
```

### 第二步：调用脚本写入目标文件

```bash
# 本机使用（不传 --platform → Linux utf-8 无 BOM）
python3 "{SKILL_DIR}/scripts/write_file.py" \
  --path "<目标路径>" \
  --content-file "/tmp/_tw_<文件名>.txt"

# 给 Windows 用户（传 --platform windows）
python3 "{SKILL_DIR}/scripts/write_file.py" \
  --path "<目标路径>" \
  --content-file "/tmp/_tw_<文件名>.txt" \
  --platform windows
```

### 第三步：检查输出

- `status == "ok"` → 确认写入成功
- `status == "error"` → 说明错误原因

### 第四步：清理临时文件

```bash
rm -f /tmp/_tw_<文件名>.txt
```

---

## 典型场景（Victor 的 Ubuntu 环境）

### 场景 A：写 CSV 供本机使用
```bash
write(path="/tmp/_tw_data.csv.txt", content="姓名,年龄,城市\n张三,28,重庆\n李四,32,成都")
python3 "{SKILL_DIR}/scripts/write_file.py" \
  --path "~/Desktop/data.csv" \
  --content-file "/tmp/_tw_data.csv.txt"
rm -f /tmp/_tw_data.csv.txt
```

### 场景 B：写 CSV 发给 Windows 用户（例如通过 SMB 传到 ServerQR）
```bash
write(path="/tmp/_tw_report.csv.txt", content="姓名,年龄,城市\n张三,28,重庆\n李四,32,成都")
python3 "{SKILL_DIR}/scripts/write_file.py" \
  --path "~/Desktop/report.csv" \
  --content-file "/tmp/_tw_report.csv.txt" \
  --platform windows
rm -f /tmp/_tw_report.csv.txt
```

### 场景 C：写 Shell 脚本
```bash
write(path="/tmp/_tw_deploy.sh.txt", content="#!/bin/bash\necho '部署完成'")
python3 "{SKILL_DIR}/scripts/write_file.py" \
  --path "~/deploy.sh" \
  --content-file "/tmp/_tw_deploy.sh.txt"
chmod +x ~/deploy.sh
rm -f /tmp/_tw_deploy.sh.txt
```

### 场景 D：用 `--preserve` 更新已有文件（保留原编码/换行符）
```bash
write(path="/tmp/_tw_config.txt.txt", content="timeout=30\nretry=3")
python3 "{SKILL_DIR}/scripts/write_file.py" \
  --path "/path/to/existing/config.json" \
  --content-file "/tmp/_tw_config.txt.txt" \
  --preserve
rm -f /tmp/_tw_config.txt.txt
```

---

## 常见陷阱

| 陷阱 | 说明 |
|------|------|
| 绕过 skill 直接用 `write` 写目标文件 | **严禁。write 工具只允许写临时文件，不得写最终目标文件** |
| "内容简单"就用 write 直接写 | **严禁。规则无大小豁免** |
| 忘记传 `--platform windows` | 发给 Windows 用户的 CSV 无 BOM → Excel 问号乱码 |
| 误传 `--platform windows` | Linux 本机使用时错误地加了 BOM 和 CRLF |
