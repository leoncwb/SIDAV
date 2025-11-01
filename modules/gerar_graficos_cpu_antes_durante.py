import matplotlib.pyplot as plt
import pandas as pd
import os

# Configurações atualizadas
arquivo_log = 'results/cpu_asterisk_log.txt'
amostragem_segundos = 1  # 1 segundo (coleta pelo pidstat)
tempo_antes_ataque = 10  # 10s antes
duracao_ataque_estimado = 10  # 10s de ataque

os.makedirs('results', exist_ok=True)

# Carregar o log
tempos = []
cpu_usos = []

with open(arquivo_log) as f:
    for linha in f:
        if linha.startswith("#") or "Linux" in linha or "UID" in linha or not linha.strip():
            continue
        partes = linha.split()
        if len(partes) >= 8:
            tempos.append(len(tempos) * amostragem_segundos)
            cpu_usos.append(float(partes[7]))

df = pd.DataFrame({"Tempo (s)": tempos, "Uso de CPU (%)": cpu_usos})

# Salvar CSV para conferência
df.to_csv("results/cpu_monitorado_1s.csv", index=False)

# Dividir em três fases
idx_antes = int(tempo_antes_ataque / amostragem_segundos)
idx_durante = int((tempo_antes_ataque + duracao_ataque_estimado) / amostragem_segundos)

df_antes = df.iloc[:idx_antes]
df_durante = df.iloc[idx_antes:idx_durante]
df_total = df

# --- Gráfico 1 ---
plt.figure(figsize=(10, 5))
plt.plot(df_antes["Tempo (s)"], df_antes["Uso de CPU (%)"], marker="o", linestyle="-", color="green", label="CPU Asterisk (antes do ataque)")
plt.xlabel("Tempo (s)")
plt.ylabel("Uso de CPU (%)")
plt.title("Uso de CPU do Asterisk antes do ataque SIP Flood")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('results/grafico_cpu_antes_ataque.png')
plt.close()

# --- Gráfico 2 ---
plt.figure(figsize=(10, 5))
plt.plot(df_durante["Tempo (s)"], df_durante["Uso de CPU (%)"], marker="o", linestyle="-", color="red", label="CPU Asterisk (durante o ataque)")
plt.xlabel("Tempo (s)")
plt.ylabel("Uso de CPU (%)")
plt.title("Uso de CPU do Asterisk durante ataque SIP Flood")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('results/grafico_cpu_durante_ataque.png')
plt.close()

# --- Gráfico 3 ---
plt.figure(figsize=(10, 5))
plt.plot(df_total["Tempo (s)"], df_total["Uso de CPU (%)"], marker="o", linestyle="-", color="blue", label="CPU Asterisk (completo)")
plt.axvspan(tempo_antes_ataque, tempo_antes_ataque + duracao_ataque_estimado, color='red', alpha=0.3, label='Período do Ataque')
plt.xlabel("Tempo (s)")
plt.ylabel("Uso de CPU (%)")
plt.title("Uso de CPU do Asterisk antes, durante e após ataque SIP Flood")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('results/grafico_cpu_completo.png')
plt.close()

print("✅ Gráficos gerados e salvos em 'results/' com sucesso!")
