#!/usr/bin/env python3
"""Grava .env de producao com segredos gerados automaticamente."""

import secrets
from pathlib import Path

# Valores fixos bancada Matriz — ajuste APP_URL_BASE se necessario
ESP32_TOKEN_MATRIZ = "2e5bb4db71d8330be8bae43b13ac19f6"
APP_URL = "http://177.74.79.32:15000"
TOTEM_ARMARIO = "2"


def gerar_conteudo():
    secret = secrets.token_hex(32)
    whatsapp_key = secrets.token_urlsafe(24)
    pin = "".join(str(secrets.randbelow(10)) for _ in range(6))

    return f"""# ELEVA LOCKER — producao (Sandro / Matriz)
# Gerado por tools/criar_env_producao.py — segredos aleatorios

SECRET_KEY={secret}
FLASK_DEBUG=0
SKIP_BACKUP=0

APP_URL_BASE={APP_URL}

ESP32_TOKEN={ESP32_TOKEN_MATRIZ}
ESP32_MODO_SIMULACAO=0

NOTIF_MODO=producao
NOTIF_EMAIL_ATIVO=1
NOTIF_WHATSAPP_ATIVO=1
WHATSAPP_PROVIDER=evolution
WHATSAPP_API_URL=http://192.168.16.130:8080
WHATSAPP_SERVER_URL=http://192.168.16.130:8080
WHATSAPP_API_KEY={whatsapp_key}
WHATSAPP_INSTANCIA=eleva-locker
WHATSAPP_RETRY_MAX=3
WHATSAPP_RETRY_DELAY=1.5

NOTIF_SMS_ATIVO=0
PAGAMENTO_MODO=console

POSTGRES_USER=eleva
POSTGRES_PASSWORD=ALTERE_SENHA_POSTGRES
POSTGRES_DB=elevalocker

TOTEM_DEPOSITO_PIN={pin}
TOTEM_AJUDA_TELEFONE=(48) 99657-7857
ENCOMENDA_DIAS_VALIDADE=7
TOTEM_ARMARIO_ID={TOTEM_ARMARIO}

ELEVA_BANCADA=1
"""


def main():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        print(f"AVISO: {env_path} ja existe.")
        print("  Use tools/corrigir_env_seguranca.py para corrigir sem perder ESP32_TOKEN")
        print("  Ou apague/renomeie .env antes de gerar novo.")
        return 1

    conteudo = gerar_conteudo()
    env_path.write_text(conteudo, encoding="utf-8")
    print(f"OK — .env gravado em:\n  {env_path}")
    print()
    print("ANOTE o TOTEM_DEPOSITO_PIN e WHATSAPP_API_KEY do arquivo .env")
    print("Atualize WHATSAPP_API_KEY no docker-compose Evolution se usar WhatsApp")
    print()
    print("Proximo: tools\\verificar_seguranca.bat && tools\\iniciar_elevalocker.bat")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
