#!/usr/bin/env python3
"""
Configura instalação OFICIAL ELEVA LOCKER: empresa + armário + ESP32 + 8 compartimentos.

Substitui o fluxo de "Bancada Teste" para operação real no painel.

Uso:
  py tools/setup_oficial.py
  py tools/setup_oficial.py --ip-esp 192.168.16.162
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SKIP_BACKUP", "1")

from database import criar_banco

criar_banco()

import config
from repositories.armario_repository import ArmarioRepository
from repositories.empresa_repository import EmpresaRepository
from repositories.esp32_repository import Esp32Repository
from services.esp32_service import Esp32Service
from services.esp32_portas_service import Esp32PortasService
from repositories.base_repository import BaseRepository

NOME_ARMARIO = "ELEVA Locker Matriz"
NOME_ESP = "ESP Matriz 8ch"
RAZAO_EMPRESA = "ELEVA Energia Solar Ltda"
FANTASIA_EMPRESA = "ELEVA Energia Solar"


def obter_site_id(conn):
    row = conn.execute("SELECT id FROM sites ORDER BY id LIMIT 1").fetchone()
    return row["id"] if row else 1


def obter_ou_criar_empresa(conn, site_id):
    row = conn.execute("""
        SELECT id FROM empresas WHERE razao_social = ? LIMIT 1
    """, (RAZAO_EMPRESA,)).fetchone()

    if row:
        print(f"Empresa já existe (id={row['id']})")
        return row["id"]

    empresa_id = EmpresaRepository.inserir({
        "razao_social": RAZAO_EMPRESA,
        "nome_fantasia": FANTASIA_EMPRESA,
        "cnpj": "",
        "inscricao_estadual": "",
        "responsavel": "ELEVA",
        "telefone": "",
        "whatsapp": "",
        "email": "contato@elevaenergiasolar.com.br",
        "cep": "",
        "endereco": "Matriz ELEVA",
        "numero": "",
        "bairro": "",
        "cidade": "São Paulo",
        "estado": "SP",
        "status": 1,
    })
    print(f"Empresa criada id={empresa_id}")
    return empresa_id


def main():
    parser = argparse.ArgumentParser(description="Setup oficial ELEVA LOCKER")
    parser.add_argument("--ip-esp", default="192.168.16.162", help="IP da ESP32")
    parser.add_argument("--nome-armario", default=NOME_ARMARIO, help="Nome do armário")
    parser.add_argument("--nome-esp", default=NOME_ESP, help="Nome do ESP32")
    parser.add_argument(
        "--portas", type=int, default=8, choices=config.ESP32_PORTAS_OPCOES,
        help="Quantidade de portas (8, 16, 24, 32, 64)",
    )
    args = parser.parse_args()

    max_portas = config.normalizar_max_portas(args.portas)

    with BaseRepository.get_connection() as conn:
        site_id = obter_site_id(conn)
        empresa_id = obter_ou_criar_empresa(conn, site_id)

        arm = conn.execute(
            "SELECT id FROM armarios WHERE nome = ? LIMIT 1",
            (args.nome_armario,),
        ).fetchone()

    if arm:
        armario_id = arm["id"]
        ArmarioRepository.atualizar(armario_id, {
            "nome": args.nome_armario,
            "endereco": "Matriz ELEVA — Instalação oficial",
            "cidade": "São Paulo",
            "estado": "SP",
            "status": "ativo",
            "empresa_id": empresa_id,
            "site_id": site_id,
            "max_portas": max_portas,
        })
        print(f"Armário '{args.nome_armario}' atualizado (id={armario_id})")
    else:
        armario_id = ArmarioRepository.criar({
            "nome": args.nome_armario,
            "endereco": "Matriz ELEVA — Instalação oficial",
            "cidade": "São Paulo",
            "estado": "SP",
            "status": "ativo",
            "empresa_id": empresa_id,
            "site_id": site_id,
            "max_portas": max_portas,
        })
        print(f"Armário criado id={armario_id}")

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
        })
        print(f"ESP atualizado id={esp_id} ip={args.ip_esp} portas={max_portas}")
    else:
        esp_id = Esp32Service.criar({
            "nome": args.nome_esp,
            "ip": args.ip_esp,
            "mac": "",
            "armario": armario_id,
            "porta": 80,
            "max_portas": max_portas,
            "status": "offline",
        })
        esp = Esp32Repository.buscar_por_id(esp_id)
        token = esp["token"]
        print(f"ESP criado id={esp_id} ip={args.ip_esp} portas={max_portas}")

    resultado = Esp32PortasService.sincronizar_compartimentos(esp_id, max_portas)
    print(f"  Compartimentos: {resultado['criados']} criados, {resultado['atualizados']} atualizados")

    with BaseRepository.get_connection() as conn:
        revinc = conn.execute("""
            UPDATE usuarios SET armario_id = ?
            WHERE perfil = 'Usuário' AND status = 1
              AND (armario_id IS NULL OR armario_id != ?)
        """, (armario_id, armario_id)).rowcount

        orfaos = conn.execute("""
            UPDATE usuarios SET armario_id = ?
            WHERE perfil IN ('Usuário', 'Operador') AND status = 1
              AND armario_id IS NOT NULL
              AND armario_id NOT IN (SELECT id FROM armarios)
        """, (armario_id,)).rowcount
        conn.commit()
    if revinc:
        print(f"  Moradores revinculados ao armário: {revinc}")
    if orfaos:
        print(f"  Usuários com armario_id órfão corrigidos: {orfaos}")

    print("\n" + "=" * 60)
    print("INSTALAÇÃO OFICIAL CONFIGURADA")
    print("=" * 60)
    print(f"\n  Armário : {args.nome_armario}")
    print(f"  ESP32   : {args.nome_esp} @ {args.ip_esp}")
    print(f"  Portas  : {max_portas}")
    print(f"  Empresa : {FANTASIA_EMPRESA}")
    print(f"\n  Firmware elevalocker_sync.ino:")
    print(f'    SERVIDOR_URL = "http://192.168.16.130:15000"')
    print(f'    ESP32_TOKEN  = "{token}"')
    print(f"\n  Painel:")
    print(f"    http://192.168.16.130:15000/armarios")
    print(f"    http://192.168.16.130:15000/encomendas")
    print(f"    http://192.168.16.130:15000/esp32/bancada  (teste relés)")
    print(f"\n  Totem ESP: http://{args.ip_esp}/")
    print(f"\n  TOKEN (copie para o .ino):")
    print(f"  {token}")
    print("=" * 60)


if __name__ == "__main__":
    main()
