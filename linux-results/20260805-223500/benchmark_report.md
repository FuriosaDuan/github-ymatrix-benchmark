# YMatrix 与 MySQL SQL Benchmark 报告

## 1. 项目目标

比较 YMatrix 与 MySQL 在相同简化 TPC-H 风格查询和数据上的端到端客户端耗时。

## 2. 测试环境

- data_sizes: customer=1000, part=500, orders=10000, lineitem=30000, seed=2026
- measurement_rounds: 5
- mysql_version: 5.7.44
- timeout_seconds: 60
- warmup_rounds: 1
- ymatrix_version: PostgreSQL 12 (MatrixDB 5.2.1+community) (Greenplum Database 7.0.0+dev.21200.gc9be2875939 build commit:c9be2875939af91d1c583b3d420d2eca5c0499f7) on x86_64-pc-linux-gnu, compiled by gcc (GCC) 11.2.1 20220127 (Red Hat 11.2.1-9), 64-bit compiled on Dec 28 2023 07:45:27

## 3. 数据模型与规模

customer=1000, part=500, orders=10000, lineitem=30000, seed=2026

## 4. 测试方法

warmup_rounds=1，measurement_rounds=5，concurrency=1，timeout_seconds=60。

## 5. 查询说明

Q01 为订单/明细/销售额聚合；Q02 为按月份聚合；Q03 为销售额 Top-N。

## 6. 查询结果一致性

| query_id | match | summary |
|---|---|---|
| q01 | True | equal |
| q02 | True | equal |
| q03 | True | equal |

## 7. Benchmark 统计结果

| database | query_id | avg | min | max | p95 | success_rate |
|---|---|---:|---:|---:|---:|---:|
| mysql | q01 | 211.59157599995524 | 151.60997700013468 | 343.0059369998162 | 343.0059369998162 | 100.00% |
| mysql | q02 | 51.80942180004422 | 33.78317700025946 | 103.95015199992486 | 103.95015199992486 | 100.00% |
| mysql | q03 | 165.75450679993082 | 117.47676799996043 | 301.0716419998971 | 301.0716419998971 | 100.00% |
| ymatrix | q01 | 207.75350599997182 | 131.1578209997606 | 379.1981710000982 | 379.1981710000982 | 100.00% |
| ymatrix | q02 | 115.06375379995006 | 83.84551200015267 | 196.6160359997957 | 196.6160359997957 | 100.00% |
| ymatrix | q03 | 202.31264279991592 | 117.29157699983261 | 301.15079699999114 | 301.15079699999114 | 100.00% |

## 8. YMatrix 与 MySQL 对比

| query_id | ymatrix_avg_ms | mysql_avg_ms | faster_database | faster_by_percent | ymatrix_to_mysql_ratio |
|---|---:|---:|---|---:|---:|
| q01 | 207.75350599997182 | 211.59157599995524 | ymatrix | 1.85% | 0.9819 |
| q02 | 115.06375379995006 | 51.80942180004422 | mysql | 122.09% | 2.2209 |
| q03 | 202.31264279991592 | 165.75450679993082 | mysql | 22.06% | 1.2206 |

## 9. Top 慢 SQL

- mysql q01 avg=211.59157599995524 ms
- ymatrix q01 avg=207.75350599997182 ms
- ymatrix q03 avg=202.31264279991592 ms
- mysql q03 avg=165.75450679993082 ms
- ymatrix q02 avg=115.06375379995006 ms

## 10. 失败 SQL 分类

- none

## 11. 执行计划与性能分析

本版本保留客户端端到端计时；短 SQL 的结果会受到客户端启动和连接建立开销影响。

## 12. 项目结论

结论应基于真实报告中的逐查询结果、成功率、波动和结果一致性，不预设某一数据库获胜。

## 13. 测试限制

本项目当前使用简化的 TPC-H 风格数据和查询，不属于标准 TPC-H 测试。

MVP 通过命令行客户端进程记录端到端执行时间，其中包含客户端进程启动和连接建立开销。

本次结果来自单节点、小规模、低轮数环境，不能代表生产集群性能。

YMatrix 与 MySQL 的结果仅适用于报告所记录的硬件、版本、参数和数据规模。
