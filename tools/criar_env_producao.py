#!/usr/bin/env python3
"""Grava .env de producao na pasta do projeto (C:\\ElevaLocker\\.env)."""

from pathlib import Path

CONTEUDO = """# ELEVA LOCKER — producao (Sandro / Matriz)
# Gerado por tools/criar_env_producao.py

SECRET_KEY=ElevaLocker2026
SKIP_BACKUP=0

APP_URL_BASE=http://177.74.79.32:15000

ESP32_TOKEN=eleva-esp32-token-2026
ESP32_MODO_SIMULACAO=0

NOTIF_MODO=producao
NOTIF_EMAIL_ATIVO=1
NOTIF_WHATSAPP_ATIVO=1
WHATSAPP_PROVIDER=evolution
WHATSAPP_API_URL=http://192.168.16.130:8080
WHATSAPP_SERVER_URL=http://192.168.16.130:8080
WHATSAPP_API_KEY=ElevaWhatsApp2026
WHATSAPP_INSTANCIA=eleva-locker
WHATSAPP_RETRY_MAX=3
WHATSAPP_RETRY_DELAY=1.5

TOTEM_AJUDA_TELEFONE=
TOTEM_DEPOSITO_PIN=2026
TOTEM_ARMARIO_ID=3
TOTEM_DEPOSITO_SEM_PIN=1
PAGAMENTO_MODO=console

POSTGRES_USER=eleva
POSTGRES_PASSWORD=eleva
POSTGRES_DB=elevalocker
"""


def main():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    env_path.write_text(CONTEUDO, encoding="utf-8")
    print(f"OK — .env gravado em:\n  {env_path}")
    print()
    print("Proximo passo:")
    print("  python tools/verificar_env.py")
    print("  python app.py")


if __name__ == "__main__":
    main()
