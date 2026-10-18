#!/usr/bin/env python3
"""Cadastra morador no armário — 1 comando, sem modal nem checkbox."""

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SKIP_BACKUP", "1")

from services.usuario_service import UsuarioService  # noqa: E402


def main():
    parser = argparse.ArgumentParser(
        description="Cadastra morador (Usuário) vinculado a um armário — uso admin/síndico.",
    )
    parser.add_argument("--nome", required=True, help="Nome completo do morador")
    parser.add_argument("--telefone", required=True, help="Celular com DDD, ex: 48996757335")
    parser.add_argument("--armario", type=int, default=2, help="ID do armário (padrão: 2 Matriz)")
    parser.add_argument("--email", help="Opcional — se omitir, gera morador.TEL@eleva.local")
    args = parser.parse_args()

    print()
    print("=" * 60)
    print("  CADASTRAR MORADOR — ELEVA LOCKER")
    print("=" * 60)

    try:
        usuario_id = UsuarioService.criar_morador_armario(
            nome=args.nome,
            telefone=args.telefone,
            armario_id=args.armario,
            email=args.email,
        )
    except ValueError as erro:
        print(f"  ERRO: {erro}")
        print("=" * 60)
        return 1

    print(f"  OK      Usuário #{usuario_id} cadastrado no armário #{args.armario}")
    print(f"  Nome:    {args.nome}")
    print(f"  Tel:     {args.telefone}")
    print()
    print("  No totem: depósito → buscar morador pelo nome na lista.")
    print("=" * 60)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
