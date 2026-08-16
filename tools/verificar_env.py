#!/usr/bin/env python3
"""Mostra se o .env está sendo lido corretamente."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config

env_path = Path(__file__).resolve().parent.parent / ".env"

print("=== Arquivo .env ===")
print(f"Caminho: {env_path}")
print(f"Existe:  {'SIM' if env_path.exists() else 'NAO — crie a partir de .env.example'}")
print()
print("=== Valores carregados ===")
print(f"NOTIF_MODO           = {config.NOTIF_MODO}")
print(f"NOTIF_WHATSAPP_ATIVO = {config.NOTIF_WHATSAPP_ATIVO}")
print(f"WHATSAPP_API_URL     = {config.WHATSAPP_API_URL}")
print(f"WHATSAPP_INSTANCIA   = {config.WHATSAPP_INSTANCIA}")
print(f"APP_URL_BASE         = {config.APP_URL_BASE}")
print()

ok = (
    config.NOTIF_MODO == "producao"
    and config.NOTIF_WHATSAPP_ATIVO
    and config.WHATSAPP_API_URL
    and config.WHATSAPP_INSTANCIA
)

if ok:
    print("OK — WhatsApp pronto para producao. Reinicie py app.py se acabou de alterar.")
else:
    print("PROBLEMA — edite C:\\ElevaLocker\\.env e defina:")
    print("  NOTIF_MODO=producao")
    print("  NOTIF_WHATSAPP_ATIVO=1")
    sys.exit(1)
