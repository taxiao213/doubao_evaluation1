# 测评素材总索引

> 生成日期：2026-09-22 ｜ 配套方案：《Seed-2.1-pro-测评方案.md》
> 除 `repo-invana` 外，所有图像类素材均为 PNG，并附带同名/同目录 `ground_truth.json` 预记录真值。
> 生成脚本在 `../scripts/`，可随时重新生成或调整数据。

## 目录对照表

| 目录 | 文件 | 对应 Case | 说明 |
|------|------|-----------|------|
| `图表/` | chart1–chart5 PNG + 5 份 GT | M6-03 | 柱状/折线/饼图/分组柱状/堆叠面积，GT 内含"数值反查"问答对；chart5 为高难度（堆叠图反查底层系列） |
| `表格/` | table1/table2 CSV+PNG + GT | M6-02、M3-04 | table1 财务摘要；table2 库存明细含同名列易混淆项（测列对齐） |
| `工程图纸/` | drawing1 PNG + GT | M6-01 | 法兰盘零件图：主视图+剖视图、尺寸/公差（H7、h9、±0.2）、粗糙度、跨视图引用；GT 含 11 项预标注字段 |
| `财报PDF/` | 华晟精密2024年报节选.pdf + GT | M4-01/03、M6-02 | 2 页虚构年报：表格+脚注①②③+图表+**跨页引用**（第1页脚注③→第2页附注3）+分季度核验陷阱 |
| `UI设计稿/` | 3 张 PNG（附 HTML 源）+ GT | M5-03 | 落地页（1440）/后台仪表盘（1440）/移动端卡片流（390），难度递增；HTML 源文件可作还原度 diff 基准 |
| `3D素材/` | render1/render2 PNG + GT | M6-04 | 阶梯轴（4 级阶梯双视角）、法兰座（矩形缺口+4 安装孔，俯视+斜视） |
| `repo-invana/` | 51 个文件的 Python 项目 | M5-01/02 | 见下方详细说明 |
| `ComputerUse/` | 退货申请表单.html + case卡与真值.json | M8-B | 自包含网页表单，内埋 4 类意外 + 事件日志；详见下方说明 |

## repo-invana（Coding 测试仓库）

- 结构：`models / repo / services / utils / adapters / cli / tests / docs`，51 文件
- **预埋 bug（唯一）**：`src/invana/utils/currency.py` 的 `round_money()` 使用 `ROUND_DOWN`（截断），而 `docs/spec.md` 规范要求四舍五入（ROUND_HALF_UP）。bug 在工具层，但症状经 `services/pricing.py` → `services/report.py` 跨层传导至对账测试——测"跨文件根因定位"。
- **当前基线**：`python3 -m pytest tests/ -q` → **2 failed, 21 passed**（仅 `tests/test_report_totals.py` 两个财务对账测试失败）
- **标准答案已验证**：将 `ROUND_DOWN` 改为 `ROUND_HALF_UP` 后 **23 全部通过**
- 测评任务已写入仓库 `README.md`（禁止修改测试文件；观察被测模型是否只做最小改动、是否跑测试验证、是否提前宣告完成）
- 运行方式：`cd repo-invana && python3 -m pytest tests/ -q`（pytest 需要可用环境，本机在 `../.venv`）

## ComputerUse（M8-B 表单 + 异常恢复）

- `退货申请表单.html`：自包含页面（file:// 直接打开，无服务端）。埋点：①首次提交 100% 弹"E-1024 网络错误"，须点【重试提交】才成功 ②"质量问题"下拉项需滚动 ③选中后动态展开描述/凭证字段 ④订单号/手机号格式校验
- 事件日志与提交记录：页面内 `window.__cuDump()`（也落盘 localStorage：`cu_event_log` / `cu_return_submissions`），评分脚本直接读取断言
- 任务指令、预期最终状态、8 检查点、40/30/20/10 评分权重、一票否决项：见 `退货申请_case卡与真值.json`
- **每次执行前必须清空 localStorage**（两个键），否则事件会跨轮次累积
- 正确路径事件流（已验证）：`page_loaded → quality_block_revealed → submit_clicked → network_error_shown → retry_clicked → submit_succeeded`
- M8-A（跨应用数据搬运）复用 `财报PDF/` 素材，M8-C（看图整理文件）复用 `图表/工程图纸/UI设计稿/` 素材，均无需额外准备

## M1-03（搜索工具不可用诚实性）素材

无需预置素材——在禁用搜索工具的环境下直接提问即可（方案 M1-03）。

## 待补充（暂无现成生成脚本）

- [ ] 如需更多工程图纸变体，可扩展 `scripts/gen_visual_assets.py` 的 `gen_drawing()`
- [ ] 如需 M8-B 变体（不同陷阱组合），可复制退货申请表单.html 修改 submit 逻辑
