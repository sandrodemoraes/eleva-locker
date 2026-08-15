#!/usr/bin/env python3
"""
Testa backup e restauração do ELEVA LOCKER.

Modos:
  --listar              Conteúdo de cada backup (armários, ESP, usuários…)
  --validar             Valida integridade de todos os backups
  --comparar [N]        Compara banco atual vs backup (padrão: #1)
  --teste               Teste seguro em pasta temporária (não altera produção)
  --restaurar N         Restaura backup #N no projeto (requer --confirmar)

Uso na bancada:
  py tools\\testar_backup_restore.py --listar
  py tools\\testar_backup_restore.py --teste
  py tools\\testar_backup_restore.py --restaurar 1 --confirmar
"""
import argparse
import hashlib
import os
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from services.backup.backup_service import BackupService  # noqa: E402

TABELAS_RESUMO = [
    "armarios",
    "esp32",
    "compartimentos",
    "usuarios",
    "encomendas",
    "sites",
    "empresas",
    "totem_ajuda_pedidos",
]

IGNORAR_COPIA = {
    "__pycache__",
    ".git",
    "venv",
    ".venv",
    "node_modules",
    "backups",
}


def _hash_arquivo(caminho):
    sha = hashlib.sha256()
    with open(caminho, "rb") as f:
        while True:
            bloco = f.read(65536)
            if not bloco:
                break
            sha.update(bloco)
    return sha.hexdigest()


def _resumo_banco(caminho_db):
    if not Path(caminho_db).exists():
        return None

    conn = sqlite3.connect(str(caminho_db))
    conn.row_factory = sqlite3.Row
    resumo = {"caminho": str(caminho_db), "tamanho_kb": Path(caminho_db).stat().st_size // 1024}

    for tabela in TABELAS_RESUMO:
        try:
            resumo[tabela] = conn.execute(
                f"SELECT COUNT(*) AS n FROM {tabela}"
            ).fetchone()["n"]
        except sqlite3.Error:
            resumo[tabela] = None

    try:
        resumo["armarios_lista"] = [
            dict(r) for r in conn.execute("SELECT id, nome, site_id FROM armarios ORDER BY id")
        ]
    except sqlite3.Error:
        resumo["armarios_lista"] = []

    try:
        resumo["esp32_lista"] = [
            dict(r) for r in conn.execute(
                "SELECT id, nome, ip, armario_id, status FROM esp32 ORDER BY id"
            )
        ]
    except sqlite3.Error:
        resumo["esp32_lista"] = []

    try:
        resumo["usuarios_lista"] = [
            dict(r) for r in conn.execute(
                "SELECT id, nome, email, perfil, armario_id FROM usuarios ORDER BY id"
            )
        ]
    except sqlite3.Error:
        resumo["usuarios_lista"] = []

    conn.close()
    return resumo


def _imprimir_resumo(resumo, titulo):
    print(f"\n  {titulo}")
    print(f"  {'─' * 50}")
    if not resumo:
        print("  (banco ausente)")
        return

    print(f"  Arquivo: {resumo['caminho']}")
    print(f"  Tamanho: {resumo['tamanho_kb']} KB")
    for tabela in TABELAS_RESUMO:
        if resumo.get(tabela) is not None:
            print(f"  {tabela}: {resumo[tabela]}")

    for a in resumo.get("armarios_lista", []):
        print(f"    armário id={a['id']} | {a['nome']} | site={a.get('site_id')}")

    for e in resumo.get("esp32_lista", []):
        print(f"    ESP id={e['id']} | {e['nome']} | {e['ip']} | arm={e['armario_id']}")

    for u in resumo.get("usuarios_lista", []):
        print(f"    user id={u['id']} | {u['perfil']} | {u['email']}")


def cmd_listar():
    print("=" * 60)
    print("  BACKUPS DISPONÍVEIS — ELEVA LOCKER")
    print("=" * 60)

    backups = BackupService.listar()
    if not backups:
        print("\n  Nenhum backup encontrado.")
        print("  Rode: tools\\backup_obrigatorio.bat")
        return 1

    for b in backups:
        print(f"\n  backup_{b['numero']:02d} — {b['tamanho_kb']} KB — banco={'OK' if b['tem_banco'] else 'FALTA'}")
        db = Path(b["caminho"]) / "database" / "elevalocker.db"
        env = Path(b["caminho"]) / ".env"
        print(f"    .env: {'OK' if env.exists() else 'FALTA'}")
        _imprimir_resumo(_resumo_banco(db), f"Conteúdo backup #{b['numero']}")

    print("\n" + "=" * 60)
    return 0


def cmd_validar():
    print("=" * 60)
    print("  VALIDAÇÃO DE BACKUPS")
    print("=" * 60)

    ok_total = True
    for i in range(1, int(os.getenv("BACKUP_MAX", "5")) + 1):
        destino = BackupService._destino_backup(i)
        if not destino.exists():
            continue
        ok, msg = BackupService.validar_backup(destino)
        status = "OK" if ok else "ERRO"
        print(f"\n  backup_{i:02d}: {status}")
        print(f"    {msg}")
        ok_total = ok_total and ok

    print("\n" + "=" * 60)
    if ok_total:
        print("  Todos os backups válidos.")
    else:
        print("  Há backups com problemas — corrija antes de restaurar.")
    print("=" * 60)
    return 0 if ok_total else 1


def cmd_comparar(numero):
    print("=" * 60)
    print(f"  COMPARAR — banco atual vs backup #{numero}")
    print("=" * 60)

    atual = _resumo_banco(ROOT / "database" / "elevalocker.db")
    backup_db = BackupService._destino_backup(numero) / "database" / "elevalocker.db"
    backup = _resumo_banco(backup_db)

    _imprimir_resumo(atual, "Banco ATUAL (produção)")
    _imprimir_resumo(backup, f"Backup #{numero}")

    if not backup:
        print("\n  ERRO: backup não encontrado ou sem banco.")
        return 1

    print("\n  Diferenças:")
    difs = []
    for tabela in TABELAS_RESUMO:
        va = atual.get(tabela)
        vb = backup.get(tabela)
        if va != vb:
            difs.append(f"    {tabela}: atual={va} → backup={vb}")

    if not difs:
        print("    Nenhuma diferença nas contagens.")
    else:
        for d in difs:
            print(d)

    if backup_db.exists() and (ROOT / "database" / "elevalocker.db").exists():
        ha = _hash_arquivo(ROOT / "database" / "elevalocker.db")
        hb = _hash_arquivo(backup_db)
        print(f"\n  Hash banco atual:  {ha[:16]}…")
        print(f"  Hash backup #{numero}: {hb[:16]}…")
        print(f"  Idênticos: {'SIM' if ha == hb else 'NÃO'}")

    print("\n" + "=" * 60)
    return 0


def _backup_manual(raiz, destino):
    """Cópia local de backup (isolada do BackupService global)."""
    destino = Path(destino)
    if destino.exists():
        shutil.rmtree(destino)

    for pasta in BackupService.PASTAS:
        origem = Path(raiz) / pasta
        if origem.exists():
            shutil.copytree(origem, destino / pasta, dirs_exist_ok=True)

    for arquivo in BackupService.ARQUIVOS:
        origem = Path(raiz) / arquivo
        if origem.exists():
            destino.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origem, destino / arquivo)

    return destino


def _restaurar_manual(origem, raiz):
    """Restore local (isolado do BackupService global)."""
    origem = Path(origem)
    raiz = Path(raiz)

    for pasta in BackupService.PASTAS:
        origem_pasta = origem / pasta
        if not origem_pasta.exists():
            continue
        destino_pasta = raiz / pasta
        if destino_pasta.exists():
            shutil.rmtree(destino_pasta)
        shutil.copytree(origem_pasta, destino_pasta)

    for arquivo in BackupService.ARQUIVOS:
        origem_arquivo = origem / arquivo
        if origem_arquivo.exists():
            shutil.copy2(origem_arquivo, raiz / arquivo)


def cmd_teste():
    print("=" * 60)
    print("  TESTE DE RESTORE (sandbox — não altera produção)")
    print("=" * 60)

    db_atual = ROOT / "database" / "elevalocker.db"
    if not db_atual.exists():
        print("\n  ERRO: database/elevalocker.db não encontrado.")
        return 1

    hash_producao_antes = _hash_arquivo(db_atual)
    resumo_original = _resumo_banco(db_atual)

    with tempfile.TemporaryDirectory(prefix="eleva_restore_test_") as tmp:
        proj = Path(tmp) / "proj"
        print(f"\n  Pasta temporária: {tmp}")

        def _ignore(dir_path, names):
            rel = Path(dir_path).relative_to(ROOT)
            return [n for n in names if n in IGNORAR_COPIA or (rel.parts and rel.parts[0] in IGNORAR_COPIA)]

        shutil.copytree(ROOT, proj, ignore=_ignore)

        backup_dir = Path(tmp) / "backups" / "backup_01"

        print("\n  [1/4] Criando backup no sandbox…")
        dest = _backup_manual(proj, backup_dir)
        ok, msg = BackupService.validar_backup(dest)
        if not ok:
            print(f"    ERRO: {msg}")
            return 1
        print(f"    OK: {dest}")

        db_sandbox = proj / "database" / "elevalocker.db"
        hash_pos_backup = _hash_arquivo(db_sandbox)

        print("\n  [2/4] Simulando perda de dados (apaga armários e ESP)…")
        conn = sqlite3.connect(str(db_sandbox))
        conn.execute("DELETE FROM esp32")
        conn.execute("DELETE FROM compartimentos")
        conn.execute("DELETE FROM armarios")
        conn.commit()
        conn.close()

        resumo_corrompido = _resumo_banco(db_sandbox)
        if resumo_corrompido["armarios"] != 0:
            print("    ERRO: simulação de perda falhou.")
            return 1
        print(f"    OK — armários={resumo_corrompido['armarios']} esp32={resumo_corrompido['esp32']}")

        print("\n  [3/4] Restaurando backup #1 no sandbox…")
        _restaurar_manual(backup_dir, proj)

        hash_pos_restore = _hash_arquivo(db_sandbox)
        resumo_restaurado = _resumo_banco(db_sandbox)

        print("\n  [4/4] Verificando integridade…")
        ok_hash = hash_pos_restore == hash_pos_backup
        ok_contagens = all(
            resumo_restaurado.get(t) == resumo_original.get(t)
            for t in TABELAS_RESUMO
            if resumo_original.get(t) is not None
        )
        hash_producao_depois = _hash_arquivo(ROOT / "database" / "elevalocker.db")
        ok_producao = hash_producao_depois == hash_producao_antes

        print(f"    Hash sandbox restaurado: {'SIM' if ok_hash else 'NÃO'}")
        print(f"    Contagens iguais: {'SIM' if ok_contagens else 'NÃO'}")
        print(f"    Produção intacta: {'SIM' if ok_producao else 'NÃO'}")

        for tabela in TABELAS_RESUMO:
            vo = resumo_original.get(tabela)
            vr = resumo_restaurado.get(tabela)
            if vo != vr:
                print(f"      {tabela}: antes={vo} depois={vr}")

    print("\n" + "=" * 60)
    if ok_hash and ok_contagens and ok_producao:
        print("  TESTE OK — backup restaura banco e dados corretamente.")
        print("  Produção NÃO foi alterada.")
    else:
        print("  TESTE FALHOU — verifique a lógica de backup/restore.")
    print("=" * 60)
    return 0 if (ok_hash and ok_contagens and ok_producao) else 1


def cmd_restaurar(numero, confirmar):
    print("=" * 60)
    print(f"  RESTAURAR backup #{numero} — PRODUÇÃO")
    print("=" * 60)

    origem = BackupService._destino_backup(numero)
    if not origem.exists():
        print(f"\n  ERRO: backup #{numero} não encontrado em {origem}")
        return 1

    ok, msg = BackupService.validar_backup(origem)
    if not ok:
        print(f"\n  ERRO: backup inválido — {msg}")
        return 1

    _imprimir_resumo(_resumo_banco(ROOT / "database" / "elevalocker.db"), "ANTES (atual)")
    _imprimir_resumo(
        _resumo_banco(origem / "database" / "elevalocker.db"),
        f"DEPOIS (backup #{numero})",
    )

    if not confirmar:
        print("\n  ⚠ Operação destrutiva — sobrescreve database/, uploads/, config/, logs/, .env")
        print("  Para executar, adicione: --confirmar")
        print("\n  Recomendado antes:")
        print("    tools\\backup_obrigatorio.bat")
        print("=" * 60)
        return 1

    print("\n  Criando backup de segurança antes de restaurar…")
    ok_bak, msg_bak = BackupService.criar_backup_obrigatorio()
    if not ok_bak:
        print(f"  ERRO: não foi possível criar backup de segurança — {msg_bak}")
        return 1
    print(f"  OK — estado atual salvo em backup_01 (antigo virou backup_02)")

    print(f"\n  Restaurando backup #{numero}…")
    BackupService.restaurar(numero)

    _imprimir_resumo(_resumo_banco(ROOT / "database" / "elevalocker.db"), "RESULTADO")

    print("\n  Reinicie o servidor: tools\\iniciar_elevalocker.bat")
    print("=" * 60)
    return 0


def main():
    parser = argparse.ArgumentParser(description="Testa backup/restauração ELEVA LOCKER")
    parser.add_argument("--listar", action="store_true", help="Lista conteúdo dos backups")
    parser.add_argument("--validar", action="store_true", help="Valida integridade dos backups")
    parser.add_argument("--comparar", type=int, nargs="?", const=1, metavar="N",
                        help="Compara banco atual vs backup N (padrão: 1)")
    parser.add_argument("--teste", action="store_true", help="Teste seguro em pasta temporária")
    parser.add_argument("--restaurar", type=int, metavar="N", help="Restaura backup #N na produção")
    parser.add_argument("--confirmar", action="store_true", help="Confirma restore na produção")
    args = parser.parse_args()

    if args.listar:
        return cmd_listar()
    if args.validar:
        return cmd_validar()
    if args.comparar is not None:
        return cmd_comparar(args.comparar)
    if args.teste:
        return cmd_teste()
    if args.restaurar is not None:
        return cmd_restaurar(args.restaurar, args.confirmar)

    parser.print_help()
    print("\nExemplos:")
    print("  py tools\\testar_backup_restore.py --listar")
    print("  py tools\\testar_backup_restore.py --teste")
    print("  py tools\\testar_backup_restore.py --comparar 2")
    print("  py tools\\testar_backup_restore.py --restaurar 1 --confirmar")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
