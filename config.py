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


def gerar_token_esp32():
    return secrets.token_hex(16)
