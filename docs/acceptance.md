# Benchmark V3 可复现验收流程

## 1. 验收范围

本流程验收原题要求的 SQL Benchmark 工具：配置、8 张关联表、Q01–Q22、多轮统计、两数据库对比和完整报告。数据由纯 Python 生成器产生，属于 TPC-H 兼容测试，不是官方 dbgen/qgen 或经审计结果；TPC-C 作为扩展说明。

## 2. Windows 提交与手动推送

```powershell
cd "D:\Furiosa\性能测试"
git status --short --branch
python -m unittest discover -s tests -v
python -m compileall run.py src tests
git diff --check
git log -5 --oneline
git push origin master
```

这里的 `origin` 和 `master` 来自本项目当前实际配置；若你的本地状态变化，请以 `git remote -v` 和 `git branch --show-current` 的实际输出为准。

## 3. Linux 恢复标准 Git 状态

此前 GitHub HTTPS 推送失败时，Linux 工作树曾直接应用 `src/command.py` 与 `tests/test_command.py` 的 psql 制表符修复。手动 push 完成后先检查：

```bash
cd /home/mxadmin/ymatrix-mysql-benchmark
git status --short --branch
git diff -- src/command.py tests/test_command.py
```

如果差异只包含已经推送的 `-F '\t'` 修复，可以备份差异后恢复这两个文件再拉取：

```bash
git diff -- src/command.py tests/test_command.py > /tmp/benchmark-direct-fix.patch
git restore src/command.py tests/test_command.py
git pull --ff-only
```

不要删除远端原有的未知未跟踪文件。`config.local.json` 必须保留在 Linux 且不得提交。

## 4. 环境检查

```bash
python3 --version
test -f config.local.json
test -x /opt/ymatrix/matrixdb5/bin/psql
command -v mysql
mysql -u root -e "CREATE DATABASE IF NOT EXISTS benchmark_mvp;"
```

预期 Python 为 3.6.8，psql 可执行，mysql 在 PATH 中。不要输出 `config.local.json` 内容。

## 5. 一键真实验收

```bash
bash scripts/acceptance_linux.sh config.local.json
```

脚本任一步失败会立即停止。成功时最后输出带时间戳的验收目录。

## 6. 必须人工核对的结果

默认 SF=0.01 时，`linux_validate.txt` 必须包含：

```text
tpch_region,5,5,5,True
tpch_nation,25,25,25,True
tpch_supplier,100,100,100,True
tpch_customer,1500,1500,1500,True
tpch_part,2000,2000,2000,True
tpch_partsupp,8000,8000,8000,True
tpch_orders,15000,15000,15000,True
tpch_lineitem,60000,60000,60000,True
```

两次 `benchmark_report.md` 都必须满足：

- Q01–Q22 的结果一致性全部为 `True`。
- 每库每查询有 5 条正式明细，共 220 条；warmup 不出现在明细中。
- 正式行 `success=True`，失败时报告中有分类。
- start/end 是带时区 ISO 8601；elapsed_ms 大于零。
- avg/min/max/p95/成功率来自明细。
- 第 8 节给出逐查询两库差异。
- 第 9–13 节包含慢 SQL、失败分类、分析、结论与限制。

## 7. 原题逐项验收

| 原题要求 | 核对位置 |
|---|---|
| 连接、SQL 目录、轮数、并发、预热、超时、数据库参数 | `config.example.json`、`environment.md` |
| 批量执行 SQL | `src/discovery.py`、detail 中 q01–q03 |
| 必需明细字段 | `benchmark_detail.csv` 表头 |
| avg/min/max/p95/成功率 | 报告第 7 节 |
| 两数据库差异 | 报告第 8 节 |
| Top 慢 SQL | 报告第 9 节 |
| 失败 SQL 分类 | 报告第 10 节 |
| 环境与限制 | `environment.md`、报告第 2/13 节 |
| TPC-H 优先支持 | Q01–Q22 与八张关联表 |
| TPC-C 扩展说明 | `docs/interview_demo.md` |

## 8. 回收结果到 Windows

```powershell
$KeyPath = Join-Path $env:USERPROFILE ".ssh\codex_ymatrix_ed25519"
$Target = Join-Path (Get-Location) "linux-results\验收时间戳"
New-Item -ItemType Directory -Force $Target
scp -i $KeyPath -o IdentitiesOnly=yes -o BatchMode=yes -r `
  mxadmin@192.168.58.133:/home/mxadmin/ymatrix-mysql-benchmark/acceptance-results/验收时间戳/* `
  $Target
```

不得复制私钥或 `config.local.json`。

## 9. 如何扩展为标准 TPC-H / TPC-C

标准 TPC-H 需要引入官方数据生成规则、8 张表、22 条查询、scale factor、刷新函数和官方运行口径。标准 TPC-C 需要事务模型、终端并发、New-Order 等事务、吞吐 tpmC 与响应时间统计。它们是本项目下一阶段，不应与当前简化 MVP 混淆。
