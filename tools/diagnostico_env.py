"""Verifica se o .env esta sendo lido pelo servidor."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.pop("TOTEM_AJUDA_TELEFONE", None)

import config  # noqa: E402

print()
print("=" * 60)
print("  DIAGNOSTICO .env — ELEVA LOCKER")
print("=" * 60)
print(f"  Arquivo: {ROOT / '.env'}")
print(f"  Existe:  {(ROOT / '.env').exists()}")
print()
print(f"  TOTEM_AJUDA_TELEFONE = {config.TOTEM_AJUDA_TELEFONE!r}")
print(f"  TOTEM_AJUDA_ALERTA   = {config.TOTEM_AJUDA_ALERTA}")
print(f"  NOTIF_WHATSAPP_ATIVO = {config.NOTIF_WHATSAPP_ATIVO}")
print(f"  WHATSAPP_INSTANCIA   = {config.WHATSAPP_INSTANCIA!r}")
print(f"  APP_URL_BASE         = {config.APP_URL_BASE!r}")
print()
print("  LGPD — Fase 1")
print(f"  LGPD_AVISO_ATIVO           = {config.LGPD_AVISO_ATIVO}")
print(f"  LGPD_POLITICA_VERSAO       = {config.LGPD_POLITICA_VERSAO!r}")
print()
print("  LGPD — Fase 2")
print(f"  LGPD_CONSENTIMENTO_USUARIO = {config.LGPD_CONSENTIMENTO_USUARIO}")
print(f"  LGPD_AVISO_TOTEM           = {config.LGPD_AVISO_TOTEM}")
print()

if (config.TOTEM_AJUDA_TELEFONE or "").strip():
    print("  OK — .env carregado. Reinicie INICIAR.bat se acabou de atualizar.")
else:
    print("  FALTA TOTEM_AJUDA_TELEFONE — confira o .env ou rode git pull.")
print("=" * 60)
print()
