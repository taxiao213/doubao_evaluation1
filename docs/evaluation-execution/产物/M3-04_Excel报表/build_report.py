#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M3-04 由 table1_财务摘要（CSV+截图）生成带公式与条件格式的 Excel 报表。
注意：CSV 含千分位逗号（如 3,842），不能按逗号直接 split，按截图 5 列结构对齐解析。"""
import csv, os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import CellIsRule, DataBarRule, FormulaRule
from openpyxl.utils import get_column_letter

BASE = "/Users/secneo/Documents/workspace/ai_project/doubao_work2"
SRC = os.path.join(BASE, "素材/表格/table1_财务摘要.csv")
OUT = os.path.join(BASE, "测评执行/产物/M3-04_Excel报表/财务摘要分析报表.xlsx")

# ---------- 1. 解析 CSV（千分位逗号陷阱：行内逗号既可能是分隔符也可能在数字里） ----------
rows = []
with open(SRC, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split(",")
        name = parts[0]
        # 指标名之后应为 3 个年度值 + 1 个同比；数字内部逗号已把一个数拆成多段，
        # 用“是否含数字/百分号”重组：末尾字段是同比，往前三个年度值按段合并。
        tail = parts[1:]
        yoy = tail[-1]                      # 同比变化在最后
        year_segs = [s.strip() for s in tail[:-1]]
        # 已知 3 个年度列：比率行每年 1 段（共 3 段）；4 位金额被千分位逗号
        # 拆成 2 段（如 3,842 -> '3','842'），共 6 段，按相邻两两合并。
        if len(year_segs) == 3:
            year_vals = year_segs
        elif len(year_segs) == 6:
            year_vals = [year_segs[i] + year_segs[i + 1] for i in (0, 2, 4)]
        else:
            raise ValueError(f"无法按 3 年度列对齐解析：{name} -> {year_segs}")
        rows.append((name, year_vals[0], year_vals[1], year_vals[2], yoy))

def num(v):
    return float(v.replace(",", ""))
def pct(v):
    return float(v.replace("%", "")) / 100.0

# 取值
get = {r[0]: r for r in rows}
rev = [num(get["营业收入（万元）"][i]) for i in (1, 2, 3)]
cost = [num(get["营业成本（万元）"][i]) for i in (1, 2, 3)]
gm = [pct(get["毛利率"][i]) for i in (1, 2, 3)]
rd = [num(get["研发费用（万元）"][i]) for i in (1, 2, 3)]
ni = [num(get["净利润（万元）"][i]) for i in (1, 2, 3)]
debt = [pct(get["资产负债率"][i]) for i in (1, 2, 3)]

# ---------- 2. 建工作簿 ----------
wb = Workbook()
ws = wb.active
ws.title = "财务分析报表"

# 配色
NAVY = "17365D"; BLUE = "5B9BD5"; LIGHT = "DCE6F1"; LINE = "B8C7D9"
GREEN_FILL = PatternFill("solid", fgColor="C6EFCE"); GREEN_FONT = Font(color="006100")
RED_FILL = PatternFill("solid", fgColor="FFC7CE"); RED_FONT = Font(color="9C0006")
thin = Side(style="thin", color=LINE)
navy_fill = PatternFill("solid", fgColor=NAVY)
light_fill = PatternFill("solid", fgColor=LIGHT)

F_TITLE = Font(name="微软雅黑", size=14, bold=True, color="FFFFFF")
F_HEAD = Font(name="微软雅黑", size=11, bold=True, color="FFFFFF")
F_LABEL = Font(name="微软雅黑", size=11, bold=True, color="1F1F1F")
F_BODY = Font(name="Arial", size=11, color="1F1F1F")
F_DERIV = Font(name="Arial", size=11, italic=True, color="1F4E79")
CTR = Alignment(horizontal="center", vertical="center")
RGT = Alignment(horizontal="right", vertical="center")
LFT = Alignment(horizontal="left", vertical="center")

# 标题
ws.merge_cells("A1:E1")
ws["A1"] = "华晟精密财务摘要分析报表（2022–2024 年）"
ws["A1"].font = F_TITLE; ws["A1"].alignment = CTR
ws["A1"].fill = navy_fill
ws.row_dimensions[1].height = 28
ws.merge_cells("A2:E2")
ws["A2"] = "金额单位：万元；比率为百分比；数据来源：table1_财务摘要（CSV 与表格截图一致）"
ws["A2"].font = Font(name="微软雅黑", size=9, color="595959"); ws["A2"].alignment = LFT

# 表头
headers = ["指标", "2022年", "2023年", "2024年", "2024年同比"]
for j, h in enumerate(headers, 1):
    c = ws.cell(row=3, column=j, value=h)
    c.font = F_HEAD; c.fill = PatternFill("solid", fgColor=BLUE); c.alignment = CTR
    c.border = Border(bottom=Side(style="medium", color=NAVY))
ws.row_dimensions[3].height = 22

# 源指标行（4-9）：输入值
def put_amount(r, label, vals, derived=False):
    ws.cell(row=r, column=1, value=label).font = F_DERIV if derived else F_LABEL
    ws.cell(row=r, column=1).alignment = LFT
    for j, v in enumerate(vals, 2):
        c = ws.cell(row=r, column=j)
        if v is not None: c.value = v
        c.number_format = "#,##0"; c.font = F_DERIV if derived else F_BODY; c.alignment = RGT

def put_ratio(r, label, vals, derived=False):
    ws.cell(row=r, column=1, value=label).font = F_DERIV if derived else F_LABEL
    ws.cell(row=r, column=1).alignment = LFT
    for j, v in enumerate(vals, 2):
        c = ws.cell(row=r, column=j)
        if v is not None: c.value = round(v, 4)
        c.number_format = "0.0%"; c.font = F_DERIV if derived else F_BODY; c.alignment = RGT

put_amount(4, "营业收入（万元）", rev)
put_amount(5, "营业成本（万元）", cost)
put_ratio(6, "毛利率", gm)
put_amount(7, "研发费用（万元）", rd)
put_amount(8, "净利润（万元）", ni)
put_ratio(9, "资产负债率", debt)

# 派生指标（10-12）：全部公式
put_amount(10, "毛利额（万元）", [None, None, None], derived=True)
put_ratio(11, "研发费用率", [None, None, None], derived=True)
put_ratio(12, "净利率", [None, None, None], derived=True)
for col in ("B", "C", "D"):
    ws[f"{col}10"] = f"={col}4-{col}5"; ws[f"{col}10"].number_format = "#,##0"; ws[f"{col}10"].font = F_DERIV; ws[f"{col}10"].alignment = RGT
    ws[f"{col}11"] = f"={col}7/{col}4"; ws[f"{col}11"].number_format = "0.0%"; ws[f"{col}11"].font = F_DERIV; ws[f"{col}11"].alignment = RGT
    ws[f"{col}12"] = f"={col}8/{col}4"; ws[f"{col}12"].number_format = "0.0%"; ws[f"{col}12"].font = F_DERIV; ws[f"{col}12"].alignment = RGT

# 同比列 E：金额行=增长率公式；比率行=百分点差（×100，显示 pct）
growth_rows = [4, 5, 7, 8, 10]
pct_rows = [6, 9, 11, 12]
for r in growth_rows:
    ws[f"E{r}"] = f"=IF(C{r}=0,\"\",D{r}/C{r}-1)"
    ws[f"E{r}"].number_format = '+0.0%;-0.0%;0.0%'
    ws[f"E{r}"].font = F_BODY; ws[f"E{r}"].alignment = RGT
for r in pct_rows:
    ws[f"E{r}"] = f"=(D{r}-C{r})*100"
    ws[f"E{r}"].number_format = '+0.0"pct";-0.0"pct";0.0"pct"'
    ws[f"E{r}"].font = F_BODY; ws[f"E{r}"].alignment = RGT

# 汇总区（14-15）
ws["A14"] = "三年净利润合计（万元）"; ws["A14"].font = F_LABEL
ws["B14"] = "=SUM(B8:D8)"; ws["B14"].number_format = "#,##0"; ws["B14"].font = Font(name="Arial", size=11, bold=True)
ws["A15"] = "三年营业收入合计（万元）"; ws["A15"].font = F_LABEL
ws["B15"] = "=SUM(B4:D4)"; ws["B15"].number_format = "#,##0"; ws["B15"].font = Font(name="Arial", size=11, bold=True)
for r in (14, 15):
    ws.cell(row=r, column=1).alignment = LFT
    ws.cell(row=r, column=2).alignment = RGT
    ws.cell(row=r, column=1).border = Border(top=Side(style="thin", color=NAVY))
    ws.cell(row=r, column=2).border = Border(top=Side(style="thin", color=NAVY))

# ---------- 3. 条件格式 ----------
# 同比列：正增长绿、负增长红（增长率与百分点差均以 0 为界）
ws.conditional_formatting.add("E4:E12",
    CellIsRule(operator="greaterThan", formula=["0"], fill=GREEN_FILL, font=GREEN_FONT))
ws.conditional_formatting.add("E4:E12",
    CellIsRule(operator="lessThan", formula=["0"], fill=RED_FILL, font=RED_FONT))
# 金额行 2022-2024 数据条（同量纲：万元）
for rng in ("B4:D5", "B7:D8", "B10:D10"):
    ws.conditional_formatting.add(rng,
        DataBarRule(start_type="min", end_type="max", color=BLUE, showValue=True))
# 资产负债率超过 40% 标红（业务阈值）
ws.conditional_formatting.add("B9:D9",
    CellIsRule(operator="greaterThan", formula=["0.4"], fill=RED_FILL, font=RED_FONT))
# 毛利率/净利率低于 40%/10% 提示（毛利率阈值 40%）
ws.conditional_formatting.add("B6:D6",
    CellIsRule(operator="lessThan", formula=["0.4"], fill=PatternFill("solid", fgColor="FFF2CC")))

# 列宽 / 冻结
ws.column_dimensions["A"].width = 22
for col in ("B", "C", "D", "E"):
    ws.column_dimensions[col].width = 14
ws.freeze_panes = "B4"
ws.sheet_view.showGridLines = False

# ---------- 4. 说明 sheet ----------
ws2 = wb.create_sheet("口径与问答")
ws2.column_dimensions["A"].width = 26; ws2.column_dimensions["B"].width = 70
notes = [
    ("项目", "说明"),
    ("数据来源", "素材/表格/table1_财务摘要.csv 与 table1_财务摘要.png，二者一致；CSV 数字含千分位逗号，已按 5 列结构正确解析。"),
    ("金额口径", "营业收入、营业成本、研发费用、净利润、毛利额单位均为万元；金额单元格为数值型并采用千分位格式。"),
    ("比率口径", "毛利率、资产负债率、研发费用率、净利率按小数存储、百分比显示（如 42.3% 存为 0.423）。"),
    ("同比口径", "金额行 2024 年同比 = 2024/2023-1（增长率）；比率行 2024 年同比 = 2024-2023，单位为百分点（pct）。"),
    ("派生指标公式", "毛利额=营业收入-营业成本；研发费用率=研发费用/营业收入；净利率=净利润/营业收入。"),
    ("条件格式", "同比列正增长绿底、负增长红底；金额行 2022–2024 加数据条；资产负债率>40% 标红；毛利率<40% 黄色提示。"),
    ("问答1：2024年净利润", "618 万元（单元格 财务分析报表!D8）"),
    ("问答2：毛利率同比变化", "+1.0pct（单元格 财务分析报表!E6，42.5%-41.5%）"),
    ("问答3：三年净利润合计", "1,456 万元（单元格 财务分析报表!B14 =SUM(B8:D8)，386+452+618）"),
]
for i, (a, b) in enumerate(notes, 1):
    ca, cb = ws2.cell(row=i, column=1, value=a), ws2.cell(row=i, column=2, value=b)
    ca.alignment = Alignment(vertical="top", wrap_text=True)
    cb.alignment = Alignment(vertical="top", wrap_text=True)
    if i == 1:
        ca.font = F_HEAD; cb.font = F_HEAD; ca.fill = PatternFill("solid", fgColor=BLUE); cb.fill = PatternFill("solid", fgColor=BLUE)
    else:
        ca.font = F_LABEL; cb.font = Font(name="微软雅黑", size=10)

wb.save(OUT)
print("saved:", OUT)

# 自检：打印解析结果与关键派生值
for r in rows:
    print("解析:", r)
print("三年净利润合计 =", sum(ni), "| 三年营收合计 =", sum(rev))
print("毛利额 =", [rev[i]-cost[i] for i in range(3)])
