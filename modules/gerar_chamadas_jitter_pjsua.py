import subprocess
import time
import csv
import os
import shutil
from shutil import which

# Configurações
DESTINO_SIP = "sip:9999@192.168.0.75"
USUARIO_SIP = "1000"
SENHA_SIP = "1234"
TEMPO_MAXIMO = 10  # Tempo máximo em segundos por chamada
TOTAL_CHAMADAS = 100
JITTER_MS = 100  # Jitter em milissegundos

# Descobrir automaticamente o caminho do pjsua
pjsua_path = which("pjsua")
if not pjsua_path:
    raise FileNotFoundError("pjsua não encontrado no PATH do sistema.")

# Aplicar jitter na interface
print(f"🌐 Aplicando {JITTER_MS}ms de jitter na interface de rede...")
os.system(f"tc qdisc add dev eth0 root netem delay {JITTER_MS}ms 2>/dev/null")

dataset_path = "results/dataset_chamadas_jitter.csv"
os.makedirs("results", exist_ok=True)

with open(dataset_path, mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["chamada", "duracao_segundos", "status"])

    try:
        for i in range(1, TOTAL_CHAMADAS + 1):
            print(f"🔵 Iniciando chamada {i}/{TOTAL_CHAMADAS} com jitter...")

            comando = [
                pjsua_path,
                f"--id", f"sip:{USUARIO_SIP}@192.168.0.75",
                f"--registrar", "sip:192.168.0.75",
                f"--realm", "*",
                f"--username", USUARIO_SIP,
                f"--password", SENHA_SIP,
                f"--null-audio",
                f"--auto-answer", "200",
                f"--auto-play",
                DESTINO_SIP
            ]

            inicio = time.time()
            processo = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                processo.wait(timeout=TEMPO_MAXIMO)
                fim = time.time()
                duracao = round(fim - inicio, 2)

                if duracao >= 9:
                    status = "Sucesso"
                else:
                    status = "Timeout"

            except subprocess.TimeoutExpired:
                processo.kill()
                fim = time.time()
                duracao = round(fim - inicio, 2)
                if duracao >= 9:
                    status = "Sucesso"
                else:
                    status = "Timeout"

            writer.writerow([i, duracao, status])

            if status == "Sucesso":
                print(f"💚 Chamada {i} encerrada. Duração: {duracao} segundos. Status: {status}")
            else:
                print(f"⚠️ Tempo limite atingido para a chamada {i}. Forçando encerramento...")
                print(f"❌ Chamada {i} encerrada. Duração: {duracao} segundos. Status: {status}")

    except KeyboardInterrupt:
        print("\n🔚 Execução interrompida pelo usuário.")
    finally:
        # Remover a regra de jitter aplicada
        print("🔄 Removendo jitter da interface de rede...")
        os.system("tc qdisc del dev eth0 root netem 2>/dev/null")

print(f"📂 Dataset salvo em {dataset_path}")
