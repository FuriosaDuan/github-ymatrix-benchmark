# YMatrix / MySQL TPC-H-Compatible Benchmark

## 项目定位

这是一个仅使用 Python 3.6.8 标准库实现的双数据库 SQL Benchmark 工具。项目用固定 seed 生成同一份供应链数据，在 YMatrix 与 MySQL 中装载八张关联表、执行 Q01～Q22、多轮统计执行时间、校验查询结果一致性，并自动输出 CSV 和 Markdown 报告。

本项目是 **TPC-H-compatible 工作负载**，不是官方或经审计的 TPC-H：它没有使用官方 `dbgen/qgen`，也没有实现完整 Power、Throughput、Refresh Function 和审计流程。当前项目也不是 TPC-C。

## 数据模型

```text
region → nation → supplier ─┐
            └→ customer     ├→ partsupp → part
                 └→ orders → lineitem ──┘
```

实际表统一使用 `tpch_` 前缀：

- `tpch_region`、`tpch_nation`：地区与国家层级。
- `tpch_supplier`、`tpch_customer`：供应商与采购商。
- `tpch_part`、`tpch_partsupp`：商品及供应商供货关系。
- `tpch_orders`、`tpch_lineitem`：采购订单与明细。

每条订单明细的 `(partkey, suppkey)` 都存在于 `partsupp`，两套数据库加载完全相同的 CSV。

## 已实现能力

- JSON 配置：双数据库连接、SQL 目录、scale factor、warmup、正式轮数、并发、超时和 `session_sql`。
- 固定 seed `2026` 的确定性八表数据生成；默认 SF=0.01。
- YMatrix 与 MySQL 真实 preflight、建表、清表和分批多行 INSERT。
- CSV 行数、表间关联和双数据库 `COUNT(*)` 三方校验。
- 非递归、按文件名排序发现两个 SQL 目录中的全部 `.sql` 文件。
- Q01～Q22 双数据库查询结果规范化和业务一致性校验。
- warmup 与 measurement 分离，使用 `time.monotonic()` 记录客户端端到端耗时。
- avg、min、max、nearest-rank p95、成功率、失败分类和逐查询性能差异。
- CSV 明细、Markdown 汇总、环境说明和 `benchmark.log`。
- Linux 两轮自动验收和时间戳结果归档。

## 环境要求

- Linux x86_64；已验证 CentOS 7.9。
- Python 3.6.8，仅使用标准库。
- YMatrix/PostgreSQL 兼容数据库和可执行的 `psql`。
- MySQL 5.7 兼容数据库和 PATH 中的 `mysql` 客户端。
- Git、Bash，以及项目表和项目数据库所需权限。

Windows 只用于 unittest、compileall 和 mock；真实数据库流程在 Linux 执行。

## 最短复现流程

首次拉取：

```bash
git clone https://github.com/FuriosaDuan/TPC-test.git ymatrix-mysql-benchmark
cd ymatrix-mysql-benchmark
cp config.example.json config.local.json
chmod 600 config.local.json
vi config.local.json
```

不要显示或提交 `config.local.json`。确认连接配置后执行：

```bash
mysql -u root -e "CREATE DATABASE IF NOT EXISTS benchmark_mvp;"
python3 -m compileall run.py src tests
python3 -m unittest discover -s tests -v
python3 run.py preflight --config config.local.json
python3 run.py all --config config.local.json
```

需要保存每个阶段日志和两轮正式结果时执行：

```bash
bash scripts/acceptance_linux.sh config.local.json
```

完整的拉取、更新、配置说明、分步骤命令、预期行数、结果核对和故障定位见 [Linux 完整复现与验收指南](docs/linux_reproduction.md)。

## 输出文件

最近一次 `benchmark` 或 `all` 结果：

```text
results/
├── benchmark_detail.csv
├── benchmark_report.md
├── environment.md
└── benchmark.log
```

两轮验收结果：

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
├── run1/  # 四个结果文件
└── run2/  # 四个结果文件
```

`data/`、`results/` 和 `acceptance-results/` 都是可重新生成的本地目录，不进入 Git。

## 项目结构

```text
run.py                 CLI 和流程编排
config.example.json    无真实凭据的配置模板
src/                   配置、客户端、生成、装载、校验、Benchmark、统计和报告
schema/                YMatrix 与 MySQL 八表 DDL
sql/ymatrix/           YMatrix/PostgreSQL Q01～Q22
sql/mysql/             MySQL 5.7 Q01～Q22
scripts/               Linux 验收与远端检查脚本
tests/                 标准库 unittest 和数据库 mock
docs/                  公共复现与验收文档
data/                  自动生成 CSV（已忽略）
results/               最近一次报告（已忽略）
acceptance-results/    两轮验收证据（已忽略）
```

每个代码文件的职责、输入、输出和调用关系见 [Linux 指南第 12 节](docs/linux_reproduction.md#12-项目文件逐一说明)。

## 测试边界

本项目当前使用简化的 TPC-H 风格数据和查询，不属于标准 TPC-H 测试。

MVP 通过命令行客户端进程记录端到端执行时间，其中包含客户端进程启动和连接建立开销。

本次结果来自单节点、小规模、低轮数环境，不能代表生产集群性能。

YMatrix 与 MySQL 的结果仅适用于报告所记录的硬件、版本、参数和数据规模。
