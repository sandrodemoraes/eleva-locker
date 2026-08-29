#!/usr/bin/env python3
"""Configura TOTEM_AJUDA_TELEFONE no .env (WhatsApp da portaria)."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"


def _gravar_env(chave, valor):
    linhas = []
    achou = False
    if ENV_PATH.exists():
        for linha in ENV_PATH.read_text(encoding="utf-8").splitlines():
            if re.match(rf"^\s*{re.escape(chave)}\s*=", linha) and not linha.strip().startswith("#"):
                linhas.append(f"{chave}={valor}")
                achou = True
            else:
                linhas.append(linha)
    if not achou:
        if linhas and linhas[-1].strip():
            linhas.append("")
        linhas.append("# Ajuda no totem — WhatsApp da portaria")
        linhas.append(f"{chave}={valor}")
    ENV_PATH.write_text("\n".join(linhas).rstrip() + "\n", encoding="utf-8")


def _ler_env(chave):
    if not ENV_PATH.exists():
        return ""
    for linha in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if re.match(rf"^\s*{re.escape(chave)}\s*=", linha) and not linha.strip().startswith("#"):
            return linha.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def main():
    print()
    print("=" * 60)
    print("  AJUDA NO TOTEM — telefone WhatsApp da portaria")
    print("=" * 60)
    print()
    print("  Quando alguém toca 'Preciso de ajuda' no totem,")
    print("  o sistema envia WhatsApp para este número.")
    print()

    atual = _ler_env("TOTEM_AJUDA_TELEFONE")
    if atual:
        print(f"  Atual no .env: {atual}")
        print()

    if len(sys.argv) > 1:
        telefone = sys.argv[1].strip()
    else:
        telefone = input("  Telefone portaria (DDD+numero, ex: 48999998888): ").strip()

    digits = re.sub(r"\D", "", telefone)
    if len(digits) not in (10, 11):
        print("  ERRO: use DDD + numero (10 ou 11 digitos).")
        return 1

    _gravar_env("TOTEM_AJUDA_TELEFONE", digits)
    if not _ler_env("TOTEM_AJUDA_ALERTA"):
        _gravar_env("TOTEM_AJUDA_ALERTA", "1")

    print()
    print("  Reinicie o servidor: pare INICIAR.bat (Ctrl+C) e abra de novo.")
    print()
    print("  WhatsApp precisa estar ativo no .env:")
    print("    NOTIF_WHATSAPP_ATIVO=1")
    print("    WHATSAPP_API_URL=...  WHATSAPP_API_KEY=...  WHATSAPP_INSTANCIA=...")
    print("=" * 60)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
