# 架构说明

```
adapters ──▶ repo ──▶ services ──▶ cli
                │           │
                └── models  └── utils（currency/dates/…）
```

- `services.pricing` 是金额计算的唯一入口，所有金额必须经过 `utils.currency.round_money`。
- `services.report` 汇总行级金额生成对账报表，财务对账依赖其输出。
- `utils.currency` 是全项目唯一允许处理舍入的地方。
