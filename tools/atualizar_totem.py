#!/usr/bin/env python3
"""Atualiza totem v2 no PC servidor — para o Docker antigo e valida arquivos."""

import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRANCH = "cursor/totem-seguro-c05c"
TOTEM_URL = "http://127.0.0.1:15000/totem/versao"


def run(cmd, **kwargs):
    print(f">>> {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    return subprocess.run(cmd, cwd=ROOT, text=True, **kwargs)


def parar_docker_web():
    print("\n--- Parando container Docker web (imagem antiga) ---")
    run(["docker", "stop", "elevalocker-web-1"], capture_output=True)


def git_atualizar():
    print(f"\n--- Git pull ({BRANCH}) ---")
    run(["git", "fetch", "origin", BRANCH], check=False)
    r = run(["git", "checkout", BRANCH], capture_output=True)
    if r.returncode != 0:
        print(r.stderr or r.stdout)
        return False
    r = run(["git", "pull", "origin", BRANCH], capture_output=True)
    print(r.stdout or r.stderr or "")
    return r.returncode == 0


def verificar_arquivos():
    print("\n--- Verificando templates/totem.html ---")
    r = run([sys.executable, "tools/verificar_totem.py"], capture_output=False)
    return r.returncode == 0


def checar_servidor():
    print(f"\n--- Servidor em execucao? ({TOTEM_URL}) ---")
    try:
        with urllib.request.urlopen(TOTEM_URL, timeout=3) as resp:
            body = resp.read().decode("utf-8", errors="replace")
        print(body)
        if '"ok": true' in body.replace(" ", ""):
            print("\nTotem v2 ATIVO no servidor.")
            return True
        print("\nServidor respondeu mas totem ainda e ANTIGO (provavel Docker ou app.py antigo).")
        return False
    except urllib.error.URLError:
        print("Nenhum servidor na porta 15000 — rode tools\\iniciar_tudo.bat")
        return False


def main():
    print("=" * 55)
    print("  ELEVA LOCKER — Atualizar totem v2")
    print("=" * 55)

    parar_docker_web()
    git_atualizar()
    verificar_arquivos()

    print("\n" + "=" * 55)
    print("  PROXIMO PASSO (obrigatorio)")
    print("=" * 55)
    print("1. Feche qualquer janela antiga com python app.py (Ctrl+C)")
    print("2. Rode:  tools\\iniciar_tudo.bat")
    print("3. Abra:   http://192.168.16.130:15000/totem/versao")
    print("   Deve mostrar: \"ok\": true")
    print("4. Totem:  http://192.168.16.130:15000/totem/3  (Ctrl+F5)")
    print()

    checar_servidor()
    return 0


if __name__ == "__main__":
    sys.exit(main())
