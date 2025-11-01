import os
import csv
import time
import subprocess
import shutil

# Função para encontrar o caminho do pjsua
pjsua_path = shutil.which("pjsua")
if not pjsua_path:
    print("Erro: pjsua não encontrado no sistema.")
    exit(1)

# Aplica jitter de 100ms
print("\U0001f310 Aplicando 100ms de jitter na interface de rede...")
os.system("tc qdisc add dev eth0 root netem delay 100ms 10ms")

# Define o tempo máximo da chamada em segundos
TEMPO_MAXIMO = 10

# Cria/abre o arquivo CSV para armazenar os resultados
csv_path = "results/dataset_chamadas_jitter.csv"
os.makedirs("results", exist_ok=True)

with open(csv_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["chamada", "duracao_segundos", "status"])

    for i in range(1, 101):
        print(f"\U0001f535 Iniciando chamada {i}/100 com jitter...")
        comando = [
            pjsua_path,
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
            processo.wait(timeout=TEMPO_MAXIMO)
            status = "Sucesso"
        except subprocess.TimeoutExpired:
            processo.kill()
            status = "Timeout"
            print(f"\u26a0\ufe0f Tempo limite atingido para a chamada {i}. Forçando encerramento...")

        fim = time.time()
        duracao = round(fim - inicio, 2)

        print(f"ὓ4 Chamada {i} encerrada. Duração: {duracao} segundos. Status: {status}\n")
        writer.writerow([i, duracao, status])

# Remove o jitter aplicado na interface
tc_reset = os.system("tc qdisc del dev eth0 root netem")
if tc_reset == 0:
    print("\u2705 Jitter removido da interface.")
else:
    print("\u26a0\ufe0f Aviso: problema ao remover o jitter (talvez não estivesse aplicado).")

print(f"\n✨ Arquivo {csv_path} gerado com sucesso!")
