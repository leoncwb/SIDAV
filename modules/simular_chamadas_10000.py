import subprocess
import time

# Configuração dos parâmetros do pjsua
pjsua_command = [
    "pjsua",
    "--id", "sip:1000@192.168.0.75",
    "--registrar", "sip:192.168.0.75",
    "--realm", "*",
    "--username", "1000",
    "--password", "1234",
    "--play-file", "/usr/src/pjproject/test_audio/audio.wav",
    "--auto-play",
    "--auto-answer", "200",
    "--null-audio"
]

# Inicia o pjsua como subprocesso
print("🚀 Iniciando pjsua...")
process = subprocess.Popen(
    pjsua_command,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

# Espera o pjsua iniciar corretamente
time.sleep(5)

# Manda os comandos 'm sip:9999@192.168.0.75'
try:
    for i in range(1, 10001):
        print(f"➡️ Disparando chamada {i}/10000")
        process.stdin.write(f"m sip:9999@192.168.0.75\n")
        process.stdin.flush()
        time.sleep(0.5)  # meio segundo entre chamadas para o Asterisk aguentar

except KeyboardInterrupt:
    print("⛔ Interrompido manualmente.")

finally:
    print("⏹ Encerrando pjsua...")
    process.stdin.write("q\n")  # envia comando para sair do pjsua
    process.stdin.flush()
    process.stdin.close()
    process.terminate()
