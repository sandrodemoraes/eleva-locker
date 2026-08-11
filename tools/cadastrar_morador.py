#!/usr/bin/env python3
"""
Cadastra morador (perfil Usuário) para autocomplete do totem.

Uso:
  python tools/cadastrar_morador.py --nome "Karen Silva" --telefone 48999123456
  python tools/cadastrar_morador.py --nome "Karla" --telefone 48999887766 --email karla@morador.local
"""
import argparse
import os
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

from env_bancada import aplicar_bancada_processo

aplicar_bancada_processo()

NOME_ARMARIO = "ELEVA Locker Matriz"


def slug_email(nome):
    base = unicodedata.normalize("NFKD", nome)
    base = base.encode("ascii", "ignore").decode("ascii").lower()
    base = re.sub(r"[^a-z0-9]+", ".", base).strip(".") or "morador"
    return f"{base}@morador.local"


def obter_armario_id():
    from database import criar_banco
    criar_banco()
    from repositories.base_repository import BaseRepository
    with BaseRepository.get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM armarios WHERE nome = ? LIMIT 1",
            (NOME_ARMARIO,),
        ).fetchone()
        if row:
            return row["id"]
        row = conn.execute("SELECT id FROM armarios ORDER BY id LIMIT 1").fetchone()
        return row["id"] if row else None


def main():
    parser = argparse.ArgumentParser(description="Cadastra morador para totem")
    parser.add_argument("--nome", required=True)
    parser.add_argument("--telefone", required=True)
    parser.add_argument("--email", help="Opcional — gera @morador.local se omitido")
    args = parser.parse_args()

    os.environ.setdefault("SKIP_BACKUP", "1")
    from database import criar_banco
    criar_banco()
    from services.usuario_service import UsuarioService

    armario_id = obter_armario_id()
    if not armario_id:
        print("ERRO: cadastre o armário Matriz primeiro (setup_oficial.py)")
        return 1

    email = (args.email or slug_email(args.nome)).strip().lower()
    senha = "morador2026"

    try:
        uid = UsuarioService.criar(
            nome=args.nome.strip(),
            email=email,
            telefone=args.telefone.strip(),
            senha=senha,
            confirmar=senha,
            perfil="Usuário",
            status=1,
            armario_id=armario_id,
        )
    except ValueError as e:
        print(f"ERRO: {e}")
        return 1

    print("=" * 50)
    print("  MORADOR CADASTRADO")
    print("=" * 50)
    print(f"  id={uid} | {args.nome}")
    print(f"  telefone: {args.telefone}")
    print(f"  email:    {email}")
    print(f"  armário:  {NOME_ARMARIO} (id={armario_id})")
    print(f"\n  Totem: http://192.168.16.130:15000/totem/{armario_id}")
    print("  Digite o nome no depósito — autocomplete deve aparecer.")
    print("=" * 50)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
