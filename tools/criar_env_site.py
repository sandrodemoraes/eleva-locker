#!/usr/bin/env python3
"""Gera .env para site piloto (Modelo A) a partir de .env.site.example."""

import argparse
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXEMPLO = ROOT / ".env.site.example"


def main():
    parser = argparse.ArgumentParser(description="Gera .env de site piloto ELEVA LOCKER.")
    parser.add_argument("--codigo", default="piloto-050", help="ELEVA_SITE_CODIGO")
    parser.add_argument("--nome", default="Condomínio Piloto", help="ELEVA_SITE_NOME")
    parser.add_argument("--ip", required=True, help="IP fixo do PC na LAN (ex.: 192.168.50.10)")
    parser.add_argument("--armario-id", type=int, default=1, help="TOTEM_ARMARIO_ID")
    parser.add_argument("--porta", type=int, default=15000, help="Porta Flask")
    parser.add_argument("--forcar", action="store_true", help="Sobrescreve .env existente")
    args = parser.parse_args()

    destino = ROOT / ".env"
    if destino.exists() and not args.forcar:
        print(f"AVISO: {destino} já existe. Use --forcar ou copie manualmente de .env.site.example")
        return 1

    base = EXEMPLO.read_text(encoding="utf-8") if EXEMPLO.exists() else ""
    app_url = f"http://{args.ip.strip()}:{args.porta}"

    substituicoes = {
        "SECRET_KEY=ALTERE_GERE_COM_tools_criar_env_site_py": f"SECRET_KEY={secrets.token_hex(32)}",
        "ELEVA_SITE_CODIGO=piloto-050": f"ELEVA_SITE_CODIGO={args.codigo}",
        "ELEVA_SITE_NOME=Condomínio Piloto": f"ELEVA_SITE_NOME={args.nome}",
        "APP_URL_BASE=http://192.168.50.10:15000": f"APP_URL_BASE={app_url}",
        "ELEVA_PAINEL_URL=http://192.168.50.10:15000/dashboard": f"ELEVA_PAINEL_URL={app_url}/dashboard",
        "TOTEM_ARMARIO_ID=1": f"TOTEM_ARMARIO_ID={args.armario_id}",
        "ESP32_TOKEN=eleva-esp32-token-2026": f"ESP32_TOKEN={secrets.token_hex(16)}",
    }

    for antigo, novo in substituicoes.items():
        base = base.replace(antigo, novo)

    destino.write_text(base, encoding="utf-8")
    print(f"OK — .env gravado em:\n  {destino}")
    print(f"  APP_URL_BASE={app_url}")
    print(f"  TOTEM_ARMARIO_ID={args.armario_id}")
    print()
    print("Próximo: INICIAR.bat ou tools\\iniciar_servidor.bat")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
