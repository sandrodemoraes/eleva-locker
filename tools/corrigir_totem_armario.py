#!/usr/bin/env python3
"""
Corrige totem: cria armário Matriz no banco e grava TOTEM_ARMARIO_ID no .env.

Uso:
  python tools/corrigir_totem_armario.py
  python tools/corrigir_totem_armario.py --ip-esp 192.168.16.162
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

NOME_ARMARIO = "ELEVA Locker Matriz"
ENV_PATH = ROOT / ".env"


def run_setup(ip_esp):
    return subprocess.run(
        [sys.executable, "tools/setup_oficial.py", "--ip-esp", ip_esp, "--portas", "8"],
        cwd=ROOT,
    ).returncode == 0


def obter_id_matriz():
    from database import criar_banco

    criar_banco()
    from repositories.base_repository import BaseRepository

    with BaseRepository.get_connection() as conn:
        row = conn.execute(
            "SELECT id, nome FROM armarios WHERE nome = ? LIMIT 1",
            (NOME_ARMARIO,),
        ).fetchone()
    return dict(row) if row else None


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
    args = parser.parse_args()

    print("=" * 60)
    print("  CORRIGIR TOTEM — armário + .env")
    print("=" * 60)

    arm = obter_id_matriz()
    if not arm and not args.sem_setup:
        print(f"\nArmário '{NOME_ARMARIO}' não encontrado — rodando setup_oficial...")
        if not run_setup(args.ip_esp):
            print("ERRO: setup_oficial falhou")
            return 1
        arm = obter_id_matriz()

    if not arm:
        print(f"\nERRO: armário '{NOME_ARMARIO}' não existe no banco.")
        print("Rode: python tools/setup_oficial.py --ip-esp 192.168.16.162 --portas 8")
        return 1

    env_path = atualizar_env(arm["id"])
    print(f"\n  Armário: {arm['nome']} (id={arm['id']})")
    print(f"  .env:    TOTEM_ARMARIO_ID={arm['id']}")
    print(f"  Arquivo: {env_path}")

    print("\n" + "=" * 60)
    print("  REINICIE o servidor: python app.py")
    print("=" * 60)
    print(f"\n  Totem: http://192.168.16.130:15000/totem/{arm['id']}")
    print(f"        http://localhost:15000/totem/{arm['id']}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
