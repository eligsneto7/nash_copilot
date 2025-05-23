# backend/sentinel.py
import subprocess, time, signal, os, sys

# <<< MODIFICADO >>> Adicionar ajuste de PYTHONPATH

def launch():
    env = os.environ.copy()
    cwd = os.getcwd()

    python_path = env.get('PYTHONPATH', '')
    if cwd not in python_path.split(os.pathsep):
        env['PYTHONPATH'] = f"{cwd}{os.pathsep}{python_path}" if python_path else cwd
        print(f"[SENTINEL] Adjusted PYTHONPATH: {env['PYTHONPATH']}")
    else:
        print(f"[SENTINEL] PYTHONPATH already contains CWD: {python_path}")

    port = env.get("PORT", "8080")
    if not port.isdigit():
        print(f"[SENTINEL] WARNING: PORT environment variable ('{port}') is not a valid number. Falling back to 8080.")
        port = "8080"

    app_module = "backend.nash_app:app"
    bind_address = f"0.0.0.0:{port}"
    # <<< MODIFICADO >>> Aumentar timeout para 300 segundos (5 minutos)
    gunicorn_timeout = "300"
    APP_CMD = ["gunicorn", "--bind", bind_address, "--timeout", gunicorn_timeout, app_module]

    print(f"[SENTINEL] Launching app with command: {' '.join(APP_CMD)}")
    print(f"[SENTINEL] Current Working Directory: {cwd}")

    return subprocess.Popen(APP_CMD, env=env)

# O restante do arquivo (main, __main__) permanece o mesmo da versão anterior...

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