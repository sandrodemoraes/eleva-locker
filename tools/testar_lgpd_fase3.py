#!/usr/bin/env python3
"""Testa LGPD Fase 3 — migração, export e anonimização."""

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import config  # noqa: E402
from app import app  # noqa: E402
from database import criar_banco  # noqa: E402
from repositories.base_repository import BaseRepository  # noqa: E402
from repositories.usuario_repository import UsuarioRepository  # noqa: E402
from services.lgpd_titular_service import LgpdTitularService  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402


def _tabela_existe(nome):
    with BaseRepository.get_connection() as conn:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (nome,),
        ).fetchone()
        return row is not None


def _coluna_existe(tabela, coluna):
    with BaseRepository.get_connection() as conn:
        rows = conn.execute(f"PRAGMA table_info({tabela})").fetchall()
        return any(r["name"] == coluna for r in rows)


def main():
    print()
    print("=" * 60)
    print("  TESTE LGPD FASE 3")
    print("=" * 60)

    falhas = 0
    criar_banco()

    checks = [
        ("Tabela lgpd_solicitacoes", _tabela_existe("lgpd_solicitacoes")),
        ("Coluna usuarios.lgpd_anonimizado_em", _coluna_existe("usuarios", "lgpd_anonimizado_em")),
        ("Coluna usuarios.marketing_opt_out", _coluna_existe("usuarios", "marketing_opt_out")),
        ("Coluna encomendas.lgpd_anonimizado_em", _coluna_existe("encomendas", "lgpd_anonimizado_em")),
    ]

    for nome, ok in checks:
        if ok:
            print(f"  OK     {nome}")
        else:
            falhas += 1
            print(f"  FALHA  {nome}")

    if config.LGPD_TITULAR_ATIVO:
        print("  OK     Flag LGPD_TITULAR_ATIVO ligada")
    else:
        print("  OK     Flag LGPD_TITULAR_ATIVO off (padrão)")

    c = app.test_client()
    r = c.get("/lgpd/admin/titular")
    if config.LGPD_TITULAR_ATIVO:
        if r.status_code not in (200, 302):
            falhas += 1
            print(f"  FALHA  Rota admin HTTP {r.status_code}")
        else:
            print("  OK     Rota admin titular acessível (auth redirect ok)")
    elif r.status_code not in (404, 302):
        falhas += 1
        print(f"  FALHA  Rota admin deveria 404/302 com flag off (got {r.status_code})")
    else:
        print("  OK     Rota admin oculta com flag off")

    email_teste = f"lgpd_teste_fase3_{int(time.time())}@elevalocker.local"
    uid = UsuarioRepository.criar(
        "LGPD Teste Fase3",
        email_teste,
        "48999001122",
        generate_password_hash("teste123"),
        "Usuário",
        1,
    )

    try:
        dados = LgpdTitularService.coletar_dados("usuario", uid)
        if dados.get("usuario", {}).get("email") == email_teste:
            print("  OK     Coletar dados titular")
        else:
            falhas += 1
            print("  FALHA  Coletar dados titular")

        j = LgpdTitularService.exportar_json("usuario", uid)
        parsed = json.loads(j)
        if parsed.get("titular_tipo") == "usuario":
            print("  OK     Exportar JSON")
        else:
            falhas += 1
            print("  FALHA  Exportar JSON")

        csv_data = LgpdTitularService.exportar_csv("usuario", uid)
        if "usuario" in csv_data and email_teste in csv_data:
            print("  OK     Exportar CSV")
        else:
            falhas += 1
            print("  FALHA  Exportar CSV")

        LgpdTitularService.anonimizar("usuario", uid, "teste_fase3")
        u2 = UsuarioRepository.buscar_por_id(uid)
        if u2 and u2["nome"] == "*** ANONIMIZADO ***":
            print("  OK     Anonimizar usuario teste")
        else:
            falhas += 1
            print("  FALHA  Anonimizar usuario teste")
    except Exception as erro:
        falhas += 1
        print(f"  FALHA  Fluxo titular: {erro}")

    print()
    if falhas:
        print(f"  {falhas} teste(s) com problema")
    else:
        estado = "ligada" if config.LGPD_TITULAR_ATIVO else "off"
        print(f"  Fase 3 LGPD OK — migração e serviços (flag {estado})")
    print("=" * 60)
    print()
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
