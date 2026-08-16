"""
Utilitários .env — instalação bancada (SQLite único, sem Postgres).

Todos os scripts de bancada devem chamar garantir_bancada() ANTES de importar config.
"""
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"

CHAVES_BANCADA = {
    "ELEVA_BANCADA": "1",
    "ESP32_MODO_SIMULACAO": "0",
    "SKIP_BACKUP": "0",
    "ELEVA_PAINEL_URL": "http://192.168.16.130:15000",
}


def _ler_linhas():
    if not ENV_PATH.exists():
        return ["# ELEVA LOCKER — bancada Matriz"]
    return ENV_PATH.read_text(encoding="utf-8").splitlines()


def _gravar(linhas):
    ENV_PATH.write_text("\n".join(linhas).rstrip() + "\n", encoding="utf-8")


def comentar_database_url(linhas):
    out = []
    alterou = False
    for linha in linhas:
        if re.match(r"^\s*DATABASE_URL\s*=", linha) and not linha.strip().startswith("#"):
            out.append("# " + linha.strip() + "  # OFF — bancada usa SQLite")
            alterou = True
        else:
            out.append(linha)
    return out, alterou


def definir_chave(linhas, chave, valor):
    regex = re.compile(rf"^\s*{re.escape(chave)}\s*=")
    out = []
    achou = False
    for linha in linhas:
        if regex.match(linha):
            out.append(f"{chave}={valor}")
            achou = True
        else:
            out.append(linha)
    if not achou:
        if out and out[-1].strip():
            out.append("")
        out.append(f"{chave}={valor}")
    return out


def garantir_bancada_env():
    """
    Grava .env para bancada: ELEVA_BANCADA=1, sem DATABASE_URL ativo.
    Retorna True se alterou o arquivo.
    """
    linhas = _ler_linhas()
    linhas, db_off = comentar_database_url(linhas)
    for chave, valor in CHAVES_BANCADA.items():
        linhas = definir_chave(linhas, chave, valor)
    _gravar(linhas)
    aplicar_bancada_processo()
    return db_off or True


def aplicar_bancada_processo():
    """Força SQLite neste processo (antes de importar config)."""
    os.environ["ELEVA_BANCADA"] = "1"
    os.environ.pop("DATABASE_URL", None)


def env_subprocess():
    """Ambiente para subprocessos de bancada."""
    env = os.environ.copy()
    env["ELEVA_BANCADA"] = "1"
    env.pop("DATABASE_URL", None)
    env.setdefault("SKIP_BACKUP", "1")
    return env
