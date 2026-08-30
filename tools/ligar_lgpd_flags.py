#!/usr/bin/env python3
"""Ativa flags LGPD Fase 2 no .env local (sem parar o servidor)."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"

FLAGS = {
    "usuario": "LGPD_CONSENTIMENTO_USUARIO",
    "totem": "LGPD_AVISO_TOTEM",
}


def _ler_linhas():
    if not ENV_PATH.exists():
        return []
    return ENV_PATH.read_text(encoding="utf-8").splitlines(keepends=True)


def _definir_var(linhas, chave, valor):
    prefixo = f"{chave}="
    encontrou = False
    novas = []
    for linha in linhas:
        texto = linha.strip()
        if texto.startswith(prefixo) or texto.startswith(f"# {prefixo}"):
            novas.append(f"{chave}={valor}\n")
            encontrou = True
        else:
            novas.append(linha if linha.endswith("\n") else linha + "\n")
    if not encontrou:
        if novas and not novas[-1].endswith("\n"):
            novas[-1] = novas[-1] + "\n"
        novas.append(f"{chave}={valor}\n")
    return novas


def main():
    parser = argparse.ArgumentParser(description="Liga flags LGPD Fase 2 no .env")
    parser.add_argument("--usuario", action="store_true", help="Só LGPD_CONSENTIMENTO_USUARIO=1")
    parser.add_argument("--totem", action="store_true", help="Só LGPD_AVISO_TOTEM=1")
    args = parser.parse_args()

    ligar_usuario = args.usuario or (not args.usuario and not args.totem)
    ligar_totem = args.totem or (not args.usuario and not args.totem)

    print()
    print("=" * 60)
    print("  LIGAR FLAGS LGPD FASE 2")
    print("=" * 60)

    linhas = _ler_linhas()
    if not linhas:
        linhas = ["# ELEVA LOCKER — .env\n"]

    alterados = []
    if ligar_usuario:
        linhas = _definir_var(linhas, FLAGS["usuario"], "1")
        alterados.append(FLAGS["usuario"])
    if ligar_totem:
        linhas = _definir_var(linhas, FLAGS["totem"], "1")
        alterados.append(FLAGS["totem"])

    ENV_PATH.write_text("".join(linhas), encoding="utf-8")

    print(f"  Arquivo: {ENV_PATH}")
    for chave in alterados:
        print(f"  OK      {chave}=1")
    print()
    print("  Reinicie o servidor: feche INICIAR.bat e rode de novo.")
    print("  Depois: TESTAR_LGPD.bat")
    print("=" * 60)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
