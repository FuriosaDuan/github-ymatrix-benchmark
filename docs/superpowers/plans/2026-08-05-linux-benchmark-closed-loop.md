# Linux Benchmark Closed Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the YMatrix/MySQL MVP form a safe, real Linux execution loop from preflight through data load, row-count validation, and benchmark reporting.

**Architecture:** Add a shared database client layer built on the existing subprocess wrapper. It will execute read-only preflight, safe prefixed schema/reset SQL, escaped batched INSERT statements, and COUNT queries for both databases. The CLI will orchestrate one strict `all` pipeline and never execute the real database path on Windows.

**Tech Stack:** Python 3.6.8 standard library, `subprocess`, `csv`, `datetime`, `time.monotonic`, `unittest` mocks.

## Global Constraints

- Target Linux is CentOS 7.9 x86_64 with Python 3.6.8.
- Use only Python standard library.
- Windows runs only unittest, compileall, and mock tests; never real database commands.
- Do not use DROP DATABASE, COPY, LOAD DATA LOCAL INFILE, or third-party packages.
- MySQL target database is configured as `benchmark_mvp`; MVP never operates on a MySQL system database.
- YMatrix uses configured `postgres`; project tables are `bench_customer`, `bench_part`, `bench_orders`, `bench_lineitem`.
- Do not read, print, commit, or push real `config.local.json` secrets.

### Task 1: Add failing contracts

**Files:** `tests/test_command.py`, `tests/test_initializer.py`, `tests/test_loader.py`, `tests/test_validator.py`, `tests/test_benchmark.py`, `tests/test_run.py`, `tests/test_config.py`

- [ ] Assert MySQL commands select `database` and preserve local_default argument restrictions.
- [ ] Assert preflight invokes psql and mysql with version queries and rejects missing executables or failed connections.
- [ ] Assert loader reads all four CSVs, emits at most 500 rows per INSERT batch, uses prefixed tables, and never uses repr/COPY/LOAD DATA.
- [ ] Assert validation queries both databases and rejects any row-count mismatch.
- [ ] Assert warmups do not enter detail rows, monotonic timestamps are used, failed elapsed values are excluded from summaries, and timestamps include timezone offsets.
- [ ] Assert `all` calls preflight, generate, load, validate, benchmark in order and stops after a failure.
- [ ] Run the suite and observe expected failures before implementation.

### Task 2: Implement database commands and configuration

**Files:** `config.example.json`, `src/config.py`, `src/command.py`, `src/initializer.py`

- [ ] Require `mysql.database`, build `mysql --database <name>` for both transports, and keep credentials out of argv.
- [ ] Add safe ISO timestamp and SQL literal helpers.
- [ ] Implement read-only preflight for executable checks, YMatrix `SELECT version()`, MySQL `SELECT VERSION()`, and target database usability.

### Task 3: Implement schema, load, and validate

**Files:** `schema/ymatrix.sql`, `schema/mysql.sql`, `src/loader.py`, `src/validator.py`, `run.py`

- [ ] Rename all project tables with `bench_` prefix and add per-database schema/reset/insert/count operations.
- [ ] Load each CSV in escaped multi-row INSERT batches of at most 500 rows into both databases.
- [ ] Make `validate` print `table,expected,ymatrix,mysql,match` and return failure on any mismatch.

### Task 4: Implement benchmark and strict orchestration

**Files:** `src/benchmark.py`, `src/statistics.py`, `src/reporter.py`, `run.py`

- [ ] Execute configured warmups without recording them.
- [ ] Measure with `time.monotonic`, use timezone-aware ISO 8601 strings, and summarize only successful elapsed values.
- [ ] Sequence `all` exactly as preflight → generate → load → validate → benchmark, stopping immediately on failure.

### Task 5: Documentation and verification

**Files:** `README.md`, `prompt.md`, `docs/superpowers/...`

- [ ] Document database initialization without DROP DATABASE and the new MySQL database key.
- [ ] Append this prompt change with timestamp to `prompt.md`.
- [ ] Run `python -m unittest discover -s tests -v`, `python -m compileall run.py src tests`, inspect `git diff`, and do not push.
