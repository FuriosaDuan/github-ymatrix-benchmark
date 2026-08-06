# Linux 完整复现与验收指南

本文给出从拉取代码到查看双数据库 Benchmark 结果的完整流程。命令默认在 Linux Bash 中运行，除 Python 3.6.8、YMatrix `psql` 和 MySQL 命令行客户端外，不需要安装额外工具或 Python 包。

## 1. 项目边界

本项目使用八张供应链关系表和 Q01～Q22 分析查询，对同一份确定性 CSV 数据分别在 YMatrix 与 MySQL 中执行，校验结果一致性并统计端到端耗时。

本项目是 **TPC-H-compatible（TPC-H 兼容）工作负载**，不是官方或经审计的 TPC-H：数据由项目内 Python 生成器产生，没有使用官方 `dbgen/qgen`，也没有实现官方 Power、Throughput、Refresh Function 和审计规则。它同样不是 TPC-C；当前没有 TPC-C 的事务终端、仓库并发和 tpmC 指标。

八表关系如下：

```text
tpch_region
└── tpch_nation
    ├── tpch_supplier
    │   └── tpch_partsupp ── tpch_part
    └── tpch_customer
        └── tpch_orders
            └── tpch_lineitem ── tpch_part
                              └── tpch_supplier
```

- `region → nation`：地区和国家。
- `nation → supplier/customer`：供应商和采购商所属国家。
- `part ↔ supplier`：`partsupp` 是商品与供应商的供货桥表，记录库存和供货成本。
- `customer → orders → lineitem`：采购商创建订单，订单明细记录商品、实际供应商、数量、金额和物流日期。
- 每条 `lineitem(l_partkey, l_suppkey)` 都必须能关联到 `partsupp(ps_partkey, ps_suppkey)`。

## 2. 完整执行链路

```text
git clone / git pull
→ 创建 config.local.json
→ 创建 benchmark_mvp
→ compileall
→ unittest
→ preflight
→ generate
→ load
→ validate
→ benchmark
→ 查看 detail/report/environment/log
```

`python3 run.py all` 会执行一次 `preflight → generate → load → validate → benchmark`。如果需要完整验收证据和两轮稳定性复测，使用 `scripts/acceptance_linux.sh`，它会保留每个阶段的日志以及两套独立结果。

## 3. 环境要求

最低目标环境：

- Linux x86_64；已验证环境为 CentOS 7.9。
- Python 3.6.8，仅使用标准库。
- YMatrix/PostgreSQL 兼容实例和可执行的 `psql`。
- MySQL 5.7 兼容实例和 PATH 中的 `mysql`。
- Git 和 Bash。
- 操作账号可以创建项目专用 MySQL 数据库，并能在配置的 YMatrix 数据库中创建 `tpch_` 前缀表。

检查命令：

```bash
python3 --version
git --version
test -x /opt/ymatrix/matrixdb5/bin/psql && echo "psql executable: OK"
command -v mysql
```

预期 Python 显示 `3.6.8`，`psql executable: OK`，并输出 `mysql` 的可执行文件路径。

## 4. 拉取或更新代码

### 4.1 首次拉取

```bash
export REPO_URL="https://github.com/FuriosaDuan/TPC-test.git"
export PROJECT_DIR="${HOME}/ymatrix-mysql-benchmark"

git clone "$REPO_URL" "$PROJECT_DIR"
cd "$PROJECT_DIR"
git status --short --branch
git remote -v
```

### 4.2 已有工作目录更新

```bash
export PROJECT_DIR="${HOME}/ymatrix-mysql-benchmark"
cd "$PROJECT_DIR"

git status --short --branch
git branch --show-current
git remote -v
git pull --ff-only
git log -5 --oneline
```

如果 `git status` 显示本地修改，先确认这些修改的归属，不要用 `git reset --hard` 或删除未知文件来强行拉取。`config.local.json`、`data/`、`results/` 和 `acceptance-results/` 已被忽略，不应出现在待提交列表中。

## 5. 创建本地配置

配置模板不包含真实密码。首次运行时复制模板并限制权限：

```bash
cd "$PROJECT_DIR"
cp config.example.json config.local.json
chmod 600 config.local.json
vi config.local.json
```

不要执行 `cat config.local.json`，不要把它提交到 Git，也不要把密码写进命令行、截图或验收日志。

需要检查的配置组：

- `ymatrix`：`psql_path`、host、port、user、database、password 和 `session_sql`。
- `mysql`：`transport`、database、user、password 和 `session_sql`。`local_default` 使用本地默认连接，不传 host、port 或密码参数。
- `benchmark`：`scale_factor`、`warmup_rounds`、`measurement_rounds`、`concurrency` 和 `timeout_seconds`。
- `paths`：CSV、报告以及两套数据库 SQL 目录。

推荐首次闭环参数：

```json
"scale_factor": 0.01,
"warmup_rounds": 1,
"measurement_rounds": 5,
"concurrency": 1,
"timeout_seconds": 60
```

首次运行建议两套数据库的 `session_sql` 都保持空数组。确认语句与真实数据库版本兼容后，才能添加会话参数；每组 `session_sql` 与查询会在同一个客户端进程和数据库会话内执行。

只检查配置文件是否存在，不显示内容：

```bash
test -f config.local.json && echo "local config: OK"
git check-ignore -v config.local.json
```

## 6. 初始化项目专用 MySQL 数据库

项目使用 `benchmark_mvp`，不得把测试表装进 MySQL 系统数据库。数据库不存在时执行：

```bash
mysql -u root -e "CREATE DATABASE IF NOT EXISTS benchmark_mvp;"
```

该命令可重复执行。不要执行 `DROP DATABASE`、`DROP SCHEMA`，也不要操作项目之外的表。

## 7. Windows 或 Linux 静态验证

Linux：

```bash
cd "$PROJECT_DIR"
python3 -m compileall run.py src tests
python3 -m unittest discover -s tests -v
git diff --check
```

Windows PowerShell 的等价 mock 验证：

```powershell
python -m compileall run.py src tests
python -m unittest discover -s tests -v
git diff --check
```

Windows 不运行真实 `preflight/load/validate/benchmark`，真实数据库闭环只在 Linux 执行。

## 8. 分步骤运行任务

以下命令都在项目根目录执行：

```bash
cd "$PROJECT_DIR"
export CONFIG_PATH="config.local.json"
```

### 8.1 preflight：真实连接检查

```bash
python3 run.py preflight --config "$CONFIG_PATH"
```

作用：检查两个客户端可启动，分别执行 `SELECT version();` 和 `SELECT VERSION();`，验证 YMatrix、MySQL 和目标 `benchmark_mvp` 可用。输出应包含两套数据库的真实版本，不应包含密码。

### 8.2 generate：生成确定性 CSV

```bash
python3 run.py generate --config "$CONFIG_PATH"
find data -maxdepth 1 -type f -name '*.csv' -printf '%f %s bytes\n' | sort
```

作用：使用 seed `2026` 和配置的 scale factor 重新生成八个 CSV。相同配置会覆盖旧 CSV 并生成相同内容。默认 SF=0.01 的数据行数（不含表头）为：

| CSV / 表 | 行数 |
|---|---:|
| region / `tpch_region` | 5 |
| nation / `tpch_nation` | 25 |
| supplier / `tpch_supplier` | 100 |
| customer / `tpch_customer` | 1,500 |
| part / `tpch_part` | 2,000 |
| partsupp / `tpch_partsupp` | 8,000 |
| orders / `tpch_orders` | 15,000 |
| lineitem / `tpch_lineitem` | 60,000 |

### 8.3 load：双库建表和装载

```bash
python3 run.py load --config "$CONFIG_PATH"
```

作用：分别执行 `schema/ymatrix.sql` 和 `schema/mysql.sql`，清空八张 `tpch_` 项目表，然后把同一份 CSV 以每批最多 500 行的多行 `INSERT` 装入两套数据库。输出每个数据库、每张表的实际写入行数。任一写入失败，命令返回非零退出码。

### 8.4 validate：关联、CSV 和双库行数校验

```bash
python3 run.py validate --config "$CONFIG_PATH"
```

作用：检查本地 CSV 行数和关键外键关系，再查询两套数据库八张表的 `COUNT(*)`。默认规模应看到：

```text
table,expected,ymatrix,mysql,match
tpch_region,5,5,5,True
tpch_nation,25,25,25,True
tpch_supplier,100,100,100,True
tpch_customer,1500,1500,1500,True
tpch_part,2000,2000,2000,True
tpch_partsupp,8000,8000,8000,True
tpch_orders,15000,15000,15000,True
tpch_lineitem,60000,60000,60000,True
```

任何一行不一致都会返回非零退出码，不能继续正式 Benchmark。

### 8.5 benchmark：执行 Q01～Q22

```bash
python3 run.py benchmark --config "$CONFIG_PATH"
```

作用：动态读取两个 SQL 目录下所有精确以 `.sql` 结尾的普通文件，按文件名排序；先执行 warmup，再执行正式轮次，比较首次结果摘要，最后生成：

```text
results/benchmark_detail.csv
results/benchmark_report.md
results/environment.md
results/benchmark.log
```

默认正式明细数量为 `22 查询 × 2 数据库 × 5 轮 = 220` 行，加 CSV 表头后 `wc -l` 为 `221`。warmup 不进入正式明细。`elapsed_ms` 是包括客户端进程启动和连接建立开销的端到端 `time.monotonic()` 差值。

## 9. 一次执行完整业务闭环

确认 MySQL 项目数据库已创建后，可以执行：

```bash
cd "$PROJECT_DIR"
python3 run.py all --config config.local.json
```

严格顺序为：

```text
preflight → generate → load → validate → benchmark
```

任一步失败立即停止。`all` 生成一套当前结果到 `results/`，后一次 benchmark 会覆盖该目录中的前一次报告。

## 10. 两轮正式验收

项目提供可复现验收脚本：

```bash
cd "$PROJECT_DIR"
bash scripts/acceptance_linux.sh config.local.json
```

脚本使用 `set -euo pipefail`，任一步或管道中的 Python 命令失败都会停止。它执行 compileall、unittest、preflight、generate、load、validate 和两次 benchmark，并把结果保存到：

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
    ├── benchmark_detail.csv
    ├── benchmark_report.md
    ├── environment.md
    └── benchmark.log
```

获取最新一次验收目录：

```bash
RUN_DIR=$(find acceptance-results -mindepth 1 -maxdepth 1 -type d | sort | tail -1)
test -n "$RUN_DIR"
printf 'Latest acceptance directory: %s\n' "$RUN_DIR"
```

## 11. 查看和核对结果

### 11.1 阶段日志

```bash
ls -lh "$RUN_DIR"
sed -n '1,200p' "$RUN_DIR/linux_preflight.txt"
sed -n '1,200p' "$RUN_DIR/linux_generate.txt"
sed -n '1,240p' "$RUN_DIR/linux_load.txt"
sed -n '1,200p' "$RUN_DIR/linux_validate.txt"
tail -100 "$RUN_DIR/linux_benchmark_run1.txt"
tail -100 "$RUN_DIR/linux_benchmark_run2.txt"
```

### 11.2 报告和明细

```bash
ls -lh "$RUN_DIR/run1" "$RUN_DIR/run2"
sed -n '1,260p' "$RUN_DIR/run1/benchmark_report.md"
sed -n '1,260p' "$RUN_DIR/run2/benchmark_report.md"
sed -n '1,220p' "$RUN_DIR/run2/environment.md"
head -20 "$RUN_DIR/run2/benchmark_detail.csv"
tail -100 "$RUN_DIR/run2/benchmark.log"
wc -l "$RUN_DIR/run1/benchmark_detail.csv" "$RUN_DIR/run2/benchmark_detail.csv"
```

### 11.3 必须通过的核对项

```bash
grep ',False$' "$RUN_DIR/linux_validate.txt" || true
grep '| False |' "$RUN_DIR/run1/benchmark_report.md" || true
grep '| False |' "$RUN_DIR/run2/benchmark_report.md" || true
grep -n 'none' "$RUN_DIR/run1/benchmark_report.md" "$RUN_DIR/run2/benchmark_report.md"
```

人工确认：

- validate 的八张表都满足 `expected == ymatrix == mysql`。
- 两份报告的 Q01～Q22 查询结果一致性都为 `True`。
- 两份 detail 都是 221 行（1 个表头 + 220 个正式执行记录）。
- 正式记录包含 `query_id/start_time/end_time/elapsed_ms/success/error_message`。
- `start_time/end_time` 是带时区 ISO 8601；成功耗时大于零。
- 报告包含 avg/min/max/nearest-rank p95、成功率、双库差异、Top 慢 SQL、失败分类、环境、数据规模和限制。
- 比较两轮平均值和 p95；若波动明显，记录原因并增加轮数，不得只挑对某一数据库有利的一轮。

## 12. 项目文件逐一说明

### 12.1 入口与配置

| 文件 | 职责 | 输入 | 输出/副作用 |
|---|---|---|---|
| `run.py` | CLI 入口和六个命令的流程编排 | 命令名、`--config` | 控制台状态、CSV/报告、数据库操作 |
| `config.example.json` | 无真实凭据的配置模板 | 人工复制和编辑 | `config.local.json` 的结构基准 |
| `.gitignore` | 隔离密码、生成数据、报告和维护者私有材料 | Git 路径 | 防止敏感或生成文件进入提交 |
| `AGENTS.md` | 约束自动化维护者的 Python、测试和安全边界 | 维护任务 | 无运行输出 |

### 12.2 `src/` 运行模块

| 文件 | 职责 | 主要输入 | 主要输出 |
|---|---|---|---|
| `src/__init__.py` | 标记 `src` 为 Python 包 | 无 | 包初始化 |
| `src/config.py` | 读取 JSON、校验 transport/concurrency/轮数并补默认值 | 配置路径 | 标准化配置字典或 `ConfigError` |
| `src/command.py` | 构造安全的 `psql/mysql` 参数，运行 subprocess，隐藏环境变量密码 | 数据库配置、SQL、timeout | stdout 或 `CommandError` |
| `src/database.py` | 在同一客户端会话拼接 `session_sql` 和查询，解析制表符结果并规范 Decimal | 配置、数据库名、SQL | 原始输出和二维结果行 |
| `src/discovery.py` | 非递归发现并排序精确 `.sql` 文件 | SQL 目录 | `(query_id, path)` 列表 |
| `src/generator.py` | 使用 seed=2026 生成八表确定性 CSV，维持供货关系 | 输出目录、scale factor | 八个 CSV 和规模字典 |
| `src/initializer.py` | 读取 schema，执行真实版本查询，确认 MySQL 目标库可用 | 配置、schema 路径 | preflight 信息或 SQL 执行结果 |
| `src/loader.py` | 安全转义 CSV 值，建表、清表、分批多行 INSERT，并创建公平索引 | 配置、数据库、CSV、schema | 每张表装载行数 |
| `src/validator.py` | 校验 CSV 行数和关联关系，查询双库 `COUNT(*)` | 配置、数据目录 | 八表对比行，失配时抛错 |
| `src/benchmark.py` | 发现查询、分离 warmup/measurement、monotonic 计时、结果摘要比较 | 配置、双 SQL 目录 | detail、统计、一致性和双库比较 |
| `src/statistics.py` | 计算 avg/min/max、nearest-rank p95 和成功率 | 成功耗时、成功标记 | 统计字典 |
| `src/reporter.py` | 从真实 detail/summary 写出四类结果 | 统计、明细、元数据 | CSV、Markdown、环境说明、日志 |

调用关系：

```text
run.py
├── config.load_config
├── initializer.preflight
├── generator.generate_data
├── loader.load_database ── command/database
├── validator.validate_databases ── command/database
└── benchmark.run_benchmark_suite ── discovery/database/statistics
    └── reporter.write_*
```

### 12.3 Schema、SQL 和脚本

| 路径 | 说明 |
|---|---|
| `schema/ymatrix.sql` | YMatrix/PostgreSQL 语法的八表 DDL 和项目表结构。 |
| `schema/mysql.sql` | MySQL 5.7 语法的同逻辑八表 DDL。 |
| `sql/ymatrix/q01.sql`～`q22.sql` | YMatrix/PostgreSQL 方言的 22 类分析查询。 |
| `sql/mysql/q01.sql`～`q22.sql` | MySQL 5.7 方言的等价查询；日期和字符串函数按 MySQL 适配。 |
| `scripts/acceptance_linux.sh` | Linux 两轮验收编排和时间戳结果归档。 |
| `scripts/remote_preflight.ps1` | 从 Windows 使用显式 SSH 私钥执行远端只读环境检查；不是 Linux 闭环必需文件。 |

Q01～Q22 依次覆盖：价格汇总、最低供货成本、市场订单收入、订单优先级、区域收入、折扣收入、跨国贸易、市场份额、商品利润、退货客户收入、库存价值、运输方式、客户订单分布、促销占比、头部供应商、供应商数量、低数量商品收入、大额订单、指定商品收入、潜在供应商、延迟供货供应商和无订单客户分析。两套目录中的同名 SQL 必须保持业务含义、列顺序和排序一致。

### 12.4 测试文件

| 文件 | 覆盖范围 |
|---|---|
| `tests/test_config.py` | 配置默认值、MySQL database、transport 和边界校验。 |
| `tests/test_command.py` | 两客户端参数、数据库选择、输出模式、timeout 和密码脱敏。 |
| `tests/test_database.py` | 客户端输出解析、Decimal 规范化和同会话 session SQL。 |
| `tests/test_discovery.py` | 非递归、普通文件、`.sql` 后缀和排序发现。 |
| `tests/test_generator.py` | SF=0.01 规模、seed 确定性、金额和八表关联。 |
| `tests/test_initializer.py` | 两客户端真实调用协议、版本查询和目标数据库处理（mock）。 |
| `tests/test_loader.py` | 八 CSV 装载、批次不超过 500、安全 SQL 字面量和索引。 |
| `tests/test_validator.py` | CSV/关联/双库 COUNT 以及失配失败。 |
| `tests/test_benchmark.py` | warmup、measurement、monotonic、ISO 8601、结果一致性和查询发现。 |
| `tests/test_statistics.py` | avg/min/max、nearest-rank p95 和成功率。 |
| `tests/test_reporter.py` | detail、报告章节、双库比较、失败分类和环境输出。 |
| `tests/test_run.py` | CLI 平台保护和 `all` 顺序。 |
| `tests/test_acceptance_script.py` | `pipefail` 与两轮结果归档脚本契约。 |
| `tests/test_repository_hygiene.py` | Git 对配置、生成目录和维护者私有文档的真实忽略行为。 |

### 12.5 生成目录

| 路径 | 产生者 | 是否提交 |
|---|---|---|
| `data/` | `run.py generate` | 否，可完全重新生成 |
| `results/` | `run.py benchmark/all` | 否，保存最近一次结果 |
| `acceptance-results/<时间戳>/` | `acceptance_linux.sh` | 否，保存两轮验收证据 |
| `config.local.json` | 操作者从模板创建 | 绝不提交 |

## 13. 常见错误定位

### `psql` 不存在或不可执行

检查 `ymatrix.psql_path` 与实际安装路径，并运行：

```bash
test -x /opt/ymatrix/matrixdb5/bin/psql
```

### MySQL 目标数据库不可用

确认 `mysql.transport` 为现场要求的 `local_default`，配置的 database 是 `benchmark_mvp`，再执行第 6 节的幂等创建命令。

### preflight 失败

只查看命令错误和数据库服务状态；不要打印完整配置。核对 host、port、user、database、客户端路径和账号权限。

### load 失败

依次检查 schema 方言、CSV 是否齐全、字段类型、SQL 转义、批次大小和目标 database。修复后重新运行 `generate → load → validate`。

### validate 失配

先比较 `linux_generate.txt`、`linux_load.txt` 和 `linux_validate.txt`。不要跳过校验直接 benchmark；重新生成并装载两套数据库同一份 CSV。

### 查询结果不一致

报告会列出具体 query_id 和摘要。先核对同名 SQL 的业务含义、日期边界、NULL、Decimal、列顺序和排序，再重新运行正式 benchmark。

### 短查询波动明显

当前计时包含客户端启动和连接开销。保留 warmup，比较两轮结果；必要时增加 `measurement_rounds`，并在报告中记录真实参数。

## 14. 清理与重新运行

通常不需要手工清理：

- `generate` 覆盖八个生成 CSV。
- `load` 只清空并重载八张 `tpch_` 项目表。
- `benchmark` 覆盖 `results/` 中四个当前结果文件。
- `acceptance_linux.sh` 新建时间戳目录，不覆盖旧验收证据。

安全重跑：

```bash
cd "$PROJECT_DIR"
python3 run.py generate --config config.local.json
python3 run.py load --config config.local.json
python3 run.py validate --config config.local.json
python3 run.py benchmark --config config.local.json
```

不得为了重跑执行 `DROP DATABASE`、`DROP SCHEMA`，不得删除项目外目录或操作项目之外的表。

## 15. 完整复制命令清单

以下清单适用于已经安装客户端、具备数据库权限且准备好密码的 Linux 主机：

```bash
export REPO_URL="https://github.com/FuriosaDuan/TPC-test.git"
export PROJECT_DIR="${HOME}/ymatrix-mysql-benchmark"

git clone "$REPO_URL" "$PROJECT_DIR"
cd "$PROJECT_DIR"
cp config.example.json config.local.json
chmod 600 config.local.json
vi config.local.json

python3 --version
test -x /opt/ymatrix/matrixdb5/bin/psql
command -v mysql
mysql -u root -e "CREATE DATABASE IF NOT EXISTS benchmark_mvp;"

python3 -m compileall run.py src tests
python3 -m unittest discover -s tests -v
python3 run.py preflight --config config.local.json
python3 run.py generate --config config.local.json
python3 run.py load --config config.local.json
python3 run.py validate --config config.local.json
python3 run.py benchmark --config config.local.json

bash scripts/acceptance_linux.sh config.local.json
RUN_DIR=$(find acceptance-results -mindepth 1 -maxdepth 1 -type d | sort | tail -1)
printf 'Latest acceptance directory: %s\n' "$RUN_DIR"
sed -n '1,200p' "$RUN_DIR/linux_validate.txt"
sed -n '1,260p' "$RUN_DIR/run2/benchmark_report.md"
head -20 "$RUN_DIR/run2/benchmark_detail.csv"
tail -100 "$RUN_DIR/run2/benchmark.log"
wc -l "$RUN_DIR/run1/benchmark_detail.csv" "$RUN_DIR/run2/benchmark_detail.csv"
```

如果仓库已经存在，使用第 4.2 节的 `git pull --ff-only` 更新流程，不要重复 clone。
