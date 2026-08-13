#!/usr/bin/env python3
"""
Corrige segredos fracos no .env de produção (com backup automático).

Preserva: ESP32_TOKEN, APP_URL_BASE, TOTEM_ARMARIO_ID, telefones, URLs WhatsApp.

Gera novo: SECRET_KEY, WHATSAPP_API_KEY (se padrão)
Ajusta: FLASK_DEBUG=0, PIN fraco (opcional), avisos HTTP público

Uso:
  python tools/corrigir_env_seguranca.py
  python tools/corrigir_env_seguranca.py --simular
  python tools/corrigir_env_seguranca.py --gerar-pin
"""
import argparse
import re
import secrets
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"

DEFAULTS = {
    "SECRET_KEY": "ElevaLocker2026",
    "ESP32_TOKEN": "eleva-esp32-token-2026",
    "WHATSAPP_API_KEY": "ElevaWhatsApp2026",
}
PIN_FRACOS = {"1234", "123456", "2026", "0000", "1111", "4321"}
IP_PUBLICO = re.compile(r"^https?://(\d{1,3}\.){3}\d+")


def ler_env(texto):
    linhas = texto.splitlines()
    vals = {}
    for linha in linhas:
        s = linha.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        vals[k.strip()] = v.strip()
    return linhas, vals


def definir_chave(linhas, chave, valor):
    prefixo = f"{chave}="
    for i, linha in enumerate(linhas):
        if linha.strip().startswith(prefixo):
            linhas[i] = f"{chave}={valor}"
            return linhas
    linhas.append(f"{chave}={valor}")
    return linhas


def main():
    parser = argparse.ArgumentParser(description="Corrige segredos fracos no .env")
    parser.add_argument("--simular", action="store_true", help="Só mostra o que faria")
    parser.add_argument("--gerar-pin", action="store_true", help="Gera PIN totem aleatório 6 dígitos")
    args = parser.parse_args()

    print("=" * 60)
    print("  CORRIGIR SEGURANÇA — .env")
    print("=" * 60)

    if not ENV_PATH.exists():
        print(f"\nERRO: .env não encontrado em {ENV_PATH}")
        return 1

    texto = ENV_PATH.read_text(encoding="utf-8")
    linhas, vals = ler_env(texto)
    alteracoes = []

    if vals.get("SECRET_KEY") == DEFAULTS["SECRET_KEY"] or not vals.get("SECRET_KEY"):
        novo = secrets.token_hex(32)
        alteracoes.append(("SECRET_KEY", vals.get("SECRET_KEY", "(vazio)"), novo))

    if vals.get("WHATSAPP_API_KEY") == DEFAULTS["WHATSAPP_API_KEY"]:
        novo = secrets.token_urlsafe(24)
        alteracoes.append(("WHATSAPP_API_KEY", DEFAULTS["WHATSAPP_API_KEY"], novo))

    if vals.get("FLASK_DEBUG") != "0":
        alteracoes.append(("FLASK_DEBUG", vals.get("FLASK_DEBUG", "(não definido)"), "0"))

    pin = vals.get("TOTEM_DEPOSITO_PIN", "")
    if args.gerar_pin or pin in PIN_FRACOS:
        if args.gerar_pin or pin in PIN_FRACOS:
            novo_pin = "".join(str(secrets.randbelow(10)) for _ in range(6))
            while novo_pin in PIN_FRACOS or novo_pin.startswith("0"):
                novo_pin = "".join(str(secrets.randbelow(10)) for _ in range(6))
            alteracoes.append(("TOTEM_DEPOSITO_PIN", pin or "(vazio)", novo_pin))

    url = vals.get("APP_URL_BASE", "")
    if url and IP_PUBLICO.match(url) and url.startswith("http://"):
        print(f"\n  ⚠ APP_URL_BASE em HTTP com IP público: {url}")
        print("    Qualquer um na internet pode interceptar login/sessão.")
        print("    Ideal: HTTPS (nginx/Caddy) ou VPN — não corrigido automaticamente.")

    if vals.get("POSTGRES_PASSWORD") == "eleva":
        print("\n  ℹ POSTGRES_PASSWORD=eleva — fraco; troque se usar PostgreSQL.")

    if not alteracoes:
        print("\n  ✓ Nada a corrigir automaticamente.")
        print("  Rode: tools\\verificar_seguranca.bat")
        return 0

    print("\nAlterações propostas:")
    for chave, antigo, novo in alteracoes:
        show_novo = novo if chave != "SECRET_KEY" else novo[:16] + "..."
        print(f"  {chave}: {antigo} → {show_novo}")

    if args.simular:
        print("\n(simular — nenhum arquivo alterado)")
        return 0

    backup = ROOT / "backups" / f"env_antes_seguranca_{datetime.now():%Y%m%d_%H%M%S}.txt"
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ENV_PATH, backup)
    print(f"\n  Backup: {backup}")

    for chave, _, novo in alteracoes:
        linhas = definir_chave(linhas, chave, novo)

    ENV_PATH.write_text("\n".join(linhas).rstrip() + "\n", encoding="utf-8")
    print(f"  OK — .env atualizado: {ENV_PATH}")

    if any(c[0] == "TOTEM_DEPOSITO_PIN" for c in alteracoes):
        pin_novo = next(c[2] for c in alteracoes if c[0] == "TOTEM_DEPOSITO_PIN")
        print(f"\n  NOVO PIN TOTEM (anote): {pin_novo}")

    if any(c[0] == "WHATSAPP_API_KEY" for c in alteracoes):
        key_novo = next(c[2] for c in alteracoes if c[0] == "WHATSAPP_API_KEY")
        print(f"\n  NOVA WHATSAPP_API_KEY — atualize também no docker-compose / Evolution:")
        print(f"    {key_novo}")

    print("\n  Reinicie o servidor: tools\\iniciar_elevalocker.bat")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
