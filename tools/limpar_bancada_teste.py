#!/usr/bin/env python3
"""
Remove ESP/armário de teste duplicados no mesmo IP da instalação oficial.

Problema comum: ESP Bancada 8ch online + ESP Matriz 8ch offline no mesmo IP,
porque o firmware ainda usa o token antigo.

Uso:
  py tools/limpar_bancada_teste.py
  py tools/limpar_bancada_teste.py --simular
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SKIP_BACKUP", "1")

from database import criar_banco

criar_banco()

from repositories.base_repository import BaseRepository
from repositories.esp32_repository import Esp32Repository
from services.armario_service import ArmarioService

NOME_ARMARIO_OFICIAL = "ELEVA Locker Matriz"
NOME_ESP_OFICIAL = "ESP Matriz 8ch"
NOMES_ESP_TESTE = ("ESP Bancada 8ch", "ESP Bancada", "Bancada 8ch")
NOME_ARMARIO_TESTE = "Bancada Teste"


def listar_esps(conn):
    return conn.execute("""
        SELECT e.id, e.nome, e.ip, e.token, e.status, e.ultimo_heartbeat,
               e.armario, a.nome AS armario_nome
        FROM esp32 e
        LEFT JOIN armarios a ON a.id = e.armario
        ORDER BY e.id
    """).fetchall()


def main():
    parser = argparse.ArgumentParser(description="Remove ESP/armário de bancada duplicados")
    parser.add_argument(
        "--simular", action="store_true",
        help="Mostra o que seria feito, sem alterar o banco",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("LIMPEZA BANCADA TESTE → OFICIAL")
    print("=" * 60)

    with BaseRepository.get_connection() as conn:
        esps = listar_esps(conn)
        print(f"\nESP cadastrados: {len(esps)}")
        for e in esps:
            print(
                f"  id={e['id']} | {e['nome']} | {e['ip'] or '—'} | "
                f"{e['status']} | armário={e['armario_nome'] or '—'}"
            )

        oficial = conn.execute(
            "SELECT id, token FROM esp32 WHERE nome = ? LIMIT 1",
            (NOME_ESP_OFICIAL,),
        ).fetchone()

        if not oficial:
            print(f"\n⚠ ESP oficial '{NOME_ESP_OFICIAL}' não encontrado.")
            print("  Rode: py tools/setup_oficial.py --ip-esp 192.168.16.162 --portas 8")
            return 1

        oficial_ip_row = conn.execute(
            "SELECT ip FROM esp32 WHERE id = ?", (oficial["id"],)
        ).fetchone()
        oficial_ip = oficial_ip_row["ip"] if oficial_ip_row else None

        remover = []
        for e in esps:
            if e["id"] == oficial["id"]:
                continue
            if (
                e["nome"] in NOMES_ESP_TESTE
                or e["armario_nome"] == NOME_ARMARIO_TESTE
                or (oficial_ip and e["ip"] == oficial_ip)
            ):
                remover.append(e)

        if not remover:
            print("\n✅ Nenhum ESP de teste/duplicado para remover.")
        else:
            print(f"\nRemover {len(remover)} ESP(s) de teste/duplicado(s):")
            for e in remover:
                print(f"  - id={e['id']} {e['nome']} ({e['armario_nome'] or 'sem armário'})")
                if not args.simular:
                    Esp32Repository.excluir(e["id"])
                    print("    excluído")

        arm_teste = conn.execute(
            "SELECT id FROM armarios WHERE nome = ? LIMIT 1",
            (NOME_ARMARIO_TESTE,),
        ).fetchone()

        arm_oficial = conn.execute(
            "SELECT id FROM armarios WHERE nome = ? LIMIT 1",
            (NOME_ARMARIO_OFICIAL,),
        ).fetchone()

        if arm_teste:
            restantes = conn.execute(
                "SELECT COUNT(*) AS n FROM esp32 WHERE armario = ?",
                (arm_teste["id"],),
            ).fetchone()["n"]
            comps = conn.execute(
                "SELECT COUNT(*) AS n FROM compartimentos WHERE armario = ?",
                (arm_teste["id"],),
                ).fetchone()["n"]
            enc = conn.execute(
                "SELECT COUNT(*) AS n FROM encomendas e "
                "JOIN compartimentos c ON c.id = e.compartimento "
                "WHERE c.armario = ? AND e.status != 'retirada'",
                (arm_teste["id"],),
            ).fetchone()["n"]

            vinculados = conn.execute(
                "SELECT COUNT(*) AS n FROM usuarios WHERE armario_id = ?",
                (arm_teste["id"],),
            ).fetchone()["n"]

            if restantes == 0 and enc == 0:
                print(f"\nArmário '{NOME_ARMARIO_TESTE}' (id={arm_teste['id']}, {comps} compartimentos)")
                if vinculados and arm_oficial:
                    print(
                        f"  {vinculados} usuário(s) serão migrados para "
                        f"'{NOME_ARMARIO_OFICIAL}' (id={arm_oficial['id']})"
                    )
                if args.simular:
                    print("  seria excluído (sem ESP e sem encomendas ativas)")
                else:
                    try:
                        migrar = arm_oficial["id"] if arm_oficial else None
                        ArmarioService.excluir(arm_teste["id"], migrar_usuarios_para=migrar)
                        if migrar and vinculados:
                            print(f"  excluído — {vinculados} usuário(s) migrados para Matriz")
                        else:
                            print("  excluído")
                    except ValueError as erro:
                        print(f"  não excluído: {erro}")
            else:
                print(
                    f"\nArmário '{NOME_ARMARIO_TESTE}' mantido "
                    f"(esps={restantes}, encomendas ativas={enc})"
                )

    print("\n" + "=" * 60)
    print("PRÓXIMOS PASSOS")
    print("=" * 60)
    print(f"\n1. No firmware elevalocker_sync.ino use o token do ESP oficial:")
    print(f'   ESP32_TOKEN = "{oficial["token"]}"')
    print(f"\n2. Gravar firmware e reiniciar a ESP")
    print(f"\n3. Painel: http://192.168.16.130:15000/armarios")
    print(f"   Abra '{NOME_ARMARIO_OFICIAL}' — ESP deve ficar Online")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
