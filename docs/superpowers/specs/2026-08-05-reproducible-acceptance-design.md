# Benchmark V3 可复现验收设计

## 目标

将当前项目整理成完全贴合原题、可由项目所有者在 CentOS 7.9 上独立复现的验收包。真实结果必须由命令行客户端执行产生，不能手工填写；mock 测试与真实数据库结果必须明确区分。

## 题目验收矩阵

| 原题要求 | 实现证据 | 运行证据 |
|---|---|---|
| 数据库连接、SQL 目录、轮数、并发、预热、超时、数据库参数 | `config.example.json`、`src/config.py` | `environment.md`、报告测试方法 |
| 批量执行 SQL | `src/discovery.py`、`src/benchmark.py` | `benchmark_detail.csv` |
| query_id/start/end/elapsed/success/error | `src/reporter.py` | `benchmark_detail.csv` |
| avg/min/max/p95/成功率 | `src/statistics.py` | `benchmark_report.md` |
| 两数据库逐查询对比 | `src/benchmark.py` | 报告第 8 节 |
| CSV、Markdown、Top 慢 SQL、失败分类、环境、限制 | `src/reporter.py` | 四个结果文件 |
| 结果业务一致性 | `src/database.py`、`src/benchmark.py` | 报告第 6 节 |
| TPC-C 扩展说明 | `docs/interview_demo.md` | 面试验收说明 |

## TPC 实现边界

当前实现是简化 TPC-H 风格 Benchmark，不是标准 TPC-H；TPC-C 当前是扩展说明，尚未实现标准事务负载执行器。这符合原题“TPC-H 可优先支持，TPC-C 可作为命令包装或扩展说明”的验收边界。网络连接方式仍应在环境报告中按实际配置记录，但不是本题所称的 TPC 测试流程。

## 输出与可复现流程

新增 Linux 验收脚本，严格执行 preflight、generate、load、validate、两次 benchmark，并将每一步输出及两次结果分别保存在带时间戳的验收目录。脚本遇到任一步失败立即停止，不读取或打印配置密码。

报告统一以 UTF-8 写入，包含题目要求的 13 个章节、连接方式、索引、结果一致性、逐查询统计和总体结论。结论只根据真实明细生成，不宣称某数据库普遍更快。

## 错误处理与安全

脚本只操作项目四张 `bench_` 表；不执行 DROP DATABASE、DROP SCHEMA、COPY、LOAD DATA LOCAL INFILE、sudo 或服务重启。密码只通过环境变量传给客户端，命令、日志和异常继续执行脱敏。

## 测试策略

先增加报告 UTF-8、完整章节、连接方式和结论的失败测试，再修复生成器。Windows 运行 unittest、compileall、diff check；Linux 运行同样检查及真实数据库闭环。最终提交源代码、文档、验收脚本和脱敏后的真实结果，不提交 `config.local.json`。
