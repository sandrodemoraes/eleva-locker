#!/usr/bin/env python3
"""
Reenvia notificações de encomendas há mais de 24h no armário.

Uso:
  py tools/lembretes_encomenda.py
  py tools/lembretes_encomenda.py --dry-run

Agendar no Windows (Agendador de Tarefas, a cada 30 min):
  py tools/lembretes_encomenda.py
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("SKIP_BACKUP", "1")

from database import criar_banco

criar_banco()

import config
from repositories.encomenda_repository import EncomendaRepository
from services.encomenda_service import EncomendaService


def main():
    parser = argparse.ArgumentParser(description="Lembretes automáticos de encomenda")
    parser.add_argument("--dry-run", action="store_true", help="Só listar, não enviar")
    args = parser.parse_args()

    print("=" * 60)
    print("  LEMBRETES ENCOMENDA — ELEVA LOCKER")
    print(f"  Reenvio após {config.ENCOMENDA_HORAS_REENVIO}h no armário")
    print(f"  Automático ativo: {config.ENCOMENDA_LEMBRETE_AUTOMATICO}")
    print("=" * 60)

    if args.dry_run:
        pendentes = 0
        for e in EncomendaRepository.listar_aguardando_retirada():
            if EncomendaService._precisa_lembrete_automatico(e):
                pendentes += 1
                print(
                    f"  #{e['id']} {e['cliente']} — comp. #{e['compartimento_numero']} "
                    f"entrada {e['data_entrada']}"
                )
        print(f"\n  {pendentes} encomenda(s) receberiam lembrete agora.")
        return

    r = EncomendaService.processar_lembretes_automaticos()
    print(f"\n  Enviados: {r['enviados']} | Erros: {r['erros']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
