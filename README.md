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

## TPC-C拓展设计说明
当前项目使用 Python 3.6.8 标准库实现了 YMatrix 与 MySQL 的双数据库性能对比流程，主要包括：

- 生成确定、可复现的 TPC-H 风格八表数据；
- 为 YMatrix 和 MySQL 分别提供 Q01～Q22；
- 完成数据生成、加载、行数与关联关系校验；
- 顺序执行查询的预热轮次和正式测量轮次；
- 比较两个数据库的查询结果一致性；
- 统计平均耗时、最小耗时、最大耗时、p95 和成功率；
- 输出 CSV 明细、Markdown 报告、运行环境和日志；
- 在 Windows 上使用 unittest 和 mock 验证，在 Linux 上运行真实数据库流程。

因此，当前项目的主要负载是分析型、只读型 SQL 查询，更接近 TPC-H 所代表的 OLAP 场景。


TPC-C 面向联机事务处理场景，与当前项目的执行模型存在明显差异：

| 对比项 | 当前 TPC-H-compatible 流程 | TPC-C 类型流程 |
|---|---|---|
| 主要场景 | 分析查询、报表统计 | 订单录入、付款等联机事务 |
| 数据操作 | 以只读查询为主 | 查询、插入、更新和回滚并存 |
| 执行单位 | 单条 SQL 查询 | 由多条 SQL 组成的原子事务 |
| 并发模型 | 当前固定 `concurrency=1` | 通常包含多个并发终端或工作线程 |
| 主要指标 | 单条查询延迟、结果一致性 | 事务吞吐、响应时间、提交与回滚 |
| 数据模型 | TPC-H 风格八表 | TPC-C 风格九表 |


未来 MVP 范围如下：

- 只配置 1 个 warehouse；
- 使用 TPC-C 风格九表；
- 只实现 New-Order 和 Payment 两种事务；
- 使用固定随机种子生成可复现的数据与事务输入；
- 第一版只支持单工作线程；
- 使用固定事务次数，不实现长时间压力测试；
- 分别在 YMatrix 和 MySQL 上从相同初始数据开始运行；
- 输出事务成功率、回滚数、平均延迟和 p95；
- 运行后校验订单、库存、余额和付款历史等业务不变量；
- 明确声明不是标准或经审计的 TPC-C，不输出 tpmC。

### 最小数据模型

未来 Smoke MVP 使用以下九张独立表，并统一使用 `tpcc_` 前缀：

1. `tpcc_warehouse`：仓库；
2. `tpcc_district`：仓库下属区域；
3. `tpcc_customer`：客户；
4. `tpcc_history`：付款历史；
5. `tpcc_new_order`：待处理新订单；
6. `tpcc_orders`：订单头；
7. `tpcc_order_line`：订单明细；
8. `tpcc_item`：商品；
9. `tpcc_stock`：仓库库存。

这些表与当前 `tpch_*` 表完全隔离，不删除、不覆盖也不复用现有 TPC-H 数据。

为控制首次实现和验收成本，建议使用以下简化规模：

| 数据项 | 建议规模 |
|---|---:|
| warehouse | 1 |
| 每仓库 district | 10 |
| 每 district customer | 300 |
| item | 1,000 |
| stock | 1,000 |
| 每 district 初始 orders | 300 |
| 每 district 初始 new_order | 90 |
| 每个订单 order_line | 5 |

该数据量属于工程验证规模，不属于官方 TPC-C 标准规模。

### 两类最小事务

#### New-Order

New-Order 用于模拟创建订单，最少包含以下操作：

1. 读取仓库、区域和客户信息；
2. 更新区域的下一个订单编号；
3. 插入订单头；
4. 插入待处理新订单；
5. 检查并更新相关商品库存；
6. 插入订单明细；
7. 全部成功后提交事务。

上述操作必须在同一个数据库事务中执行。如果任一步骤失败，不能保留部分订单或部分库存更新。

### Payment

Payment 用于模拟客户付款，最少包含以下操作：

1. 更新仓库累计付款金额；
2. 更新区域累计付款金额；
3. 更新客户余额和付款统计；
4. 插入一条付款历史；
5. 全部成功后提交事务。

如果付款事务失败，仓库、区域、客户和付款历史不能出现部分更新。

### 工作流

```text
生成 1 warehouse 的确定性数据
        ↓
加载独立的 tpcc_* 九表
        ↓
校验初始行数和表间关系
        ↓
生成固定的 New-Order / Payment 事务序列
        ↓
在 YMatrix 上顺序执行并记录结果
        ↓
恢复相同初始数据
        ↓
在 MySQL 上顺序执行并记录结果
        ↓
校验运行后的业务不变量
        ↓
输出明细、汇总和限制说明
```

YMatrix 和 MySQL 必须从相同初始数据开始测试。由于这是两个独立数据库，不要求数据库内部生成值逐字段完全一致；应重点比较事务完成数量、失败类型、响应时间以及业务不变量是否成立。

### 命令设计

真正完成代码实现和测试后，可以增加以下命令：

```bash
python3 run.py tpcc-generate --config config.local.json
python3 run.py tpcc-load --config config.local.json
python3 run.py tpcc-validate --config config.local.json
python3 run.py tpcc-benchmark --config config.local.json
```

这些命令目前属于规划接口，尚不是当前仓库已经实现的可用命令。在代码、测试和文档全部完成前，不应把它们加入 README 的当前可用命令列表。

不建议提供 `tpcc-all` 命令。该命令会自动组合建表、清理数据、加载和 Benchmark，容易在没有明确批准时执行数据库写入，不符合本项目的安全边界。

### 1最小统计指标

每次事务至少记录：

- 数据库名称；
- 事务类型；
- 事务序号；
- 开始时间和结束时间；
- 端到端耗时；
- 是否提交；
- 错误分类；
- 脱敏后的错误信息。

汇总报告至少包含：

- 尝试事务数；
- 成功提交数；
- 回滚或失败数；
- 成功率；
- 平均、最小、最大和 nearest-rank p95 响应时间；
- 总运行时间；
- 每秒成功提交事务数。

“每秒成功提交事务数”只能作为 Smoke MVP 的工程指标，不能换算、命名或暗示为 tpmC。

### 错误处理与事务边界

每个业务事务必须作为一段完整脚本交给同一个数据库客户端进程执行，使 `BEGIN`、业务 SQL 和 `COMMIT` 位于同一个数据库会话中。

预期业务拒绝路径可以在事务脚本中显式执行 `ROLLBACK`。如果 SQL 执行过程中出现异常，当前命令行客户端模式会终止失败的客户端连接，由数据库回滚尚未提交的事务。报告必须如实说明该机制，不能宣称项目实现了基于数据库驱动的持续连接事务管理器。

错误至少分为：

- `timeout`：执行超时；
- `connection`：数据库连接失败；
- `sql`：SQL 语法或执行失败；
- `expected_rollback`：预期的业务回滚；
- `other`：其他错误。

日志不得记录数据库密码、密码环境变量或完整客户敏感字段。

### 验收标准

- 所有代码兼容 Python 3.6.8，只使用标准库；
- Windows 单元测试和 mock 不连接真实数据库；
- 固定 seed 生成的数据和事务序列完全可复现；
- 九表行数、主键和引用关系校验通过；
- New-Order 成功后，订单、待处理订单、明细和库存变化保持一致；
- Payment 成功后，仓库、区域、客户金额和付款历史保持一致；
- 人工注入 SQL 失败后不存在部分提交；
- TPC-H 原有命令和测试不受影响；
- 报告明确写明不是标准 TPC-C；
- 未经用户明确批准，不在 Linux 执行建表、加载或 Benchmark。





### 结论

对于当前题目，TPC-C 采用最小 MVP 或扩展说明是合理且足够的。推荐优先保证现有 TPC-H-compatible 流程、测试、报告和复现材料完整，再把 TPC-C 两事务 Smoke MVP 作为后续独立迭代。


