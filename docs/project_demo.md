# YMatrix 与 MySQL TPC-H 兼容 Benchmark 项目展示与验收记录

## 1. 项目定位

本项目用 Python 3.6.8 标准库实现确定性供应链数据生成、双数据库装载、22 类分析查询、多轮统计、结果一致性校验和自动报告，适用于数据库 PoC、性能验证和竞品对比。

本项目没有使用官方 dbgen/qgen，不属于标准或经审计的 TPC-H。当前结果应称为“SF=0.01 的 TPC-H 兼容双数据库 Benchmark”。

## 2. 数据模型

```text
tpch_region
  └─ tpch_nation
      ├─ tpch_supplier
      │   └─ tpch_partsupp ── tpch_part
      └─ tpch_customer
          └─ tpch_orders
              └─ tpch_lineitem
                   ├─ tpch_supplier
                   └─ tpch_part
```

- region/nation 表示供应链地理层级。
- supplier 和 customer 分别表示供应商与采购商。
- partsupp 是商品与供应商的供货桥表，记录库存和采购成本。
- customer 通过 orders 发起采购；lineitem 记录商品、实际供货商、数量、价格、折扣、税和物流日期。
- 每条 lineitem 的 `(partkey, suppkey)` 均在 partsupp 中存在，生成后由本地关联校验再次确认。

默认 `scale_factor=0.01`，seed=2026：

| 表 | 行数 |
|---|---:|
| tpch_region | 5 |
| tpch_nation | 25 |
| tpch_supplier | 100 |
| tpch_customer | 1,500 |
| tpch_part | 2,000 |
| tpch_partsupp | 8,000 |
| tpch_orders | 15,000 |
| tpch_lineitem | 60,000 |

## 3. 测试环境

- Linux：CentOS 7.9 x86_64
- Python：3.6.8
- YMatrix：MatrixDB 5.2.1+community，PostgreSQL 12 / Greenplum 7 基础
- MySQL：5.7.44，local_default 本地连接
- warmup_rounds：1
- measurement_rounds：5
- concurrency：1
- timeout_seconds：60
- 计时口径：命令行客户端端到端时间，包含进程启动和连接建立开销

## 4. 完整执行过程

项目在 Linux 的绝对路径：

```text
/home/mxadmin/ymatrix-mysql-benchmark
```

执行命令：

```bash
cd /home/mxadmin/ymatrix-mysql-benchmark
mysql -u root -e "CREATE DATABASE IF NOT EXISTS benchmark_mvp;"
bash scripts/acceptance_linux.sh config.local.json
```

脚本按以下顺序执行，任一步失败立即停止：

```text
compileall
→ unittest
→ preflight
→ generate
→ load YMatrix/MySQL
→ validate 八表关联与两库 COUNT
→ benchmark run1
→ benchmark run2
```

本次真实验收输出：

```text
Acceptance results: /home/mxadmin/ymatrix-mysql-benchmark/acceptance-results/20260805-235544
```

## 5. 实际验收结果

- Linux unittest：37/37 通过。
- YMatrix 和 MySQL preflight：通过。
- 八张表两数据库实际行数均与 CSV 一致。
- run1：Q01–Q22 结果一致性 22/22，失败 SQL 为 none，明细 221 行。
- run2：Q01–Q22 结果一致性 22/22，失败 SQL 为 none，明细 221 行。

run2 的逐查询平均端到端耗时：

| Query | YMatrix avg ms | MySQL avg ms | 本轮更快 |
|---|---:|---:|---|
| Q01 | 369.905 | 355.517 | MySQL |
| Q02 | 140.055 | 75.527 | MySQL |
| Q03 | 196.699 | 40.257 | MySQL |
| Q04 | 134.900 | 26.903 | MySQL |
| Q05 | 305.126 | 43.962 | MySQL |
| Q06 | 102.816 | 102.640 | 接近持平，MySQL 略低 |
| Q07 | 212.236 | 36.223 | MySQL |
| Q08 | 421.356 | 110.104 | MySQL |
| Q09 | 1499.735 | 1269.857 | MySQL |
| Q10 | 222.303 | 34.849 | MySQL |
| Q11 | 118.568 | 53.907 | MySQL |
| Q12 | 105.519 | 94.077 | MySQL |
| Q13 | 244.522 | 65.288 | MySQL |
| Q14 | 113.243 | 131.340 | YMatrix |
| Q15 | 167.055 | 331.101 | YMatrix |
| Q16 | 156.847 | 31.347 | MySQL |
| Q17 | 178.907 | 30.671 | MySQL |
| Q18 | 264.429 | 124.545 | MySQL |
| Q19 | 153.848 | 19.209 | MySQL |
| Q20 | 260.186 | 117.915 | MySQL |
| Q21 | 448.718 | 707.478 | YMatrix |
| Q22 | 121.591 | 21.670 | MySQL |

Q01 在两轮中的领先方发生变化，Q06 在 run2 基本持平，说明小规模、低轮数和客户端启动开销会造成可见波动。不能据此得出某数据库在所有分析负载上普遍更快的结论。

## 6. 结果文件绝对路径

阶段日志：

```text
/home/mxadmin/ymatrix-mysql-benchmark/acceptance-results/20260805-235544/linux_compileall.txt
/home/mxadmin/ymatrix-mysql-benchmark/acceptance-results/20260805-235544/linux_unittest.txt
/home/mxadmin/ymatrix-mysql-benchmark/acceptance-results/20260805-235544/linux_preflight.txt
/home/mxadmin/ymatrix-mysql-benchmark/acceptance-results/20260805-235544/linux_generate.txt
/home/mxadmin/ymatrix-mysql-benchmark/acceptance-results/20260805-235544/linux_load.txt
/home/mxadmin/ymatrix-mysql-benchmark/acceptance-results/20260805-235544/linux_validate.txt
/home/mxadmin/ymatrix-mysql-benchmark/acceptance-results/20260805-235544/linux_benchmark_run1.txt
/home/mxadmin/ymatrix-mysql-benchmark/acceptance-results/20260805-235544/linux_benchmark_run2.txt
```

第一轮正式结果：

```text
/home/mxadmin/ymatrix-mysql-benchmark/acceptance-results/20260805-235544/run1/benchmark_detail.csv
/home/mxadmin/ymatrix-mysql-benchmark/acceptance-results/20260805-235544/run1/benchmark_report.md
/home/mxadmin/ymatrix-mysql-benchmark/acceptance-results/20260805-235544/run1/environment.md
/home/mxadmin/ymatrix-mysql-benchmark/acceptance-results/20260805-235544/run1/benchmark.log
```

第二轮正式结果：

```text
/home/mxadmin/ymatrix-mysql-benchmark/acceptance-results/20260805-235544/run2/benchmark_detail.csv
/home/mxadmin/ymatrix-mysql-benchmark/acceptance-results/20260805-235544/run2/benchmark_report.md
/home/mxadmin/ymatrix-mysql-benchmark/acceptance-results/20260805-235544/run2/environment.md
/home/mxadmin/ymatrix-mysql-benchmark/acceptance-results/20260805-235544/run2/benchmark.log
```

## 7. 现场展示顺序

1. 展示 `config.example.json`，解释 scale、warmup、measurement、timeout、SQL 目录和 session_sql。
2. 展示 `src/generator.py`，解释 seed 和 partsupp/lineitem 供货完整性。
3. 展示 `sql/ymatrix` 与 `sql/mysql` 的 Q01–Q22，以及日期/NULL/Decimal 的跨库适配。
4. 展示 `linux_validate.txt`，证明八表 CSV、YMatrix、MySQL 行数相同。
5. 展示两个 `benchmark_report.md` 的第 6–13 节。
6. 展示 `benchmark_detail.csv`，说明带时区时间、monotonic elapsed、warmup 不入明细。
7. 解释 nearest-rank p95、成功率、失败分类和性能差异公式。
8. 最后说明 TPC-H 兼容范围与单节点 SF=0.01 的限制。

## 8. 本次真实问题与修复

- psql 默认 `|` 分隔导致结果解析错误：改为制表符。
- psql 与 MySQL 的 NULL 输出不同：统一为 `NULL`。
- PostgreSQL 与 MySQL 聚合小数显示精度不同：一致性比较统一到 6 位小数，不忽略超过容差的真实差异。
- Q02/Q20 相关子查询在 YMatrix 分布式执行中结果或性能异常：改为等价预聚合连接。
- Bash `tee` 曾掩盖非零退出码：启用 `set -euo pipefail`。
- GitHub HTTPS 拉取长时间阻塞：使用 Git bundle + fast-forward merge，同步后仍保留完整 Git 历史。

## 9. 限制

本项目不是官方 TPC-H，未使用 dbgen/qgen、刷新函数或官方 Power/Throughput 规则。当前 SF=0.01、单节点、concurrency=1、每查询 5 轮，结果只适用于本文记录的环境。若用于正式容量评估，应扩大数据规模和轮数、增加并发模型，并把客户端连接时间与服务端执行时间分别记录。
