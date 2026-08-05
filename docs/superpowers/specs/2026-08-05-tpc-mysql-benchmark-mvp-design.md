# TPC-H 风格 YMatrix / MySQL Benchmark MVP 设计

## 目标

构建一个只依赖 Python 3.6 标准库的命令行工具，生成可复现的四表测试数据，校验 YMatrix 与 MySQL 的连接与 schema，顺序执行三条业务 SQL，并输出可审计的 benchmark 明细和汇总报告。

## 边界

- Windows 只运行静态检查、单元测试和 mock subprocess 测试。
- Linux 才连接真实数据库；密码只从 Linux 本地 `config.local.json` 读取，并且不写入日志、命令行或仓库。
- MVP 只支持 `concurrency=1`，不自动执行 `load`、`benchmark` 或 `all`。
- 不安装第三方依赖，不修改远程数据库服务配置，不执行 destructive SQL。

## 架构

`run.py` 负责 CLI 分发。`src/config.py` 负责配置读取、默认值和安全校验；`src/command.py` 负责构造不泄漏密码的子进程命令；`src/generator.py` 生成固定 seed 的 CSV；`src/initializer.py` 运行 schema/load/preflight；`src/validator.py` 验证生成文件和数据库对象；`src/benchmark.py` 采集每轮结果；`src/statistics.py` 计算 avg/min/max/p95/success rate；`src/reporter.py` 输出 CSV、Markdown、环境和日志。

## 数据与 SQL

生成 `customer`、`part`、`orders`、`lineitem` 四张简化 TPC-H 风格表，规模固定为 1000、1000、10000、30000，seed 为 2026。YMatrix 使用 PostgreSQL 语法，MySQL 使用对应日期和 LIMIT 语法；Q01/Q02/Q03 业务含义一致。

## 错误处理与安全

配置缺失、transport 不合法、TCP 缺 host/port、并发度不为 1、子进程超时和非零退出都返回明确错误。密码仅通过子进程环境变量传递；默认本地 MySQL 空密码不添加 `-p` 或 `MYSQL_PWD`。

## 验证

提供 unittest 覆盖配置、命令安全、统计、报告和 subprocess 错误路径；运行 `python3 -m compileall run.py src tests` 与 `python3 -m unittest discover -s tests -v`。PowerShell 脚本只在用户明确执行时通过 SSH 运行 Linux 的 pull、compileall、unittest 和 preflight。
