import os
import secrets
from pathlib import Path


def _carregar_env_arquivo():
    """Lê C:\\ElevaLocker\\.env (ou ./.env) para os.getenv funcionar no py app.py."""
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return
    valores = {}
    for linha in env_path.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, _, valor = linha.partition("=")
        chave = chave.strip()
        if not chave:
            continue
        valores[chave] = valor.strip().strip('"').strip("'")
    for chave, valor in valores.items():
        os.environ.setdefault(chave, valor)


_carregar_env_arquivo()

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
    for op in ESP32_PORTAS_OPCOES:
        if n <= op:
            return op
    return ESP32_MAX_PORTAS

# Backup — pasta local ou disco D:
BACKUP_DIR = os.getenv("BACKUP_DIR", "backups")
BACKUP_MAX = int(os.getenv("BACKUP_MAX", "5"))
SKIP_BACKUP = os.getenv("SKIP_BACKUP", "0") == "1"

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

# Database — sqlite (dev) | postgresql (produção)
DATABASE_URL = os.getenv("DATABASE_URL", "")
DB_ENGINE = os.getenv("DB_ENGINE", "sqlite")
PAGAMENTO_MODO = os.getenv("PAGAMENTO_MODO", "console")
PAGAMENTO_API_URL = os.getenv("PAGAMENTO_API_URL", "")
PAGAMENTO_API_KEY = os.getenv("PAGAMENTO_API_KEY", "")
PAGAMENTO_DIAS_VENCIMENTO = int(os.getenv("PAGAMENTO_DIAS_VENCIMENTO", "10"))

# Encomendas — prazo para retirada pelo morador (dias); após isso status retida
ENCOMENDA_DIAS_VALIDADE = int(os.getenv("ENCOMENDA_DIAS_VALIDADE", "3"))
# Reenvio automático de lembrete após X horas no armário (aguardando retirada)
ENCOMENDA_HORAS_REENVIO = int(os.getenv("ENCOMENDA_HORAS_REENVIO", "24"))
ENCOMENDA_LEMBRETE_AUTOMATICO = os.getenv("ENCOMENDA_LEMBRETE_AUTOMATICO", "1") == "1"

# Totem — ID fixo do armário (default 2 = Matriz bancada). /totem → /totem/<id>
_totem_armario = os.getenv("TOTEM_ARMARIO_ID", "2").strip()
TOTEM_ARMARIO_ID = _totem_armario if _totem_armario.isdigit() else None

TOTEM_RATE_LIMIT = int(os.getenv("TOTEM_RATE_LIMIT", "8"))
TOTEM_RATE_JANELA = int(os.getenv("TOTEM_RATE_JANELA", "300"))
TOTEM_AJUDA_TELEFONE = os.getenv("TOTEM_AJUDA_TELEFONE", "")
TOTEM_AJUDA_ALERTA = os.getenv("TOTEM_AJUDA_ALERTA", "1") == "1"
TOTEM_DEPOSITO_PIN = os.getenv("TOTEM_DEPOSITO_PIN", "")
_sem_pin_env = os.getenv("TOTEM_DEPOSITO_SEM_PIN", "").strip()
if _sem_pin_env:
    TOTEM_DEPOSITO_SEM_PIN = _sem_pin_env == "1"
else:
    TOTEM_DEPOSITO_SEM_PIN = bool(TOTEM_ARMARIO_ID)
TOTEM_DEPOSITO_SOMENTE_CADASTRADO = os.getenv("TOTEM_DEPOSITO_SOMENTE_CADASTRADO", "1") == "1"

# LGPD — Fase 1 (documentação; flags avançadas na Fase 2+)
LGPD_AVISO_ATIVO = os.getenv("LGPD_AVISO_ATIVO", "1") == "1"
LGPD_POLITICA_VERSAO = os.getenv("LGPD_POLITICA_VERSAO", "2026-08-30")
LGPD_CONTATO_EMAIL = os.getenv("LGPD_CONTATO_EMAIL", "").strip()
LGPD_CONTATO_TELEFONE = os.getenv("LGPD_CONTATO_TELEFONE", "").strip()
LGPD_CONTROLADOR_NOME = os.getenv("LGPD_CONTROLADOR_NOME", "ELEVA LOCKER — Matriz ELEVA").strip()

# LGPD — Fase 2 (consentimento; flags 0 = comportamento idêntico ao anterior)
LGPD_CONSENTIMENTO_USUARIO = os.getenv("LGPD_CONSENTIMENTO_USUARIO", "0") == "1"
LGPD_AVISO_TOTEM = os.getenv("LGPD_AVISO_TOTEM", "0") == "1"

# LGPD — Fase 3 (direitos do titular; 0 = menu/ações ocultos)
LGPD_TITULAR_ATIVO = os.getenv("LGPD_TITULAR_ATIVO", "0") == "1"

# LGPD — Fase 4 (retenção + mascaramento; job 0 = não roda automático)
LGPD_RETENCAO_ENCOMENDA_DIAS = int(os.getenv("LGPD_RETENCAO_ENCOMENDA_DIAS", "365"))
LGPD_RETENCAO_LOG_DIAS = int(os.getenv("LGPD_RETENCAO_LOG_DIAS", "180"))
LGPD_RETENCAO_AJUDA_TOTEM_DIAS = int(os.getenv("LGPD_RETENCAO_AJUDA_TOTEM_DIAS", "90"))
LGPD_RETENCAO_NOTIFICACAO_DIAS = int(os.getenv("LGPD_RETENCAO_NOTIFICACAO_DIAS", "365"))
LGPD_JOB_ATIVO = os.getenv("LGPD_JOB_ATIVO", "0") == "1"
LGPD_MASCARAR_TELEFONE = os.getenv("LGPD_MASCARAR_TELEFONE", "0") == "1"


def gerar_token_esp32():
    return secrets.token_hex(16)
