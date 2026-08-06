#!/usr/bin/env python3
"""Diagnostico rapido — qual versao do totem esta rodando."""

import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOTEM = ROOT / "templates" / "totem.html"


def git_info():
    try:
        r = subprocess.run(
            ["git", "log", "-1", "--oneline"],
            cwd=ROOT, capture_output=True, text=True,
        )
        b = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=ROOT, capture_output=True, text=True,
        )
        return (b.stdout or "").strip(), (r.stdout or "").strip()
    except Exception as e:
        return "?", str(e)


def arquivo_info():
    if not TOTEM.exists():
        return {"erro": "totem.html nao encontrado"}
    t = TOTEM.read_text(encoding="utf-8")
    return {
        "deposito_pin": "tela-deposito-pin" in t,
        "home_botoes": "Retirar encomenda" in t,
        "layout_antigo": "Abrir compartimento" in t,
    }


def servidor_info():
    try:
        with urllib.request.urlopen("http://127.0.0.1:15000/totem/versao", timeout=3) as r:
            return json.loads(r.read().decode())
    except urllib.error.URLError:
        return {"erro": "servidor nao responde na porta 15000"}
    except Exception as e:
        return {"erro": str(e)}


def main():
    print("=" * 55)
    print("  DIAGNOSTICO ELEVA LOCKER")
    print("=" * 55)
    print(f"Pasta: {ROOT}")
    branch, commit = git_info()
    print(f"Git branch: {branch}")
    print(f"Git commit: {commit}")
    print()
    print("Arquivo templates/totem.html:")
    for k, v in arquivo_info().items():
        print(f"  {k}: {v}")
    print()
    print("Servidor http://127.0.0.1:15000/totem/versao:")
    srv = servidor_info()
    print(f"  {json.dumps(srv, ensure_ascii=False)}")
    print()
    ok_arquivo = arquivo_info().get("home_botoes") and not arquivo_info().get("layout_antigo")
    ok_srv = srv.get("ok") is True
    if ok_arquivo and ok_srv:
        print("STATUS: OK — totem v2 no disco E no servidor")
    elif ok_arquivo and not ok_srv:
        print("STATUS: PROBLEMA — arquivos novos mas servidor antigo (Docker?)")
        print("Rode: tools\\corrigir_totem.bat")
    else:
        print("STATUS: PROBLEMA — arquivos antigos no disco")
        print("Rode: tools\\corrigir_totem.bat")
    return 0


if __name__ == "__main__":
    sys.exit(main())
