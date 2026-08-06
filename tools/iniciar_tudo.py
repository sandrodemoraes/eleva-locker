#!/usr/bin/env python3
"""Sobe Docker (Evolution WhatsApp) após reboot — use via tools/iniciar_tudo.bat."""

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVICOS_WHATSAPP = ("evolution-api", "evolution-postgres", "evolution-redis")
DOCKER_TIMEOUT = 180


def run(cmd, check=False):
    try:
        return subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
            shell=isinstance(cmd, str),
            check=check,
        )
    except FileNotFoundError:
        r = subprocess.CompletedProcess(cmd, 127, "", "comando nao encontrado")
        return r


def docker_ok():
    r = run(["docker", "info"])
    return r.returncode == 0


def aguardar_docker():
    print("Aguardando Docker Desktop...")
    for i in range(DOCKER_TIMEOUT // 3):
        if docker_ok():
            print("Docker OK.")
            return True
        time.sleep(3)
        if i % 5 == 4:
            print("  ... ainda aguardando (abra o Docker Desktop se estiver fechado)")
    print("ERRO: Docker nao respondeu a tempo.")
    print("Abra o Docker Desktop manualmente e rode tools\\iniciar_tudo.bat de novo.")
    return False


def parar_web_docker():
    """Evita conflito na porta 15000 — app roda com python app.py."""
    run(["docker", "stop", "elevalocker-web-1"])
    run(["docker", "rm", "-f", "elevalocker-web-1"])
    run(["docker", "compose", "stop", "web"])
    run(["docker", "compose", "--profile", "legacy-docker", "stop", "web"])


def subir_whatsapp():
    print()
    print("Subindo Evolution API (WhatsApp)...")
    cmd = [
        "docker",
        "compose",
        "--profile",
        "whatsapp",
        "up",
        "-d",
        *SERVICOS_WHATSAPP,
    ]
    r = run(cmd)
    if r.returncode != 0:
        print(r.stderr or r.stdout or "Falha ao subir containers.")
        return False
    print("Containers WhatsApp iniciados.")
    return True


def mostrar_status():
    print()
    print("=== Status Docker ===")
    r = run(["docker", "compose", "ps"])
    print(r.stdout or r.stderr or "(sem saida)")


def verificar_env():
    env = ROOT / ".env"
    if not env.exists():
        print()
        print("AVISO: .env nao encontrado. Rode tools\\criar_env_producao.bat antes.")
        return False
    return True


def main():
    print("=" * 50)
    print("  ELEVA LOCKER — Iniciar servicos")
    print("=" * 50)
    print()

    verificar_env()

    if not aguardar_docker():
        return 1

    parar_web_docker()

    if not subir_whatsapp():
        return 1

    mostrar_status()

    print()
    print("Proximo: esta janela vai iniciar python app.py")
    print("  Painel:  http://192.168.16.130:15000")
    print("  Manager: http://192.168.16.130:8080/manager")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
