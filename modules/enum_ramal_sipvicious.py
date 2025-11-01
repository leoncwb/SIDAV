import socket
import csv
import os
import argparse

# Argumentos de linha de comando
parser = argparse.ArgumentParser(description="Enumeração de ramais SIP manual via socket.")
parser.add_argument("--metodo", choices=["OPTIONS", "INVITE"], default="OPTIONS", help="Método SIP para enumeração (OPTIONS ou INVITE)")
args = parser.parse_args()

# Configurações
IP_DESTINO = "192.168.0.75"
PORTA_SIP = 5060
RAMAL_INICIAL = 1000
RAMAL_FINAL = 1100
METODO_ENUMERACAO = args.metodo

# Criar pasta de resultados se não existir
os.makedirs("results", exist_ok=True)

# Função para enviar pacote SIP e receber resposta
def enviar_pacote_sip(ramal):
    mensagem = f"""
{METODO_ENUMERACAO} sip:{ramal}@{IP_DESTINO} SIP/2.0
Via: SIP/2.0/UDP 192.168.0.100:5060;branch=z9hG4bK-12345
From: <sip:scanner@{IP_DESTINO}>;tag=12345
To: <sip:{ramal}@{IP_DESTINO}>
Call-ID: 12345@192.168.0.100
CSeq: 1 {METODO_ENUMERACAO}
Contact: <sip:scanner@192.168.0.100>
Max-Forwards: 70
User-Agent: SIPScanner
Content-Length: 0

"""

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(3)
        sock.sendto(mensagem.encode(), (IP_DESTINO, PORTA_SIP))
        resposta, _ = sock.recvfrom(4096)
        resposta = resposta.decode(errors="ignore").lower()
        sock.close()
        return resposta
    except socket.timeout:
        return None
    except Exception as e:
        print(f"Erro ao consultar ramal {ramal}: {e}")
        return None

# Função para executar a enumeração
def enumerar_ramais():
    encontrados = []
    print(f"\n🔎 Iniciando enumeração de ramais de {RAMAL_INICIAL} a {RAMAL_FINAL} usando {METODO_ENUMERACAO}...")

    for ramal in range(RAMAL_INICIAL, RAMAL_FINAL + 1):
        resposta = enviar_pacote_sip(ramal)

        if resposta:
            if ("200 ok" in resposta) or ("401 unauthorized" in resposta) or ("403 forbidden" in resposta):
                print(f"✅ Ramal encontrado: {ramal}")
                encontrados.append(ramal)
            else:
                print(f"❌ Ramal {ramal} não encontrado.")
        else:
            print(f"⚠️ Sem resposta do ramal {ramal}.")

    return encontrados

# Executar a enumeração
resultados = enumerar_ramais()

# Salvar no CSV
dataset_path = "results/enum_ramal_resultados.csv"
with open(dataset_path, mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["ramal"])
    for ramal in resultados:
        writer.writerow([ramal])

print(f"\n📂 Resultados salvos em {dataset_path}")
