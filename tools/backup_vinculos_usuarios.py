#!/usr/bin/env python3
"""
Snapshot dos vínculos usuário ↔ armário antes de scripts de manutenção.

Grava backups/vinculos_usuarios_latest.json (sempre sobrescreve)
e backups/vinculos_usuarios_YYYYMMDD_HHMMSS.json (histórico).

Uso:
  python tools/backup_vinculos_usuarios.py
"""
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

from env_bancada import aplicar_bancada_processo

aplicar_bancada_processo()


def main():
    from database import criar_banco
    criar_banco()

    from repositories.base_repository import BaseRepository

    dest_dir = ROOT / "backups"
    dest_dir.mkdir(parents=True, exist_ok=True)

    with BaseRepository.get_connection() as conn:
        usuarios = conn.execute("""
            SELECT u.id, u.nome, u.email, u.perfil, u.status, u.armario_id, a.nome AS armario_nome
            FROM usuarios u
            LEFT JOIN armarios a ON a.id = u.armario_id
            ORDER BY u.id
        """).fetchall()
        armarios = conn.execute(
            "SELECT id, nome, site_id FROM armarios ORDER BY id"
        ).fetchall()

    payload = {
        "criado_em": datetime.now().isoformat(timespec="seconds"),
        "armarios": [dict(r) for r in armarios],
        "usuarios": [dict(u) for u in usuarios],
    }

    latest = dest_dir / "vinculos_usuarios_latest.json"
    historico = dest_dir / f"vinculos_usuarios_{datetime.now():%Y%m%d_%H%M%S}.json"

    texto = json.dumps(payload, ensure_ascii=False, indent=2)
    latest.write_text(texto, encoding="utf-8")
    historico.write_text(texto, encoding="utf-8")

    vinculados = sum(1 for u in payload["usuarios"] if u.get("armario_id"))
    print(f"    OK  {vinculados} vínculo(s) | {len(payload['usuarios'])} usuário(s)")
    print(f"    {latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
