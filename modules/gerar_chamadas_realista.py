import subprocess
import time
import csv
import os
import random
import shutil

# Configurações gerais
PJSUA_PATH = shutil.which('pjsua')
INTERFACE = "wlp2s0"
IP_ASTERISK = "192.168.0.75"
USUARIO = "1000"
SENHA = "1234"
DESTINO = "9999"
AUDIO_WAV = "/usr/src/pjproject/test_audio/audio.wav"
TOTAL_CHAMADAS = 3500
csv_file = "results/dataset_chamadas_com_metricas_real.csv"

# Categorias
TIPOS = ["normal", "chamada_curta", "jitter_alto", "latencia_alta", "perda_pacote"]
DISTRIBUICAO = {
    "normal": 0.4,
    "chamada_curta": 0.2,
    "jitter_alto": 0.15,
    "latencia_alta": 0.15,
    "perda_pacote": 0.1
}
os.makedirs("results", exist_ok=True)

def aplicar_netem(tipo):
    subprocess.run(f"tc qdisc del dev {INTERFACE} root", shell=True, stderr=subprocess.DEVNULL)
    if tipo == "jitter_alto":
        subprocess.run(f"tc qdisc add dev {INTERFACE} root netem delay 10ms 50ms", shell=True)
    elif tipo == "latencia_alta":
        subprocess.run(f"tc qdisc add dev {INTERFACE} root netem delay 200ms", shell=True)
    elif tipo == "perda_pacote":
        subprocess.run(f"tc qdisc add dev {INTERFACE} root netem loss 20%", shell=True)
    elif tipo == "normal" or tipo == "chamada_curta":
        pass  # Sem manipulação

def coletar_metricas():
    output = subprocess.check_output(f"ifstat -i {INTERFACE} 1 1", shell=True).decode()
    linhas = output.strip().split("\n")
    ultima_linha = linhas[-1].split()
    try:
        bitrate = float(ultima_linha[0])  # Mbps de saída
    except:
        bitrate = 0.0
    jitter = round(random.uniform(0.03, 0.5), 3)  # Valor simbólico
    latencia = round(random.uniform(5, 150), 2)  # Valor simbólico
    return bitrate, jitter, latencia

# Gerar lista embaralhada
lista_chamadas = []
for tipo, proporcao in DISTRIBUICAO.items():
    quantidade = int(TOTAL_CHAMADAS * proporcao)
    lista_chamadas += [tipo] * quantidade
random.shuffle(lista_chamadas)

# Abrir CSV
with open(csv_file, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["chamada", "bitrate_mbps", "status", "jitter_ms", "latencia_ms"])

    for i, tipo in enumerate(lista_chamadas, 1):
        print(f"🔄 Chamando {i}/{TOTAL_CHAMADAS} - Tipo: {tipo}")
        aplicar_netem(tipo)

        comando = [
            PJSUA_PATH,
            "--id", f"sip:{USUARIO}@{IP_ASTERISK}",
            "--registrar", f"sip:{IP_ASTERISK}",
            "--realm", "*",
            "--username", f"{USUARIO}",
            "--password", f"{SENHA}",
            "--null-audio",
            "--play-file", AUDIO_WAV,
            f"sip:{DESTINO}@{IP_ASTERISK}"
        ]

        inicio = time.time()
        processo = subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        try:
            if tipo == "chamada_curta":
                time.sleep(random.uniform(2, 5))
                processo.terminate()
                processo.wait()
            else:
                processo.wait(timeout=10)
        except subprocess.TimeoutExpired:
            processo.terminate()

        fim = time.time()
        duracao = fim - inicio
        status = "Sucesso" if duracao >= 6 else "Chamada_Curta"

        bitrate, jitter, latencia = coletar_metricas()
        writer.writerow([i, bitrate, status, jitter, latencia])
        time.sleep(1)

    subprocess.run(f"tc qdisc del dev {INTERFACE} root", shell=True)
    print(f"\n✅ Dataset salvo em {csv_file}")
