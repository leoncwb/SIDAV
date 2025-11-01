import os
import hashlib
from difflib import SequenceMatcher
from datetime import datetime

def sha256sum(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def read_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        return str(e)

def compare_files(file1, file2):
    content1, content2 = read_file(file1), read_file(file2)
    ratio = SequenceMatcher(None, content1, content2).ratio()
    return ratio

# Local onde estão os scripts
base_path = os.path.dirname(os.path.abspath(__file__))
files = [f for f in os.listdir(base_path) if f.startswith("gerar_chamadas_") and f.endswith(".py")]

print("=== Comparação entre scripts gerar_chamadas_* ===\n")
report = []
for file in sorted(files):
    full_path = os.path.join(base_path, file)
    stats = os.stat(full_path)
    size_kb = round(stats.st_size / 1024, 1)
    mtime = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    sha = sha256sum(full_path)
    lines = sum(1 for _ in open(full_path, encoding="utf-8", errors="ignore"))
    report.append((file, lines, size_kb, mtime, sha))

print(f"{'Arquivo':40s} | {'Linhas':6s} | {'Tamanho(KB)':12s} | {'Última modificação':19s}")
print("-" * 90)
for f, lines, kb, mtime, sha in report:
    print(f"{f:40s} | {lines:<6d} | {kb:<12.1f} | {mtime}")

# Comparação cruzada
print("\n=== Similaridade (0–100%) ===")
for i in range(len(report)):
    for j in range(i+1, len(report)):
        file1, file2 = report[i][0], report[j][0]
        ratio = compare_files(os.path.join(base_path, file1), os.path.join(base_path, file2))
        if ratio > 0.75:
            print(f"{file1:35s} ↔ {file2:35s} → {ratio*100:.1f}% semelhantes")

print("\nAnálise concluída.")
