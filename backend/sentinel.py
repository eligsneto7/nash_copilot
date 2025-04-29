# nash/sentinel.py <-- Lembre-se que este arquivo está em backend/sentinel.py
import subprocess, time, signal, os, sys

# <<< MODIFICADO >>> Usar Gunicorn para rodar a aplicação Flask (nash_app:app)
# Gunicorn precisa saber onde encontrar o arquivo (backend/nash_app.py) e o objeto Flask (app)
# O Railway define a variável $PORT, que o Gunicorn usará.
APP_CMD = ["gunicorn", "--bind", "0.0.0.0:$PORT", "backend.nash_app:app"]

def launch():
    # Passar as variáveis de ambiente do sentinel para o processo filho (gunicorn)
    # Isso garante que Gunicorn e Flask tenham acesso a $PORT, API keys, etc.
    env = os.environ.copy()
    print(f"[SENTINEL] Launching app with command: {' '.join(APP_CMD)}")
    # Adiciona PWD ao log para debug de caminho, se necessário
    print(f"[SENTINEL] Current Working Directory: {os.getcwd()}")
    return subprocess.Popen(APP_CMD, env=env) # Passa o ambiente

def main():
    proc = None # Inicializa proc fora do loop
    while True:
        try:
            proc = launch()
            print(f"[SENTINEL] Spawned app process with pid {proc.pid}")
            while True:
                time.sleep(10)                     # health-check interval
                return_code = proc.poll()
                if return_code is not None:        # app morreu
                    print(f"[SENTINEL] App process (PID: {proc.pid}) exited with code {return_code}")
                    break                          # sai do inner loop → relança
        except Exception as e:
            print(f"[SENTINEL] Error launching or monitoring app process: {e}")
            # Se houve erro ao lançar, espera antes de tentar de novo
            if proc and proc.poll() is None:
                 print(f"[SENTINEL] Terminating potentially running app process (PID: {proc.pid}) due to error.")
                 proc.terminate() # Tenta terminar graciosamente
                 try:
                     proc.wait(timeout=5) # Espera um pouco
                 except subprocess.TimeoutExpired:
                     print(f"[SENTINEL] App process (PID: {proc.pid}) did not terminate, killing.")
                     proc.kill() # Força terminação
        # Cooldown antes de restart, independentemente se saiu por erro ou término normal
        print("[SENTINEL] Cooling down for 5 seconds before potential restart...")
        time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[SENTINEL] Received KeyboardInterrupt, exiting.")
        # Tenta garantir que o processo filho seja terminado ao sair
        # Esta parte pode não funcionar perfeitamente dependendo de como o Railway envia sinais
        # Mas é uma boa prática tentar.
        if 'proc' in locals() and proc and proc.poll() is None:
             print(f"[SENTINEL] Terminating app process (PID: {proc.pid}) on exit.")
             proc.terminate()
             try:
                 proc.wait(timeout=2)
             except subprocess.TimeoutExpired:
                 proc.kill()
        sys.exit(0)
    except Exception as e:
         print(f"[SENTINEL] Unhandled exception in main loop: {e}")
         # Tenta limpar se possível
         if 'proc' in locals() and proc and proc.poll() is None:
              proc.kill()
         sys.exit(1) # Sai com erro