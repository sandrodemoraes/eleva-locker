#!/usr/bin/env python3
"""
Corrige totem: cria armário Matriz no banco e grava TOTEM_ARMARIO_ID no .env.

Também alinha site_id do armário e avisa se .env usa Postgres (bancada = SQLite).

Uso:
  python tools/corrigir_totem_armario.py
  python tools/corrigir_totem_armario.py --ip-esp 192.168.16.162
  python tools/corrigir_totem_armario.py --fix-sqlite
"""
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SKIP_BACKUP", "1")
from env_bancada import aplicar_bancada_processo, garantir_bancada_env

aplicar_bancada_processo()

NOME_ARMARIO = "ELEVA Locker Matriz"
ENV_PATH = ROOT / ".env"


def mostrar_banco():
    import config
    from db.connection import get_engine

    engine = get_engine()
    if engine == "postgresql":
        dest = config.DATABASE_URL.split("@")[-1] if config.DATABASE_URL else "?"
        print(f"\n  Banco ativo: PostgreSQL ({dest})")
        print("  !!  Na bancada use SQLite — remova DATABASE_URL= do .env")
        return "postgresql"
    db = ROOT / "database" / "elevalocker.db"
    print(f"\n  Banco ativo: SQLite ({db})")
    return "sqlite"


def remover_database_url_env():
    if not ENV_PATH.exists():
        return False
    linhas = []
    removido = False
    for linha in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if re.match(r"^\s*DATABASE_URL\s*=", linha) and not linha.strip().startswith("#"):
            linhas.append("# " + linha + "  # desativado — bancada usa SQLite")
            removido = True
        else:
            linhas.append(linha)
    if removido:
        ENV_PATH.write_text("\n".join(linhas).rstrip() + "\n", encoding="utf-8")
        print("  OK  DATABASE_URL comentado no .env")
        # Recarregar config
        if "config" in sys.modules:
            del sys.modules["config"]
    return removido


def run_setup(ip_esp):
    return subprocess.run(
        [sys.executable, "tools/setup_oficial.py", "--ip-esp", ip_esp, "--portas", "8"],
        cwd=ROOT,
    ).returncode == 0


def alinhar_site_armario():
    from database import criar_banco

    criar_banco()
    from repositories.base_repository import BaseRepository

    with BaseRepository.get_connection() as conn:
        site = conn.execute("""
            SELECT id FROM sites
            WHERE codigo = 'matriz' OR nome LIKE '%Matriz%'
            ORDER BY id LIMIT 1
        """).fetchone()
        if not site:
            site = conn.execute("SELECT id FROM sites ORDER BY id LIMIT 1").fetchone()
        if not site:
            return None
        conn.execute(
            "UPDATE armarios SET site_id = ? WHERE nome = ?",
            (site["id"], NOME_ARMARIO),
        )
        conn.commit()
        arm = conn.execute(
            "SELECT id, nome, site_id FROM armarios WHERE nome = ? LIMIT 1",
            (NOME_ARMARIO,),
        ).fetchone()
    return dict(arm) if arm else None


def obter_id_matriz():
    from database import criar_banco

    criar_banco()
    from repositories.base_repository import BaseRepository

    with BaseRepository.get_connection() as conn:
        row = conn.execute(
            "SELECT id, nome, site_id FROM armarios WHERE nome = ? LIMIT 1",
            (NOME_ARMARIO,),
        ).fetchone()
    return dict(row) if row else None


def contar_armarios_site(site_id):
    from repositories.base_repository import BaseRepository

    with BaseRepository.get_connection() as conn:
        return conn.execute(
            "SELECT COUNT(*) AS n FROM armarios WHERE site_id = ?",
            (site_id,),
        ).fetchone()["n"]


def atualizar_env(armario_id):
    chave = "TOTEM_ARMARIO_ID"
    valor = str(armario_id)
    linhas = []
    achou = False

    if ENV_PATH.exists():
        texto = ENV_PATH.read_text(encoding="utf-8")
        for linha in texto.splitlines():
            if re.match(rf"^\s*{re.escape(chave)}\s*=", linha):
                linhas.append(f"{chave}={valor}")
                achou = True
            else:
                linhas.append(linha)
    else:
        linhas = ["# ELEVA LOCKER — .env"]

    if not achou:
        if linhas and linhas[-1].strip():
            linhas.append("")
        linhas.append(f"{chave}={valor}")

    ENV_PATH.write_text("\n".join(linhas).rstrip() + "\n", encoding="utf-8")
    return ENV_PATH


def main():
    parser = argparse.ArgumentParser(description="Corrige TOTEM_ARMARIO_ID + armário Matriz")
    parser.add_argument("--ip-esp", default="192.168.16.162")
    parser.add_argument("--sem-setup", action="store_true", help="Só ajusta .env se armário já existe")
    parser.add_argument(
        "--fix-sqlite", action="store_true",
        help="Comenta DATABASE_URL no .env (bancada usa SQLite)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  CORRIGIR TOTEM — armário + .env + banco")
    print("=" * 60)

    garantir_bancada_env()

    engine = mostrar_banco()

    arm = obter_id_matriz()
    if not arm and not args.sem_setup:
        print(f"\nArmário '{NOME_ARMARIO}' não encontrado — rodando setup_oficial...")
        if not run_setup(args.ip_esp):
            print("ERRO: setup_oficial falhou")
            return 1
        arm = alinhar_site_armario() or obter_id_matriz()
    elif arm:
        arm = alinhar_site_armario() or arm

    if not arm:
        print(f"\nERRO: armário '{NOME_ARMARIO}' não existe no banco.")
        if engine == "postgresql":
            print("  Provável causa: scripts gravaram SQLite, painel lê Postgres.")
            print("  Rode: python tools/corrigir_totem_armario.py --fix-sqlite")
        print("  Ou: python tools/setup_oficial.py --ip-esp 192.168.16.162 --portas 8")
        return 1

    env_path = atualizar_env(arm["id"])
    n_site = contar_armarios_site(arm.get("site_id"))

    print(f"\n  Armário: {arm['nome']} (id={arm['id']}, site_id={arm.get('site_id')})")
    print(f"  .env:    TOTEM_ARMARIO_ID={arm['id']}")
    print(f"  Arquivo: {env_path}")
    print(f"  Painel (site filtrado): {n_site} armário(s) visível(is)")

    if engine == "postgresql":
        print("\n  !!  Ainda em PostgreSQL — dashboard pode mostrar 0 armários.")
        print("      Rode: tools\\corrigir_totem_armario.bat --fix-sqlite")

    print("\n" + "=" * 60)
    print("  REINICIE o servidor: python app.py")
    print("=" * 60)
    print(f"\n  Totem: http://192.168.16.130:15000/totem/{arm['id']}")
    print(f"  Painel: http://192.168.16.130:15000/armarios")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
