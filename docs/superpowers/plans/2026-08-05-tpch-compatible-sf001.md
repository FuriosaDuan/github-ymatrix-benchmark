# TPC-H Compatible SF=0.01 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the four-table demo with a reproducible eight-table, 22-query TPC-H-compatible dual-database workflow.

**Architecture:** A deterministic standard-library generator produces referentially valid CSV files. Existing CLI loading, validation, benchmarking and reporting are generalized to eight tables and 22 dynamically discovered database-specific SQL files.

**Tech Stack:** Python 3.6.8 standard library, PostgreSQL-compatible psql, MySQL 5.7 CLI, Bash, unittest.

## Global Constraints

- No dbgen/qgen or third-party Python packages.
- Default scale_factor is 0.01; never label results as official TPC-H.
- Batch INSERT maximum is 500 rows; no COPY or LOAD DATA.
- Both databases load identical CSV and execute semantically equivalent SQL.

### Task 1: Eight-table deterministic generator

- [ ] Add failing tests for eight filenames, exact SF=0.01 base counts, deterministic hashes and referential integrity.
- [ ] Generalize config and generator with `scale_factor` and eight-table dependency-valid records.
- [ ] Run generator tests and verify deterministic output.

### Task 2: Eight-table schema, loader and validator

- [ ] Add failing tests for dependency-safe delete/load order, batch size, eight counts and foreign-key validation.
- [ ] Replace schemas and generalize loader/validator to all eight tables with fair indexes.
- [ ] Run loader/validator tests.

### Task 3: Twenty-two dual-database analytical queries

- [ ] Add discovery tests requiring q01–q22 in each SQL directory and matching IDs.
- [ ] Add 22 fixed-parameter PostgreSQL/YMatrix SQL files and 22 MySQL 5.7 equivalents.
- [ ] Verify files are nonempty, read-only SELECT/WITH statements and deterministic where ordering matters.

### Task 4: Complete report and acceptance workflow

- [ ] Update report metadata and query descriptions for eight tables/22 queries/SF=0.01.
- [ ] Update README, acceptance and interview docs with model relationships and manual flow.
- [ ] Run Windows unittest, compileall, diff check and deterministic generation.
- [ ] Commit all source, docs, tests and historical password-free evidence without pushing.
- [ ] After owner push, run Linux one-click acceptance and collect two real runs.
