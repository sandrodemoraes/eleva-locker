#!/usr/bin/env python3
"""Para o servidor ELEVA LOCKER (Docker web + python app.py na porta 15000)."""

import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORTA = 15000


def run(cmd, capture=True):
    show = " ".join(cmd) if isinstance(cmd, list) else cmd
    print(f">>> {show}")
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=capture)


def parar_docker_web():
    print("Parando container Docker web...")
    run(["docker", "stop", "elevalocker-web-1"])


def parar_app_py():
    print("Parando python app.py...")
    sistema = platform.system()

    if sistema == "Windows":
        r = run([
            "wmic", "process", "where",
            "CommandLine like '%app.py%'",
            "get", "ProcessId",
        ])
        pids = [ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip().isdigit()]
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


def parar_porta(porta=PORTA):
    print(f"Liberando porta {porta}...")
    sistema = platform.system()

    if sistema == "Windows":
        r = run(["netstat", "-ano"])
        pids = set()
        for linha in (r.stdout or "").splitlines():
            if f":{porta}" in linha and "LISTENING" in linha.upper():
                pid = linha.split()[-1]
                if pid.isdigit():
                    pids.add(pid)
        for pid in pids:
            print(f"    Encerrando PID {pid} na porta {porta}")
            run(["taskkill", "/F", "/PID", pid])
        if not pids:
            print(f"    Porta {porta} livre.")
        return

    for cmd in (["fuser", "-k", f"{porta}/tcp"],):
        try:
            run(cmd)
        except FileNotFoundError:
            pass


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
