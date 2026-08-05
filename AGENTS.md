# Agent Guidelines

- 运行代码必须兼容 Python 3.6.8，只使用标准库。
- Windows 仅执行 unittest、compileall 和 mock；真实数据库操作只在 Linux 由用户明确执行。
- 不读取、输出或提交 `config.local.json` 中的真实密码。
- 修改后运行：`python3 -m compileall run.py src tests` 和 `python3 -m unittest discover -s tests -v`。
- 未经用户明确批准，不执行 `git push`、数据库写入或 benchmark 全量流程。
