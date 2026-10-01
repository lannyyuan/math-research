#!/usr/bin/env python3
"""Regenerate mel-research/MEL-complete-report.md from the synthesis report,
appendices 01-17 and the sanity-check output. Do not edit the output by hand.

Usage (from anywhere):  python3 tools/build_complete_report.py
"""
import glob
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mel-research")
os.chdir(ROOT)


def demote(text, by=1):
    """Push markdown headings down `by` levels, leaving fenced code untouched."""
    out, fence = [], False
    for line in text.split("\n"):
        if line.startswith("```"):
            fence = not fence
        if not fence and re.match(r"^#{1,5} ", line):
            line = "#" * by + line
        out.append(line)
    return "\n".join(out)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


final = read("final-mel-research-report.md")
final_body = final.split("\n", 1)[1]  # drop own title
final_body = re.sub(r"\n---\n\n## 8\. 文件索引.*\Z", "\n", final_body, flags=re.S)
final_body = demote(final_body)

toc = ["- **第一部分 总报告**(结论、发现、Q1–Q12、下一步)"]
parts = []
for f in sorted(glob.glob("[0-9][0-9]-*.md")):
    t = read(f)
    title = t.split("\n", 1)[0].lstrip("# ").strip()
    num = f[:2]
    heading = re.sub(r"^\d\d\s*—\s*", "", title)
    toc.append(f"- 附录 {num} — {heading}")
    parts.append(f"\n\n---\n\n## 附录 {num} — {heading}\n" + demote(t.split("\n", 1)[1]))

exp = read("experiments/sanity_checks.out.txt").rstrip()
toc.append("- 附录 S — 计算验证输出(`experiments/sanity_checks.py`)")
nl = "\n"

doc = f"""# Mathematical Expression Layer (MEL) — 完整研究报告

> **Learn from Linear Algebra's design, not from its dominance.**
> **Search for compression before coverage.**

本文件是**单一完整版**:第一部分为总报告,附录 01–17 为 prompt 所要求的各分项研究,附录 S 为计算验证输出。
文中以反引号标出的 `01`–`17` 指**本文件的对应附录**;`final-…` 指第一部分。
证据标签:`[T]` 定理/标准事实 · `[S]` 结构对应 · `[A]` 类比 · `[H]` 本研究假设;`(web)` 本次检索核实 · `(bg)` 背景知识未复核。

## 目录

{nl.join(toc)}

---

## 第一部分 总报告
{final_body}
{''.join(parts)}

---

## 附录 S — 计算验证输出

`experiments/sanity_checks.py` 的实际运行输出(全部通过):

```text
{exp}
```
"""
with open("MEL-complete-report.md", "w", encoding="utf-8") as fh:
    fh.write(doc)
print(f"wrote MEL-complete-report.md ({len(doc)} chars, {doc.count(chr(10))} lines)")
