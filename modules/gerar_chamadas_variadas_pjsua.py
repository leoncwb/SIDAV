import subprocess
import time
import csv
import os
import signal
import shutil
import random

# Configurações
PJSUA_PATH = shutil.which('pjsua')
if PJSUA_PATH is None:
    print("❌ Erro: pjsua não encontrado no PATH do sistema.")
    exit(1)

IP_ASTERISK = "192.168.0.75"
USUARIO = "1000"
SENHA = "1234"
DESTINO = "9999"
AUDIO_WAV = "/usr/src/pjproject/test_audio/audio.wav"

csv_file = 'results/dataset_chamadas_variado.csv'
os.makedirs('results', exist_ok=True)

TOTAL_CHAMADAS = 10000
PERCENTUAL_CURTAS = 0.3

quantidade_chamadas_curtas = int(TOTAL_CHAMADAS * PERCENTUAL_CURTAS)
quantidade_chamadas_normais = TOTAL_CHAMADAS - quantidade_chamadas_curtas

# Gerar lista de chamadas misturadas
chamadas = ["Chamada_Normal"] * quantidade_chamadas_normais + ["Chamada_Curta"] * quantidade_chamadas_curtas
random.shuffle(chamadas)

print(f"\n🎯 Gerando {TOTAL_CHAMADAS} chamadas variadas de verdade...\n")

# Criar CSV
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["chamada", "duracao_segundos", "status"])

    for i, tipo_chamada in enumerate(chamadas, 1):
        print(f"🔵 Iniciando chamada {i}/{TOTAL_CHAMADAS} ({tipo_chamada})...")

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
            if tipo_chamada == "Chamada_Normal":
                processo.wait(timeout=10)  # Espera normal (10s)
            else:
                tempo_curto = random.uniform(2, 5)  # Tempo aleatório entre 2 e 5 segundos
                time.sleep(tempo_curto)
                processo.send_signal(signal.SIGINT)
                processo.wait()

        except subprocess.TimeoutExpired:
            processo.send_signal(signal.SIGINT)

        fim = time.time()
        duracao = round(fim - inicio, 2)

        if tipo_chamada == "Chamada_Normal":
            status = "Sucesso"
        else:
            status = "Chamada_Curta"

        writer.writerow([i, duracao, status])
        time.sleep(1)  # Pequena pausa entre chamadas

print(f"\n✅ Dataset real salvo: {csv_file}")
print(f"   -> {quantidade_chamadas_normais} chamadas normais (Sucesso)")
print(f"   -> {quantidade_chamadas_curtas} chamadas anormais (Chamada_Curta)")
print("\nPronto para treinar os modelos de IA! 🚀")
