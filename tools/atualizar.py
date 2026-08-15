#!/usr/bin/env python3
"""Atualiza o ELEVA LOCKER do Git e reinicia o servidor automaticamente."""

import argparse
import platform
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOTEM_URL = "http://127.0.0.1:15000/totem/versao"
BRANCH_TOTEM = "cursor/fix-retirada-rele-c05c"

sys.path.insert(0, str(ROOT / "tools"))
from parar_servidor import parar_app_py, parar_docker_web, parar_porta  # noqa: E402


def run(cmd, check=False, capture=False):
    show = cmd if isinstance(cmd, str) else " ".join(cmd)
    print(f">>> {show}")
    try:
        return subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            check=check,
            capture_output=capture,
        )
    except FileNotFoundError:
        print("    ERRO: comando nao encontrado.")
        return subprocess.CompletedProcess(cmd, 127, "", "nao encontrado")


def parar_servidor():
    print("\n[1/5] Parando servidor...")
    parar_docker_web()
    parar_app_py()
    parar_porta()


def git_atualizar(branch=None):
    print("\n[2/5] Atualizando codigo (git pull)...")

    if not branch:
        branch = BRANCH_TOTEM
        r = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture=True)
        atual = (r.stdout or "").strip()
        if atual and atual != branch:
            print(f"    Branch atual: {atual} → mudando para {branch}")

    print(f"    Branch: {branch}")
    run(["git", "fetch", "origin", branch], capture=True)

    atual = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture=True)
    if (atual.stdout or "").strip() != branch:
        r = run(["git", "checkout", branch], capture=True)
        if r.returncode != 0:
            print(r.stderr or r.stdout or "Erro no checkout.")
            return False

    r = run(["git", "pull", "origin", branch], capture=True)
    saida = (r.stdout or "") + (r.stderr or "")
    if saida.strip():
        print(saida.strip())

    if r.returncode != 0:
        print("ERRO: git pull falhou.")
        return False

    r = run(["git", "log", "-1", "--oneline"], capture=True)
    if r.stdout.strip():
        print(f"    Commit: {r.stdout.strip()}")
    return True


def verificar_arquivos():
    print("\n[3/5] Verificando totem...")
    return run([sys.executable, "tools/verificar_totem.py"]).returncode == 0


def reiniciar_servidor():
    print("\n[4/5] Reiniciando servidor...")
    bat = ROOT / "tools" / "iniciar_tudo.bat"

    if platform.system() == "Windows":
        cmd = f'start "ELEVA LOCKER" cmd /k "cd /d {ROOT} && tools\\iniciar_tudo.bat"'
        subprocess.Popen(cmd, shell=True, cwd=ROOT)
        print("    Nova janela aberta com python app.py")
        return True

    run([sys.executable, "tools/iniciar_tudo.py"])
    subprocess.Popen([sys.executable, "app.py"], cwd=ROOT)
    print("    app.py iniciado em background")
    return True


def aguardar_totem_ok(segundos=90):
    print("\nAguardando servidor responder...")
    fim = time.time() + segundos
    while time.time() < fim:
        try:
            with urllib.request.urlopen(TOTEM_URL, timeout=3) as resp:
                body = resp.read().decode("utf-8", errors="replace")
            print(f"    {TOTEM_URL}")
            print(f"    {body}")
            if '"ok":true' in body.replace(" ", "") or '"ok": true' in body:
                return True
            print("    Servidor respondeu, mas totem ainda e versao antiga.")
            return False
        except urllib.error.URLError:
            time.sleep(3)
    print("    Timeout — servidor nao respondeu a tempo.")
    return False


def main():
    parser = argparse.ArgumentParser(description="Atualiza ELEVA LOCKER do Git e reinicia.")
    parser.add_argument("--branch", help="Branch para pull (padrao: branch atual)")
    parser.add_argument("--no-restart", action="store_true", help="So atualiza, nao reinicia")
    args = parser.parse_args()

    print("=" * 55)
    print("  ELEVA LOCKER — Atualizar automatico")
    print("=" * 55)
    print(f"  Pasta: {ROOT}")
    print()

    parar_servidor()

    if not git_atualizar(args.branch):
        return 1

    verificar_arquivos()

    if args.no_restart:
        print("\nAtualizacao concluida (--no-restart).")
        print("Reinicie manualmente: tools\\iniciar_tudo.bat")
        return 0

    reiniciar_servidor()

    if aguardar_totem_ok():
        print("\n[5/5] Confirmando totem v2...")
        print("\n" + "=" * 55)
        print("  SUCESSO — Totem v2 ativo!")
        print("=" * 55)
        print("  Totem:  http://192.168.16.130:15000/totem/3")
        print("  Versao: http://192.168.16.130:15000/totem/versao")
        return 0

    print("\n" + "=" * 55)
    print("  ATENCAO — Verifique a janela do servidor")
    print("=" * 55)
    print("  Se abriu nova janela CMD, aguarde Docker subir e tente:")
    print("  http://192.168.16.130:15000/totem/versao")
    return 1


if __name__ == "__main__":
    sys.exit(main())
