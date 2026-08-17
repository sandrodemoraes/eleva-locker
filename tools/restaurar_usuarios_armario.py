#!/usr/bin/env python3
"""
Restaura vínculo usuários ↔ armário Matriz.

Problema recorrente na bancada:
  - consertar_bancada / limpar_bancada_teste exclui "Bancada Teste"
  - usuários ficam com armario_id NULL ou apontando para id antigo (ex.: 3 em vez de 2)
  - somem da página Armários → abrir armário → Usuários

Este script:
  1. Corrige armario_id órfão (aponta para armário que não existe mais)
  2. Revincula moradores (perfil Usuário) ao armário Matriz
  3. Revincula operadores órfãos (perfil Operador com id inválido)
  4. Restaura vínculos do backup_01 quando o banco atual perdeu armario_id
  5. Importa moradores faltantes do backup

Uso:
  python tools/restaurar_usuarios_armario.py
  python tools/restaurar_usuarios_armario.py --listar
  python tools/restaurar_usuarios_armario.py --armario-id 2
"""
import argparse
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

from env_bancada import aplicar_bancada_processo

aplicar_bancada_processo()

NOME_ARMARIO = "ELEVA Locker Matriz"
BACKUP_DB = ROOT / "backups" / "backup_01" / "database" / "elevalocker.db"
PERFIS_VINCULAVEIS = ("Usuário", "Operador")


def obter_armario_matriz(conn, armario_id=None):
    if armario_id:
        row = conn.execute(
            "SELECT id, nome FROM armarios WHERE id = ? LIMIT 1",
            (armario_id,),
        ).fetchone()
        if row:
            return row["id"], row["nome"]

    row = conn.execute(
        "SELECT id, nome FROM armarios WHERE nome = ? LIMIT 1",
        (NOME_ARMARIO,),
    ).fetchone()
    if row:
        return row["id"], row["nome"]

    row = conn.execute(
        "SELECT id, nome FROM armarios ORDER BY id LIMIT 1"
    ).fetchone()
    if row:
        return row["id"], row["nome"]
    return None, None


def listar_por_armario(conn, armario_id):
    return conn.execute("""
        SELECT id, nome, email, telefone, perfil, armario_id, status
        FROM usuarios
        WHERE armario_id = ?
        ORDER BY perfil, nome
    """, (armario_id,)).fetchall()


def listar_orfaos(conn):
    return conn.execute("""
        SELECT id, nome, email, perfil, armario_id
        FROM usuarios
        WHERE armario_id IS NOT NULL
          AND armario_id NOT IN (SELECT id FROM armarios)
        ORDER BY nome
    """).fetchall()


def listar_desvinculados(conn):
    return conn.execute("""
        SELECT id, nome, email, perfil, armario_id
        FROM usuarios
        WHERE perfil IN ('Usuário', 'Operador')
          AND status = 1
          AND armario_id IS NULL
        ORDER BY perfil, nome
    """).fetchall()


def corrigir_orfaos(conn, armario_id):
    cur = conn.execute("""
        UPDATE usuarios
        SET armario_id = ?
        WHERE armario_id IS NOT NULL
          AND armario_id NOT IN (SELECT id FROM armarios)
          AND perfil IN ('Usuário', 'Operador')
    """, (armario_id,))
    conn.commit()
    return cur.rowcount


def vincular_moradores(conn, armario_id):
    cur = conn.execute("""
        UPDATE usuarios
        SET armario_id = ?
        WHERE perfil = 'Usuário' AND status = 1
          AND (armario_id IS NULL OR armario_id != ?)
    """, (armario_id, armario_id))
    conn.commit()
    return cur.rowcount


def copiar_moradores_backup(conn_atual, armario_id):
    if not BACKUP_DB.exists():
        return 0

    conn_bak = sqlite3.connect(str(BACKUP_DB))
    conn_bak.row_factory = sqlite3.Row
    rows = conn_bak.execute("""
        SELECT nome, email, telefone, senha, perfil, status, armario_id
        FROM usuarios
        WHERE perfil = 'Usuário' AND status = 1
    """).fetchall()
    conn_bak.close()

    inseridos = 0
    for r in rows:
        existe = conn_atual.execute(
            "SELECT id FROM usuarios WHERE email = ? LIMIT 1",
            (r["email"],),
        ).fetchone()
        if existe:
            continue
        conn_atual.execute("""
            INSERT INTO usuarios (nome, email, telefone, senha, perfil, status, armario_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            r["nome"], r["email"], r["telefone"], r["senha"],
            r["perfil"], r["status"], armario_id,
        ))
        inseridos += 1
    conn_atual.commit()
    return inseridos


def restaurar_vinculos_backup(conn_atual, armario_id):
    """Recupera armario_id perdido comparando e-mail com backup_01."""
    if not BACKUP_DB.exists():
        return 0

    conn_bak = sqlite3.connect(str(BACKUP_DB))
    conn_bak.row_factory = sqlite3.Row
    rows = conn_bak.execute("""
        SELECT email, perfil, armario_id
        FROM usuarios
        WHERE perfil IN ('Usuário', 'Operador')
          AND status = 1
          AND armario_id IS NOT NULL
    """).fetchall()
    conn_bak.close()

    atualizados = 0
    for r in rows:
        atual = conn_atual.execute("""
            SELECT id, armario_id, perfil
            FROM usuarios
            WHERE email = ? AND status = 1
            LIMIT 1
        """, (r["email"],)).fetchone()
        if not atual:
            continue
        if atual["perfil"] not in PERFIS_VINCULAVEIS:
            continue
        if atual["armario_id"] is not None:
            continue
        conn_atual.execute(
            "UPDATE usuarios SET armario_id = ? WHERE id = ?",
            (armario_id, atual["id"]),
        )
        atualizados += 1

    conn_atual.commit()
    return atualizados


def main():
    parser = argparse.ArgumentParser(description="Restaura usuários vinculados ao armário")
    parser.add_argument("--listar", action="store_true", help="Só diagnostica, não altera")
    parser.add_argument("--armario-id", type=int, help="ID do armário alvo (padrão: Matriz)")
    args = parser.parse_args()

    from database import criar_banco
    criar_banco()

    from repositories.base_repository import BaseRepository

    print("=" * 60)
    print("  RESTAURAR USUÁRIOS DO ARMÁRIO")
    print("=" * 60)

    with BaseRepository.get_connection() as conn:
        armario_id, armario_nome = obter_armario_matriz(conn, args.armario_id)
        if not armario_id:
            print("\nERRO: nenhum armário no banco. Rode setup_oficial.py")
            return 1

        print(f"\n  Armário alvo: {armario_nome} (id={armario_id})")

        orfaos = listar_orfaos(conn)
        desvinc = listar_desvinculados(conn)
        vinculados = listar_por_armario(conn, armario_id)

        print(f"\n  Usuários no armário (armario_id={armario_id}): {len(vinculados)}")
        for u in vinculados:
            print(f"    • [{u['perfil']}] {u['nome']} ({u['email']})")

        if orfaos:
            print(f"\n  Órfãos (armario_id inválido): {len(orfaos)}")
            for u in orfaos:
                print(f"    ! id={u['id']} {u['nome']} → armario_id={u['armario_id']} (inexistente)")

        if desvinc:
            print(f"\n  Desvinculados (Operador/Usuário ativo, sem armário): {len(desvinc)}")
            for u in desvinc[:15]:
                print(f"    ? [{u['perfil']}] {u['nome']} ({u['email']})")
            if len(desvinc) > 15:
                print(f"    ... +{len(desvinc) - 15}")

        if args.listar:
            print("\n  Use sem --listar para aplicar correções.")
            print("=" * 60)
            return 0 if vinculados else 1

        print("\n[1] Corrigindo armario_id órfãos...")
        n_orf = corrigir_orfaos(conn, armario_id)
        print(f"    {n_orf} usuário(s) corrigido(s)")

        print("\n[2] Restaurando vínculos do backup (e-mail)...")
        n_bak = restaurar_vinculos_backup(conn, armario_id)
        print(f"    {n_bak} usuário(s) revinculado(s) via backup")

        n_mor = contar_moradores(conn)
        if n_mor == 0:
            print("\n[3] Importando moradores do backup_01...")
            n_imp = copiar_moradores_backup(conn, armario_id)
            print(f"    {n_imp} morador(es) importado(s)")
        else:
            print(f"\n[3] Banco já tem {n_mor} morador(es) — pulando import")

        print(f"\n[4] Vinculando moradores (Usuário) ao armário id={armario_id}...")
        n_vinc = vincular_moradores(conn, armario_id)
        print(f"    {n_vinc} morador(es) atualizado(s)")

        vinculados = listar_por_armario(conn, armario_id)
        print(f"\n  RESULTADO: {len(vinculados)} usuário(s) no armário")
        for u in vinculados:
            print(f"    • [{u['perfil']}] {u['nome']}")

    print("\n" + "=" * 60)
    if vinculados:
        print("  OK — abra Armários → abrir Matriz → Usuários")
        print(f"  http://192.168.16.130:15000/armarios/{armario_id}")
    else:
        print("  AINDA VAZIO — cadastre em Armários → Usuários ou /usuarios")
        print("  Operador global (todos armários) fica só em /usuarios — é normal.")
    print("=" * 60)
    return 0 if vinculados else 1


def contar_moradores(conn):
    return conn.execute("""
        SELECT COUNT(*) AS n FROM usuarios
        WHERE status = 1 AND perfil = 'Usuário'
    """).fetchone()["n"]


if __name__ == "__main__":
    raise SystemExit(main())
