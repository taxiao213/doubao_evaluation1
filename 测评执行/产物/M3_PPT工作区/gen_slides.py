#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M3-01/02 invana 项目介绍 PPT 生成器（参数化：主色/字体/图表/章节）。
用法: python3 gen_slides.py --out v1 --theme blue --font 思源黑体 [--chart] [--no-adapters]
"""
import argparse, os, html

# ---------- 主题 ----------
THEMES = {
    "blue":  dict(primary="rgb(0,48,135)",   secondary="rgb(0,112,186)",
                  light="rgb(212,229,247)",  title="rgb(0,28,84)",
                  body="rgb(71,85,105)",     line="rgb(203,213,225)",
                  pale="rgb(242,246,252)"),
    "green": dict(primary="rgb(76,122,90)",  secondary="rgb(107,155,124)",
                  light="rgb(228,239,231)",  title="rgb(46,74,54)",
                  body="rgb(46,50,56)",      line="rgb(206,218,210)",
                  pale="rgb(244,246,245)"),
}
MONO = "Roboto Mono"

def esc(s):
    return html.escape(str(s), quote=False)

def shape_text(x, y, w, h, text, size, color, bold=False, align="left",
               ttype="body", font=None, spacing="multiple:1.3", wrap=True, mono=False):
    fam = MONO if mono else font
    b = ' bold="true"' if bold else ""
    wattr = "" if wrap else ' wrap="false"'
    if isinstance(text, list):
        ps = "".join(f"<p>{t}</p>" for t in text)
    else:
        ps = f"<p>{text}</p>"
    return (f'<shape type="text" topLeftX="{x}" topLeftY="{y}" width="{w}" height="{h}">'
            f'<content textType="{ttype}" fontSize="{size}" color="{color}" '
            f'fontFamily="{fam}" textAlign="{align}" lineSpacing="{spacing}"{b}{wattr}>{ps}</content></shape>')

def rect(x, y, w, h, fill, border=None, bw=1):
    b = f'<border color="{border}" width="{bw}"/>' if border else ""
    return (f'<shape type="rect" topLeftX="{x}" topLeftY="{y}" width="{w}" height="{h}">'
            f'<fill><fillColor color="{fill}"/></fill>{b}</shape>')

def hline(x1, x2, y, color, width=1):
    return (f'<line startX="{x1}" startY="{y}" endX="{x2}" endY="{y}">'
            f'<border color="{color}" width="{width}"/></line>')

def arrow(x1, y1, x2, y2, color, width=2):
    return (f'<line startX="{x1}" startY="{y1}" endX="{x2}" endY="{y2}">'
            f'<border color="{color}" width="{width}"/><endArrow type="arrow"/></line>')

def footer(idx, total, C, font):
    return (hline(60, 900, 498, C["line"], 1) +
            shape_text(60, 506, 500, 20, "invana 项目介绍 · 技术评审", 9, C["body"], font=font) +
            shape_text(800, 506, 100, 20, f"{idx:02d} / {total:02d}", 9, C["body"], align="right", font=font))

def header(chapter, title, C, font):
    return (shape_text(60, 40, 600, 18, chapter, 11, C["secondary"], bold=True, mono=False, font=font, spacing="multiple:1.0") +
            shape_text(60, 64, 840, 56, title, 24, C["title"], bold=True, ttype="headline",
                       font=font, spacing="multiple:1.15") +
            hline(60, 900, 128, C["line"], 1))

def slide_wrap(body):
    return ('<slide xmlns="https://www.larkoffice.com/sml/2.0">'
            '<style><fill><fillColor color="rgb(255,255,255)"/></fill></style>'
            f'<data>{body}</data></slide>')

# ---------- 各页 ----------
def p1_cover(C, f):
    s = (hline(60, 180, 96, C["primary"], 3) +
         shape_text(60, 112, 600, 20, "TECHNICAL REVIEW · 架构介绍", 11, C["secondary"], bold=True, font=f) +
         shape_text(60, 176, 840, 70, "invana 库存与订单分析 SDK", 44, C["title"], bold=True,
                    ttype="title", font=f, spacing="multiple:1.0", wrap=False) +
         shape_text(60, 262, 840, 34, "Python 3.10+ · 零第三方运行时依赖 · 分层架构", 18, C["body"], font=f) +
         hline(60, 900, 330, C["line"], 1) +
         shape_text(60, 352, 840, 80,
                    ["一条从外部数据接入到财务对账报表的可测试数据流，",
                     "金额计算收敛到唯一入口，舍入规则集中在唯一工具函数。"],
                    15, C["body"], font=f, spacing="multiple:1.6") +
         shape_text(60, 470, 500, 20, "v0.1 · 架构评审材料", 11, C["body"], font=f) +
         shape_text(700, 470, 200, 20, "2026-09-22", 11, C["body"], align="right", font=f))
    return slide_wrap(s)

def p2_toc(C, f, total, include_adapters=True):
    items = [
        ("01", "背景与定位", "项目目标、输入输出与运行约束"),
        ("02", "分层架构", "adapters 到 cli 的单向数据流"),
        ("03", "核心模块",
         "models / repo / services / adapters / utils" if include_adapters else "models / repo / services"),
        ("04", "质量与规范", "Decimal 金额规则与 pytest 基线"),
        ("05", "现状与路线", "失败用例、根因定位与功能规划"),
    ]
    s = shape_text(60, 56, 840, 48, "目录", 34, C["title"], bold=True, ttype="title", font=f) + \
        shape_text(60, 108, 200, 18, "CONTENTS", 11, C["secondary"], bold=True, font=f)
    pos = [(60, 170), (60, 250), (60, 330), (490, 170), (490, 250)]
    for (num, name, desc), (x, y) in zip(items, pos):
        s += shape_text(x, y, 70, 40, num, 28, C["primary"], bold=True, font=f, spacing="multiple:1.0")
        s += shape_text(x + 78, y + 2, 340, 28, name, 20, C["title"], bold=True, font=f, spacing="multiple:1.0")
        s += shape_text(x + 78, y + 36, 340, 18, desc, 11, C["body"], font=f)
        s += hline(x + 78, x + 410, y + 62, C["line"], 1)
    s += footer(2, total, C, f)
    return slide_wrap(s)

def p3_background(C, f, total, chart=False):
    s = header("01 · 背景与定位", "订单、定价、库存与对账被收敛为一条可测试的数据流", C, f)
    rows = [
        ("定位", "库存与订单分析的教学 / 评审项目，运行时无第三方依赖，Python 3.10+ 即可运行"),
        ("输入", "CSV / JSON 订单与客户数据：tests/fixtures/orders.csv、orders.json、customers.csv"),
        ("输出", "行级定价、库存校验结果，以及 services/report 生成的财务对账报表"),
        ("运行", "PYTHONPATH=src<br/>python3 -m invana.cli summary tests/fixtures/orders.csv"),
    ]
    if chart:
        y = 158
        for label, desc in rows:
            is_mono = label == "运行"
            s += shape_text(60, y, 70, 24, label, 14, C["primary"], bold=True, font=f)
            s += shape_text(132, y, 360, 44, desc, 11 if is_mono else 12, C["body"],
                            mono=is_mono, font=f, spacing="multiple:1.35")
            s += hline(132, 492, y + 48, C["line"], 1)
            y += 78
        # 右侧：各模块文件数柱状图
        s += shape_text(540, 150, 360, 20, "图 1 · 各层 Python 文件数（共 43 个源文件）", 11, C["secondary"], bold=True, font=f)
        s += chart_files(C)
        s += shape_text(540, 432, 360, 40,
                        ["测试与工具层占比最高，说明项目把正确性校验", "与通用能力下沉，业务层保持轻薄。"],
                        10, C["body"], font=f, spacing="multiple:1.3")
    else:
        y = 170
        for label, desc in rows:
            s += shape_text(60, y, 80, 26, label, 15, C["primary"], bold=True, font=f)
            s += shape_text(150, y, 750, 26, desc, 14, C["body"], font=f, spacing="multiple:1.2")
            s += hline(60, 900, y + 44, C["line"], 1)
            y += 72
        s += shape_text(60, 470, 840, 18,
                        "数据来源：repo-invana 仓库实际目录（src/invana、tests、docs）", 9, C["body"], font=f)
    s += footer(3, total, C, f)
    return slide_wrap(s)

def chart_files(C):
    # 原生柱状图：tests 9, utils 8, services 6, models 5, repo 5, adapters 5, 顶层 5
    return f'''<chart width="360" height="260" topLeftX="540" topLeftY="176">
  <chartPlotArea>
    <chartPlot type="column"><chartExtra/></chartPlot>
    <chartAxes>
      <chartAxis type="x"><chartLabel fontSize="9"/></chartAxis>
      <chartAxis type="y" position="left"><chartGridLine color="rgb(226,232,240)"/><chartLabel fontSize="9"/></chartAxis>
    </chartAxes>
  </chartPlotArea>
  <chartData>
    <dim1><chartField name="模块">tests,utils,services,models,repo,adapters,顶层</chartField></dim1>
    <dim2><chartField name="文件数">9,8,6,5,5,5,5</chartField></dim2>
  </chartData>
  <chartStyle>
    <chartBackground color="rgba(0,0,0,0)"/>
    <chartBorder color="rgb(222,224,227)" width="0"/>
    <chartColorTheme><color value="{C['primary']}"/></chartColorTheme>
  </chartStyle>
</chart>'''

def p4_architecture(C, f, total):
    s = header("02 · 分层架构", "数据单向流经四层：adapters → repo → services → cli", C, f)
    layers = [
        ("adapters", "外部数据适配", "csv_reader · json_reader · http_client · retry"),
        ("repo", "数据访问", "base · memory · csv_repo · queries"),
        ("services", "业务服务", "pricing · orders · report · stock · notifications"),
        ("cli", "命令入口", "invana.cli summary"),
    ]
    x0, w, gap, y, h = 60, 186, 24, 186, 96
    xs = []
    for i, (name, role, files) in enumerate(layers):
        x = x0 + i * (w + gap)
        xs.append(x)
        s += rect(x, y, w, h, C["pale"], border=C["line"], bw=1)
        s += rect(x, y, w, 6, C["primary"])
        s += shape_text(x + 14, y + 18, w - 28, 24, name, 16, C["title"], bold=True, mono=True, font=f, spacing="multiple:1.0")
        s += shape_text(x + 14, y + 46, w - 28, 20, role, 12, C["secondary"], bold=True, font=f)
        s += shape_text(x + 14, y + 66, w - 28, 26, files, 9, C["body"], mono=True, font=f, spacing="multiple:1.3")
    for i in range(3):
        ax = xs[i] + w
        s += arrow(ax + 2, y + 48, ax + gap - 4, y + 48, C["secondary"], 2)
    # 共享层
    s += rect(240, 330, 200, 60, "rgb(255,255,255)", border=C["secondary"], bw=1)
    s += shape_text(254, 342, 172, 20, "models", 14, C["title"], bold=True, mono=True, font=f)
    s += shape_text(254, 366, 172, 16, "order · customer · item · enums", 9, C["body"], mono=True, font=f)
    s += rect(520, 330, 200, 60, "rgb(255,255,255)", border=C["secondary"], bw=1)
    s += shape_text(534, 342, 172, 20, "utils", 14, C["title"], bold=True, mono=True, font=f)
    s += shape_text(534, 366, 172, 16, "currency · dates · validators …", 9, C["body"], mono=True, font=f)
    s += arrow(340, 330, 340, 284, C["line"], 1)
    s += arrow(620, 330, 620, 284, C["line"], 1)
    s += shape_text(60, 420, 840, 56,
                    ["关键约束：services.pricing 是金额计算的唯一入口；utils.currency.round_money 是全项目唯一允许处理舍入的位置。",
                     "models 被 repo 与 services 共享；utils 仅被 services 调用，不允许反向依赖。"],
                    12, C["body"], font=f, spacing="multiple:1.6")
    s += footer(4, total, C, f)
    return slide_wrap(s)

def p5_models(C, f, total):
    s = header("03 · 核心模块 / models", "models 层用四个模型固定订单数据的语义边界", C, f)
    rows = [
        ("enums.py", "枚举与状态取值域", "订单状态、折扣类型等枚举，禁止散落魔法字符串"),
        ("order.py", "订单聚合根", "订单头与行项目 line；折扣、税费在行级计算"),
        ("customer.py", "客户实体", "客户编号、等级与分组字段，支撑分组查询"),
        ("item.py", "商品实体", "SKU、单价、税率，行级金额的输入来源"),
    ]
    s += native_table(C, f, 60, 158, 840, rows,
                      ["模块", "职责", "关键内容"], [190, 250, 400])
    s += shape_text(60, 408, 840, 60,
                    ["设计含义：订单合计不是单独录入的字段，而是各行金额之和；",
                     "这与 spec.md 第 3 条“订单合计为各行之和，不重复舍入”直接对应。"],
                    13, C["body"], font=f, spacing="multiple:1.6")
    s += footer(5, total, C, f)
    return slide_wrap(s)

def p6_repo(C, f, total):
    s = header("03 · 核心模块 / repo", "repo 层面向接口编程，内存与 CSV 两种实现可互换", C, f)
    rows = [
        ("base.py", "仓库抽象接口", "定义订单、客户、商品的读写契约，上层只依赖接口"),
        ("memory.py", "内存实现", "测试与样例数据的默认实现，无 IO 副作用"),
        ("csv_repo.py", "CSV 实现", "对接 tests/fixtures 下的 CSV 数据文件"),
        ("queries.py", "查询封装", "订单汇总、按客户分组等跨实体查询"),
    ]
    s += native_table(C, f, 60, 158, 840, rows,
                      ["模块", "角色", "说明"], [190, 250, 400])
    s += shape_text(60, 408, 840, 60,
                    ["依赖方向：adapters 负责把 CSV / JSON 读成内存对象，repo 负责持久化与查询；",
                     "services 不直接接触文件格式，切换数据源时业务代码不变。"],
                    13, C["body"], font=f, spacing="multiple:1.6")
    s += footer(6, total, C, f)
    return slide_wrap(s)

def p7_services(C, f, total):
    s = header("03 · 核心模块 / services", "所有金额经 pricing 与 round_money，report 只汇总行级金额", C, f)
    # 流向
    s += rect(80, 160, 200, 84, C["pale"], border=C["line"])
    s += shape_text(96, 174, 168, 22, "services.pricing", 14, C["title"], bold=True, mono=True, font=f)
    s += shape_text(96, 204, 168, 32, "行级折扣、税费计算\nDecimal 舍入", 11, C["body"], font=f, spacing="multiple:1.4")
    s += arrow(286, 202, 340, 202, C["secondary"], 2)
    s += shape_text(290, 178, 46, 16, "唯一入口", 9, C["secondary"], font=f)
    s += rect(346, 160, 200, 84, C["pale"], border=C["line"])
    s += shape_text(362, 174, 168, 22, "utils.currency", 14, C["title"], bold=True, mono=True, font=f)
    s += shape_text(362, 204, 168, 32, "round_money\nROUND_HALF_UP 两位小数", 11, C["body"], font=f, spacing="multiple:1.4")
    s += arrow(552, 202, 606, 202, C["secondary"], 2)
    s += rect(612, 160, 200, 84, C["pale"], border=C["line"])
    s += shape_text(628, 174, 168, 22, "services.report", 14, C["title"], bold=True, mono=True, font=f)
    s += shape_text(628, 204, 168, 32, "订单合计、对账总额\n财务对账依赖其输出", 11, C["body"], font=f, spacing="multiple:1.4")
    # 金额规范
    s += shape_text(80, 286, 300, 20, "金额计算规范（docs/spec.md）", 13, C["secondary"], bold=True, font=f)
    rules = [
        "1. 金额运算一律使用 Decimal，禁止二进制浮点参与",
        "2. 展示与落库保留 2 位小数，四舍五入 ROUND_HALF_UP",
        "3. 折扣、税费在行级计算并舍入，合计为各行之和",
        "4. 默认币种 CNY，对账以行级金额为准",
    ]
    s += shape_text(80, 316, 500, 130, rules, 12, C["body"], font=f, spacing="multiple:1.9")
    s += rect(612, 300, 200, 120, "rgb(255,255,255)", border=C["secondary"])
    s += shape_text(628, 316, 168, 20, "周边服务", 12, C["secondary"], bold=True, font=f)
    s += shape_text(628, 344, 168, 64,
                    ["orders 下单编排", "stock 库存校验", "notifications 通知"],
                    11, C["body"], font=f, spacing="multiple:1.7")
    s += footer(7, total, C, f)
    return slide_wrap(s)

def p8_adapters_utils(C, f, total):
    s = header("03 · 核心模块 / adapters · utils", "adapters 隔离外部 IO，utils 收敛通用能力", C, f)
    s += shape_text(60, 158, 400, 22, "adapters · 外部数据适配", 15, C["primary"], bold=True, font=f)
    s += hline(60, 460, 188, C["line"], 1)
    ad = [("csv_reader", "CSV 读取与行解析"), ("json_reader", "JSON 订单读取"),
          ("http_client", "HTTP 访问封装"), ("retry", "失败重试策略")]
    y = 206
    for name, desc in ad:
        s += shape_text(60, y, 170, 20, name, 12, C["title"], bold=True, mono=True, font=f)
        s += shape_text(240, y, 220, 20, desc, 12, C["body"], font=f)
        y += 48
    s += shape_text(500, 158, 400, 22, "utils · 通用工具", 15, C["primary"], bold=True, font=f)
    s += hline(500, 900, 188, C["line"], 1)
    ut = [("currency", "货币舍入（唯一舍入点）"), ("dates", "日期处理"),
          ("validators", "输入校验"), ("formatters", "展示格式化"),
          ("ids / mathx / text", "编号、数值与文本工具")]
    y = 206
    for name, desc in ut:
        s += shape_text(500, y, 190, 20, name, 12, C["title"], bold=True, mono=True, font=f)
        s += shape_text(690, y, 210, 20, desc, 12, C["body"], font=f)
        y += 42
    s += shape_text(60, 440, 840, 40,
                    "注意：currency 是全项目唯一允许处理舍入的位置，其他模块不得自行 round，避免舍入口径分叉。",
                    12, C["body"], font=f)
    s += footer(8, total, C, f)
    return slide_wrap(s)

def p9_quality(C, f, total, idx=9):
    s = header("04 · 质量与现状", "23 个用例中 21 个通过，2 个对账用例失败且根因指向舍入方向", C, f)
    # 大数字
    nums = [("23", "用例总数"), ("21", "通过"), ("2", "失败（对账）")]
    x = 80
    for n, label in nums:
        s += shape_text(x, 156, 200, 64, n, 56, C["primary"], bold=True, ttype="headline", font=f,
                        spacing="multiple:1.0", wrap=False)
        s += shape_text(x, 226, 200, 20, label, 13, C["body"], font=f)
        x += 260
    s += hline(60, 900, 268, C["line"], 1)
    rows = [
        ("test_order_totals_match_finance", "SO-1001 实测 88.53 ≠ 期望 88.55；SO-1003 实测 146.52 ≠ 期望 146.53"),
        ("test_grand_total_matches_finance", "对账总额实测 476.25 ≠ 期望 476.28"),
    ]
    s += shape_text(60, 290, 840, 20, "失败用例（tests/test_report_totals.py）", 13, C["secondary"], bold=True, font=f)
    y = 320
    for name, detail in rows:
        s += shape_text(60, y, 360, 20, name, 11, C["title"], bold=True, mono=True, font=f)
        s += shape_text(430, y, 470, 20, detail, 11, C["body"], mono=True, font=f)
        y += 34
    s += shape_text(60, 408, 840, 70,
                    ["症状跨层传导：currency.round_money 使用 ROUND_DOWN 截断 → pricing 行级金额 → report 汇总 → 对账测试失败。",
                     "约束：不得修改任何测试文件；要求最小改动；修复后以 pytest 全绿作为完成判据。"],
                    12, C["body"], font=f, spacing="multiple:1.6")
    s += footer(idx, total, C, f)
    return slide_wrap(s)

def p10_roadmap(C, f, total, idx=10):
    s = header("05 · 现状与路线", "先以一处最小改动修复舍入，再扩展按客户分组导出", C, f)
    steps = [
        ("01", "修复（当前）", "round_money 由 ROUND_DOWN 改为 ROUND_HALF_UP，与 spec.md 对齐"),
        ("02", "验证", "python3 -m pytest tests/ -q 全绿；23 个用例全部通过，不改动测试"),
        ("03", "扩展（选做）", "services/report 增加按客户分组导出 CSV 的能力"),
    ]
    y = 172
    for num, name, desc in steps:
        s += shape_text(60, y, 64, 40, num, 26, C["primary"], bold=True, font=f, spacing="multiple:1.0")
        s += shape_text(140, y + 2, 200, 24, name, 17, C["title"], bold=True, font=f)
        s += shape_text(360, y + 4, 540, 40, desc, 13, C["body"], font=f, spacing="multiple:1.4")
        s += hline(140, 900, y + 56, C["line"], 1)
        y += 88
    s += rect(60, 430, 840, 44, C["pale"])
    s += shape_text(78, 442, 800, 22, "验收命令：python3 -m pytest tests/ -q     预期：23 passed", 13,
                   C["title"], bold=True, mono=True, font=f)
    s += footer(idx, total, C, f)
    return slide_wrap(s)

def native_table(C, f, x, y, w, rows, headers, colw):
    hhead, hbody = 34, 52
    total_h = hhead + hbody * len(rows)
    out = f'<table topLeftX="{x}" topLeftY="{y}" width="{w}" height="{total_h}">'
    out += '<colgroup>' + "".join(f'<col width="{cw}"/>' for cw in colw) + '</colgroup>'
    out += f'<tr height="{hhead}">'
    for h in headers:
        out += (f'<td><fill><fillColor color="{C["primary"]}"/></fill>'
                f'<content textType="body" fontSize="12" bold="true" color="rgba(255,255,255,1)" '
                f'fontFamily="{f}" textAlign="left"><p>{esc(h)}</p></content></td>')
    out += '</tr>'
    for i, r in enumerate(rows):
        bg = "rgb(255,255,255)" if i % 2 == 0 else C["pale"]
        out += f'<tr height="{hbody}">'
        for j, cell in enumerate(r):
            mono = j == 0
            out += (f'<td><fill><fillColor color="{bg}"/></fill>'
                    f'<content textType="body" fontSize="11" color="{C["body"]}" fontFamily="{MONO if mono else f}" '
                    f'textAlign="left" bold="{"true" if j==0 else "false"}"><p>{esc(cell)}</p></content></td>')
        out += '</tr>'
    out += '</table>'
    return out

def build(theme, font, chart, include_adapters):
    C = THEMES[theme]
    f = font
    total = 10 if include_adapters else 9
    pages = [p1_cover(C, font), p2_toc(C, f, total, include_adapters), p3_background(C, f, total, chart),
             p4_architecture(C, f, total), p5_models(C, f, total), p6_repo(C, f, total),
             p7_services(C, f, total)]
    if include_adapters:
        pages.append(p8_adapters_utils(C, f, total))
        pages.append(p9_quality(C, f, total, idx=9))
        pages.append(p10_roadmap(C, f, total, idx=10))
    else:
        pages.append(p9_quality(C, f, total, idx=8))
        pages.append(p10_roadmap(C, f, total, idx=9))
    return pages

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--theme", default="blue", choices=["blue", "green"])
    ap.add_argument("--font", default="思源黑体")
    ap.add_argument("--chart", action="store_true")
    ap.add_argument("--no-adapters", action="store_true")
    args = ap.parse_args()
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.out)
    os.makedirs(outdir, exist_ok=True)
    pages = build(args.theme, args.font, args.chart, not args.no_adapters)
    for i, xml in enumerate(pages, 1):
        with open(os.path.join(outdir, f"slide-{i:02d}.xml"), "w", encoding="utf-8") as fp:
            fp.write(xml)
    print(f"generated {len(pages)} slides -> {outdir}")
