#!/usr/bin/env python3
"""
Checklist de segurança do .env e configuração.

Uso:
  python tools/verificar_seguranca.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import dotenv_values

DEFAULTS = {
    "SECRET_KEY": "ElevaLocker2026",
    "ESP32_TOKEN": "eleva-esp32-token-2026",
    "WHATSAPP_API_KEY": "ElevaWhatsApp2026",
}

PIN_FRACOS = {"1234", "123456", "2026", "0000", "1111"}


def main():
    env_path = ROOT / ".env"
    print("=" * 60)
    print("  VERIFICAR SEGURANÇA — ELEVA LOCKER")
    print("=" * 60)
    print(f"\nArquivo: {env_path}")

    if not env_path.exists():
        print("\n  ⚠ .env não encontrado — usando padrões do código")
        env = {}
    else:
        env = dotenv_values(env_path)

    ok = 0
    alertas = 0
    criticos = 0

    def checar(nome, msg_ok, msg_alerta, critico=False):
        nonlocal ok, alertas, criticos
        val = env.get(nome) or DEFAULTS.get(nome, "")
        if nome in DEFAULTS and val == DEFAULTS[nome]:
            print(f"  ⚠ {nome}: {msg_alerta}")
            if critico:
                criticos += 1
            else:
                alertas += 1
        elif not val and nome in ("SECRET_KEY", "ESP32_TOKEN"):
            print(f"  ⚠ {nome}: não definido (usa padrão do código)")
            alertas += 1
        else:
            print(f"  ✓ {nome}: {msg_ok}")
            ok += 1

    print("\n[Segredos]")
    checar("SECRET_KEY", "personalizado", "ainda padrão ElevaLocker2026 — troque!", critico=True)
    checar("ESP32_TOKEN", "personalizado", "ainda padrão — alinhe firmware + banco")
    checar("WHATSAPP_API_KEY", "personalizado", "ainda padrão ElevaWhatsApp2026")

    print("\n[Totem]")
    pin = (env.get("TOTEM_DEPOSITO_PIN") or "").strip()
    sem_pin = (env.get("TOTEM_DEPOSITO_SEM_PIN") or "").strip()
    if sem_pin == "1":
        print("  ℹ TOTEM_DEPOSITO_SEM_PIN=1 — depósito sem PIN (OK bancada fixa na rede local)")
    elif pin:
        if pin in PIN_FRACOS:
            print(f"  ⚠ TOTEM_DEPOSITO_PIN={pin} — PIN fraco, use 6+ dígitos aleatórios")
            alertas += 1
        else:
            print("  ✓ TOTEM_DEPOSITO_PIN definido")
            ok += 1
    else:
        print("  ⚠ Totem sem PIN — configure TOTEM_DEPOSITO_PIN ou SEM_PIN=1 na bancada")
        alertas += 1

    print("\n[Rede / Flask]")
    bancada = (env.get("ELEVA_BANCADA") or "").strip().lower() in ("1", "true", "yes")
    debug = env.get("FLASK_DEBUG", "")
    if bancada:
        print("  ✓ ELEVA_BANCADA=1 (SQLite local)")
        ok += 1
    if debug == "0":
        print("  ✓ FLASK_DEBUG=0 (produção)")
        ok += 1
    elif debug == "1":
        print("  ℹ FLASK_DEBUG=1 (desenvolvimento)")
    else:
        print("  ℹ FLASK_DEBUG não definido (bancada=ligado, produção=desligado)")

    print("\n[Recomendações]")
    print("  • Admin: senha forte (já trocou ✓)")
    print("  • PC bancada: PIN Windows + rede Wi-Fi com senha")
    print("  • Totem/tablet: só na rede local (192.168.x.x)")
    print("  • Produção na internet: FLASK_DEBUG=0 + HTTPS + SECRET_KEY nova")
    print("  • Gerar SECRET_KEY: python -c \"import secrets; print(secrets.token_hex(32))\"")

    print("\n" + "=" * 60)
    if criticos:
        print(f"  ATENÇÃO: {criticos} item(ns) crítico(s) — troque SECRET_KEY antes de expor na internet")
    elif alertas:
        print(f"  OK para bancada local — {alertas} melhoria(s) opcional(is)")
    else:
        print("  Configuração de segurança OK")
    print("=" * 60)
    return 1 if criticos else 0


if __name__ == "__main__":
    raise SystemExit(main())
