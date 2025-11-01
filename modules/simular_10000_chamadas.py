import subprocess
import time
import threading

# Configurações
total_chamadas = 10000
chamadas_por_lote = 100
espera_entre_lotes = 5  # segundos
ip_asterisk = "192.168.0.75"
ramal_origem = "1000"
senha_origem = "1234"
ramal_destino = "9999"
arquivo_audio = "/usr/src/pjproject/test_audio/audio.wav"

def fazer_chamada(contador):
    comando = [
        "pjsua",
        f"--id=sip:{ramal_origem}@{ip_asterisk}",
        f"--registrar=sip:{ip_asterisk}",
        "--realm=*",
        f"--username={ramal_origem}",
        f"--password={senha_origem}",
        f"--play-file={arquivo_audio}",
        f"sip:{ramal_destino}@{ip_asterisk}",
        "--auto-play",
        "--auto-answer=200",
        "--hangup-on-term",
        "--null-audio",  # não usa áudio de verdade para ser rápido
        "--duration=5"   # derruba a chamada em 5 segundos
    ]
    subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def rodar_simulacao():
    chamadas_realizadas = 0

    while chamadas_realizadas < total_chamadas:
        threads = []
        print(f"➡️ Iniciando lote: chamadas {chamadas_realizadas + 1} até {chamadas_realizadas + chamadas_por_lote}...")

        for _ in range(chamadas_por_lote):
            t = threading.Thread(target=fazer_chamada, args=(chamadas_realizadas,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        chamadas_realizadas += chamadas_por_lote
        print(f"✅ Lote finalizado. Total até agora: {chamadas_realizadas} chamadas.")
        time.sleep(espera_entre_lotes)

    print("🏁 Simulação finalizada: 10.000 chamadas realizadas!")

if __name__ == "__main__":
    rodar_simulacao()
