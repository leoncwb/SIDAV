# main.py
import argparse
from modules import (
    enum_ramal_sipvicious,
    brute_force_sipvicious,
    flood_sip_socket,
    hijack_register_multiple,
    spoof_invite_scapy,
    gerar_chamadas_real,
    isolation_forest_voip
)

def main():
    parser = argparse.ArgumentParser(description="VoIP Pentest Tool")
    parser.add_argument("ataque", help="Tipo de ataque a executar", choices=[
        "enum", "brute", "flood", "hijack", "spoof", "chamadas", "isolation"
    ])
    args = parser.parse_args()

    if args.ataque == "enum":
        enum_ramal_sipvicious.run()
    elif args.ataque == "brute":
        brute_force_sipvicious.run()
    elif args.ataque == "flood":
        flood_sip_socket.run()
    elif args.ataque == "hijack":
        hijack_register_multiple.run()
    elif args.ataque == "spoof":
        spoof_invite_scapy.run()
    elif args.ataque == "chamadas":
        gerar_chamadas_real.run()
    elif args.ataque == "isolation":
        isolation_forest_voip.run()
    else:
        print("Ataque desconhecido")

if __name__ == "__main__":
    main()
