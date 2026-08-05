# YMatrix / MySQL Benchmark MVP

这是一个 Python 3.6.8 标准库实现的、可复现的 TPC-H 风格小规模 benchmark 工具。它使用 `customer`、`part`、`orders`、`lineitem` 四张表和 Q01–Q03 三条查询，记录客户端进程端到端耗时。

## Windows 安全流程

```text
copy config.example.json config.local.json
python run.py preflight --config config.local.json
python run.py generate --config config.local.json
python -m unittest discover -s tests -v
python -m compileall run.py src tests
```

Windows 不连接真实数据库。Linux 部署后，先人工检查 `config.local.json`，再按需执行 `load`、`validate`、`benchmark`。密码只保存在 Linux 本地配置中，不要提交。

## 结果

benchmark 输出 `results/benchmark_detail.csv`、`results/benchmark_report.md`、`results/environment.md` 和 `results/benchmark.log`。p95 使用 nearest-rank：`ceil(0.95 * n)`。

本项目当前使用简化的 TPC-H 风格数据和查询，不属于标准 TPC-H 测试；结果来自单节点、小规模、低并发环境，不能代表生产集群性能。
