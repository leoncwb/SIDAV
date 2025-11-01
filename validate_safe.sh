#!/usr/bin/env bash
set -euo pipefail

ROOT="$(pwd)"
OUT="$ROOT/validation_report_safe.txt"

echo "Safe Validation started at $(date)" > "$OUT"
echo "" >> "$OUT"

echo "=== PYTHON SYNTAX CHECK (py_compile) ===" >> "$OUT"
find . -type f -name "*.py" ! -path "./.venv_validate/*" | sort | while read -r py; do
  printf "Checking %s ... " "$py" | tee -a "$OUT"
  if python3 -m py_compile "$py" 2>/tmp/pyerr; then
    echo "OK" | tee -a "$OUT"
  else
    echo "SYNTAX_ERROR" | tee -a "$OUT"
    sed -n '1,200p' /tmp/pyerr | tee -a "$OUT"
  fi
done

echo "" >> "$OUT"
echo "=== STATIC LINT (ruff if available, else pyflakes fallback) ===" >> "$OUT"
if command -v ruff >/dev/null 2>&1; then
  ruff check . --exclude .venv_validate --format text | tee -a "$OUT" || true
elif python3 -c "import pyflakes" >/dev/null 2>&1; then
  python3 -m pyflakes $(find . -name '*.py' | tr '\n' ' ' ) 2>&1 | tee -a "$OUT" || true
else
  echo "No ruff/pyflakes installed. Skipping static lint (install ruff for better checks)." | tee -a "$OUT"
fi

echo "" >> "$OUT"
echo "Large python files (>300 lines):" >> "$OUT"
find . -name "*.py" -not -path "./.venv_validate/*" -exec awk 'END{print FNR,ARGV[1]}' {} \; | awk '$1>300{print $2 " (" $1 " lines)"}' >> "$OUT" || true

echo "" >> "$OUT"
echo "Safe Validation finished at $(date)" >> "$OUT"
echo "Report: $OUT"
