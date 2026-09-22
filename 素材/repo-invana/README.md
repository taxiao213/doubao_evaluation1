# invana

库存与订单分析模拟项目（Python 3.10+，无第三方运行时依赖）。

## 目录结构
- `src/invana/models` 数据模型
- `src/invana/repo` 数据访问（内存 / CSV）
- `src/invana/services` 业务服务（定价、订单、报表、库存）
- `src/invana/utils` 工具（货币、日期、校验、格式化）
- `src/invana/adapters` 外部数据适配（CSV / JSON / HTTP）
- `docs/` 规范与架构说明

## 快速开始
```bash
python3 -m pytest tests/ -q          # 运行测试（PYTHONPATH 已在 pyproject 配置说明）
PYTHONPATH=src python3 -m invana.cli summary tests/fixtures/orders.csv
```

## 当前任务
1. **[BUG] `tests/test_report_totals.py` 失败**：报表订单合计金额与业务方对账结果不一致。
   请根据 `docs/spec.md` 的金额舍入规范定位根因，并以最小改动修复。
   要求：不得修改任何测试文件；修复后全部测试通过。
2. **[FEATURE]**（修复后选做）：为报表服务增加按客户分组导出 CSV 的能力，入口见 `services/report.py`。
