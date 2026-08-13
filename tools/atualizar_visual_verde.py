#!/usr/bin/env python3
"""
Atualiza código (visual verde) SEM rodar consertar_bancada por padrão.

consertar_bancada altera ESP/armários de teste — use só quando armário sumiu
ou token ESP desalinhado. Para só atualizar telas:

  python tools/atualizar_visual_verde.py

Com consertar completo (bancada com problema):

  python tools/atualizar_visual_verde.py --com-consertar
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRANCH = "cursor/ui-eleva-verde-c05c"


def _iniciar_servidor():
    import os
    import time
    import urllib.error
    import urllib.request

    sys.path.insert(0, str(ROOT / "tools"))
    from env_bancada import env_subprocess, garantir_bancada_env

    garantir_bancada_env()
    env = env_subprocess()
    print("\n[Iniciar] app.py...")
    if sys.platform == "win32":
        cmd = (
            f'start "ELEVA LOCKER" cmd /k "cd /d {ROOT} && set ELEVA_BANCADA=1 && '
            f'set DATABASE_URL= && python app.py"'
        )
        subprocess.Popen(cmd, shell=True, cwd=ROOT)
    else:
        subprocess.Popen([sys.executable, "app.py"], cwd=ROOT, env=env)
    fim = time.time() + 30
    while time.time() < fim:
        try:
            urllib.request.urlopen("http://127.0.0.1:15000/totem/versao", timeout=3)
            print("    OK  servidor respondendo")
            return
        except urllib.error.URLError:
            time.sleep(2)
    print("    AVISO: rode tools\\iniciar_elevalocker.bat se o painel não abrir")


def run(cmd, check=True):
    show = cmd if isinstance(cmd, str) else " ".join(str(c) for c in cmd)
    print(f">>> {show}")
    return subprocess.run(cmd, cwd=ROOT, text=True, check=check)


def main():
    parser = argparse.ArgumentParser(description="Atualiza visual verde (git pull)")
    parser.add_argument(
        "--com-consertar",
        action="store_true",
        help="Também roda consertar_bancada (só se armário/ESP/token com problema)",
    )
    args = parser.parse_args()

    print("\n  ATUALIZAR VISUAL VERDE")
    print("  ======================\n")

    run([sys.executable, "tools/parar_servidor.py"])

    print("\n[Git] Buscando branch visual verde...")
    run(["git", "fetch", "origin", BRANCH])
    run(["git", "checkout", BRANCH])
    run(["git", "pull", "origin", BRANCH])

    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    atual = (branch.stdout or "").strip()
    print(f"\n    Branch ativa: {atual}")
    if atual != BRANCH:
        print(f"    ERRO: esperado {BRANCH}")
        return 1

    if args.com_consertar:
        print("\n[Consertar] SQLite + armário Matriz (modo completo)...")
        r = run([sys.executable, "tools/consertar_bancada.py"], check=False)
        if r.returncode != 0:
            print("\n  consertar_bancada falhou — veja acima.")
            return r.returncode
    else:
        print(
            "\n[OK] Pulando consertar_bancada (preserva vínculos de usuários)."
            "\n     Se armário sumiu ou ESP offline: rode tools\\consertar_bancada.bat"
        )
        _iniciar_servidor()

    print(
        """
  PRONTO — código atualizado

  Abra: http://192.168.16.130:15000/dashboard
  Ctrl+F5 no navegador

  Scripts de manutenção (usar só quando necessário):
    tools\\consertar_bancada.bat      — ESP/token/armário
    tools\\restaurar_usuarios_armario.bat — usuários sumiram do armário
"""
    )
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
