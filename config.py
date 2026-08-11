import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

# Carrega .env da pasta do projeto (C:\ElevaLocker\.env)
_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(_ENV_PATH)

# Flask
SECRET_KEY = os.getenv("SECRET_KEY", "ElevaLocker2026")

# ESP32
ESP32_TOKEN = os.getenv("ESP32_TOKEN", "eleva-esp32-token-2026")
ESP32_RELE_DURACAO = int(os.getenv("ESP32_RELE_DURACAO", "3"))
ESP32_HEARTBEAT_TIMEOUT = int(os.getenv("ESP32_HEARTBEAT_TIMEOUT", "90"))
ESP32_HTTP_TIMEOUT = int(os.getenv("ESP32_HTTP_TIMEOUT", "5"))
ESP32_MODO_SIMULACAO = os.getenv("ESP32_MODO_SIMULACAO", "0") == "1"
ESP32_PORTAS_OPCOES = [8, 16, 24, 32, 64]
ESP32_MAX_PORTAS = max(ESP32_PORTAS_OPCOES)


def normalizar_max_portas(valor, padrao=16):
    """Valida max_portas — apenas 8, 16, 24, 32 ou 64."""
    try:
        n = int(valor)
    except (TypeError, ValueError):
        n = padrao
    if n in ESP32_PORTAS_OPCOES:
        return n
    # Arredonda para opção válida mais próxima (para cima)
    for op in ESP32_PORTAS_OPCOES:
        if n <= op:
            return op
    return ESP32_MAX_PORTAS

# Backup
BACKUP_MAX = int(os.getenv("BACKUP_MAX", "5"))
BACKUP_DIR = os.getenv("BACKUP_DIR", "backups")

# Notificações — modo: console | producao
NOTIF_MODO = os.getenv("NOTIF_MODO", "console")

NOTIF_EMAIL_ATIVO = os.getenv("NOTIF_EMAIL_ATIVO", "1") == "1"
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", "noreply@elevalocker.com")

NOTIF_WHATSAPP_ATIVO = os.getenv("NOTIF_WHATSAPP_ATIVO", "0") == "1"
WHATSAPP_PROVIDER = os.getenv("WHATSAPP_PROVIDER", "evolution")  # evolution | meta
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL", "")
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY", "")
WHATSAPP_INSTANCIA = os.getenv("WHATSAPP_INSTANCIA", "")
WHATSAPP_RETRY_MAX = int(os.getenv("WHATSAPP_RETRY_MAX", "3"))
WHATSAPP_RETRY_DELAY = float(os.getenv("WHATSAPP_RETRY_DELAY", "1.5"))

# Meta Cloud API (WHATSAPP_PROVIDER=meta)
WHATSAPP_META_TOKEN = os.getenv("WHATSAPP_META_TOKEN", "")
WHATSAPP_META_PHONE_ID = os.getenv("WHATSAPP_META_PHONE_ID", "")
WHATSAPP_META_TEMPLATE = os.getenv("WHATSAPP_META_TEMPLATE", "encomenda_chegou")

NOTIF_SMS_ATIVO = os.getenv("NOTIF_SMS_ATIVO", "0") == "1"
SMS_API_URL = os.getenv("SMS_API_URL", "")
SMS_API_KEY = os.getenv("SMS_API_KEY", "")

# URL base para links no totem/QR (ex: http://192.168.1.10:15000)
APP_URL_BASE = os.getenv("APP_URL_BASE", "http://localhost:15000")

# Totem / encomendas
ENCOMENDA_DIAS_VALIDADE = int(os.getenv("ENCOMENDA_DIAS_VALIDADE", "7"))
TOTEM_RATE_LIMIT = int(os.getenv("TOTEM_RATE_LIMIT", "8"))
TOTEM_RATE_JANELA = int(os.getenv("TOTEM_RATE_JANELA", "300"))
TOTEM_AJUDA_TELEFONE = os.getenv("TOTEM_AJUDA_TELEFONE", "")
TOTEM_DEPOSITO_PIN = os.getenv("TOTEM_DEPOSITO_PIN", "")
TOTEM_ARMARIO_ID = os.getenv("TOTEM_ARMARIO_ID", "").strip()
_sem_pin_env = os.getenv("TOTEM_DEPOSITO_SEM_PIN", "").strip()
if _sem_pin_env:
    TOTEM_DEPOSITO_SEM_PIN = _sem_pin_env == "1"
else:
    # Totem fixo no armário: sem PIN (acesso físico já restringe)
    TOTEM_DEPOSITO_SEM_PIN = bool(TOTEM_ARMARIO_ID)

TOTEM_DEPOSITO_SOMENTE_CADASTRADO = os.getenv("TOTEM_DEPOSITO_SOMENTE_CADASTRADO", "1") == "1"

# Bancada local — força SQLite mesmo se DATABASE_URL existir no .env
ELEVA_BANCADA = os.getenv("ELEVA_BANCADA", "").strip().lower() in ("1", "true", "yes")

# Database — sqlite (dev/bancada) | postgresql (produção)
DATABASE_URL = os.getenv("DATABASE_URL", "")
if ELEVA_BANCADA:
    DATABASE_URL = ""
DB_ENGINE = os.getenv("DB_ENGINE", "sqlite")
PAGAMENTO_MODO = os.getenv("PAGAMENTO_MODO", "console")
PAGAMENTO_API_URL = os.getenv("PAGAMENTO_API_URL", "")
PAGAMENTO_API_KEY = os.getenv("PAGAMENTO_API_KEY", "")
PAGAMENTO_DIAS_VENCIMENTO = int(os.getenv("PAGAMENTO_DIAS_VENCIMENTO", "10"))


def gerar_token_esp32():
    return secrets.token_hex(16)
