#!/usr/bin/env python3
"""
Prepara o armário Bancada para 24 portas (3× ESP 8ch com sensores).

Uso:
  py tools/configurar_bancada_24_portas.py
  py tools/configurar_bancada_24_portas.py --armario-id 3
  py tools/configurar_bancada_24_portas.py --listar

Depois cadastre as ESP novas (módulos 2 e 3):
  py tools/cadastrar_esp_nova.py --ip-esp IP_M2 --nome-esp "ESP Bancada M2" \\
      --armario-id 3 --porta-inicial 9 --portas 8 --max-portas-armario 24
  py tools/cadastrar_esp_nova.py --ip-esp IP_M3 --nome-esp "ESP Bancada M3" \\
      --armario-id 3 --porta-inicial 17 --portas 8 --max-portas-armario 24

Grave o firmware em cada placa com o TOKEN impresso.
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("SKIP_BACKUP", "1")

from database import criar_banco

criar_banco()

import config
from repositories.armario_repository import ArmarioRepository
from repositories.esp32_repository import Esp32Repository
from services.esp32_portas_service import Esp32PortasService
from repositories.base_repository import BaseRepository

NOME_BANCADA = "ELEVA Locker Bancada 2"
TOTAL_PORTAS = 24
MODULOS = (
    (1, "ESP Bancada M1", 1),
    (9, "ESP Bancada M2", 9),
    (17, "ESP Bancada M3", 17),
)


def listar_armarios():
    with BaseRepository.get_connection() as conn:
        rows = conn.execute("""
            SELECT a.id, a.nome, a.max_portas,
                   (SELECT COUNT(*) FROM esp32 e WHERE e.armario = a.id) AS esps
            FROM armarios a
            ORDER BY a.id
        """).fetchall()

    print("\nArmários cadastrados:")
    for r in rows:
        print(f"  id={r['id']} | {r['nome']} | max_portas={r['max_portas']} | ESPs={r['esps']}")
    print()


def resolver_armario(armario_id=None, armario_nome=None):
    if armario_id:
        arm = ArmarioRepository.buscar_por_id(armario_id)
        if not arm:
            raise SystemExit(f"Armário id={armario_id} não encontrado.")
        return arm

    nome = armario_nome or NOME_BANCADA
    with BaseRepository.get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM armarios WHERE nome = ? LIMIT 1",
            (nome,),
        ).fetchone()

    if not row:
        raise SystemExit(
            f"Armário '{nome}' não encontrado. Use --armario-id ou --listar."
        )

    return dict(row)


def sincronizar_modulo(esp, porta_inicial, max_portas=8):
    esp_id = esp["id"]
    Esp32Repository.atualizar(esp_id, {
        "nome": esp["nome"],
        "ip": esp["ip"],
        "mac": esp["mac"] or "",
        "armario": esp["armario"],
        "status": esp["status"],
        "token": esp["token"],
        "porta": esp["porta"] or 80,
        "max_portas": max_portas,
        "porta_inicial": porta_inicial,
    })
    return Esp32PortasService.sincronizar_compartimentos(
        esp_id, max_portas, porta_inicial=porta_inicial,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Configura armário Bancada com 24 portas (3× ESP 8ch)",
    )
    parser.add_argument("--armario-id", type=int, help="ID do armário Bancada")
    parser.add_argument("--armario-nome", help=f"Nome (padrão: {NOME_BANCADA})")
    parser.add_argument("--listar", action="store_true", help="Lista armários e sai")
    parser.add_argument(
        "--portas", type=int, default=TOTAL_PORTAS,
        help=f"Total de compartimentos do armário (padrão: {TOTAL_PORTAS})",
    )
    args = parser.parse_args()

    if args.listar:
        listar_armarios()
        return

    arm = resolver_armario(args.armario_id, args.armario_nome)
    armario_id = arm["id"]
    total = config.normalizar_max_portas(args.portas)

    ArmarioRepository.atualizar(armario_id, {
        "nome": arm["nome"],
        "endereco": arm["endereco"],
        "cidade": arm["cidade"],
        "estado": arm["estado"],
        "status": arm["status"],
        "empresa_id": arm["empresa_id"],
        "site_id": arm["site_id"],
        "max_portas": total,
    })

    esps = Esp32Repository.listar_por_armario(armario_id)
    print(f"\nArmário: {arm['nome']} (id={armario_id}) → {total} portas")
    print(f"ESPs vinculadas: {len(esps)}")

    if not esps:
        print("\nNenhuma ESP no armário. Cadastre a primeira:")
        print(
            f"  py tools/cadastrar_esp_nova.py --ip-esp IP --nome-esp \"ESP Bancada M1\" "
            f"--armario-id {armario_id} --porta-inicial 1 --portas 8 --max-portas-armario {total}"
        )
        return

    esps = sorted(esps, key=lambda e: Esp32PortasService.resolver_porta_inicial(e["id"]))
    for i, esp in enumerate(esps):
        porta_inicial = 1 + (i * 8)
        if porta_inicial + 7 > total:
            print(f"  AVISO: módulo {i + 1} excede {total} portas — verifique cadastro.")
            break

        r = sincronizar_modulo(esp, porta_inicial, max_portas=8)
        print(
            f"  ESP {esp['nome']} (id={esp['id']}): "
            f"compartimentos {r['porta_inicial']}–{r['porta_final']} "
            f"({r['atualizados']} atualizados, {r['criados']} criados)"
        )

    faltam = 3 - len(esps)
    if faltam > 0:
        print(f"\nFaltam {faltam} ESP(s) para completar {total} portas:")
        for _, nome, porta in MODULOS[len(esps):]:
            print(
                f"  py tools/cadastrar_esp_nova.py --ip-esp IP --nome-esp \"{nome}\" "
                f"--armario-id {armario_id} --porta-inicial {porta} --portas 8 "
                f"--max-portas-armario {total}"
            )

    print("\nPróximo passo: grave o firmware em cada placa (TOKEN no cadastro).")
    print(f"Painel: /armarios/{armario_id}")
    print("=" * 62)


if __name__ == "__main__":
    main()
