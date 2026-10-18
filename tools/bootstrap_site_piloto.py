#!/usr/bin/env python3
"""Cria site + armário piloto no banco e gera snippet de .env para instalação Modelo A."""

import argparse
import os
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SKIP_BACKUP", "1")


def _gravar_snippet_env(caminho, valores):
    linhas = [
        "# Gerado por tools/bootstrap_site_piloto.py — copie para .env no PC do site",
        "",
    ]
    for chave, valor in valores.items():
        linhas.append(f"{chave}={valor}")
    caminho.write_text("\n".join(linhas).rstrip() + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Bootstrap site piloto ELEVA LOCKER (Modelo A — servidor local)."
    )
    parser.add_argument("--nome", required=True, help='Ex.: "Condomínio Residencial Piloto"')
    parser.add_argument("--codigo", default="", help="Ex.: piloto-050 (auto a partir do nome)")
    parser.add_argument("--endereco", default="", help="Endereço do armário")
    parser.add_argument("--cidade", default="", help="Cidade")
    parser.add_argument("--estado", default="SC", help="UF")
    parser.add_argument("--portas", type=int, default=16, choices=[8, 16, 24, 32, 64])
    parser.add_argument(
        "--ip-servidor",
        default="192.168.50.10",
        help="IP fixo do PC servidor na LAN do site (APP_URL_BASE)",
    )
    parser.add_argument(
        "--armario-nome",
        default="",
        help="Nome do armário (default: ELEVA Locker + codigo)",
    )
    parser.add_argument(
        "--gerar-api-key",
        action="store_true",
        help="Gera API key para Matriz monitorar via GET /api/v1/status",
    )
    parser.add_argument(
        "--saida-env",
        default="",
        help="Arquivo .env snippet (default: Sites/<codigo>/env.txt)",
    )
    args = parser.parse_args()

    from database import criar_banco

    criar_banco()

    from services.site_service import SiteService
    from services.armario_service import ArmarioService
    from services.api_key_service import ApiKeyService

    codigo = args.codigo.strip() or args.nome.lower().replace(" ", "-")[:32]
    armario_nome = args.armario_nome.strip() or f"ELEVA Locker {codigo.upper()}"

    site_id = SiteService.criar({
        "nome": args.nome.strip(),
        "codigo": codigo,
        "endereco": args.endereco.strip() or None,
        "cidade": args.cidade.strip() or None,
        "estado": args.estado.strip() or None,
        "status": 1,
    })

    armario_id = ArmarioService.criar({
        "nome": armario_nome,
        "endereco": args.endereco.strip() or args.nome.strip(),
        "cidade": args.cidade.strip() or "",
        "estado": args.estado.strip() or "SC",
        "status": "ativo",
        "site_id": site_id,
        "max_portas": args.portas,
    })

    app_url = f"http://{args.ip_servidor.strip()}:15000"
    secret = secrets.token_hex(32)
    esp_token = secrets.token_hex(16)

    pasta_site = ROOT / "Sites" / codigo
    pasta_site.mkdir(parents=True, exist_ok=True)

    saida = Path(args.saida_env) if args.saida_env else pasta_site / "env.txt"
    if not saida.is_absolute():
        saida = ROOT / saida

    env_vals = {
        "SECRET_KEY": secret,
        "ELEVA_SITE_CODIGO": codigo,
        "ELEVA_SITE_NOME": args.nome.strip(),
        "APP_URL_BASE": app_url,
        "ELEVA_PAINEL_URL": f"{app_url}/dashboard",
        "NOTIF_INCLUIR_LINK_TOTEM": "0",
        "ESP32_TOKEN": esp_token,
        "ESP32_MODO_SIMULACAO": "0",
        "NOTIF_MODO": "console",
        "TOTEM_ARMARIO_ID": str(armario_id),
        "ENCOMENDA_DIAS_VALIDADE": "7",
        "LGPD_AVISO_ATIVO": "0",
        "LGPD_CONSENTIMENTO_USUARIO": "0",
    }
    _gravar_snippet_env(saida, env_vals)

    rede_txt = pasta_site / "rede.txt"
    rede_txt.write_text(
        "\n".join([
            f"Site: {args.nome}",
            f"Código: {codigo}",
            f"Servidor: {app_url}",
            f"Armário id: {armario_id} ({args.portas} portas)",
            f"ESP32_TOKEN: {esp_token}",
            "",
            "Firmware (cada ESP):",
            f"  SERVIDOR_URL = \"{app_url}\"",
            f"  ESP32_TOKEN  = \"{esp_token}\"",
            "",
            "Totem:",
            f"  {app_url}/totem/{armario_id}?kiosk=1",
            "",
        ]),
        encoding="utf-8",
    )

    api_key = None
    if args.gerar_api_key:
        _, api_key = ApiKeyService.criar(f"Monitor {codigo}", site_id=site_id, permissoes="read")
        (pasta_site / "api_key.txt").write_text(
            f"GET {app_url}/api/v1/status\n"
            f"Header: X-API-Key: {api_key}\n",
            encoding="utf-8",
        )

    print()
    print("=" * 60)
    print("  SITE PILOTO CRIADO — Modelo A (servidor local)")
    print("=" * 60)
    print(f"  Site id:     {site_id}")
    print(f"  Código:      {codigo}")
    print(f"  Armário id:  {armario_id} ({armario_nome}, {args.portas} portas)")
    print(f"  APP_URL:     {app_url}")
    print(f"  Totem:       {app_url}/totem/{armario_id}?kiosk=1")
    print()
    print(f"  Arquivos em: {pasta_site}")
    print(f"    env.txt     → copiar para .env no PC do site")
    print(f"    rede.txt    → SSID, IPs ESP, tokens")
    if api_key:
        print(f"    api_key.txt → monitoramento Matriz via WireGuard")
    print()
    print("  Próximos passos:")
    print("  1. Instalar ElevaLocker no PC do site (C:\\ElevaLocker)")
    print("  2. Copiar env.txt → .env e reiniciar servidor")
    print("  3. Cadastrar ESPs no painel + gravar firmware (SERVIDOR_URL local)")
    print("  4. Testar totem depósito + retirada na LAN do site")
    print("  5. (Opcional) WireGuard para Matriz enxergar o site")
    print()
    print("  Docs: docs/INSTALACAO_SITE.md")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
