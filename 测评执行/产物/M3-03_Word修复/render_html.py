#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 docx 按真实 run/段落格式渲染为 HTML（用于无 LibreOffice 环境下的视觉自检）。
同时渲染原稿与修复稿，输出一个并排对照 HTML。"""
import html
from docx import Document
from docx.shared import Pt

def para_html(p):
    pf = p.paragraph_format
    align = p.alignment
    a = "left"
    if align is not None:
        a = {0:"left",1:"center",2:"right",3:"justify"}.get(int(align),"left")
    styles = [f"text-align:{a}"]
    # 缩进
    li = pf.left_indent
    if li is not None: styles.append(f"margin-left:{li.pt}pt")
    fi = pf.first_line_indent
    if fi is not None:
        styles.append(f"text-indent:{fi.pt}pt")
    ls = pf.line_spacing
    if ls: styles.append(f"line-height:{ls}")
    sb = pf.space_before.pt if pf.space_before is not None else 0
    sa = pf.space_after.pt if pf.space_after is not None else 0
    styles.append(f"margin-top:{sb}pt"); styles.append(f"margin-bottom:{sa}pt")
    runs = ""
    for r in p.runs:
        t = html.escape(r.text).replace("\n","<br/>")
        rs = []
        fn = r.font
        if fn.size: rs.append(f"font-size:{fn.size.pt}pt")
        if fn.bold: rs.append("font-weight:bold")
        if fn.italic: rs.append("font-style:italic")
        col = fn.color.rgb if fn.color and fn.color.rgb else None
        if col: rs.append(f"color:#{col}")
        ea = r._element.rPr.rFonts.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia') if r._element.rPr is not None and r._element.rPr.rFonts is not None else None
        if ea: rs.append(f"font-family:'{ea}',serif")
        runs += f'<span style="{";".join(rs)}">{t}</span>'
    if not runs:
        runs = "&nbsp;"
    return f'<p style="{";".join(styles)}">{runs}</p>'

def table_html(t):
    out = ['<table border="1" cellspacing="0" style="border-collapse:collapse;margin:8px 0;">']
    for row in t.rows:
        out.append("<tr>")
        for c in row.cells:
            inner = "".join(para_html(p) for p in c.paragraphs)
            # 背景色
            fill = ""
            tcPr = c._tc.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tcPr')
            if tcPr is not None:
                shd = tcPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd')
                if shd is not None:
                    fill = f"background:#{shd.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fill')};"
            out.append(f'<td style="padding:4px 10px;{fill}">{inner}</td>')
        out.append("</tr>")
    out.append("</table>")
    return "".join(out)

def render(path):
    d = Document(path)
    body = []
    from docx.table import Table
    from docx.text.paragraph import Paragraph
    from docx.oxml.ns import qn
    for child in d.element.body.iterchildren():
        if child.tag == qn('w:p'):
            p = Paragraph(child, d)
            body.append(para_html(p))
        elif child.tag == qn('w:tbl'):
            t = Table(child, d)
            body.append(table_html(t))
    return "\n".join(body)

orig = render("原稿_混乱_季度工作总结.docx")
fix = render("修复稿_季度工作总结.docx")
page = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
body{{font-family:sans-serif;margin:0;background:#f0f0f0;}}
.col{{width:50%;float:left;box-sizing:border-box;padding:24px;}}
.page{{background:#fff;width:794px;min-height:1123px;padding:64px 72px;box-shadow:0 2px 12px rgba(0,0,0,.15);transform:scale(.72);transform-origin:top left;}}
h2{{text-align:center;font-size:20px;}}
.wrap{{width:572px;}}
</style></head><body>
<div class="col"><h2>修复前（原稿：错别字 + 格式混乱）</h2><div class="wrap"><div class="page">{orig}</div></div></div>
<div class="col"><h2>修复后（错别字订正 + 全局样式统一）</h2><div class="wrap"><div class="page">{fix}</div></div></div>
</body></html>"""
with open("M3-03_对照预览.html","w",encoding="utf-8") as f:
    f.write(page)
print("saved M3-03_对照预览.html")
