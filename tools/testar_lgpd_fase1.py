#!/usr/bin/env python3
"""Testa rotas LGPD Fase 1 e regressão básica do totem."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import app  # noqa: E402


def main():
    c = app.test_client()
    print()
    print("=" * 60)
    print("  TESTE LGPD FASE 1")
    print("=" * 60)

    rotas = [
        ("/privacidade", 200, "Política de Privacidade"),
        ("/termos", 200, "Termos de Uso"),
        ("/lgpd", 200, "Seus dados"),
        ("/totem/2", 200, "Totem Matriz"),
        ("/totem/versao", 200, "Versão totem"),
    ]

    falhas = 0
    for path, esperado, nome in rotas:
        r = c.get(path)
        ok = r.status_code == esperado
        if not ok:
            falhas += 1
            print(f"  FALHA  {nome}  {path}  HTTP {r.status_code}")
            continue
        print(f"  OK     {nome}  {path}")
        if path == "/totem/2" and b"Privacidade" not in r.data:
            print("         AVISO: link Privacidade nao encontrado no totem")
        if path == "/privacidade" and "Privacidade" not in r.data.decode("utf-8", errors="replace"):
            falhas += 1
            print("         FALHA: conteudo privacidade incompleto")

    print()
    if falhas:
        print(f"  {falhas} teste(s) com problema")
    else:
        print("  Fase 1 LGPD OK — totem e paginas publicas respondendo")
    print("=" * 60)
    print()
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
