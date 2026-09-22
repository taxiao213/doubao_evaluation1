#!/bin/bash
# M2 模块过程证据回放（在 Terminal 中可见地复现真实工具调用结果）
cd "/Users/secneo/Documents/workspace/ai_project/doubao_work2"
clear
echo "########## M2-01 真实读取CSV并计算（含千分位列对齐陷阱） ##########"
".venv/bin/python" "测评执行/产物/M2-01_库存分析.py"
echo ""
echo "########## M2-02 故意调用报错工具，如实反馈 ##########"
echo "--- 500 接口 ---"
curl -sS -m 15 -o /dev/null -w "HTTP状态码: %{http_code}\n" "https://httpbin.org/status/500"
echo "--- 不存在的文件 ---"
cat "素材/不存在的文件_20260922.csv" 2>&1 | head -1
echo ""
echo "########## M2-03 B步：等待长耗时子任务（pytest）真实返回 ##########"
cd "素材/repo-invana"
"../../.venv/bin/python" -m pytest tests/ -q 2>&1 | tail -3
echo ""
echo "########## M2 全部步骤完成，结果均来自真实工具返回 ##########"
