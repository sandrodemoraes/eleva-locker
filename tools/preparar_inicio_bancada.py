#!/usr/bin/env python3
"""
Prepara bancada antes de subir app.py (Iniciar do Windows).

- Garante ELEVA_BANCADA=1 e SQLite no .env
- Corrige armarios.site_id NULL (0 armarios no filtro Matriz)
- Avisa se 0 armarios no banco

Uso: python tools/preparar_inicio_bancada.py
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from env_bancada import aplicar_bancada_processo, garantir_bancada_env

aplicar_bancada_processo()
os.environ.setdefault("SKIP_BACKUP", "1")


def main():
    print("[bancada] Preparando inicio...")
    garantir_bancada_env()

    from database import criar_banco
    criar_banco()

    from repositories.base_repository import BaseRepository
    from db.connection import get_engine

    engine = get_engine()
    print(f"  Banco: {engine}")

    with BaseRepository.get_connection() as conn:
        n_site = conn.execute(
            "UPDATE armarios SET site_id = 1 WHERE site_id IS NULL"
        ).rowcount
        if n_site:
            conn.commit()
            print(f"  site_id corrigido em {n_site} armario(s)")

        n_arm = conn.execute("SELECT COUNT(*) AS n FROM armarios").fetchone()["n"]
        n_esp = conn.execute("SELECT COUNT(*) AS n FROM esp32").fetchone()["n"]

    print(f"  Armarios: {n_arm} | ESP: {n_esp}")

    if engine != "sqlite":
        print("  ERRO: nao esta em SQLite — rode tools\\consertar_bancada.bat")
        return 1

    if n_arm == 0:
        print("  AVISO: 0 armarios — apos entrar rode tools\\consertar_bancada.bat")
        return 2

    # Aviso branch (nao bloqueia)
    try:
        import subprocess
        r = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=5,
        )
        branch = (r.stdout or "").strip()
        if branch and branch not in ("cursor/ui-eleva-verde-c05c", "main"):
            print(f"  Branch: {branch} (visual verde: cursor/ui-eleva-verde-c05c)")
        elif branch:
            print(f"  Branch: {branch}")
    except Exception:
        pass

    print("  OK — bancada pronta")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
