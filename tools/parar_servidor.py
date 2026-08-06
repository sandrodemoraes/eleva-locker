#!/usr/bin/env python3
"""Para o servidor ELEVA LOCKER (Docker web + python app.py na porta 15000)."""

import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORTA = 15000


def run(cmd, capture=True, shell=False):
    show = cmd if isinstance(cmd, str) else " ".join(cmd)
    print(f">>> {show}")
    try:
        return subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            capture_output=capture,
            shell=shell,
        )
    except FileNotFoundError:
        print("    AVISO: comando nao encontrado — ignorando.")
        return subprocess.CompletedProcess(cmd, 127, "", "nao encontrado")


def parar_docker_web():
    print("Parando container Docker web (totem antigo)...")
    if platform.system() == "Windows":
        run("docker update --restart=no elevalocker-web-1 2>nul", shell=True)
        run("docker stop elevalocker-web-1 2>nul", shell=True)
        run("docker rm -f elevalocker-web-1 2>nul", shell=True)
        run("docker compose stop web 2>nul", shell=True)
        run("docker compose --profile legacy-docker stop web 2>nul", shell=True)
        return
    docker = shutil.which("docker")
    if docker:
        run([docker, "update", "--restart=no", "elevalocker-web-1"])
        run([docker, "stop", "elevalocker-web-1"])
        run([docker, "rm", "-f", "elevalocker-web-1"])
        run([docker, "compose", "stop", "web"])
        run([docker, "compose", "--profile", "legacy-docker", "stop", "web"])
    else:
        print("    Docker nao instalado ou fora do PATH.")


def _pids_app_py_windows():
    ps = (
        "Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | "
        "Where-Object { $_.CommandLine -like '*app.py*' } | "
        "Select-Object -ExpandProperty ProcessId"
    )
    r = run(["powershell", "-NoProfile", "-Command", ps])
    if r.returncode != 0 and not (r.stdout or "").strip():
        # Fallback legado (Windows antigo)
        r = run("wmic process where \"CommandLine like '%%app.py%%'\" get ProcessId", shell=True)
    return [ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip().isdigit()]


def parar_app_py():
    print("Parando python app.py...")
    sistema = platform.system()

    if sistema == "Windows":
        pids = _pids_app_py_windows()
        for pid in pids:
            print(f"    Encerrando app.py PID {pid}")
            run(["taskkill", "/F", "/PID", pid])
        if not pids:
            print("    Nenhum app.py em execucao.")
        return

    r = run(["pgrep", "-f", "app.py"])
    if r.returncode == 0 and r.stdout:
        for pid in r.stdout.split():
            print(f"    Encerrando app.py PID {pid}")
            run(["kill", "-9", pid])
    else:
        print("    Nenhum app.py em execucao.")


def parar_porta(porta=PORTA):
    print(f"Liberando porta {porta}...")
    sistema = platform.system()

    if sistema == "Windows":
        r = run(["netstat", "-ano"])
        pids = set()
        for linha in (r.stdout or "").splitlines():
            if f":{porta}" in linha and "LISTENING" in linha.upper():
                pid = linha.split()[-1]
                if pid.isdigit() and int(pid) > 0:
                    pids.add(pid)
        for pid in pids:
            print(f"    Encerrando PID {pid} na porta {porta}")
            run(["taskkill", "/F", "/PID", pid])
        if not pids:
            print(f"    Porta {porta} livre.")
        return

    if shutil.which("fuser"):
        run(["fuser", "-k", f"{porta}/tcp"])
    else:
        print(f"    fuser nao disponivel — use parar_app_py.")


def parar_servidor():
    print("=" * 50)
    print("  ELEVA LOCKER — Parar servidor")
    print("=" * 50)
    print()
    parar_docker_web()
    parar_app_py()
    parar_porta()
    print()
    print("Servidor parado. WhatsApp Docker continua rodando.")
    print("Para subir de novo: tools\\iniciar_tudo.bat")
    print()


def main():
    parar_servidor()
    return 0


if __name__ == "__main__":
    sys.exit(main())
