# nash/sentinel.py
import subprocess, time, signal, os, sys

APP_CMD = ["python", "-m", "nash.app"]

def launch():
    return subprocess.Popen(APP_CMD)

def main():
    while True:
        proc = launch()
        print(f"[SENTINEL] Spawned app with pid {proc.pid}")
        while True:
            time.sleep(10)                     # health-check interval
            if proc.poll() is not None:        # app morreu
                print(f"[SENTINEL] App exited with code {proc.returncode}")
                break                          # sai do inner loop → relança
        time.sleep(5)                          # cooldown antes de restart

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)