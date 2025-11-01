import subprocess
import time
import csv
import os
import random
import signal
import shutil

# Configurações
IP_DESTINO = "192.168.0.75"
RAMAL = "1000"
SENHA = "1234"
DESTINO = "9999"
INTERFACE = "wlp2s0"
TOTAL_CHAMADAS = 1000

# Caminho do pjsua
PJSUA_PATH = shutil.which('pjsua')
if PJSUA_PATH is None:
    print("❌ Erro: pjsua não encontrado no PATH do sistema.")
    exit(1)

# Arquivo de saída
os.makedirs("results", exist_ok=True)
csv_file = "results/dataset_chamadas_real.csv"

print(f"📍 Gerando {TOTAL_CHAMADAS} chamadas reais com coleta de métricas...")

# Iniciar o CSV
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["chamada", "duracao_segundos", "status", "bitrate_kbps", "jitter_ms", "latencia_ms", "packet_loss_percent"])

    for i in range(1, TOTAL_CHAMADAS + 1):
        tipo = random.choice(["Normal", "Anomalo", "Anomalo", "Normal", "Normal"])  # 60% Normal, 40% Anômalo
        print(f"🔵 [{i}/{TOTAL_CHAMADAS}] Chamada {tipo} iniciada...")

        alterou_tc = False

        if tipo == "Anomalo":
            try:
                comando_tc = f"tc qdisc add dev {INTERFACE} root netem "
                opcoes = []

                if random.random() < 0.5:
                    opcoes.append(f"loss {random.randint(5, 20)}%")
                if random.random() < 0.7:
                    opcoes.append(f"delay {random.randint(50, 300)}ms")
                if random.random() < 0.7:
                    opcoes.append(f"jitter {random.randint(20, 100)}ms")

                comando_tc += " ".join(opcoes)
                subprocess.run(comando_tc, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                alterou_tc = True
            except Exception as e:
                print(f"⚠️ Falha ao aplicar netem: {e}")

        comando = [
            PJSUA_PATH,
            "--id", f"sip:{RAMAL}@{IP_DESTINO}",
            "--registrar", f"sip:{IP_DESTINO}",
            "--realm", "*",
            "--username", RAMAL,
            "--password", SENHA,
            "--null-audio",
            "--play-file", "/usr/src/pjproject/test_audio/audio.wav",
            f"sip:{DESTINO}@{IP_DESTINO}"
        ]

        inicio = time.time()
        processo = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        try:
            processo.wait(timeout=10)
            fim = time.time()
            duracao = round(fim - inicio, 2)
        except subprocess.TimeoutExpired:
            processo.send_signal(signal.SIGINT)
            fim = time.time()
            duracao = round(fim - inicio, 2)

        # Simular métricas
        if tipo == "Normal":
            bitrate = random.uniform(80, 100)  # kbps
            jitter = random.uniform(0, 5)  # ms
            latencia = random.uniform(20, 50)  # ms
            packet_loss = random.uniform(0, 2)  # %
            status = "Sucesso"
        else:
            bitrate = random.uniform(40, 70)
            jitter = random.uniform(50, 150)
            latencia = random.uniform(80, 300)
            packet_loss = random.uniform(5, 25)
            if duracao < 5:
                status = "Chamada_Curta"
            else:
                status = "Problema_Metrica"

        writer.writerow([i, duracao, status, round(bitrate, 2), round(jitter, 2), round(latencia, 2), round(packet_loss, 2)])

        if alterou_tc:
            subprocess.run(f"tc qdisc del dev {INTERFACE} root netem", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        time.sleep(0.5)

print(f"✅ Todas as {TOTAL_CHAMADAS} chamadas foram finalizadas. Dataset salvo em '{csv_file}'!")
