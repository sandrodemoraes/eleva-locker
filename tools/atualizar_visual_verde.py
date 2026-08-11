#!/usr/bin/env python3
"""
Atualiza para visual verde (branch ui-eleva-verde) + conserta bancada SQLite.

Uso:
  python tools/atualizar_visual_verde.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRANCH = "cursor/ui-eleva-verde-c05c"


def run(cmd, check=True):
    show = cmd if isinstance(cmd, str) else " ".join(str(c) for c in cmd)
    print(f">>> {show}")
    return subprocess.run(cmd, cwd=ROOT, text=True, check=check)


def main():
    print("\n  ATUALIZAR VISUAL VERDE + BANCADA")
    print("  =================================\n")

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

    print("\n[Consertar] SQLite + armario Matriz...")
    r = run([sys.executable, "tools/consertar_bancada.py"], check=False)
    if r.returncode != 0:
        print("\n  consertar_bancada falhou — veja acima.")
        return r.returncode

    print(
        """
  PRONTO — visual VERDE + bancada SQLite

  Abra: http://192.168.16.130:15000/dashboard
  Ctrl+F5 no navegador

  Deve aparecer:
    - Sidebar VERDE (nao azul)
    - ELEVA LOCKER em maiusculas
    - 1 armario, 8 compartimentos
"""
    )
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
