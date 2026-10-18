#!/usr/bin/env python3
"""Job LGPD Fase 4 — retenção e minimização (simulação por padrão)."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from services.lgpd_retencao_service import LgpdRetencaoService  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Retenção LGPD Fase 4")
    parser.add_argument(
        "--executar",
        action="store_true",
        help="Aplica alterações (padrão: apenas simula)",
    )
    args = parser.parse_args()

    simular = not args.executar

    print()
    print("=" * 60)
    print("  LGPD FASE 4 — RETENÇÃO")
    print("=" * 60)
    if simular:
        print("  Modo: SIMULAÇÃO (use --executar para aplicar)")
    else:
        print("  Modo: EXECUÇÃO — alterações serão gravadas")
    print()

    r = LgpdRetencaoService.executar(simular=simular)

    for chave in ("encomendas", "logs", "ajuda_totem", "notificacoes"):
        item = r[chave]
        print(f"  {chave:16} elegíveis: {item['elegiveis']:4}  (antes de {item['cutoff']})")
        if chave == "encomendas" and item.get("ids"):
            amostra = item["ids"][:5]
            if amostra:
                print(f"                   amostra ids: {amostra}")

    print()
    print(f"  Log: logs/lgpd_retencao.log")
    print("=" * 60)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
