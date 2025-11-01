import subprocess
import time
import csv
import os
import signal
import shutil

# Local onde vai salvar o dataset
csv_file = 'results/dataset_chamadas_loss.csv'

# Descobrir o caminho do pjsua automaticamente
PJSUA_PATH = shutil.which('pjsua')

if PJSUA_PATH is None:
    print("❌ Erro: pjsua não encontrado no PATH do sistema.")
    print("👉 Solução: entre no diretório /usr/src/pjproject e execute 'make install' para instalar o pjsua.")
    exit(1)

# Configuração de rede para perda de pacotes (20%)
print("🌐 Aplicado 20% de perda de pacotes (packet loss).")
subprocess.run("tc qdisc add dev wlp2s0 root netem loss 20%", shell=True)

# Número de chamadas a serem realizadas
total_chamadas = 100

# Criação do arquivo CSV
os.makedirs("results", exist_ok=True)
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["chamada", "duracao_segundos", "status"])

    for i in range(1, total_chamadas + 1):
        print(f"🔵 Iniciando chamada {i}/{total_chamadas} com perda de pacotes...")

        comando = [
            PJSUA_PATH,
            "--id", "sip:1000@192.168.0.75",
            "--registrar", "sip:192.168.0.75",
            "--realm", "*",
            "--username", "1000",
            "--password", "1234",
            "--null-audio",
            "--play-file", "/usr/src/pjproject/test_audio/audio.wav",
            "sip:9999@192.168.0.75"
        ]

        inicio = time.time()
        processo = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        try:
            processo.wait(timeout=10)  # Espera 10 segundos
            fim = time.time()
        except subprocess.TimeoutExpired:
            processo.send_signal(signal.SIGINT)  # Envia sinal para encerrar o processo
            fim = time.time()

        duracao = round(fim - inicio, 2)

        # Corrigir o status
        if 9.5 <= duracao <= 10.5:
            status = "Sucesso"
            print(f"🟢 Chamada {i} OK. Duração: {duracao} segundos. Status: {status}")
        elif duracao < 5:
            status = "Chamada_Curta"
            print(f"⚠️ Chamada {i} muito curta! Duração: {duracao} segundos. Status: {status}")
        else:
            status = "Anomalia_Desconhecida"
            print(f"❌ Chamada {i} com comportamento anômalo. Duração: {duracao} segundos. Status: {status}")

        writer.writerow([i, duracao, status])
        time.sleep(1)

# Remover a regra de perda de pacotes
subprocess.run("tc qdisc del dev wlp2s0 root netem", shell=True)
print(f"✅ Todas as {total_chamadas} chamadas foram finalizadas. Dataset salvo em '{csv_file}'.")
