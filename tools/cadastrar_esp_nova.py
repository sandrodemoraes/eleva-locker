#!/usr/bin/env python3
"""
Cadastra uma ESP32 nova no servidor (mesmo padrão da Matriz / bancada).

Uso:
  py tools/cadastrar_esp_nova.py --ip-esp 192.168.16.105
  py tools/cadastrar_esp_nova.py --ip-esp 192.168.16.105 --armario-id 2
  py tools/cadastrar_esp_nova.py --ip-esp 192.168.16.105 --armario-nome "Bancada 2"
  py tools/cadastrar_esp_nova.py --ip-esp 192.168.16.106 --armario-id 3 --porta-inicial 9 --portas 8

Depois: grave o firmware com o TOKEN impresso abaixo.
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
from services.esp32_service import Esp32Service
from services.esp32_portas_service import Esp32PortasService
from repositories.base_repository import BaseRepository

SERVIDOR_PADRAO = "http://192.168.16.130:15000"
NOME_ARMARIO_NOVO = "ELEVA Locker Bancada 2"


def obter_site_id(conn):
    row = conn.execute("SELECT id FROM sites ORDER BY id LIMIT 1").fetchone()
    return row["id"] if row else 1


def resolver_armario(args):
    if args.armario_id:
        arm = ArmarioRepository.buscar_por_id(args.armario_id)
        if not arm:
            raise SystemExit(f"Armário id={args.armario_id} não encontrado.")
        return arm["id"], arm["nome"]

    nome = args.armario_nome or NOME_ARMARIO_NOVO
    with BaseRepository.get_connection() as conn:
        row = conn.execute(
            "SELECT id, nome FROM armarios WHERE nome = ? LIMIT 1",
            (nome,),
        ).fetchone()

    if row:
        return row["id"], row["nome"]

    if not args.criar_armario and not args.armario_nome:
        print(f"Armário '{nome}' não existe.")
        print("  Use --criar-armario ou --armario-id ID")
        raise SystemExit(1)

    site_id = 1
    with BaseRepository.get_connection() as conn:
        site_id = obter_site_id(conn)

    max_portas = config.normalizar_max_portas(args.portas)
    armario_id = ArmarioRepository.criar({
        "nome": nome,
        "endereco": "Bancada ELEVA",
        "cidade": "São Paulo",
        "estado": "SP",
        "status": "ativo",
        "empresa_id": None,
        "site_id": site_id,
        "max_portas": max_portas,
    })
    print(f"Armário criado: {nome} (id={armario_id})")
    return armario_id, nome


def main():
    parser = argparse.ArgumentParser(description="Cadastrar ESP32 nova no ELEVA LOCKER")
    parser.add_argument("--ip-esp", required=True, help="IP da ESP na rede Wi-Fi (obrigatório)")
    parser.add_argument("--nome-esp", default="ESP Bancada 2", help="Nome no painel")
    parser.add_argument("--armario-id", type=int, help="Vincular a armário existente")
    parser.add_argument("--armario-nome", help="Nome do armário (cria se --criar-armario)")
    parser.add_argument(
        "--criar-armario", action="store_true",
        help=f"Cria armário '{NOME_ARMARIO_NOVO}' se não existir",
    )
    parser.add_argument(
        "--portas", type=int, default=8, choices=config.ESP32_PORTAS_OPCOES,
        help="Portas desta ESP (relés locais 1..N)",
    )
    parser.add_argument(
        "--porta-inicial", type=int, default=1,
        help="Nº do 1º compartimento no armário (ex.: 9 para módulo B em armário 24)",
    )
    parser.add_argument(
        "--max-portas-armario", type=int,
        help="Total de portas do armário (ex.: 24). Atualiza o armário ao cadastrar.",
    )
    parser.add_argument("--servidor", default=SERVIDOR_PADRAO, help="URL para o firmware")
    args = parser.parse_args()

    if not args.armario_id and not args.criar_armario and not args.armario_nome:
        args.criar_armario = True

    armario_id, armario_nome = resolver_armario(args)
    max_portas = config.normalizar_max_portas(args.portas)
    porta_inicial = int(args.porta_inicial)
    if porta_inicial < 1:
        raise SystemExit("porta-inicial deve ser >= 1.")

    arm = ArmarioRepository.buscar_por_id(armario_id)
    max_armario = max_portas
    if args.max_portas_armario:
        max_armario = config.normalizar_max_portas(args.max_portas_armario)
    elif arm and arm["max_portas"]:
        max_armario = config.normalizar_max_portas(arm["max_portas"])
    if porta_inicial + max_portas - 1 > max_armario:
        max_armario = config.normalizar_max_portas(porta_inicial + max_portas - 1)

    ArmarioRepository.atualizar(armario_id, {
        "nome": armario_nome,
        "endereco": arm.get("endereco") if arm else "Bancada ELEVA",
        "cidade": arm.get("cidade") if arm else "São Paulo",
        "estado": arm.get("estado") if arm else "SP",
        "status": "ativo",
        "empresa_id": arm.get("empresa_id") if arm else None,
        "site_id": arm.get("site_id") if arm else 1,
        "max_portas": max_armario,
    })

    with BaseRepository.get_connection() as conn:
        row = conn.execute(
            "SELECT id, token FROM esp32 WHERE nome = ? LIMIT 1",
            (args.nome_esp,),
        ).fetchone()

    if row:
        esp_id = row["id"]
        token = row["token"]
        Esp32Repository.atualizar(esp_id, {
            "nome": args.nome_esp,
            "ip": args.ip_esp,
            "mac": "",
            "armario": armario_id,
            "porta": 80,
            "status": "offline",
            "token": token,
            "max_portas": max_portas,
            "porta_inicial": porta_inicial,
        })
        print(f"ESP atualizada id={esp_id} ip={args.ip_esp}")
    else:
        esp_id = Esp32Repository.criar({
            "nome": args.nome_esp,
            "ip": args.ip_esp,
            "mac": "",
            "armario": armario_id,
            "porta": 80,
            "max_portas": max_portas,
            "porta_inicial": porta_inicial,
            "status": "offline",
            "token": config.gerar_token_esp32(),
        })
        esp = Esp32Repository.buscar_por_id(esp_id)
        token = esp["token"]
        print(f"ESP criada id={esp_id} ip={args.ip_esp}")

    resultado = Esp32PortasService.sincronizar_compartimentos(
        esp_id, max_portas, porta_inicial=porta_inicial,
    )
    print(
        f"Compartimentos {resultado['porta_inicial']}–{resultado['porta_final']}: "
        f"{resultado['criados']} criados, {resultado['atualizados']} atualizados"
    )

    print("\n" + "=" * 62)
    print("  ESP NOVA CADASTRADA — próximo passo: gravar firmware")
    print("=" * 62)
    print(f"\n  Painel : {args.servidor}/armarios/{armario_id}")
    print(f"  Armário: {armario_nome} (id={armario_id})")
    print(f"  ESP    : {args.nome_esp} (id={esp_id})")
    print(f"  Portas : {porta_inicial}–{porta_inicial + max_portas - 1} (relés locais 1–{max_portas})")
    print(f"  Armário total: {max_armario} compartimentos")
    print(f"  IP     : {args.ip_esp}")
    print(f"  Token  : {token}")
    print("\n--- Arduino: firmware/elevalocker_sync/elevalocker_sync.ino ---")
    print('const char* WIFI_SSID     = "ELEVA - ENERGIA SOLAR";')
    print('const char* WIFI_PASSWORD = "eleva2277";')
    print(f'const char* SERVIDOR_URL  = "{args.servidor}";')
    print(f'const char* ESP32_TOKEN   = "{token}";')
    print("const bool RELE_ATIVO_LOW = true;   // placa BESTER 8ch")
    print("\n--- Teste após gravar ---")
    print(f"  py tools/testar_token_esp.py --url {args.servidor} --token {token}")
    print(f"  Browser: http://{args.ip_esp}/?token={token}")
    print(f"  Painel: botão Testar Wi-Fi em /armarios/{armario_id}")
    print("=" * 62)


if __name__ == "__main__":
    main()
