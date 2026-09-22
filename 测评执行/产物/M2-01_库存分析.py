#!/usr/bin/env python3
# M2-01：真实读取库存 CSV -> 计算指标 -> 写新文件
# 注意：该 CSV 中千分位数字（1,150 / 1,032）会被朴素逗号切分拆成两列，
# 必须按 8 列标准结构做列对齐修复，不能直接 split(',')。
import csv, os, sys

SRC = "/Users/secneo/Documents/workspace/ai_project/doubao_work2/素材/表格/table2_库存明细.csv"
OUT = "/Users/secneo/Documents/workspace/ai_project/doubao_work2/测评执行/产物/M2-01_库存指标结果.csv"

HEADER = ["物料编码","物料名称","规格","单位","账面数量","可用数量","在途","仓库"]

def parse_row(fields):
    """标准 8 列；若被千分位逗号切成 10 列，合并第 5/6、7/8 个字段。"""
    if len(fields) == 8:
        return fields
    if len(fields) == 10:
        merged = fields[:4] + [fields[4]+fields[5], fields[6]+fields[7]] + fields[8:]
        return merged
    raise ValueError(f"异常列数 {len(fields)}: {fields}")

rows = []
with open(SRC, encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    assert header == HEADER, f"表头与预期不符: {header}"
    for raw in reader:
        if not raw: continue
        r = parse_row(raw)
        rows.append(r)

# 计算指标
total_book = total_avail = total_transit = 0
report = []
for r in rows:
    code, name, spec, unit, book, avail, transit, wh = r
    book, avail, transit = int(book), int(avail), int(transit)
    total_book += book; total_avail += avail; total_transit += transit
    util = avail / book
    # 预警：可用/账面 < 70% 视为低库存
    warn = "低库存" if util < 0.70 else ("无在途" if transit == 0 else "正常")
    report.append([code, name, spec, unit, book, avail, transit,
                   f"{util:.1%}", warn])

with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(HEADER[:4] + ["账面数量","可用数量","在途","可用率","预警"])
    w.writerows(report)
    w.writerow([])
    w.writerow(["合计","","","",total_book,total_avail,total_transit,
                f"{total_avail/total_book:.1%}",""])

# 真值问答
q1 = next(r for r in rows if r[2] == "6204-2RS")[4]
q2 = next(r for r in rows if r[2] == "M8×30")
q3 = [r[0] for r in rows if int(r[6]) == 0]

print(f"实际读取行数: {len(rows)}")
print(f"总账面: {total_book:,}  总可用: {total_avail:,}  总在途: {total_transit:,}")
print(f"整体可用率: {total_avail/total_book:.2%}")
print(f"Q1 6204-2RS 账面数量 = {int(q1):,}")
print(f"Q2 M8×30 可用/在途 = {q2[5]} / {q2[6]}")
print(f"Q3 在途为0的物料 = {', '.join(q3)}")
print(f"结果已写入: {OUT}")
