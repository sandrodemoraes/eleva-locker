#!/usr/bin/env python3
"""
Diagnóstico e teste do alerta de ajuda no totem (WhatsApp → portaria).

Uso:
  py tools/testar_ajuda_totem.py
  py tools/testar_ajuda_totem.py --enviar
  py tools/testar_ajuda_totem.py --enviar --armario-id 2
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("SKIP_BACKUP", "1")

from database import criar_banco

criar_banco()

import config  # noqa: E402
from services.totem_ajuda_service import TotemAjudaService  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Testar ajuda totem + WhatsApp portaria")
    parser.add_argument("--enviar", action="store_true", help="Simula pedido de ajuda (envia WhatsApp)")
    parser.add_argument("--armario-id", type=int, default=2, help="ID do armário (padrão 2)")
    args = parser.parse_args()

    print("=" * 60)
    print("  ELEVA LOCKER — Diagnóstico ajuda totem")
    print("=" * 60)
    print()

    diag = TotemAjudaService.diagnosticar()
    print(f"  TOTEM_AJUDA_ALERTA   = {diag['totem_ajuda_alerta']}")
    print(f"  TOTEM_AJUDA_TELEFONE = {diag['totem_ajuda_telefone'] or '(vazio)'}")
    print(f"  Telefone normalizado = {diag['telefone_valido'] or '—'}")
    if diag["telefone_erro"]:
        print(f"  ERRO telefone       = {diag['telefone_erro']}")
    print(f"  NOTIF_MODO           = {diag['notif_modo']}")
    print(f"  NOTIF_WHATSAPP_ATIVO = {diag['whatsapp_ativo']}")
    print()

    wa = diag["whatsapp_status"]
    print(f"  WhatsApp pronto      = {wa.get('pronto')}")
    print(f"  WhatsApp mensagem    = {wa.get('mensagem')}")
    if wa.get("conexao"):
        print(f"  Instância status     = {wa.get('conexao')}")
    print()

    if not TotemAjudaService.ajuda_habilitada():
        print("ERRO: Ajuda desabilitada — defina TOTEM_AJUDA_ALERTA=1 ou TOTEM_AJUDA_TELEFONE")
        return 1

    if not args.enviar:
        print("Dica: rode com --enviar para simular clique em 'Preciso de ajuda'")
        print("Ex.: py tools\\testar_ajuda_totem.py --enviar --armario-id 2")
        return 0

    print("Enviando pedido de ajuda de teste...")
    try:
        r = TotemAjudaService.solicitar(armario_id=args.armario_id, ip_origem="teste-script")
    except ValueError as e:
        print(f"ERRO: {e}")
        return 1

    print()
    print(f"  Pedido id          = {r['pedido_id']}")
    print(f"  Armário            = {r['armario_nome']}")
    print(f"  WhatsApp enviado   = {r['whatsapp_enviado']}")
    if r.get("whatsapp_erro"):
        print(f"  WhatsApp erro      = {r['whatsapp_erro']}")
    print(f"  Mensagem           = {r['mensagem']}")
    print()

    if r["whatsapp_enviado"]:
        print("OK — WhatsApp enviado (ou modo console).")
        return 0

    print("FALHOU — WhatsApp não enviou. Corrija o item acima e tente de novo.")
    print("  • Evolution conectada? Abra /notificacoes no painel")
    print("  • NOTIF_MODO=producao e NOTIF_WHATSAPP_ATIVO=1?")
    print("  • Reiniciou o servidor após editar .env?")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
