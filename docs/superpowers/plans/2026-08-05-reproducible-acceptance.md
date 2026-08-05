# Benchmark V3 Reproducible Acceptance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a password-safe, UTF-8, repeatable Linux acceptance workflow whose evidence maps directly to every original benchmark requirement.

**Architecture:** Keep database execution in the existing Python modules, make report generation deterministic and metadata-driven, and add a shell orchestrator that invokes only public `run.py` commands. Store each acceptance run in a timestamped directory containing command logs and two benchmark snapshots.

**Tech Stack:** Python 3.6.8 standard library, Bash on CentOS 7.9, psql, MySQL 5.7 CLI, unittest.

## Global Constraints

- Python 3.6.8 and standard library only.
- Never print or commit `config.local.json` secrets.
- Never execute DROP DATABASE, DROP SCHEMA, COPY, LOAD DATA LOCAL INFILE, sudo, or service restarts.
- The accepted workload is simplified TPC-H style; do not claim standard TPC-H or implemented TPC-C.
- Every acceptance stage stops immediately on failure.

---

### Task 1: Complete UTF-8 benchmark report

**Files:**
- Modify: `tests/test_reporter.py`
- Modify: `src/reporter.py`

**Interfaces:**
- Consumes: `write_markdown_report(path, summaries, comparisons, correctness, metadata, detail_rows)`.
- Produces: UTF-8 Markdown containing all 13 required sections, connection modes, indexes, consistency and evidence-based conclusion.

- [ ] Add tests that read the report as UTF-8 and assert the exact Chinese title, four mandatory limitation sentences, connection modes, indexes, all section headings, and computed comparison content.
- [ ] Run `python -m unittest tests.test_reporter -v` and confirm the new assertions fail on the current mojibake/missing metadata output.
- [ ] Rewrite report literals as valid UTF-8 and add metadata-driven connection/index/conclusion text without changing statistics formulas.
- [ ] Run `python -m unittest tests.test_reporter -v` and confirm all reporter tests pass.

### Task 2: Add repeatable Linux acceptance orchestrator

**Files:**
- Create: `scripts/acceptance_linux.sh`
- Create: `docs/acceptance.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: `python3 run.py <command> --config <path>`.
- Produces: `acceptance-results/YYYYMMDD-HHMMSS/` with compile, unittest, preflight, generate, load, validate logs and two complete benchmark directories.

- [ ] Add a static unittest that verifies command order, `set -eu`, two benchmark executions, result snapshots, and absence of prohibited SQL/secret-print commands.
- [ ] Run the new test and confirm failure because the script is absent.
- [ ] Implement the Bash script with positional config argument defaulting to `config.local.json`, project-root resolution, timestamped output, and `tee` logs.
- [ ] Document exact Windows push, Linux clean pull, MySQL database initialization, acceptance invocation, expected row counts, output files, SCP collection, and TPC scope boundary.
- [ ] Run the script test and full Windows suite.

### Task 3: Preserve reproducible index setup and report metadata

**Files:**
- Modify: `schema/ymatrix.sql`
- Modify: `schema/mysql.sql`
- Modify: `src/loader.py`
- Modify: `tests/test_loader.py`
- Modify: `run.py`

**Interfaces:**
- Consumes: project schema and `execute_sql`.
- Produces: identical logical indexes on order date, lineitem order key, and lineitem part key, idempotently ensured after table creation.

- [ ] Add loader tests asserting each database receives the three fair index definitions without duplicate-index failures.
- [ ] Run loader tests and confirm failure.
- [ ] Add database-specific idempotent index checks/creation and expose the index list in report metadata.
- [ ] Run loader tests and full suite.

### Task 4: Verify and package all evidence

**Files:**
- Modify: `prompt.md`
- Add: `linux-results/<timestamp>/...`

**Interfaces:**
- Consumes: committed code and Linux `config.local.json`.
- Produces: reviewable Git commit containing source, tests, docs, script and password-free real evidence.

- [ ] Append the current user requirement to `prompt.md` with an Asia/Shanghai timestamp.
- [ ] Run `python -m unittest discover -s tests -v`, `python -m compileall run.py src tests`, and `git diff --check` on Windows.
- [ ] After manual push, run `git pull --ff-only` on Linux and execute `bash scripts/acceptance_linux.sh config.local.json`.
- [ ] Verify counts, result consistency, no SQL failures, four output artifacts per run, and no secret values in collected logs.
- [ ] Stage all intended files and create one final local commit; do not push.
