#!/bin/bash
# Exemplo de run template para experimentos
# Uso: ./run_template.sh <attack-name> <target-ip> <duration-seconds>
set -euo pipefail
attack="$1"
target="$2"
duration="${3:-60}"
timestamp=$(date +%F_%H%M%S)
run_dir="../${attack}/runs/${timestamp}"
mkdir -p "${run_dir}"
# metadata
cat > "${run_dir}/metadata.json" <<JSON
{
  "attack": "${attack}",
  "target": "${target}",
  "duration_s": ${duration},
  "timestamp": "${timestamp}",
  "host": "$(hostname -f)",
  "notes": ""
}
JSON
# start tcpdump (pcap)
sudo tcpdump -i any host "${target}" -w "../${attack}/pcaps/${timestamp}.pcap" > /dev/null 2>&1 &
TCPDUMP_PID=$!

# start monitor (example) - ajustar o script monitorar_ataque_sip.py se desejar
python3 ../../modules/monitorar_ataque_sip.py --pid $(pidof asterisk) --out "../${attack}/logs/${timestamp}_cpu.csv" &
MON_PID=$!

# executar (substitua pelo comando do ataque; exemplo com SIPp)
# sipp -sf ../${attack}/params/scenario.xml -r 100 -rp 100 -m 1000 ${target}:5060 > "../${attack}/raw/${timestamp}_sipp.out" 2> "../${attack}/raw/${timestamp}_sipp.err"
# Exemplo placeholder: sleep para simular
echo "Iniciando ataque ${attack} contra ${target} por ${duration}s..."
sleep ${duration} > "../${attack}/raw/${timestamp}_placeholder.out"

# parar monitor e tcpdump
kill ${MON_PID} || true
sudo kill ${TCPDUMP_PID} || true

# coletar stdout/stderr (se houver) e mover para run_dir
mv "../${attack}/raw/${timestamp}_placeholder.out" "${run_dir}/" || true
cp "../${attack}/pcaps/${timestamp}.pcap" "${run_dir}/" || true
cp "../${attack}/logs/${timestamp}_cpu.csv" "${run_dir}/" || true

echo "Run salva em ${run_dir}"
