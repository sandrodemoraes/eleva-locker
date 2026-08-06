#!/usr/bin/env python3
"""Testa envio WhatsApp direto na Evolution API + config do Eleva Locker."""

import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from services.notificacao_service import NotificacaoService


def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {}, method="GET")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    telefone = sys.argv[1] if len(sys.argv) > 1 else "48996587858"

    print("=== Config Eleva Locker ===")
    print(f"NOTIF_MODO          = {config.NOTIF_MODO}")
    print(f"NOTIF_WHATSAPP_ATIVO= {config.NOTIF_WHATSAPP_ATIVO}")
    print(f"WHATSAPP_API_URL    = {config.WHATSAPP_API_URL}")
    print(f"WHATSAPP_INSTANCIA  = {config.WHATSAPP_INSTANCIA}")
    print(f"WHATSAPP_API_KEY    = {config.WHATSAPP_API_KEY[:8]}...")
    print()

    numero, erro = NotificacaoService.validar_telefone_br(telefone)
    print(f"Telefone informado: {telefone}")
    print(f"Telefone normalizado: {numero} ({erro or 'OK'})")
    print()

    base = config.WHATSAPP_API_URL.rstrip("/")
    headers = {"apikey": config.WHATSAPP_API_KEY}

    print("=== Evolution API ===")
    try:
        instancias = get(f"{base}/instance/fetchInstances", headers)
        print("Instâncias:", json.dumps(instancias, indent=2, ensure_ascii=False)[:1500])
    except Exception as e:
        print(f"ERRO ao listar instâncias: {e}")
        print("Verifique se Evolution está rodando em", base)
        return 1

    print()
    print("=== Envio de teste via Eleva Locker ===")
    try:
        r = NotificacaoService.testar_whatsapp(telefone)
        print("SUCESSO:", r)
    except ValueError as e:
        print("FALHOU:", e)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
