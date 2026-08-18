#!/usr/bin/env python3
"""
Configura armário ELEVA LOCKER com 8, 16, 24, 32 ou 64 portas (módulos × ESP 8ch).

Uso:
  py tools/configurar_portas_armario.py --armario-id 2 --portas 16
  py tools/configurar_portas_armario.py --armario-id 2 --portas 64
  py tools/configurar_portas_armario.py --listar

Depois cadastre ESPs faltantes com tools/cadastrar_esp_nova.py (ver tools/portas/COMANDOS.txt).
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


def modulos_necessarios(total_portas):
    return max(1, (int(total_portas) + 7) // 8)


def nome_modulo(indice):
    return f"ESP M{indice}"


def porta_inicial_modulo(indice):
    return 1 + (indice - 1) * 8


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
        total = r["max_portas"] or 0
        need = modulos_necessarios(total) if total else "?"
        print(
            f"  id={r['id']} | {r['nome']} | max_portas={r['max_portas']} | "
            f"ESPs={r['esps']} | módulos p/ total={need}"
        )
    print()


def resolver_armario(armario_id=None, armario_nome=None):
    if armario_id:
        arm = ArmarioRepository.buscar_por_id(armario_id)
        if not arm:
            raise SystemExit(f"Armário id={armario_id} não encontrado.")
        return arm

    if not armario_nome:
        raise SystemExit("Informe --armario-id ou --armario-nome.")

    with BaseRepository.get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM armarios WHERE nome = ? LIMIT 1",
            (armario_nome,),
        ).fetchone()

    if not row:
        raise SystemExit(f"Armário '{armario_nome}' não encontrado. Use --listar.")

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


def imprimir_cadastro_esp(armario_id, total, indice_modulo):
    porta = porta_inicial_modulo(indice_modulo)
    nome = nome_modulo(indice_modulo)
    print(
        f"  py tools/cadastrar_esp_nova.py --ip-esp IP_{nome.replace(' ', '_')} "
        f'--nome-esp "{nome}" --armario-id {armario_id} '
        f"--porta-inicial {porta} --portas 8 --max-portas-armario {total}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Configura armário com 8/16/24/32/64 portas (ESP 8ch)",
    )
    parser.add_argument("--armario-id", type=int, help="ID do armário no painel")
    parser.add_argument("--armario-nome", help="Nome do armário (alternativa ao id)")
    parser.add_argument("--listar", action="store_true", help="Lista armários e sai")
    parser.add_argument(
        "--portas", type=int, default=24, choices=config.ESP32_PORTAS_OPCOES,
        help="Total de compartimentos (8, 16, 24, 32 ou 64)",
    )
    args = parser.parse_args()

    if args.listar:
        listar_armarios()
        return

    if not args.armario_id and not args.armario_nome:
        raise SystemExit("Informe --armario-id (ex.: 2) ou --armario-nome.")

    arm = resolver_armario(args.armario_id, args.armario_nome)
    armario_id = arm["id"]
    total = config.normalizar_max_portas(args.portas)
    qtd_modulos = modulos_necessarios(total)

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
    print(f"Módulos necessários: {qtd_modulos} × ESP 8ch")
    print(f"ESPs vinculadas: {len(esps)}")

    if not esps:
        print("\nNenhuma ESP no armário. Cadastre a primeira:")
        imprimir_cadastro_esp(armario_id, total, 1)
        print(f"\nPainel: /armarios/{armario_id}")
        return

    esps = sorted(esps, key=lambda e: Esp32PortasService.resolver_porta_inicial(e["id"]))
    for i, esp in enumerate(esps):
        if i >= qtd_modulos:
            print(f"  AVISO: ESP extra {esp['nome']} — armário só usa {qtd_modulos} módulo(s).")
            continue

        porta_inicial = porta_inicial_modulo(i + 1)
        if porta_inicial + 7 > total:
            print(f"  AVISO: módulo {i + 1} excede {total} portas.")
            break

        r = sincronizar_modulo(esp, porta_inicial, max_portas=8)
        print(
            f"  {esp['nome']} (id={esp['id']}): "
            f"#{r['porta_inicial']}–#{r['porta_final']} "
            f"({r['atualizados']} atualizados, {r['criados']} criados)"
        )

    faltam = qtd_modulos - len(esps)
    if faltam > 0:
        print(f"\nFaltam {faltam} ESP(s) para completar {total} portas:")
        for idx in range(len(esps) + 1, qtd_modulos + 1):
            imprimir_cadastro_esp(armario_id, total, idx)

    print("\nPróximo passo: grave firmware/elevalocker_sync/elevalocker_sync.ino em cada placa.")
    print(f"Painel: http://127.0.0.1:15000/armarios/{armario_id}")
    print("=" * 62)


if __name__ == "__main__":
    main()
