# Public Reproduction Guide Design

## Goal

Turn the repository into a public, reproducible YMatrix/MySQL TPC-H-compatible benchmark project while keeping personal interview material and generated artifacts out of Git.

## Scope

- Keep `docs/interview_demo.md` and `docs/project_demo.md` on the maintainer's local machine, remove them from Git tracking, and ignore them in future commits.
- Keep generated `data/`, `results/`, and `acceptance-results/` directories outside version control.
- Rewrite `README.md` as the concise public entry point.
- Add `docs/linux_reproduction.md` as the complete copy-and-run Linux guide.
- Document every maintained code file and directory with its responsibility, inputs, outputs, and place in the execution flow.
- Add module and function docstrings only where they materially improve understanding; avoid line-by-line comments that merely repeat the code.
- Do not append this maintenance request or its follow-up messages to `prompt.md`.

## Documentation Architecture

`README.md` provides project positioning, the TPC-H compatibility boundary, the eight-table relationship model, prerequisites, the shortest successful path, generated output names, and a link to the full guide.

`docs/linux_reproduction.md` is the authoritative operational guide. It covers repository clone/update, Linux prerequisites, configuration creation without exposing credentials, MySQL database initialization, static checks, unit tests, preflight, deterministic data generation, dual-database loading, validation, one-off benchmark execution, full acceptance execution, and result inspection.

Commands use variables such as `REPO_URL`, `PROJECT_DIR`, `CONFIG_PATH`, and `RUN_DIR` so another operator is not tied to the original developer's Windows username, SSH key, or Linux home directory.

## Reproduction Flow

The documented sequence is:

```text
clone or pull
-> verify Python 3.6.8 and database clients
-> create config.local.json from config.example.json
-> create benchmark_mvp with CREATE DATABASE IF NOT EXISTS
-> compileall and unittest
-> preflight
-> generate
-> load
-> validate
-> benchmark or all
-> run the two-pass acceptance script
-> inspect reports, detail CSV, environment metadata, and logs
```

Each stage states its command, expected evidence, output path, and common failure checks. The guide explicitly distinguishes the current TPC-H-compatible workload from an official or audited TPC-H implementation.

## Ignore Policy

The repository ignores:

- `config.local.json` and credentials;
- generated CSV data under `data/`;
- current reports under `results/`;
- timestamped acceptance artifacts under `acceptance-results/`;
- maintainer-only `docs/interview_demo.md` and `docs/project_demo.md`;
- Python bytecode and cache directories.

Because the two personal documents are already tracked, implementation removes only their index entries. Their working-tree files remain available locally.

## Code Documentation Policy

Every Python module receives a concise module-level docstring describing its single responsibility. Public orchestration and transformation functions receive docstrings where their inputs, outputs, side effects, or safety properties are not obvious from the signature. SQL files remain executable SQL without verbose comments; their role is listed in the structure guide.

No runtime behavior, database schema, generated dataset, or benchmark statistics are intentionally changed by this documentation-focused maintenance version.

## Verification

Tests will assert that generated and personal paths are ignored and that the public guide contains the complete execution stages and result artifacts. Verification commands are:

```text
python -m unittest discover -s tests -v
python -m compileall run.py src tests
git diff --check
```

The final Git diff must show no change to `prompt.md`, and `git check-ignore` must identify each protected path.
