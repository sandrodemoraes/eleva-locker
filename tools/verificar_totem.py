#!/usr/bin/env python3
"""Verifica se o totem instalado é a versão nova (com depósito)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOTEM = ROOT / "templates" / "totem.html"

print("=== ELEVA LOCKER — Verificar totem ===")
print(f"Pasta: {ROOT}")
print()

if not TOTEM.exists():
    print("ERRO: templates/totem.html nao encontrado")
    raise SystemExit(1)

texto = TOTEM.read_text(encoding="utf-8")

checks = {
    "Depositar encomenda (botao)": "Depositar encomenda" in texto,
    "Tela inicio (Retirar encomenda)": "Retirar encomenda" in texto,
    "Versao antiga (teclado direto)": "Abrir compartimento" in texto,
    "Versao antiga (footer retirada)": "Totem de retirada" in texto,
}

for nome, ok in checks.items():
    if "antiga" in nome:
        status = "PROBLEMA" if ok else "OK (nao tem)"
    else:
        status = "OK" if ok else "FALTA"
    print(f"  [{status}] {nome}")

print()
if checks["Depositar encomenda (botao)"] and not checks["Versao antiga (teclado direto)"]:
    print("Totem NOVO — reinicie: python app.py")
    print("URL: http://192.168.16.130:15000/totem/3")
else:
    print("Totem ANTIGO — rode:")
    print("  git pull origin cursor/totem-seguro-c05c")
    print("  python tools/verificar_totem.py")

try:
    import subprocess
    r = subprocess.run(
        ["git", "log", "-1", "--oneline"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if r.stdout.strip():
        print()
        print("Git:", r.stdout.strip())
except Exception:
    pass
