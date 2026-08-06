# Public Reproduction Guide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a complete, reusable Linux operation guide while keeping personal interview documents, credentials, generated data, and generated results out of Git.

**Architecture:** `README.md` becomes the concise public entry point and `docs/linux_reproduction.md` becomes the authoritative copy-and-run guide. Repository-hygiene tests lock down ignored paths and required operational stages, while concise Python docstrings explain module boundaries without changing runtime behavior.

**Tech Stack:** Python 3.6.8 standard library, `unittest`, Git, Bash, YMatrix `psql`, MySQL 5.7 command-line client.

## Global Constraints

- Runtime code must remain compatible with Python 3.6.8 and use only the standard library.
- Real database commands run only on Linux; Windows verification uses unittest, compileall, and static Git checks.
- Never read, print, or commit `config.local.json` credentials.
- Do not append this request or implementation notes to `prompt.md`.
- Preserve local copies of `docs/interview_demo.md` and `docs/project_demo.md` while removing them from Git tracking.
- Do not intentionally change schemas, generated values, SQL semantics, benchmark statistics, or database state.

---

### Task 1: Lock down repository hygiene

**Files:**
- Create: `tests/test_repository_hygiene.py`
- Modify: `.gitignore`
- Stop tracking, retain locally: `docs/interview_demo.md`
- Stop tracking, retain locally: `docs/project_demo.md`

**Interfaces:**
- Consumes: repository-root `.gitignore` rules.
- Produces: stable ignore coverage for credentials, generated artifacts, and maintainer-only documents.

- [ ] **Step 1: Write the failing ignore-policy test**

```python
import os
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class RepositoryHygieneTests(unittest.TestCase):
    def test_private_and_generated_paths_are_ignored(self):
        with open(os.path.join(ROOT, '.gitignore'), 'r', encoding='utf-8') as handle:
            rules = {line.strip() for line in handle if line.strip() and not line.startswith('#')}
        expected = {
            'config.local.json',
            'data/',
            'results/',
            'acceptance-results/',
            'docs/interview_demo.md',
            'docs/project_demo.md',
        }
        self.assertTrue(expected.issubset(rules))
```

- [ ] **Step 2: Run the focused test and verify RED**

Run: `python -m unittest tests.test_repository_hygiene -v`

Expected: FAIL because the two personal document paths are not yet ignored.

- [ ] **Step 3: Add explicit ignore rules**

Append these entries to `.gitignore`:

```gitignore

# Maintainer-only presentation material
docs/interview_demo.md
docs/project_demo.md
```

- [ ] **Step 4: Remove only the personal documents from the Git index**

Run:

```text
git rm --cached -- docs/interview_demo.md docs/project_demo.md
```

Then verify both files still exist locally with PowerShell `Test-Path` and confirm `prompt.md` is unchanged with `git diff -- prompt.md`.

- [ ] **Step 5: Run the focused test and verify GREEN**

Run: `python -m unittest tests.test_repository_hygiene -v`

Expected: 1 test passes.

---

### Task 2: Build the authoritative Linux reproduction guide

**Files:**
- Modify: `tests/test_repository_hygiene.py`
- Create: `docs/linux_reproduction.md`

**Interfaces:**
- Consumes: `config.example.json`, `run.py`, `scripts/acceptance_linux.sh`, and generated result filenames.
- Produces: a public guide whose commands can be copied on a fresh CentOS-compatible Linux host.

- [ ] **Step 1: Add a failing documentation coverage test**

Add to `RepositoryHygieneTests`:

```python
    def test_linux_guide_covers_every_execution_stage_and_result(self):
        path = os.path.join(ROOT, 'docs', 'linux_reproduction.md')
        with open(path, 'r', encoding='utf-8') as handle:
            guide = handle.read()
        required = (
            'git clone', 'git pull --ff-only', 'config.local.json',
            'CREATE DATABASE IF NOT EXISTS benchmark_mvp',
            'python3 -m compileall run.py src tests',
            'python3 -m unittest discover -s tests -v',
            'run.py preflight', 'run.py generate', 'run.py load',
            'run.py validate', 'run.py benchmark', 'run.py all',
            'scripts/acceptance_linux.sh', 'benchmark_detail.csv',
            'benchmark_report.md', 'environment.md', 'benchmark.log',
        )
        for text in required:
            self.assertIn(text, guide)
```

- [ ] **Step 2: Run the focused test and verify RED**

Run: `python -m unittest tests.test_repository_hygiene -v`

Expected: ERROR because `docs/linux_reproduction.md` does not exist.

- [ ] **Step 3: Write `docs/linux_reproduction.md`**

Use these exact top-level sections:

```markdown
# Linux 完整复现与验收指南
## 1. 项目边界
## 2. 完整执行链路
## 3. 环境要求
## 4. 拉取或更新代码
## 5. 创建本地配置
## 6. 初始化项目专用 MySQL 数据库
## 7. Windows 或 Linux 静态验证
## 8. 分步骤运行任务
## 9. 一次执行完整业务闭环
## 10. 两轮正式验收
## 11. 查看和核对结果
## 12. 项目文件逐一说明
## 13. 常见错误定位
## 14. 清理与重新运行
## 15. 完整复制命令清单
```

The guide must:

- show both `git clone "$REPO_URL" "$PROJECT_DIR"` and update-existing-repository commands;
- use `cp config.example.json config.local.json` and instruct the operator to edit without displaying the password;
- show all six `run.py` commands and explain their side effects and outputs;
- explain that `all` runs one benchmark while `acceptance_linux.sh` preserves two runs;
- show how to discover the timestamp directory with `RUN_DIR=$(find acceptance-results -mindepth 1 -maxdepth 1 -type d | sort | tail -1)`;
- show `sed`, `head`, `tail`, `wc`, and `grep` commands for inspecting every artifact;
- list every tracked Python module, schema directory, SQL directory, script, test group, configuration file, and generated directory;
- explain expected SF=0.01 row counts and 220 measurement detail rows plus one CSV header;
- warn that this is TPC-H-compatible, not an official audited TPC-H result;
- include safe rerun instructions that rely on the existing project-owned table clearing behavior and never use `DROP DATABASE`.

- [ ] **Step 4: Run the focused test and verify GREEN**

Run: `python -m unittest tests.test_repository_hygiene -v`

Expected: 2 tests pass.

---

### Task 3: Rewrite the public README entry point

**Files:**
- Modify: `tests/test_repository_hygiene.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: the authoritative workflow in `docs/linux_reproduction.md`.
- Produces: a concise repository landing page with no personal machine paths or interview-only links.

- [ ] **Step 1: Add a failing README contract test**

```python
    def test_readme_links_public_guide_without_personal_documents(self):
        with open(os.path.join(ROOT, 'README.md'), 'r', encoding='utf-8') as handle:
            readme = handle.read()
        self.assertIn('docs/linux_reproduction.md', readme)
        self.assertIn('bash scripts/acceptance_linux.sh config.local.json', readme)
        self.assertNotIn('docs/interview_demo.md', readme)
        self.assertNotIn('docs/project_demo.md', readme)
        self.assertNotIn('/home/mxadmin/', readme)
```

- [ ] **Step 2: Run the focused test and verify RED**

Run: `python -m unittest tests.test_repository_hygiene -v`

Expected: FAIL because the existing README links both personal documents and lacks the new guide.

- [ ] **Step 3: Rewrite `README.md` in UTF-8**

Use this structure:

```markdown
# YMatrix / MySQL TPC-H-Compatible Benchmark
## 项目定位
## 数据模型
## 已实现能力
## 环境要求
## 最短复现流程
## 输出文件
## 项目结构
## 测试边界
```

Keep the quick path short, link to `docs/linux_reproduction.md`, and avoid user-specific paths, credentials, previous measured values, or interview references.

- [ ] **Step 4: Run the focused test and verify GREEN**

Run: `python -m unittest tests.test_repository_hygiene -v`

Expected: 3 tests pass.

---

### Task 4: Clarify Python module responsibilities in code

**Files:**
- Modify: `run.py`
- Modify: `src/__init__.py`
- Modify: `src/benchmark.py`
- Modify: `src/command.py`
- Modify: `src/config.py`
- Modify: `src/database.py`
- Modify: `src/discovery.py`
- Modify: `src/generator.py`
- Modify: `src/initializer.py`
- Modify: `src/loader.py`
- Modify: `src/reporter.py`
- Modify: `src/statistics.py`
- Modify: `src/validator.py`

**Interfaces:**
- Consumes: existing module boundaries and public function signatures.
- Produces: human-readable module/function documentation with no behavior changes.

- [ ] **Step 1: Add a failing module-docstring test**

Add to `tests/test_repository_hygiene.py`:

```python
    def test_runtime_python_modules_have_docstrings(self):
        import ast
        paths = [os.path.join(ROOT, 'run.py')]
        src_dir = os.path.join(ROOT, 'src')
        paths.extend(os.path.join(src_dir, name) for name in os.listdir(src_dir)
                     if name.endswith('.py'))
        for path in paths:
            with open(path, 'r', encoding='utf-8') as handle:
                tree = ast.parse(handle.read(), filename=path)
            self.assertTrue(ast.get_docstring(tree), path)
```

- [ ] **Step 2: Run the focused test and verify RED**

Run: `python -m unittest tests.test_repository_hygiene -v`

Expected: FAIL and identify runtime modules without module-level docstrings.

- [ ] **Step 3: Add concise docstrings without behavior changes**

Each file begins with one sentence describing its responsibility. Add function docstrings only to orchestration or non-obvious transformation functions such as `run_load`, `run_validate`, `run_benchmark`, `load_config`, `run_command`, `execute_query`, `generate_data`, `load_database`, `validate_databases`, `run_benchmark_suite`, and report writers.

Do not rename functions, change arguments, reorder database operations, change SQL text, or modify exception handling.

- [ ] **Step 4: Run the focused test and verify GREEN**

Run: `python -m unittest tests.test_repository_hygiene -v`

Expected: 4 tests pass.

---

### Task 5: Final verification and handoff

**Files:**
- Verify: all modified files
- Verify unchanged: `prompt.md`

**Interfaces:**
- Consumes: all preceding tasks.
- Produces: review-ready local changes; no push and no Linux database execution.

- [ ] **Step 1: Run the complete Windows unit suite**

Run: `python -m unittest discover -s tests -v`

Expected: all existing tests plus 4 repository-hygiene tests pass.

- [ ] **Step 2: Verify Python 3.6-compatible compilation**

Run: `python -m compileall run.py src tests`

Expected: exit code 0.

- [ ] **Step 3: Verify patch hygiene and ignore behavior**

Run:

```text
git diff --check
git check-ignore -v data/sample.csv results/benchmark_report.md acceptance-results/example/run1/benchmark.log docs/interview_demo.md docs/project_demo.md
git diff -- prompt.md
git status --short
```

Expected: no whitespace errors; all five protected path families are ignored; `prompt.md` has no diff; the two personal files still exist locally but appear as staged repository deletions.

- [ ] **Step 4: Review the final diff**

Run: `git diff --stat` and `git diff -- .gitignore README.md docs/linux_reproduction.md run.py src tests/test_repository_hygiene.py`.

Confirm the diff contains no credentials, fixed personal filesystem paths, generated CSV/report data, or runtime behavior changes.

- [ ] **Step 5: Commit the maintenance version**

```text
git add .gitignore README.md docs/linux_reproduction.md run.py src tests/test_repository_hygiene.py
git commit -m "docs: publish reproducible Linux workflow"
```

Do not run `git push`; hand the resulting commit SHA to the user for manual review and push.
