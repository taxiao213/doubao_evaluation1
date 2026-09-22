# -*- coding: utf-8 -*-
"""生成测评视觉类素材：图表、表格、工程图纸、3D 渲染图。
每类素材附带 ground_truth JSON（预记录真值 + 问答对），供 M4/M6 评分使用。
"""
import json
import math
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, Rectangle, FancyArrow, Polygon
from matplotlib.lines import Line2D
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "素材"

plt.rcParams["font.sans-serif"] = ["PingFang SC", "Hiragino Sans GB", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False


def save_gt(path: Path, data: dict):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  GT -> {path.name}")


# ---------------------------------------------------------------- 图表（M6-03 数值反查）
def gen_charts():
    out = ASSETS / "图表"
    out.mkdir(exist_ok=True)

    # 1. 柱状图：季度营收
    quarters = ["2024Q1", "2024Q2", "2024Q3", "2024Q4"]
    revenue = [1.42, 1.63, 1.84, 2.11]
    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    bars = ax.bar(quarters, revenue, color="#4C78A8", width=0.55)
    for b, v in zip(bars, revenue):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.03, f"{v:.2f}", ha="center", fontsize=11)
    ax.set_title("图1：某公司 2024 年分季度营收（亿元）", fontsize=14)
    ax.set_ylabel("营收（亿元）")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(out / "chart1_柱状图_季度营收.png")
    plt.close(fig)
    save_gt(out / "chart1_ground_truth.json", {
        "type": "柱状图",
        "标题": "某公司 2024 年分季度营收（亿元）",
        "数据": dict(zip(quarters, revenue)),
        "问答": [
            {"问题": "2024Q3 的营收是多少亿元？", "答案": "1.84"},
            {"问题": "全年营收合计是多少亿元？", "答案": "7.00"},
            {"问题": "环比增速最快的季度是哪个？", "答案": "2024Q4（约12.6%）"},
        ],
    })

    # 2. 折线图：月活用户
    months = [f"{m}月" for m in range(1, 13)]
    mau = [320, 335, 351, 348, 372, 398, 425, 441, 470, 512, 548, 590]
    fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
    ax.plot(months, mau, marker="o", color="#E45756", linewidth=2)
    ax.set_title("图2：某产品 2024 年月活跃用户数（万）", fontsize=14)
    ax.set_ylabel("MAU（万）")
    ax.grid(axis="y", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(out / "chart2_折线图_月活用户.png")
    plt.close(fig)
    save_gt(out / "chart2_ground_truth.json", {
        "type": "折线图",
        "标题": "某产品 2024 年月活跃用户数（万）",
        "数据": dict(zip(months, mau)),
        "问答": [
            {"问题": "7 月的月活是多少万？", "答案": "425"},
            {"问题": "唯一出现环比下降的月份是？", "答案": "4月（348 < 351）"},
            {"问题": "12月比1月增长了多少万？", "答案": "270"},
        ],
    })

    # 3. 饼图：市场份额
    labels = ["厂商A", "厂商B", "厂商C", "厂商D", "其他"]
    shares = [31.5, 24.8, 17.2, 11.6, 14.9]
    fig, ax = plt.subplots(figsize=(7, 6), dpi=150)
    ax.pie(shares, labels=labels, autopct="%.1f%%", startangle=90,
           colors=["#4C78A8", "#F58518", "#E45756", "#72B7B2", "#B0B0B0"])
    ax.set_title("图3：2024 年某品类市场份额分布", fontsize=14)
    fig.tight_layout()
    fig.savefig(out / "chart3_饼图_市场份额.png")
    plt.close(fig)
    save_gt(out / "chart3_ground_truth.json", {
        "type": "饼图",
        "标题": "2024 年某品类市场份额分布",
        "数据": dict(zip(labels, shares)),
        "问答": [
            {"问题": "厂商B 的市场份额是多少？", "答案": "24.8%"},
            {"问题": "份额最大的两家合计占比多少？", "答案": "56.3%"},
            {"问题": "“其他”类别占多少？", "答案": "14.9%"},
        ],
    })

    # 4. 分组柱状图：两条产品线对比
    q4 = ["Q1", "Q2", "Q3", "Q4"]
    prod_a = [82, 95, 88, 104]
    prod_b = [64, 71, 86, 99]
    x = np.arange(len(q4)); w = 0.35
    fig, ax = plt.subplots(figsize=(8.5, 5), dpi=150)
    ax.bar(x - w/2, prod_a, w, label="产品线A", color="#4C78A8")
    ax.bar(x + w/2, prod_b, w, label="产品线B", color="#F58518")
    ax.set_xticks(x, q4)
    ax.set_title("图4：产品线A/B 分季度出货量（千件）", fontsize=14)
    ax.set_ylabel("出货量（千件）")
    ax.legend()
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(out / "chart4_分组柱状图_产品对比.png")
    plt.close(fig)
    save_gt(out / "chart4_ground_truth.json", {
        "type": "分组柱状图",
        "标题": "产品线A/B 分季度出货量（千件）",
        "数据": {"产品线A": dict(zip(q4, prod_a)), "产品线B": dict(zip(q4, prod_b))},
        "问答": [
            {"问题": "Q3 产品线B 的出货量是多少千件？", "答案": "86"},
            {"问题": "哪一季度产品线B 首次反超产品线A？", "答案": "Q3"},
            {"问题": "产品线A 全年合计多少千件？", "答案": "369"},
        ],
    })

    # 5. 高密度堆叠面积图：数值反查难点
    months6 = ["3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
    online = [120, 128, 135, 150, 158, 166, 180, 172, 190, 205]
    offline = [95, 92, 98, 104, 101, 108, 112, 96, 118, 125]
    fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
    ax.stackplot(months6, online, offline, labels=["线上", "线下"],
                 colors=["#4C78A8", "#54A24B"], alpha=0.85)
    ax.set_title("图5：渠道销售额构成（万元）", fontsize=14)
    ax.set_ylabel("销售额（万元）")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(out / "chart5_堆叠面积图_渠道构成.png")
    plt.close(fig)
    save_gt(out / "chart5_ground_truth.json", {
        "type": "堆叠面积图",
        "标题": "渠道销售额构成（万元）",
        "数据": {"线上": dict(zip(months6, online)), "线下": dict(zip(months6, offline))},
        "问答": [
            {"问题": "11月线下销售额大约是多少万元？", "答案": "118（堆叠图中需先减去线上部分，反查难度较高）"},
            {"问题": "10月为什么总销售额下降？", "答案": "线上、线下同时回落（172<180 且 96<112）"},
        ],
    })
    print("图表素材完成")


# ---------------------------------------------------------------- 表格（M6-02 / M3-04 输入）
def gen_tables():
    out = ASSETS / "表格"
    out.mkdir(exist_ok=True)

    # 表1：财务摘要表（CSV + 截图）
    rows1 = [
        ["指标", "2022年", "2023年", "2024年", "同比变化"],
        ["营业收入（万元）", "3,842", "4,517", "5,394", "+19.4%"],
        ["营业成本（万元）", "2,215", "2,644", "3,101", "+17.3%"],
        ["毛利率", "42.3%", "41.5%", "42.5%", "+1.0pct"],
        ["研发费用（万元）", "612", "748", "905", "+21.0%"],
        ["净利润（万元）", "386", "452", "618", "+36.7%"],
        ["资产负债率", "38.6%", "41.2%", "39.8%", "-1.4pct"],
    ]
    with open(out / "table1_财务摘要.csv", "w", encoding="utf-8") as f:
        f.write("\n".join(",".join(r) for r in rows1))
    fig, ax = plt.subplots(figsize=(9, 4.2), dpi=150)
    ax.axis("off")
    tb = ax.table(cellText=rows1[1:], colLabels=rows1[0], loc="center",
                  cellLoc="center", colWidths=[0.24, 0.16, 0.16, 0.16, 0.16])
    tb.auto_set_font_size(False); tb.set_fontsize(11); tb.scale(1, 1.6)
    for j in range(5):
        tb[0, j].set_facecolor("#DCE6F1"); tb[0, j].set_text_props(weight="bold")
    fig.tight_layout()
    fig.savefig(out / "table1_财务摘要.png", bbox_inches="tight")
    plt.close(fig)
    save_gt(out / "table1_ground_truth.json", {
        "预标注字段": {r[0]: r[1:] for r in rows1[1:]},
        "问答": [
            {"问题": "2024年净利润是多少万元？", "答案": "618"},
            {"问题": "毛利率同比变化是多少？", "答案": "+1.0pct"},
            {"问题": "三年净利润合计？", "答案": "1,456万元"},
        ],
    })

    # 表2：库存明细表（含易混淆列，测试列对齐能力）
    rows2 = [
        ["物料编码", "物料名称", "规格", "单位", "账面数量", "可用数量", "在途", "仓库"],
        ["WL-10021", "六角螺栓", "M8×30", "盒", "420", "385", "60", "A区-03"],
        ["WL-10022", "六角螺栓", "M10×40", "盒", "260", "245", "0", "A区-04"],
        ["WL-20035", "轴承", "6204-2RS", "个", "1,150", "1,032", "300", "B区-01"],
        ["WL-20041", "轴承", "6000-ZZ", "个", "860", "812", "150", "B区-02"],
        ["WL-30012", "密封圈", "Φ45×2", "包", "95", "60", "0", "C区-01"],
        ["WL-30018", "密封圈", "Φ60×3", "包", "180", "175", "40", "C区-02"],
    ]
    with open(out / "table2_库存明细.csv", "w", encoding="utf-8") as f:
        f.write("\n".join(",".join(r) for r in rows2))
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=150)
    ax.axis("off")
    tb = ax.table(cellText=rows2[1:], colLabels=rows2[0], loc="center", cellLoc="center")
    tb.auto_set_font_size(False); tb.set_fontsize(10); tb.scale(1, 1.5)
    for j in range(8):
        tb[0, j].set_facecolor("#E2EFDA"); tb[0, j].set_text_props(weight="bold")
    fig.tight_layout()
    fig.savefig(out / "table2_库存明细.png", bbox_inches="tight")
    plt.close(fig)
    save_gt(out / "table2_ground_truth.json", {
        "预标注字段": {r[0]: r[1:] for r in rows2[1:]},
        "问答": [
            {"问题": "规格为 6204-2RS 的轴承账面数量是多少？", "答案": "1,150"},
            {"问题": "M8×30 六角螺栓的可用数量和在途分别是多少？", "答案": "385 / 60"},
            {"问题": "哪些物料在途数量为 0？", "答案": "WL-10022、WL-30012"},
        ],
    })
    print("表格素材完成")


# ---------------------------------------------------------------- 工程图纸（M6-01）
def _dim_arrow(ax, x0, y0, x1, y1, text, offset=0.0, fontsize=9):
    """画一条带箭头的尺寸标注线。"""
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="<|-|>", color="black", lw=0.8,
                                shrinkA=0, shrinkB=0, mutation_scale=8))
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    ax.text(mx, my + offset, text, ha="center", va="bottom", fontsize=fontsize,
            bbox=dict(facecolor="white", edgecolor="none", pad=0.5))


def gen_drawing():
    out = ASSETS / "工程图纸"
    out.mkdir(exist_ok=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7), dpi=150)

    # ---- 左：主视图（法兰盘，中心孔 + 6 均布螺栓孔）
    ax1.set_aspect("equal"); ax1.axis("off")
    ax1.set_title("主视图（比例 1:1）", fontsize=12)
    outer = Circle((0, 0), 60, fill=False, lw=2)
    hub = Circle((0, 0), 24, fill=False, lw=2)
    bore = Circle((0, 0), 12.5, fill=False, lw=2)  # Ø25 H7 中心孔
    ax1.add_patch(outer); ax1.add_patch(hub); ax1.add_patch(bore)
    n_holes = 6
    hole_r = 42
    for i in range(n_holes):
        a = math.radians(90 + i * 360 / n_holes)
        cx, cy = hole_r * math.cos(a), hole_r * math.sin(a)
        ax1.add_patch(Circle((cx, cy), 4.5, fill=False, lw=1.5))
        ax1.plot([0, cx], [0, cy], ls=(0, (6, 3, 1, 3)), color="#888", lw=0.6)
    # 中心线
    ax1.plot([-72, 72], [0, 0], ls=(0, (8, 3, 1, 3)), color="#333", lw=0.8)
    ax1.plot([0, 0], [-72, 72], ls=(0, (8, 3, 1, 3)), color="#333", lw=0.8)
    # 尺寸标注
    _dim_arrow(ax1, -60, -78, 60, -78, "Ø120 ±0.2")
    _dim_arrow(ax1, 78, -24, 78, 24, "Ø48 h9")
    _dim_arrow(ax1, -12.5, 68, 12.5, 68, "Ø25 H7")
    ax1.text(42, 52, "6×Ø9 均布", fontsize=9, color="black")
    ax1.text(-58, -95, "材料：45钢  未注公差按 GB/T 1804-m", fontsize=9)
    ax1.set_xlim(-100, 100); ax1.set_ylim(-105, 85)

    # ---- 右：剖视图 A-A
    ax2.set_aspect("equal"); ax2.axis("off")
    ax2.set_title("剖视图 A-A（比例 1:1）", fontsize=12)
    # 法兰剖面轮廓：左右对称的阶梯剖面
    prof_left = [(-60, 0), (-60, 12), (-24, 12), (-24, 30), (-12.5, 30), (-12.5, 0)]
    prof_right = [(60, 0), (60, 12), (24, 12), (24, 30), (12.5, 30), (12.5, 0)]
    for prof in (prof_left, prof_right):
        ax2.add_patch(Polygon(prof, closed=True, facecolor="#E8E8E8",
                              edgecolor="black", lw=1.5, hatch="///"))
    ax2.plot([0, 0], [-8, 38], ls=(0, (8, 3, 1, 3)), color="#333", lw=0.8)
    # 厚度标注
    _dim_arrow(ax2, -75, 0, -75, 12, "12")
    _dim_arrow(ax2, -75, 12, -75, 30, "18")
    _dim_arrow(ax2, 0, 38, 0, 30, "")
    ax2.text(30, 40, "总高 30±0.1", fontsize=9)
    ax2.text(-60, -18, "表面粗糙度：配合面 Ra1.6，其余 Ra6.3", fontsize=9)
    ax2.text(-60, -28, "倒角 C1；剖切位置见主视图 A-A", fontsize=9)
    ax2.set_xlim(-100, 100); ax2.set_ylim(-40, 55)

    fig.suptitle("法兰盘 FS-45 零件图", fontsize=15, y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out / "drawing1_法兰盘零件图.png", bbox_inches="tight")
    plt.close(fig)
    save_gt(out / "drawing1_ground_truth.json", {
        "零件名称": "法兰盘 FS-45",
        "预标注字段": {
            "外径及公差": "Ø120 ±0.2",
            "轮毂外径及公差": "Ø48 h9",
            "中心孔径及公差": "Ø25 H7",
            "螺栓孔": "6×Ø9 均布，分布圆半径 42",
            "法兰厚度": "12",
            "轮毂凸台高": "18",
            "总高及公差": "30±0.1",
            "材料": "45钢",
            "未注公差标准": "GB/T 1804-m",
            "表面粗糙度": "配合面 Ra1.6，其余 Ra6.3",
            "倒角": "C1",
        },
        "问答": [
            {"问题": "中心孔的直径和公差代号是什么？", "答案": "Ø25 H7"},
            {"问题": "螺栓孔有几个、直径多大？", "答案": "6 个 Ø9，均布"},
            {"问题": "未注公差遵循哪个标准？", "答案": "GB/T 1804-m"},
            {"问题": "剖视图 A-A 中总高公差是多少？", "答案": "30±0.1"},
        ],
    })
    print("工程图纸素材完成")


# ---------------------------------------------------------------- 3D 素材（M6-04）
def gen_3d():
    out = ASSETS / "3D素材"
    out.mkdir(exist_ok=True)

    # 素材1：阶梯轴（两视角）
    fig = plt.figure(figsize=(12, 5.5), dpi=140)
    steps = [(0.0, 1.6, 1.0), (1.6, 1.2, 1.6), (2.8, 1.4, 1.2), (4.2, 1.2, 0.8)]
    for i, (elev, azim) in enumerate([(22, -55), (12, 35)]):
        ax = fig.add_subplot(1, 2, i + 1, projection="3d")
        for z0, r, length in steps:
            u = np.linspace(0, 2 * np.pi, 40)
            v = np.linspace(z0, z0 + length, 6)
            uu, vv = np.meshgrid(u, v)
            xx = r * np.cos(uu); yy = r * np.sin(uu)
            ax.plot_surface(xx, yy, np.broadcast_to(vv, xx.shape), color="#9BB7D4", alpha=0.95)
            ax.plot_surface(xx, yy, np.broadcast_to(vv[-1] + 0 * vv, xx.shape),
                            color="#7C9CBF", alpha=0.95)
        ax.set_xlim(-2, 2); ax.set_ylim(-2, 2); ax.set_zlim(-0.5, 6)
        ax.view_init(elev=elev, azim=azim)
        ax.set_title(f"视角{i+1}（elev={elev}, azim={azim}）", fontsize=10)
        ax.set_box_aspect((1, 1, 1.6))
    fig.suptitle("零件 P-01 渲染图（多视角）", fontsize=13)
    fig.tight_layout()
    fig.savefig(out / "render1_阶梯轴_双视角.png", bbox_inches="tight")
    plt.close(fig)
    save_gt(out / "render1_ground_truth.json", {
        "部件类型": "阶梯轴（4 级阶梯，沿轴从一端半径变化 1.0→1.6→1.2→0.8）",
        "问答": [
            {"问题": "该零件属于什么类型？", "答案": "阶梯轴（回转体轴类零件）"},
            {"问题": "共有几级阶梯（不同直径段）？", "答案": "4 段不同直径"},
            {"问题": "最大直径段位于轴的哪一端附近？", "答案": "距左端（起始端）第二段，半径 1.6"},
        ],
    })

    # 素材2：带缺口的法兰座（俯视 + 斜视）
    fig = plt.figure(figsize=(12, 5.5), dpi=140)
    # 构造一个圆盘 + 顶面矩形缺口 + 4 孔
    for i, (elev, azim) in enumerate([(90, -90), (30, -60)]):
        ax = fig.add_subplot(1, 2, i + 1, projection="3d")
        u = np.linspace(0, 2 * np.pi, 80)
        v = np.linspace(0, 2.4, 12)
        uu, vv = np.meshgrid(u, v)
        ax.plot_surface(3 * np.cos(uu), 3 * np.sin(uu), np.broadcast_to(vv, uu.shape),
                        color="#C9CBA3", alpha=0.9)
        top = np.zeros_like(uu)
        ax.plot_surface(3 * np.cos(uu), 3 * np.sin(uu), np.broadcast_to(top, uu.shape),
                        color="#A5B76B", alpha=0.95)
        # 缺口：在圆盘上画一块深色矩形表示切除区域
        gx, gy = np.meshgrid(np.linspace(0, 2.2, 20), np.linspace(-0.7, 0.7, 12))
        ax.plot_surface(gx, gy, np.full_like(gx, 2.41), color="#404040")
        for hx, hy in [(-1.9, -1.9), (-1.9, 1.9), (1.9, -1.9), (1.9, 1.9)]:
            hu = np.linspace(0, 2 * np.pi, 24)
            ax.plot(0.35 * np.cos(hu) + hx, 0.35 * np.sin(hu) + hy,
                    np.full_like(hu, 2.42), color="black", lw=1.2)
        ax.view_init(elev=elev, azim=azim)
        ax.set_title(f"视角{i+1}（elev={elev}, azim={azim}）", fontsize=10)
        ax.set_zlim(0, 3)
        ax.set_box_aspect((1, 1, 0.45))
    fig.suptitle("零件 P-02 渲染图（俯视 + 斜视）", fontsize=13)
    fig.tight_layout()
    fig.savefig(out / "render2_法兰座_双视角.png", bbox_inches="tight")
    plt.close(fig)
    save_gt(out / "render2_ground_truth.json", {
        "部件类型": "圆形法兰座，顶面有一处矩形缺口（切除槽），四角各有一个安装孔",
        "问答": [
            {"问题": "顶面的深色矩形区域表示什么？", "答案": "一个贯穿/沉入顶面的矩形缺口（切除槽）"},
            {"问题": "安装孔有几个，分布在什么位置？", "答案": "4 个，位于四角对称分布"},
            {"问题": "缺口位于零件的哪个方位？", "答案": "从中心偏向右侧（+X 方向）半边"},
        ],
    })
    print("3D 素材完成")


if __name__ == "__main__":
    gen_charts()
    gen_tables()
    gen_drawing()
    gen_3d()
    print("全部视觉素材生成完毕")
