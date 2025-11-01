import csv
import os
import random

# Criar pasta de resultados se não existir
os.makedirs("results", exist_ok=True)

# Caminho do novo dataset melhorado
csv_file = 'results/dataset_chamadas_melhorado.csv'

# Quantidade de chamadas
total_chamadas = 100

# Definir proporções
percentual_normais = 0.7
percentual_anomalias = 0.3

# Quantidade de cada tipo
qtd_normais = int(total_chamadas * percentual_normais)
qtd_anomalias = total_chamadas - qtd_normais

print("\U0001F4CD Gerando chamadas simuladas com múltiplas métricas...")

# Abrir arquivo CSV
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["chamada", "duracao_segundos", "jitter_medio", "bitrate_medio", "packet_loss_estimado", "latencia_media", "status"])

    chamada_id = 1

    # Gerar chamadas normais (Sucesso)
    for _ in range(qtd_normais):
        duracao = round(random.uniform(9.5, 10.5), 2)
        jitter = round(random.uniform(0.001, 0.03), 3)
        bitrate = random.randint(56, 64)
        packet_loss = random.uniform(0, 1)  # quase zero
        latencia = random.randint(30, 100)
        status = "Sucesso"

        writer.writerow([chamada_id, duracao, jitter, bitrate, packet_loss, latencia, status])
        chamada_id += 1

    # Gerar chamadas anômalas (diversificadas)
    for _ in range(qtd_anomalias):
        tipo_anomalia = random.choice(["Chamada_Curta", "Alta_Perda", "Alto_Jitter"])

        if tipo_anomalia == "Chamada_Curta":
            duracao = round(random.uniform(2, 5), 2)
            jitter = round(random.uniform(0.001, 0.03), 3)
            bitrate = random.randint(56, 64)
            packet_loss = random.uniform(0, 1)
            latencia = random.randint(30, 100)
        elif tipo_anomalia == "Alta_Perda":
            duracao = round(random.uniform(9.5, 10.5), 2)
            jitter = round(random.uniform(0.001, 0.03), 3)
            bitrate = random.randint(48, 56)
            packet_loss = random.uniform(5, 15)  # perda alta
            latencia = random.randint(100, 250)
        else:  # Alto_Jitter
            duracao = round(random.uniform(9.5, 10.5), 2)
            jitter = round(random.uniform(0.15, 0.4), 3)
            bitrate = random.randint(48, 56)
            packet_loss = random.uniform(0, 5)
            latencia = random.randint(100, 300)

        writer.writerow([chamada_id, duracao, jitter, bitrate, packet_loss, latencia, tipo_anomalia])
        chamada_id += 1

print(f"\n✅ Dataset melhorado salvo em '{csv_file}'!")
print("   -> 70% chamadas normais (Sucesso)")
print("   -> 30% chamadas anômalas (Chamada Curta, Alta Perda, Alto Jitter)")
print("\nPronto para treinar modelos de IA com várias features! \U0001F680")
