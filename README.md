# YMatrix / MySQL SQL Benchmark V3

这是一个仅使用 Python 3.6.8 标准库实现的、可复现的数据库 Benchmark 工具，支持 YMatrix 与 MySQL 的 TPC-H 兼容分析查询对比。

项目使用 region、nation、supplier、customer、part、partsupp、orders、lineitem 八张供应链表和 Q01–Q22 分析查询。数据由自研标准库生成器产生，因此它不是官方 dbgen/qgen 或经审计的标准 TPC-H；TPC-C 当前提供扩展方案。

## 数据关系

```text
region → nation → supplier ─┐
          │                 ├→ partsupp ← part
          └→ customer → orders → lineitem ─┘
```

`partsupp` 定义商品与供应商的可供货关系，`lineitem(partkey,suppkey)` 必须存在对应 partsupp；customer 通过 orders 发起采购，lineitem 记录实际商品、供应商、数量、价格、折扣、税和物流日期。

## 已实现能力

- JSON 配置：数据库连接、SQL 目录、轮数、并发、预热、超时和 `session_sql`。
- 非递归、按文件名升序批量发现全部 `.sql` 文件。
- 确定性数据生成：seed=2026，默认 SF=0.01，八表规模为 5/25/100/1500/2000/8000/15000/60000。
- 两库真实建表、清表、最多 500 行的多行 INSERT 装载。
- CSV 关联完整性、行数与两数据库 `COUNT(*)` 三方校验。
- warmup 与 measurement 分离；`time.monotonic()` 端到端计时。
- avg、min、max、nearest-rank p95、成功率和失败分类。
- 两数据库 Q01–Q22 结果业务一致性校验及逐查询性能差异。
- CSV 明细、Markdown 报告、环境说明和 benchmark.log。

## Windows 开发验证

```powershell
python -m unittest discover -s tests -v
python -m compileall run.py src tests
git diff --check
python run.py generate --config config.example.json
```

Windows 只运行 mock 测试和静态检查，不连接真实数据库。

## Linux 一键验收

首次只需创建项目专用 MySQL 数据库：

```bash
mysql -u root -e "CREATE DATABASE IF NOT EXISTS benchmark_mvp;"
```

确认 `config.local.json` 已存在且未被 Git 跟踪，然后执行：

```bash
bash scripts/acceptance_linux.sh config.local.json
```

脚本依次运行 compileall、unittest、preflight、generate、load、validate 和两次正式 benchmark。输出保存在：

```text
acceptance-results/YYYYMMDD-HHMMSS/
├── linux_compileall.txt
├── linux_unittest.txt
├── linux_preflight.txt
├── linux_generate.txt
├── linux_load.txt
├── linux_validate.txt
├── linux_benchmark_run1.txt
├── linux_benchmark_run2.txt
├── run1/
│   ├── benchmark_detail.csv
│   ├── benchmark_report.md
│   ├── environment.md
│   └── benchmark.log
└── run2/
    └── 同上四个文件
```

完整人工验收步骤见 [docs/acceptance.md](docs/acceptance.md)，面试说明见 [docs/interview_demo.md](docs/interview_demo.md)。

## 测试口径

本项目使用纯 Python 标准库生成 TPC-H 兼容数据和 22 类分析查询，不属于标准或经审计的 TPC-H 测试。

MVP 通过命令行客户端进程记录端到端执行时间，其中包含客户端进程启动和连接建立开销。

本次结果来自单节点、小规模、低轮数环境，不能代表生产集群性能。

YMatrix 与 MySQL 的结果仅适用于报告所记录的硬件、版本、参数和数据规模。
