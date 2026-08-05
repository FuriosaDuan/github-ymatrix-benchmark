# Benchmark V3 Interview Acceptance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Upgrade the benchmark MVP into a configurable, result-checked, report-complete Linux benchmark tool for YMatrix versus MySQL.

**Architecture:** Keep the standard-library subprocess boundary, but separate configuration, deterministic data generation, SQL discovery, database execution, result normalization, benchmark sampling, aggregation, and report generation. One database client process executes session SQL and the query together; query results are captured before timed rounds for correctness comparison.

**Tech Stack:** Python 3.6.8 standard library, subprocess, csv, json, decimal, datetime, time.monotonic, unittest.

## Global Constraints

- Windows runs only unit tests, compileall, mock-safe generation, and Git operations.
- Linux performs real database work through psql/mysql subprocesses.
- customer=1000, part=500, orders=10000, lineitem=30000, seed=2026.
- Defaults are warmup 1, measurement 5, concurrency 1, timeout 60 seconds.
- No third-party packages, DROP DATABASE, DROP SCHEMA, COPY, LOAD DATA LOCAL INFILE, sudo, or config.local.json commit.
- MySQL uses local_default and target database benchmark_mvp; YMatrix uses configured postgres.

### Task 1: V3 contracts and configuration

**Files:** config.example.json, src/config.py, tests/test_config.py, tests/test_command.py, tests/test_generator.py, tests/test_discovery.py

- [ ] Add failing tests for part=500, timeout=60, session_sql, SQL directories, database selection, output flags, and non-recursive .sql discovery.
- [ ] Implement strict defaults and validation while preserving Python 3.6 syntax.

### Task 2: Database execution and result parsing

**Files:** src/command.py, src/initializer.py, src/database.py, tests/test_initializer.py, tests/test_database.py

- [ ] Add psql/mysql command flags and session SQL in the same client process as each query.
- [ ] Parse tabular output without headers, normalize Decimal values, and redact secret values from errors/logs.
- [ ] Make preflight report actual client and database versions.

### Task 3: Data loading and validation

**Files:** src/generator.py, src/loader.py, src/validator.py, schema/*.sql, tests/test_loader.py, tests/test_validator.py

- [ ] Keep four prefixed project tables and load the same CSV into both databases with batches of at most 500 rows.
- [ ] Query COUNT(*) from both databases and fail on any mismatch.
- [ ] Add deterministic-generation checks and exact required scale.

### Task 4: Benchmark, correctness, and reporting

**Files:** src/benchmark.py, src/statistics.py, src/reporter.py, run.py, tests/test_benchmark.py, tests/test_reporter.py

- [ ] Discover all SQL files, capture first-run result summaries, compare database results, run warmup and measurement rounds with monotonic timing.
- [ ] Generate detail CSV, complete Markdown report, environment metadata, and benchmark.log with slow SQL, failure categories, comparison ratios, and limitations.
- [ ] Make all enforce preflight -> generate -> load -> validate -> benchmark and stop on failure.

### Task 5: Interview material, local verification, and remote workflow

**Files:** docs/interview_demo.md, README.md, report.md, scripts/remote_preflight.ps1, prompt.md

- [ ] Document the real workflow and interview explanations.
- [ ] Run Windows unittest, compileall, diff check, and generation smoke test.
- [ ] Commit and push to the actual remote/branch, then retry Linux pull and real execution.
