#!/usr/bin/env python3
"""Processa fila de notificações pendentes (ajuda totem + encomendas)."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.notificacao_fila_service import NotificacaoFilaService  # noqa: E402


def main():
    resultado = NotificacaoFilaService.processar()
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

    if not resultado.get("ativo", True):
        return 0

    if not resultado.get("whatsapp_pronto", True):
        print("\nWhatsApp ainda não está pronto — fila tentará de novo automaticamente.")
        return 1

    ajuda = resultado.get("ajuda", {})
    enc = resultado.get("encomendas", {})
    print(
        f"\nAjuda totem: {ajuda.get('enviados', 0)}/{ajuda.get('tentados', 0)} enviados"
    )
    print(
        f"Encomendas: {enc.get('enviados', 0)}/{enc.get('tentados', 0)} enviadas"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
