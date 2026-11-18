# -*- coding: utf-8 -*-
"""
md2html.py — 把「3D生成指标全景_主观客观分类.md」转成打印友好的 HTML
纯标准库，无依赖。md 更新后重跑本脚本即可重新生成 html。
"""
import re
import html as htmlmod
from pathlib import Path

BASE = Path(__file__).resolve().parent
SRC = BASE / "3D生成指标全景_主观客观分类.md"
OUT = BASE / "3D生成指标全景_主观客观分类.html"

raw = htmlmod.unescape(SRC.read_text(encoding="utf-8"))


def inline(s):
    """行内：代码 → 加粗 → 链接（先代码，避免代码里的符号被误伤）"""
    s = s.strip()
    codes = []

    def stash(m):
        codes.append(m.group(1))
        return f"\x00CODE{len(codes) - 1}\x00"

    s = re.sub(r'`([^`]+)`', stash, s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\[([^\]]+)\]\((https?://[^\)]+)\)',
               r'<a href="\2" target="_blank">\1</a>', s)
    for i, c in enumerate(codes):
        s = s.replace(f"\x00CODE{i}\x00", f"<code>{htmlmod.escape(c)}</code>")
    return s


def widths_for(headers):
    n = len(headers)
    if n == 7:
        return ["13%", "15%", "21%", "20%", "6%", "13%", "12%"]
    if n == 6:
        return ["16%", "18%", "24%", "8%", "14%", "20%"]
    return ["auto"] * n


lines = raw.split("\n")
parts = []
i = 0
in_table = False
in_code = False
code_buf = []
in_quote = False
quote_buf = []

while i < len(lines):
    line = lines[i].rstrip()

    # 代码块
    if line.strip().startswith("```"):
        if in_code:
            parts.append("<pre>" + htmlmod.escape("\n".join(code_buf)) + "</pre>")
            code_buf = []
            in_code = False
        else:
            if in_quote:
                parts.append("<blockquote>" + "<br>".join(inline(x) for x in quote_buf) + "</blockquote>")
                quote_buf = []
                in_quote = False
            in_code = True
        i += 1
        continue
    if in_code:
        code_buf.append(line)
        i += 1
        continue

    # 表格
    if line.startswith("|"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r':?-{2,}:?', c.replace(" ", "")) for c in cells):
            i += 1
            continue
        if not in_table:
            in_table = True
            ws = widths_for(cells)
            parts.append('<table class="grid">')
            parts.append("<thead><tr>" + "".join(
                f'<th style="width:{w}">{inline(c)}</th>' for c, w in zip(cells, ws)) + "</tr></thead>")
            parts.append("<tbody>")
        else:
            parts.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
        i += 1
        continue
    if in_table:
        parts.append("</tbody></table>")
        in_table = False

    # 引用块（连续 > 行合并；单独的 > 视为引用内空行）
    if line.startswith(">"):
        in_quote = True
        content = line[1:].lstrip().rstrip()
        if content == "":
            quote_buf.append('<span class="qsep"></span>')
        else:
            quote_buf.append(inline(content))
        i += 1
        continue
    if in_quote:
        parts.append("<blockquote>" + "<br>".join(quote_buf) + "</blockquote>")
        quote_buf = []
        in_quote = False

    s = line.strip()
    if s == "" or s == "---":
        pass
    elif line.startswith("### "):
        parts.append(f"<h3>{inline(line[4:])}</h3>")
    elif line.startswith("## "):
        parts.append(f"<h2>{inline(line[3:])}</h2>")
    elif line.startswith("# "):
        parts.append(f"<h1>{inline(line[2:])}</h1>")
    elif re.match(r'^-\s+', s):
        # 列表项：连续收集
        items = []
        while i < len(lines) and re.match(r'^\s*-\s+', lines[i]):
            items.append(inline(re.sub(r'^\s*-\s+', '', lines[i].rstrip())))
            i += 1
        parts.append("<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>")
        continue
    else:
        parts.append(f"<p>{inline(s)}</p>")
    i += 1

if in_table:
    parts.append("</tbody></table>")
if in_code:
    parts.append("<pre>" + htmlmod.escape("\n".join(code_buf)) + "</pre>")
if in_quote:
    parts.append("<blockquote>" + "<br>".join(quote_buf) + "</blockquote>")

CSS = r"""
:root { --ink:#1f2329; --sub:#5b6573; --line:#d8dee6; --head:#eef2f7; --accent:#2563eb; --zebra:#fafbfd; }
* { box-sizing:border-box; }
body { margin:0 auto; padding:28px 32px 48px; max-width:1400px;
  font-family:"Microsoft YaHei","PingFang SC","Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  color:var(--ink); font-size:13px; line-height:1.65; background:#fff; }
h1 { font-size:23px; margin:0 0 20px; padding-bottom:12px; border-bottom:2px solid var(--accent); letter-spacing:.3px; }
h2 { font-size:17px; margin:28px 0 12px; padding:6px 0 6px 10px; border-left:4px solid var(--accent); background:#f7f9fc; }
h3 { font-size:14.5px; margin:18px 0 8px; color:#243044; }
p { margin:8px 0; }
strong { color:#12305e; }
code { font-family:Consolas,"Courier New",monospace; font-size:.92em; color:#b03060;
  background:#f4f1f6; border:1px solid #e6dfea; border-radius:3px; padding:1px 4px; white-space:nowrap; }
pre { margin:12px 0; padding:14px 16px; background:#f6f8fb; border:1px solid var(--line); border-radius:6px;
  font-family:Consolas,"Courier New","Microsoft YaHei",monospace; font-size:12px; line-height:1.55;
  white-space:pre; overflow-x:auto; color:#2b3648; }
blockquote { margin:10px 0 16px; padding:10px 14px; background:#f5f8fc; border-left:3px solid #9db4d8; color:var(--sub); }
.qsep { display:block; height:6px; }
ul { margin:8px 0; padding-left:24px; }
li { margin:3px 0; }
table.grid { width:100%; table-layout:fixed; border-collapse:collapse; margin:10px 0 6px;
  border:1px solid var(--line); font-size:11.5px; }
table.grid th, table.grid td { border:1px solid var(--line); padding:7px 9px; vertical-align:top;
  overflow-wrap:break-word; word-break:normal; line-height:1.5; }
table.grid th { background:var(--head); font-weight:700; text-align:left; color:#243044; }
table.grid tbody tr:nth-child(even) { background:var(--zebra); }
table.grid td code { white-space:normal; word-break:break-word; font-size:10.5px; }
table.grid a { color:var(--accent); text-decoration:none; }
table.grid a:hover { text-decoration:underline; }
@page { size:A4 landscape; margin:9mm; }
@media print {
  body { padding:0; max-width:none; font-size:11px; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  pre { white-space:pre-wrap; font-size:10px; }
  table.grid { font-size:9.5px; }
  table.grid thead { display:table-header-group; }
  table.grid tr { page-break-inside:avoid; }
  h2, h3 { page-break-after:avoid; }
}
"""

doc = ("<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n<meta charset=\"utf-8\">\n"
       "<title>3D 生成任务评估 · 维度与手段</title>\n<style>" + CSS + "</style>\n</head>\n<body>\n"
       + "\n".join(parts) + "\n</body>\n</html>")

OUT.write_text(doc, encoding="utf-8")
print("WROTE", OUT)
print("tables:", doc.count('<table class="grid">'), "h2:", doc.count("<h2>"),
      "pre:", doc.count("<pre>"), "blockquote:", doc.count("<blockquote>"))
