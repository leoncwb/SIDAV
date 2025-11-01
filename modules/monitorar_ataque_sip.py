import os
import time
import psutil
import pandas as pd
import matplotlib.pyplot as plt
from threading import Thread

# CONFIGURAÇÕES
IP_ALVO = "192.168.0.75"           # IP da máquina com Asterisk
TOTAL_PACOTES = 50000              # Total de pacotes SIP do ataque
DURACAO_TOTAL = 60                 # Tempo total de monitoramento (segundos)
TEMPO_ATAQUE = 15                  # Quando o ataque ocorre (entre s 5 e 5+TEMPO_ATAQUE)
INTERVALO = 1                      # Intervalo entre coletas
CAMINHO_ATAQUE = "modules/flood_sip_socket.py"

# Obtém o PID do processo Asterisk pelo nome
def get_pid_asterisk():
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if 'asterisk' in proc.info['name'].lower():
                return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

# Executa o ataque SIP Flood
def executar_ataque():
    print("🚀 Iniciando ataque SIP Flood...")
    comando = f"python3 {CAMINHO_ATAQUE} --ip {IP_ALVO} --pacotes {TOTAL_PACOTES}"
    resultado = os.system(comando)
    if resultado != 0:
        print(f"⚠️ Erro ao executar o ataque: {comando}")
    print("✅ Ataque finalizado.")

# Coleta de métricas de CPU
def monitorar_sistema(duracao, intervalo):
    pid_asterisk = get_pid_asterisk()
    if not pid_asterisk:
        print("❌ Asterisk não encontrado! Abortando monitoramento.")
        return None

    print(f"📈 Coletando dados de CPU (Asterisk PID {pid_asterisk})...")
    registros = []
    inicio = time.time()

    while (time.time() - inicio) < duracao:
        tempo_atual = int(time.time() - inicio)
        cpu_total = psutil.cpu_percent(interval=None)
        try:
            cpu_asterisk = psutil.Process(pid_asterisk).cpu_percent(interval=None)
        except Exception:
            cpu_asterisk = 0
        registros.append([tempo_atual, cpu_total, cpu_asterisk])
        time.sleep(intervalo)

    df = pd.DataFrame(registros, columns=["Tempo", "CPU_Total", "CPU_Asterisk"])
    os.makedirs("results", exist_ok=True)
    df.to_csv("results/monitoramento_cpu.csv", index=False)
    print("✅ Monitoramento salvo em results/monitoramento_cpu.csv")
    return df

# Geração de gráficos
def gerar_graficos(df):
    plt.figure()
    plt.plot(df["Tempo"], df["CPU_Total"], label="CPU Total", color="red")
    plt.axvspan(5, 5 + TEMPO_ATAQUE, color='orange', alpha=0.3, label="Período do Ataque")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Uso de CPU (%)")
    plt.title("Uso Total da CPU durante o ataque SIP Flood")
    plt.legend()
    plt.grid(True)
    plt.savefig("results/grafico_cpu_total.png")

    plt.figure()
    plt.plot(df["Tempo"], df["CPU_Asterisk"], label="CPU Asterisk", color="blue")
    plt.axvspan(5, 5 + TEMPO_ATAQUE, color='orange', alpha=0.3, label="Período do Ataque")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Uso de CPU (%)")
    plt.title("Uso da CPU do processo Asterisk durante o ataque")
    plt.legend()
    plt.grid(True)
    plt.savefig("results/grafico_cpu_asterisk.png")

    print("📊 Gráficos salvos em:")
    print("  - results/grafico_cpu_total.png")
    print("  - results/grafico_cpu_asterisk.png")

# Execução principal
if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)

    monitoramento = Thread(target=monitorar_sistema, args=(DURACAO_TOTAL, INTERVALO))
    ataque = Thread(target=executar_ataque)

    monitoramento.start()
    time.sleep(5)  # Aguarda 5s para iniciar o ataque
    ataque.start()

    monitoramento.join()
    ataque.join()

    if os.path.exists("results/monitoramento_cpu.csv"):
        df_resultado = pd.read_csv("results/monitoramento_cpu.csv")
        gerar_graficos(df_resultado)
    else:
        print("❌ Arquivo de monitoramento não encontrado. Verifique se o Asterisk estava ativo.")
