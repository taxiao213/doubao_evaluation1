#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""渲染模型 xlsx 为 HTML 做视觉检查。
内置一个极简公式求值器（递归解析跨表引用/SUM/四则运算），
独立于飞书重算，对公式格求值，作为第二条复算路径。"""
import re, sys
import openpyxl
from openpyxl.utils import column_index_from_string, get_column_letter

XLSX = "/Users/secneo/Documents/workspace/ai_project/doubao_work2/测评执行/产物/M4_金融建模/华晟精密_盈利预测模型.xlsx"
OUT = "/Users/secneo/Documents/workspace/ai_project/doubao_work2/测评执行/产物/M4_金融建模/M4_模型预览.html"

wb = openpyxl.load_workbook(XLSX, data_only=False)
cache = {}

def cell_of(sheet, col, row):
    return wb[sheet].cell(row=int(row), column=column_index_from_string(col))

def resolve(sheet, col, row, depth=0):
    key = (sheet, col, int(row))
    if key in cache: return cache[key]
    if depth > 40: raise RuntimeError("循环引用")
    v = cell_of(sheet, col, row).value
    if v is None:
        out = 0
    elif isinstance(v, (int, float)):
        out = v
    elif isinstance(v, str) and v.startswith("="):
        out = eval_formula(v[1:], sheet, depth+1)
    else:
        out = v
    cache[key] = out
    return out

def range_cells(sheet, c1, r1, c2, r2):
    vals = []
    for r in range(int(r1), int(r2)+1):
        for ci in range(column_index_from_string(c1), column_index_from_string(c2)+1):
            vals.append(resolve(sheet, get_column_letter(ci), r, depth_stack[0]))
    return vals

depth_stack = [0]

def eval_formula(f, sheet, depth):
    depth_stack[0] = depth
    # 跨表引用： Sheet!$C$6 或 Sheet!C6
    def xref(m):
        sh, col, row = m.group(1), m.group(2), m.group(3)
        return repr(resolve(sh, col, row, depth))
    f = re.sub(r"([\u4e00-\u9fa5A-Za-z]+)!\$?([A-Z]{1,3})\$?(\d+)", xref, f)
    # SUM(范围)
    def sumrep(m):
        c1, r1, c2, r2 = m.group(1), m.group(2), m.group(3), m.group(4)
        return repr(sum(range_cells(sheet, c1, r1, c2, r2, )))
    # 重复处理直到无 SUM
    while re.search(r"SUM\(", f, re.I):
        f = re.sub(r"SUM\(([A-Z]{1,3})(\d+):([A-Z]{1,3})(\d+)\)", sumrep, f, flags=re.I)
        break
    # 本表单元格引用
    def lref(m):
        col, row = m.group(1), m.group(2)
        return repr(resolve(sheet, col, int(row), depth))
    f = re.sub(r"(?<![A-Za-z0-9_!$])\$?([A-Z]{1,3})\$?(\d+)", lref, f)
    return eval(f, {"__builtins__":{}}, {})

def fmt(cell, val):
    nf = cell.number_format
    if isinstance(val, str):
        return val.replace("&","&amp;").replace("<","&lt;")
    if val is None: return ""
    if isinstance(val, (int, float)):
        if "%" in nf: return f"{val*100:.1f}%"
        if "0.00" in nf: return f"{val:,.2f}"
        if "#,##0" in nf: return f"{val:,.0f}" if val!=0 else "-"
        return f"{val:g}"
    return str(val)

blocks = []
for ws in wb.worksheets:
    rows_html = []
    for r in range(1, ws.max_row+1):
        cells = []
        for c in range(1, ws.max_column+1):
            cell = ws.cell(row=r, column=c)
            fg = cell.fill.fgColor.rgb
            style = ""
            if isinstance(fg, str) and len(fg) == 8:
                rgb = fg[2:]
                if rgb in ("0F3B5D","3288B9","CFE3F1","FFF2CC"):
                    style += f"background:#{rgb};"
                    if rgb in ("0F3B5D","3288B9"): style += "color:#fff;"
            font = cell.font
            if font.color and isinstance(font.color.rgb, str) and len(font.color.rgb)==8:
                hexv = font.color.rgb[2:]
                if hexv in ("0000FF","008000","808080","FF0000") and "color:#fff" not in style:
                    style += f"color:#{hexv};"
            if font.bold: style += "font-weight:bold;"
            if font.italic: style += "font-style:italic;"
            ha = cell.alignment.horizontal
            if ha == "right": style += "text-align:right;"
            elif ha == "center": style += "text-align:center;"
            col = get_column_letter(c)
            raw = cell.value
            if isinstance(raw,str) and raw.startswith("="):
                val = resolve(ws.title, col, r)
            elif raw is None:
                val = ""
            else:
                val = raw
            txt = fmt(cell, val)
            cells.append(f'<td style="{style}">{txt}</td>')
        rows_html.append("<tr>" + "".join(cells) + "</tr>")
    blocks.append(f'<h2>{ws.title}</h2><table class="grid">{"".join(rows_html)}</table>')

html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
body{{font-family:'Calibri','Microsoft YaHei',sans-serif;padding:24px;color:#222;}}
h1{{color:#0F3B5D;}} h2{{color:#0F3B5D;margin:26px 0 8px;border-left:5px solid #3288B9;padding-left:8px;}}
table.grid{{border-collapse:collapse;font-size:11px;}}
table.grid td{{border:1px solid #e6e9ef;padding:2px 7px;white-space:nowrap;min-width:40px;}}
table.grid td:first-child{{text-align:left;white-space:normal;min-width:210px;}}
</style></head><body>
<h1>华晟精密 盈利预测模型 · 渲染预览（公式经独立求值器复算）</h1>
{''.join(blocks)}
</body></html>"""
open(OUT,"w",encoding="utf-8").write(html)

# 打印关键复算值，供与飞书比对
m = wb["盈利预测"]
print("2025E 营收/净利/EPS:", resolve("盈利预测","F",5), resolve("盈利预测","F",7), resolve("盈利预测","F",14))
print("2027E 营收/净利/EPS:", resolve("盈利预测","H",5), resolve("盈利预测","H",7), resolve("盈利预测","H",14))
s = wb["敏感性分析"]
print("敏感性 基准2027营收/净利/EPS:", resolve("敏感性分析","D",8), resolve("敏感性分析","D",9), resolve("敏感性分析","D",10))
print("勾稽 差异:", resolve("勾稽校验","E",15), resolve("勾稽校验","E",16), resolve("勾稽校验","E",17))
print("saved", OUT)
