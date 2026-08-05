你当前运行在 Windows 本机的项目工作区中。

请实现一个 YMatrix 与 MySQL SQL Benchmark 执行和结果汇总工具的 MVP。

## 1. 工作模式

项目采用严格分离的开发与运行环境：

Windows：
- Codex 编写和修改代码
- 执行不依赖真实数据库的单元测试
- Git commit 和 push 到当前已经配置好的 GitHub 仓库
- 通过 PowerShell SSH 脚本触发 Linux 拉取和测试

Linux：
- 不运行 Codex
- 从 GitHub git pull
- 运行 Python 3.6.8
- 连接真实 YMatrix 和 MySQL
- 执行集成测试和 Benchmark
- 生成真实运行结果

不要尝试从 Windows 直接连接数据库。
不要假设 Windows 安装了 YMatrix、MySQL、psql 或 mysql 客户端。
数据库相关单元测试必须 mock subprocess。

## 2. 已确认的 Linux 环境

操作系统：
- CentOS Linux release 7.9.2009 (Core)
- x86_64

Linux SSH：
- 当前地址：192.168.58.133
- 执行用户：mxadmin
- 项目路径：/home/mxadmin/ymatrix-mysql-benchmark

Python：
- Python 3.6.8
- pip 9.0.3

YMatrix：
- PostgreSQL 12
- MatrixDB 5.2.1+community
- Greenplum Database 7.0.0+dev 基础
- psql 精确路径：
  /opt/ymatrix/matrixdb5/bin/psql
- host：127.0.0.1
- port：5432
- user：mxadmin
- database：postgres
- password：只保存在 Linux 的 config.local.json
- Segment 端口：6000

MySQL：
- MySQL 5.7.44
- command：mysql
- user：root
- password：空字符串
- 当前仅确认本地免密登录
- MVP 默认 transport：local_default
- transport=local_default 时，不向 mysql 命令添加 host、port 或密码参数
- 不得自行认定 root@127.0.0.1 已获得 TCP 登录权限

GitHub：
- 当前 Windows 项目内已经配置 GitHub 用户、仓库和提交邮箱
- 先读取 git status、git branch --show-current 和 git remote -v
- 不修改已有远程仓库地址
- 不创建新 GitHub 仓库
- 未经用户明确批准，不执行 git push

## 3. 核心安全要求

- 不使用 sudo。
- 不修改 Linux 系统或数据库服务配置。
- 不停止或重启 YMatrix、MySQL。
- 不安装第三方 Python 包。
- 不升级 Python。
- 不读取或提交真实密码。
- 不创建包含真实凭据的 config.local.json。
- config.local.json 必须加入 .gitignore。
- 不执行 DROP DATABASE。
- 首次写入数据库前必须暂停并等待用户批准。
- 不得猜测任何路径、配置键、用户、仓库地址或命令。
- 缺少精确信息时停止并询问用户。

## 4. Python 兼容要求

所有运行代码必须兼容 Python 3.6.8。

不得使用：
- dataclasses
- pathlib.Path.is_relative_to
- f-string 的调试等号语法
- match/case
- zoneinfo
- subprocess.run 的 text 参数
- Python 3.7 及以后新增且 Python 3.6 不支持的语法或接口

可以使用：
- Python 标准库
- json
- csv
- decimal
- random
- datetime
- time
- subprocess
- statistics
- unittest
- pathlib 中 Python 3.6 已支持的接口

Windows 单元测试通过不代表 Linux 兼容。
必须提供 Linux 远程检查命令：

python3 -m compileall run.py src tests
python3 -m unittest discover -s tests -v

## 5. MVP 数据模型

使用四张简化 TPC-H 风格表：

customer
part
orders
lineitem

数据规模：

customer：1000
part：500
orders：10000
lineitem：30000
random_seed：2026

生成结果必须确定性可复现。
金额使用 Decimal 或整数分单位计算，不使用二进制浮点累计金额。

## 6. MVP SQL

分别创建：

sql/ymatrix/q01.sql
sql/ymatrix/q02.sql
sql/ymatrix/q03.sql

sql/mysql/q01.sql
sql/mysql/q02.sql
sql/mysql/q03.sql

业务含义：

Q01：
订单数量、订单明细数量和总销售额。

Q02：
按月份统计订单数和销售额。

Q03：
关联 part 与 lineitem，返回销售额最高的 10 个商品。

两套数据库 SQL 业务含义一致，但不得假设日期函数和语法完全一致。

## 7. 运行命令

run.py 必须支持：

python3 run.py preflight --config config.local.json
python3 run.py generate --config config.local.json
python3 run.py load --config config.local.json
python3 run.py validate --config config.local.json
python3 run.py benchmark --config config.local.json
python3 run.py all --config config.local.json

第一轮只允许执行：
- Windows 单元测试
- Python 静态语法检查
- 不连接数据库的 mock 测试

首次部署到 Linux 后只允许自动执行：
- compileall
- unittest
- preflight

不得自动执行 load、benchmark 或 all。

## 8. MySQL 精确行为

config.example.json 中定义：

transport 可取：
- local_default
- tcp

transport=local_default：
- 必须省略 host 和 port
- 调用 mysql 本地默认连接
- user=root
- password 为空时不得传递 -p
- 不设置 MYSQL_PWD

transport=tcp：
- host 和 port 必填
- 缺失时返回明确配置错误
- 密码非空时只通过子进程环境传递
- 密码不得出现在命令、日志或异常中

## 9. YMatrix 精确行为

使用：

/opt/ymatrix/matrixdb5/bin/psql

必须添加：
- -X
- ON_ERROR_STOP=1

使用 TCP：
- host=127.0.0.1
- port=5432
- user=mxadmin
- database=postgres

密码只通过子进程环境 PGPASSWORD 传递。
不得记录 PGPASSWORD。

## 10. Benchmark 行为

默认：

warmup_rounds：1
measurement_rounds：3
concurrency：1
timeout_seconds：60

MVP 仅支持 concurrency=1。
其他值必须明确报错。

每条明细包含：

database
query_id
round
start_time
end_time
elapsed_ms
success
error_message

输出：

results/benchmark_detail.csv
results/benchmark_report.md
results/environment.md
results/benchmark.log

统计：

avg
min
max
p95
success_rate

p95 使用 nearest-rank：

rank = ceil(0.95 * n)

## 11. 必须创建的文件

AGENTS.md
README.md
report.md
ai_usage.md
.gitignore
config.example.json
run.py

src/__init__.py
src/config.py
src/command.py
src/generator.py
src/initializer.py
src/validator.py
src/benchmark.py
src/statistics.py
src/reporter.py

schema/ymatrix.sql
schema/mysql.sql

sql/ymatrix/q01.sql
sql/ymatrix/q02.sql
sql/ymatrix/q03.sql
sql/mysql/q01.sql
sql/mysql/q02.sql
sql/mysql/q03.sql

tests/test_config.py
tests/test_command.py
tests/test_statistics.py
tests/test_reporter.py

scripts/remote_preflight.ps1

## 12. PowerShell 远程检查脚本

scripts/remote_preflight.ps1 必须：

1. 通过 SSH 连接 mxadmin@192.168.58.133。
2. 进入 /home/mxadmin/ymatrix-mysql-benchmark。
3. 执行 git pull --ff-only。
4. 执行 Python 3.6 compileall。
5. 执行 unittest。
6. 执行 preflight。
7. 任一步骤失败时返回非零退出状态。
8. 不执行 load、benchmark 或 all。
9. 不显示 config.local.json 内容。
10. 不输出数据库密码。

## 13. 测试要求

至少测试：

- 缺少配置键时报错。
- transport 值非法时报错。
- local_default 不生成 host、port、-p 参数。
- tcp 缺少 host 或 port 时拒绝运行。
- 密码不出现在命令、日志和异常中。
- concurrency 不等于 1 时拒绝运行。
- p95 nearest-rank。
- CSV 表头和字段顺序。
- Markdown 报告生成。
- subprocess 超时处理。
- subprocess 非零退出码处理。

## 14. 报告边界

报告必须包含：

“本项目当前使用简化的 TPC-H 风格数据和查询，不属于标准 TPC-H 测试。”

“MVP 通过命令行客户端进程记录端到端执行时间，其中包含客户端进程启动和连接建立开销。”

“本次结果来自单节点、小规模、低轮数环境，不能代表生产集群性能。”

“YMatrix 与 MySQL 的结果仅适用于报告所记录的硬件、版本、参数和数据规模。”

## 15. 执行顺序

1. 检查当前 Git 状态和远程仓库。
2. 输出简短实施计划。
3. 创建项目结构。
4. 先写 unittest。
5. 运行测试，确认测试先失败。
6. 实现最小代码。
7. 运行测试，确认通过。
8. 执行 Python 语法检查。
9. 创建文档。
10. 创建 PowerShell 远程检查脚本。
11. 展示 git status 和 git diff。
12. 不执行 git push。
13. 不连接 Linux。
14. 等待用户审核。

完成后报告：

- 创建和修改的文件
- Windows 测试结果
- Python 3.6 兼容性风险
- 尚需在 Linux 手动创建的配置
- 下一条需要用户批准的操作
## Prompt update — 2026-08-05 20:50:06 +08:00

修正 Linux 真实闭环：增加 MySQL 目标 database、真实 preflight、四表安全分批 INSERT 装载、双数据库 COUNT 校验、严格 all 顺序、warmup、monotonic 计时、带时区 ISO 8601 时间和对应 mock 测试；本轮禁止连接 Linux、真实数据库和 git push。
## Prompt update — 2026-08-05 21:46:25 +08:00

第三版验收要求：将 MVP 扩展为可配置、可复现、可校验、可报告的 YMatrix/MySQL Linux Benchmark；part=500，timeout=60，warmup=1，measurement=5，支持 session_sql、动态 SQL 发现、结果一致性、Top 慢 SQL、失败分类、完整报告、面试材料，并继续执行真实 Linux 闭环。
## Prompt update — 2026-08-05 22:04:59 +08:00

SSH 免密运行要求：使用 PowerShell 动态解析的 codex_ymatrix_ed25519 私钥，所有 SSH/SCP 显式携带 IdentitiesOnly=yes、BatchMode=yes；连接后继续 Linux 真实闭环，不再使用交互式密码认证。
## 2026-08-05 22:50:50 +08:00

用户要求提交全部当前成果但不由 Codex 推送，并确认需要一套完全贴合原题的可复现验收流程。验收必须修复并实际输出完整报告，明确真实环境中 YMatrix 使用 TCP、MySQL 使用 local_default，不能将当前结果描述为双 TCP 测试；同时说明此前因 GitHub HTTPS 推送失败，Linux 曾临时绕过 git pull 直接应用同一处已测试修复，最终应恢复 commit → 手动 push → Linux git pull --ff-only 的标准流程。
## 2026-08-05 23:00:48 +08:00

用户纠正术语：此前所说的是 TPC 测试流程，不是 TCP 网络连接。可复现验收必须完全贴合原题，准确说明当前项目是简化 TPC-H 风格 Benchmark、不是标准完整 TPC-H；TPC-C 当前可按原题作为命令包装或扩展说明，不得误称已经实现标准 TPC-C。需要实际生成并回收 CSV 明细、Markdown 汇总、环境说明和 benchmark.log。
## 2026-08-05 23:24:29 +08:00

用户确认采用纯 Python 标准库自研生成器方案，不增加 dbgen/qgen 等额外工具或环境；尽量贴近标准 TPC-H，重构为 region、nation、supplier、customer、part、partsupp、orders、lineitem 八张关联表，以供应商和采购商交易行为形成供应链雪花模型，提供 YMatrix 与 MySQL 5.7 各 Q01–Q22、默认 SF=0.01 mock/真实数据、Linux 双库对比和完整人工可复现流程。必须明确这属于 TPC-H 兼容测试而非官方标准或审计结果。
## 2026-08-05 23:51:35 +08:00

用户已手动 push，要求在 Linux 同步并完成真实验收；若 GitHub HTTPS 无法正常拉取，明确授权绕过网络覆盖同步。随后用户调整结果回收要求：不强制复制到 Windows，只需 Linux 项目通过八表、Q01–Q22 双库一致性及两轮 Benchmark，并交付一份具体到 Linux 结果文件绝对路径的完整项目展示过程文档。
