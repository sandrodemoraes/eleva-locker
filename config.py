import os
import secrets

# Flask
SECRET_KEY = os.getenv("SECRET_KEY", "ElevaLocker2026")

# ESP32
ESP32_TOKEN = os.getenv("ESP32_TOKEN", "eleva-esp32-token-2026")
ESP32_RELE_DURACAO = int(os.getenv("ESP32_RELE_DURACAO", "3"))
ESP32_HEARTBEAT_TIMEOUT = int(os.getenv("ESP32_HEARTBEAT_TIMEOUT", "90"))
ESP32_HTTP_TIMEOUT = int(os.getenv("ESP32_HTTP_TIMEOUT", "5"))
ESP32_MODO_SIMULACAO = os.getenv("ESP32_MODO_SIMULACAO", "0") == "1"

# Backup
BACKUP_MAX = int(os.getenv("BACKUP_MAX", "5"))

# Notificações — modo: console | producao
NOTIF_MODO = os.getenv("NOTIF_MODO", "console")

NOTIF_EMAIL_ATIVO = os.getenv("NOTIF_EMAIL_ATIVO", "1") == "1"
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", "noreply@elevalocker.com")

NOTIF_WHATSAPP_ATIVO = os.getenv("NOTIF_WHATSAPP_ATIVO", "0") == "1"
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL", "")
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY", "")
WHATSAPP_INSTANCIA = os.getenv("WHATSAPP_INSTANCIA", "")

NOTIF_SMS_ATIVO = os.getenv("NOTIF_SMS_ATIVO", "0") == "1"
SMS_API_URL = os.getenv("SMS_API_URL", "")
SMS_API_KEY = os.getenv("SMS_API_KEY", "")

# URL base para links no totem/QR (ex: http://192.168.1.10:15000)
APP_URL_BASE = os.getenv("APP_URL_BASE", "http://localhost:15000")

# Database — sqlite (dev) | postgresql (produção)
DATABASE_URL = os.getenv("DATABASE_URL", "")
DB_ENGINE = os.getenv("DB_ENGINE", "sqlite")
PAGAMENTO_MODO = os.getenv("PAGAMENTO_MODO", "console")
PAGAMENTO_API_URL = os.getenv("PAGAMENTO_API_URL", "")
PAGAMENTO_API_KEY = os.getenv("PAGAMENTO_API_KEY", "")
PAGAMENTO_DIAS_VENCIMENTO = int(os.getenv("PAGAMENTO_DIAS_VENCIMENTO", "10"))


def gerar_token_esp32():
    return secrets.token_hex(16)
