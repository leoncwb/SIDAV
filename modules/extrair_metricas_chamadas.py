import csv
import os
import random

# Configurações
CAMINHO_AUDIO_WAV = "/usr/src/pjproject/test_audio/audio.wav"
CSV_ORIGEM = "results/dataset_chamadas_variado.csv"
CSV_DESTINO = "results/dataset_chamadas_com_metricas.csv"

# Lê o tamanho do áudio uma vez
if not os.path.exists(CAMINHO_AUDIO_WAV):
    print("❌ Erro: arquivo de áudio não encontrado! Caminho:", CAMINHO_AUDIO_WAV)
    exit(1)

# Calcula tamanho do áudio em bits
tamanho_audio_bytes = os.path.getsize(CAMINHO_AUDIO_WAV)
tamanho_audio_bits = tamanho_audio_bytes * 8

# Lê o CSV existente e gera o novo
with open(CSV_ORIGEM, mode='r') as arquivo_csv_original:
    leitor = csv.DictReader(arquivo_csv_original)
    linhas = list(leitor)

# Prepara novo CSV
with open(CSV_DESTINO, mode='w', newline='') as arquivo_csv_novo:
    campos = ["chamada", "duracao_segundos", "status", "bitrate_mbps", "jitter_ms"]
    escritor = csv.DictWriter(arquivo_csv_novo, fieldnames=campos)
    escritor.writeheader()

    for linha in linhas:
        duracao_segundos = float(linha['duracao_segundos'])

        # Calcula bitrate em Mb/s
        if duracao_segundos > 0:
            bitrate_mbps = (tamanho_audio_bits / duracao_segundos) / 1_000_000
        else:
            bitrate_mbps = 0

        # Simula jitter (em ms)
        if linha['status'] == 'Sucesso':
            jitter_ms = round(random.uniform(5, 20), 2)  # Jitter normal
        else:
            jitter_ms = round(random.uniform(50, 150), 2)  # Jitter alto

        escritor.writerow({
            "chamada": linha['chamada'],
            "duracao_segundos": duracao_segundos,
            "status": linha['status'],
            "bitrate_mbps": round(bitrate_mbps, 4),
            "jitter_ms": jitter_ms
        })

print(f"\n✅ Métricas extraídas com sucesso! Novo CSV salvo em: {CSV_DESTINO}")
