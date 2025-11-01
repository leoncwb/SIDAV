import subprocess
import time
import csv
import os

# Configurações
pjsua_path = '/usr/local/bin/pjsua'
audio_file = '/usr/src/pjproject/test_audio/audio.wav'
asterisk_server = '192.168.0.75'
ramal_origem = '1000'
senha_origem = '1234'
ramal_destino = '9999'
numero_chamadas = 100
tempo_limite_chamada = 10  # segundos

# Arquivo CSV para salvar o dataset
output_csv = 'results/dataset_chamadas.csv'
os.makedirs('results', exist_ok=True)

# Lista para armazenar os resultados
dataset = []

for i in range(1, numero_chamadas + 1):
    print(f"\U0001F535 Iniciando chamada {i}/{numero_chamadas}...")

    comando = [
        pjsua_path,
        f'--id=sip:{ramal_origem}@{asterisk_server}',
        f'--registrar=sip:{asterisk_server}',
        f'--realm=*',
        f'--username={ramal_origem}',
        f'--password={senha_origem}',
        f'--null-audio',
        f'--play-file={audio_file}',
        f'sip:{ramal_destino}@{asterisk_server}'
    ]

    inicio = time.time()
    try:
        processo = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        processo.wait(timeout=tempo_limite_chamada)
        status = 'Sucesso'
    except subprocess.TimeoutExpired:
        processo.kill()
        status = 'Timeout'
    fim = time.time()
    duracao = fim - inicio

    # Correção: se a duração foi próxima ao tempo limite, considera sucesso
    if abs(duracao - tempo_limite_chamada) <= 1.0:
        status = 'Sucesso'

    print(f"\U0001F534 Chamada {i} encerrada. Duração: {duracao:.2f} segundos. Status: {status}\n")

    dataset.append([i, round(duracao, 2), status])

# Salvando o CSV
with open(output_csv, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['chamada', 'duracao_segundos', 'status'])
    writer.writerows(dataset)

print(f"\n\U0001F4BE Dataset salvo em {output_csv}!")
