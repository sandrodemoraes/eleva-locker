#!/usr/bin/env python3
"""Testa LGPD Fase 2 — migração, flags off e serviço de consentimento."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import config  # noqa: E402
from app import app  # noqa: E402
from database import criar_banco  # noqa: E402
from repositories.base_repository import BaseRepository  # noqa: E402
from repositories.lgpd_consentimento_repository import LgpdConsentimentoRepository  # noqa: E402
from services.lgpd_consentimento_service import LgpdConsentimentoService  # noqa: E402


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
    print("  TESTE LGPD FASE 2")
    print("=" * 60)

    falhas = 0

    criar_banco()

    checks = [
        ("Tabela lgpd_consentimentos", _tabela_existe("lgpd_consentimentos")),
        ("Coluna usuarios.lgpd_consentimento_em", _coluna_existe("usuarios", "lgpd_consentimento_em")),
        ("Coluna encomendas.lgpd_base_legal", _coluna_existe("encomendas", "lgpd_base_legal")),
    ]

    if config.LGPD_CONSENTIMENTO_USUARIO:
        print("  OK     Flag LGPD_CONSENTIMENTO_USUARIO ligada")
    else:
        print("  OK     Flag LGPD_CONSENTIMENTO_USUARIO off")

    if config.LGPD_AVISO_TOTEM:
        print("  OK     Flag LGPD_AVISO_TOTEM ligada")
    else:
        print("  OK     Flag LGPD_AVISO_TOTEM off")

    for nome, ok in checks:
        if ok:
            print(f"  OK     {nome}")
        else:
            falhas += 1
            print(f"  FALHA  {nome}")

    c = app.test_client()
    r = c.get("/totem/2")
    if r.status_code != 200:
        falhas += 1
        print(f"  FALHA  Totem /totem/2 HTTP {r.status_code}")
    elif config.LGPD_AVISO_TOTEM:
        if b"totem-lgpd-aviso" in r.data:
            print("  OK     Totem com aviso depósito (flag on)")
        else:
            falhas += 1
            print("  FALHA  Aviso depósito ausente com flag on")
    elif b"totem-lgpd-aviso" in r.data:
        falhas += 1
        print("  FALHA  Aviso depósito visível com flag off")
    else:
        print("  OK     Totem sem aviso depósito (flag off)")

    antes = LgpdConsentimentoRepository.contar()
    LgpdConsentimentoService.registrar(
        titular_tipo="teste",
        finalidade="teste_fase2",
        telefone="48999999999",
    )
    depois = LgpdConsentimentoRepository.contar()
    if depois == antes + 1:
        print("  OK     Serviço registrar consentimento")
    else:
        falhas += 1
        print("  FALHA  Serviço registrar consentimento")

    print()
    if falhas:
        print(f"  {falhas} teste(s) com problema")
    else:
        estado = "ligadas" if (config.LGPD_CONSENTIMENTO_USUARIO or config.LGPD_AVISO_TOTEM) else "off"
        print(f"  Fase 2 LGPD OK — migração e flags {estado}")
    print("=" * 60)
    print()
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
