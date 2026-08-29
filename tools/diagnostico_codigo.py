#!/usr/bin/env python3
"""Mostra se o codigo local esta atualizado (engrenagem, Ctrl+C, etc.)."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRANCH = "cursor/retirada-pacote-retido-c05c"


def _run(cmd):
    try:
        r = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return (r.stdout or "").strip(), r.returncode
    except Exception as erro:
        return str(erro), 1


def _git(*args):
    out, code = _run(["git", *args])
    return out if code == 0 else ""


def _tem(conteudo, texto):
    return texto in conteudo


def main():
    print()
    print("=" * 60)
    print("  DIAGNOSTICO ELEVA LOCKER — codigo local")
    print("=" * 60)
    print(f"  Pasta: {ROOT}")
    print()

    branch = _git("branch", "--show-current") or "(git falhou)"
    head = _git("rev-parse", "--short", "HEAD") or "?"
    _run(["git", "fetch", "origin", BRANCH])
    remoto = _git("rev-parse", "--short", f"origin/{BRANCH}") or "?"

    print(f"  Branch local:    {branch}")
    print(f"  Commit local:    {head}")
    print(f"  Commit GitHub:   {remoto}")
    if head != "?" and remoto != "?" and head != remoto:
        print("  >>> DESATUALIZADO — rode tools\\atualizar_bancada.bat")
    elif branch != BRANCH:
        print(f"  >>> BRANCH ERRADA — deveria ser {BRANCH}")
    else:
        print("  >>> Git parece atualizado (confira arquivos abaixo)")
    print()

    checks = [
        ("templates/armarios.html", "Cadastre armários, placas ESP", "Engrenagem na listagem"),
        ("templates/armarios.html", "fa-solid fa-gear", "Icone engrenagem verde"),
        ("templates/armarios_detalhe.html", "ESP32 deste armário", "Tela /armarios/id"),
        ("app.py", "Encerrar o servidor ELEVA LOCKER", "Confirmacao Ctrl+C"),
        ("templates/layout/navbar.html", "url_for('notificacoes.listar')", "Sino abre notificacoes"),
    ]

    ok = 0
    for path, needle, desc in checks:
        arquivo = ROOT / path
        if not arquivo.exists():
            print(f"  FALTA  {desc} — arquivo {path} nao existe")
            continue
        texto = arquivo.read_text(encoding="utf-8", errors="replace")
        if _tem(texto, needle):
            print(f"  OK     {desc}")
            ok += 1
        else:
            print(f"  FALTA  {desc} — rode tools\\atualizar_bancada.bat")

    print()
    print(f"  Arquivos OK: {ok}/{len(checks)}")
    print()
    print("  IMPORTANTE: depois de atualizar, pare o servidor (Ctrl+C)")
    print("  e rode de novo: py app.py")
    print("  No navegador: Ctrl+F5 em /armarios")
    print("=" * 60)
    print()
    return 0 if ok == len(checks) and branch == BRANCH and head == remoto else 1


if __name__ == "__main__":
    raise SystemExit(main())
