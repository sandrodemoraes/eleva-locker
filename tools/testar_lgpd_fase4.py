#!/usr/bin/env python3
"""Testa LGPD Fase 4 — retenção (simulação) e mascaramento."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import config  # noqa: E402
from services.lgpd_mascara_service import LgpdMascaraService  # noqa: E402
from services.lgpd_retencao_service import LgpdRetencaoService  # noqa: E402


def main():
    print()
    print("=" * 60)
    print("  TESTE LGPD FASE 4")
    print("=" * 60)

    falhas = 0

    checks = [
        ("Retenção encomenda dias", config.LGPD_RETENCAO_ENCOMENDA_DIAS > 0),
        ("Retenção log dias", config.LGPD_RETENCAO_LOG_DIAS > 0),
        ("Job off por padrão", not config.LGPD_JOB_ATIVO),
        ("Mascara off por padrão", not config.LGPD_MASCARAR_TELEFONE),
    ]
    for nome, ok in checks:
        if ok:
            print(f"  OK     {nome}")
        else:
            falhas += 1
            print(f"  FALHA  {nome}")

    tel = LgpdMascaraService.mascarar_telefone("48991095679")
    if "**" in tel and "48" in tel:
        print(f"  OK     Mascara telefone ({tel})")
    else:
        falhas += 1
        print(f"  FALHA  Mascara telefone ({tel})")

    if LgpdMascaraService.telefone_para_exibicao("48991095679", "Administrador") == "48991095679":
        print("  OK     Admin ve telefone completo")
    else:
        falhas += 1
        print("  FALHA  Admin deveria ver telefone completo")

    op = LgpdMascaraService.telefone_para_exibicao("48991095679", "Operador")
    if not config.LGPD_MASCARAR_TELEFONE:
        if op == "48991095679":
            print("  OK     Operador com flag off ve completo")
        else:
            falhas += 1
            print("  FALHA  Operador deveria ver telefone completo (flag off)")
    elif "**" in op:
        print("  OK     Operador com flag on ve mascarado")
    else:
        falhas += 1
        print("  FALHA  Operador deveria ver telefone mascarado")

    r = LgpdRetencaoService.executar(simular=True)
    if r["modo"] == "SIMULACAO":
        print("  OK     Simulação retenção executada")
    else:
        falhas += 1
        print("  FALHA  Simulação retenção")

    print()
    if falhas:
        print(f"  {falhas} teste(s) com problema")
    else:
        print("  Fase 4 LGPD OK — retenção simulada e mascaramento")
    print("=" * 60)
    print()
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
