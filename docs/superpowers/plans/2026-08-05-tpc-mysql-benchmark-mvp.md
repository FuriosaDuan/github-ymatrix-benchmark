# TPC-H Style Benchmark MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python 3.6-compatible CLI MVP for reproducible TPC-H-style YMatrix/MySQL benchmarking.

**Architecture:** Keep CLI dispatch, configuration, command construction, deterministic data generation, validation, benchmarking, statistics, and reporting in focused standard-library modules. Windows tests use mock subprocesses; real database execution is Linux-only and opt-in.

**Tech Stack:** Python 3.6.8 standard library, unittest, PowerShell SSH wrapper, SQL.

## Global Constraints

- No third-party Python packages.
- No Windows direct database connections.
- No automatic `load`, `benchmark`, or `all` execution.
- No real password in `config.local.json`, logs, commands, or committed files.
- Support only `concurrency=1`.

### Task 1: Define test contracts

**Files:** `tests/test_config.py`, `tests/test_command.py`, `tests/test_statistics.py`, `tests/test_reporter.py`

- [ ] Add failing tests for required config keys, transport rules, command password safety, concurrency validation, nearest-rank p95, CSV headers, Markdown output, timeout and non-zero subprocess handling.
- [ ] Run `python -m unittest discover -s tests -v` and confirm failures are due to missing modules/functions.

### Task 2: Implement core modules

**Files:** `run.py`, `src/*.py`

- [ ] Implement configuration loading and validation.
- [ ] Implement subprocess wrapper with timeout and sanitized errors.
- [ ] Implement deterministic CSV generation and validation.
- [ ] Implement schema loading, benchmark execution, statistics, and report writers.
- [ ] Re-run the tests and keep the implementation minimal until green.

### Task 3: Add SQL, schema, and operator files

**Files:** `schema/*.sql`, `sql/**/*.sql`, `config.example.json`, `.gitignore`, `AGENTS.md`, `README.md`, `report.md`, `ai_usage.md`, `scripts/remote_preflight.ps1`

- [ ] Add safe schema and equivalent Q01-Q03 SQL for both databases.
- [ ] Add sample configuration without secrets and ignore local configuration/results.
- [ ] Document commands, Linux-only workflow, safety gates, and report limitations.

### Task 4: Verify and hand off

- [ ] Run full unittest suite.
- [ ] Run `python -m compileall run.py src tests`.
- [ ] Run a mock-safe `preflight` and `generate` smoke check without databases.
- [ ] Inspect `git status` and `git diff`; do not push.
