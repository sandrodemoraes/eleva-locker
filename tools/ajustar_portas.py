#!/usr/bin/env python3
"""
Altera quantidade de portas de um ESP (8, 16, 24, 32, 64) e sincroniza compartimentos.

Uso:
  py tools/ajustar_portas.py --portas 16
  py tools/ajustar_portas.py --nome-esp "ESP Matriz 8ch" --portas 32
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SKIP_BACKUP", "1")

from database import criar_banco

criar_banco()

import config
from repositories.base_repository import BaseRepository
from repositories.esp32_repository import Esp32Repository
from repositories.armario_repository import ArmarioRepository
from services.esp32_portas_service import Esp32PortasService


def main():
    parser = argparse.ArgumentParser(description="Ajusta portas do ESP32")
    parser.add_argument("--portas", type=int, required=True, choices=config.ESP32_PORTAS_OPCOES)
    parser.add_argument("--porta-inicial", type=int, help="1º compartimento desta ESP (ex.: 9)")
    parser.add_argument("--nome-esp", default="ESP Matriz 8ch")
    args = parser.parse_args()

    max_portas = config.normalizar_max_portas(args.portas)

    with BaseRepository.get_connection() as conn:
        esp = conn.execute(
            "SELECT * FROM esp32 WHERE nome = ? LIMIT 1",
            (args.nome_esp,),
        ).fetchone()

    if not esp:
        print(f"ESP '{args.nome_esp}' não encontrado.")
        sys.exit(1)

    esp_id = esp["id"]
    print(f"ESP {args.nome_esp} (id={esp_id}): {esp['max_portas']} → {max_portas} portas")

    Esp32Repository.atualizar(esp_id, {
        "nome": esp["nome"],
        "ip": esp["ip"],
        "mac": esp["mac"] or "",
        "armario": esp["armario"],
        "status": esp["status"],
        "token": esp["token"],
        "porta": esp["porta"] or 80,
        "max_portas": max_portas,
        "porta_inicial": args.porta_inicial or esp["porta_inicial"] or 1,
    })

    if esp["armario"]:
        arm = ArmarioRepository.buscar_por_id(esp["armario"])
        if arm:
            ArmarioRepository.atualizar(esp["armario"], {
                "nome": arm["nome"],
                "endereco": arm["endereco"],
                "cidade": arm["cidade"],
                "estado": arm["estado"],
                "status": arm["status"],
                "empresa_id": arm["empresa_id"],
                "site_id": arm["site_id"],
                "max_portas": max_portas,
            })

    porta_inicial = args.porta_inicial
    r = Esp32PortasService.sincronizar_compartimentos(
        esp_id, max_portas, porta_inicial=porta_inicial,
    )
    print(
        f"OK — compartimentos {r['porta_inicial']}–{r['porta_final']}: "
        f"{r['criados']} criados, {r['atualizados']} atualizados, {r['removidos']} removidos"
    )
    print("Regrave o firmware (suporta até 64 portas) e aguarde Sync na ESP.")


if __name__ == "__main__":
    main()
