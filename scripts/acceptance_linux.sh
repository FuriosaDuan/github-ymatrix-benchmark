#!/usr/bin/env bash
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
CONFIG_PATH=${1:-config.local.json}
RUN_ID=$(date +%Y%m%d-%H%M%S)
OUTPUT_DIR="$PROJECT_DIR/acceptance-results/$RUN_ID"
RESULTS_DIR="$PROJECT_DIR/results"

mkdir -p "$OUTPUT_DIR/run1" "$OUTPUT_DIR/run2"
cd "$PROJECT_DIR"

python3 -m compileall run.py src tests 2>&1 | tee "$OUTPUT_DIR/linux_compileall.txt"
python3 -m unittest discover -s tests -v 2>&1 | tee "$OUTPUT_DIR/linux_unittest.txt"
python3 run.py preflight --config "$CONFIG_PATH" 2>&1 | tee "$OUTPUT_DIR/linux_preflight.txt"
python3 run.py generate --config "$CONFIG_PATH" 2>&1 | tee "$OUTPUT_DIR/linux_generate.txt"
python3 run.py load --config "$CONFIG_PATH" 2>&1 | tee "$OUTPUT_DIR/linux_load.txt"
python3 run.py validate --config "$CONFIG_PATH" 2>&1 | tee "$OUTPUT_DIR/linux_validate.txt"

python3 run.py benchmark --config "$CONFIG_PATH" 2>&1 | tee "$OUTPUT_DIR/linux_benchmark_run1.txt"
for name in benchmark_detail.csv benchmark_report.md environment.md benchmark.log; do
    cp "$RESULTS_DIR/$name" "$OUTPUT_DIR/run1/$name"
done

python3 run.py benchmark --config "$CONFIG_PATH" 2>&1 | tee "$OUTPUT_DIR/linux_benchmark_run2.txt"
for name in benchmark_detail.csv benchmark_report.md environment.md benchmark.log; do
    cp "$RESULTS_DIR/$name" "$OUTPUT_DIR/run2/$name"
done

echo "Acceptance results: $OUTPUT_DIR"
