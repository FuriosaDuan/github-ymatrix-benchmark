# Linux 真实运行历史证据

`20260805-223500/` 是修复 psql 制表符解析后在真实 CentOS 7.9、YMatrix 和 MySQL 5.7 环境中回收的历史结果与命令日志。

该目录中的旧版 `benchmark_report.md` 由修复 UTF-8 报告生成器之前的代码产生，因此中文正文可能出现编码损坏；CSV 明细、环境信息和命令日志仍保留为真实运行证据，不应伪装成新版正式验收报告。

新版正式验收报告应在本次提交手动 push、Linux `git pull --ff-only` 后执行：

```bash
bash scripts/acceptance_linux.sh config.local.json
```

新结果位于 `acceptance-results/YYYYMMDD-HHMMSS/run1` 和 `run2`，两轮都应包含四个完整输出文件。
