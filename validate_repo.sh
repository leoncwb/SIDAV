#!/usr/bin/env bash
set -euo pipefail

ROOT="$(pwd)"
OUT="$ROOT/validation_report.txt"
VENV_DIR="$ROOT/.venv_validate"

echo "Validation started at $(date)" > "$OUT"
echo "" >> "$OUT"

# 1) Create venv (safe)
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# 2) Install minimal requirements if file exists
REQ="$ROOT/requirements.min.txt"
if [ -f "$REQ" ]; then
  echo "Installing requirements from $REQ..." | tee -a "$OUT"
  pip install --upgrade pip setuptools wheel >/dev/null
  pip install -r "$REQ" >/dev/null 2>&1 || echo "Warning: some packages failed to install (see console)" | tee -a "$OUT"
else
  echo "No requirements.min.txt found — skipping pip install." | tee -a "$OUT"
fi

echo "" >> "$OUT"
echo "=== PYTHON SYNTAX CHECK (py_compile) ===" >> "$OUT"
find . -type f -name "*.py" ! -path "./.venv_validate/*" | sort | while read -r py; do
  printf "Checking %s ... " "$py" | tee -a "$OUT"
  if python -m py_compile "$py" 2>/tmp/pyerr; then
    echo "OK" | tee -a "$OUT"
  else
    echo "SYNTAX_ERROR" | tee -a "$OUT"
    sed -n '1,200p' /tmp/pyerr | tee -a "$OUT"
  fi
done

echo "" >> "$OUT"
echo "=== STATIC LINT (ruff if available, else pyflakes fallback) ===" >> "$OUT"
if command -v ruff >/dev/null 2>&1; then
  echo "Running ruff (fast)..." | tee -a "$OUT"
  ruff check . --exclude .venv_validate --format text | tee -a "$OUT" || true
elif python -c "import pyflakes" >/dev/null 2>&1; then
  echo "Running pyflakes..." | tee -a "$OUT"
  python -m pyflakes $(find . -name '*.py' | tr '\n' ' ') 2>&1 | tee -a "$OUT" || true
else
  echo "No ruff/pyflakes installed. Skipping static lint (install ruff for better checks)." | tee -a "$OUT"
fi

echo "" >> "$OUT"
echo "=== IMPORT RESOLUTION SCAN (dry) ===" >> "$OUT"
# This tries to import each module in isolated subprocess to catch missing package imports (without running their main)
find . -name "*.py" ! -path "./.venv_validate/*" | while read -r f; do
  # skip generated files and big results folders
  rel="${f#./}"
  # Attempt to import by path using python -c (not perfect for all modules)
  python - <<PY 2>/tmp/importerr || true
import runpy, sys
try:
    runpy.run_path("$f", run_name="__import_check__", init_globals={"__name__": "__import_check__"}, run_name_allowed=True)
    print("IMPORT_OK: $rel")
except SystemExit:
    # some scripts call sys.exit after --help
    print("IMPORT_MAY_EXIT: $rel")
except Exception as e:
    print("IMPORT_ERROR: $rel ->", type(e).__name__, str(e))
PY
  sed -n '$p' /tmp/importerr 2>/dev/null || true
done >> "$OUT" 2>&1 || true

echo "" >> "$OUT"
echo "=== MAIN-ENTRY HELP CHECK ===" >> "$OUT"
# Detect files with main guard and try -h/--help
grep -Rnl "if __name__ *== *['\"]__main__['\"]" . | while read -r script; do
  echo "Script with main: $script" | tee -a "$OUT"
  # Try common help flags
  for flag in -h --help --dry-run; do
    printf "  Trying: python %s %s ... " "$script" "$flag" | tee -a "$OUT"
    if python "$script" "$flag" >/tmp/hout 2>/tmp/herr; then
      echo "EXIT0" | tee -a "$OUT"
      break
    else
      rc=$?
      echo "RC=$rc" | tee -a "$OUT"
      tail -n 20 /tmp/herr | sed 's/^/    /' | tee -a "$OUT"
    fi
  done
done

echo "" >> "$OUT"
echo "=== SUMMARY SUGGESTIONS ===" >> "$OUT"
# heuristic: list python files > 300 lines as candidates to split or validate manually
echo "Large python files (>300 lines):" >> "$OUT"
awk 'FNR==1{file=FILENAME} {n++} END{ }' $(find . -name '*.py') >/dev/null 2>&1 || true
find . -name "*.py" -not -path "./.venv_validate/*" -exec awk 'END{print FNR,ARGV[1]}' {} \; | awk '$1>300{print $2 " (" $1 " lines)"}' >> "$OUT" || true

echo "" >> "$OUT"
echo "Validation finished at $(date)" >> "$OUT"

deactivate 2>/dev/null || true
echo "Report written to $OUT"
