#!/usr/bin/env python3
"""
Configura bancada de teste: armário + ESP32 + 8 compartimentos.
Uso: python tools/setup_bancada.py [--ip-esp 192.168.16.162]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SKIP_BACKUP", "1")

from database import criar_banco

criar_banco()

from repositories.armario_repository import ArmarioRepository
from repositories.compartimento_repository import CompartimentoRepository
from repositories.esp32_repository import Esp32Repository
from services.esp32_service import Esp32Service
from services.compartimento_service import CompartimentoService
from repositories.base_repository import BaseRepository

GPIO_BANCADA = [16, 17, 18, 19, 21, 22, 23, 25]


def main():

    parser = argparse.ArgumentParser(description="Setup bancada ELEVA LOCKER")
    parser.add_argument("--ip-esp", default="192.168.16.162", help="IP da ESP32")
    parser.add_argument("--nome-esp", default="ESP Bancada 8ch", help="Nome do ESP")
    args = parser.parse_args()

    with BaseRepository.get_connection() as conn:
        arm = conn.execute("""
            SELECT id FROM armarios WHERE nome = 'Bancada Teste' LIMIT 1
        """).fetchone()

    if arm:
        armario_id = arm["id"]
        print(f"Armário 'Bancada Teste' já existe (id={armario_id})")
    else:
        armario_id = ArmarioRepository.criar({
            "nome": "Bancada Teste",
            "endereco": "Laboratório ELEVA",
            "cidade": "Bancada",
            "estado": "SP",
            "status": "ativo",
            "empresa_id": None,
            "site_id": 1,
        })
        print(f"Armário criado id={armario_id}")

    esp_id = None
    token = None

    with BaseRepository.get_connection() as conn:
        row = conn.execute("""
            SELECT id, token FROM esp32 WHERE nome = ? LIMIT 1
        """, (args.nome_esp,)).fetchone()

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
            "max_portas": 8,
        })
        print(f"ESP atualizado id={esp_id} ip={args.ip_esp}")
    else:
        esp_id = Esp32Service.criar({
            "nome": args.nome_esp,
            "ip": args.ip_esp,
            "mac": "",
            "armario": armario_id,
            "porta": 80,
            "max_portas": 8,
            "status": "offline",
        })
        esp = Esp32Repository.buscar_por_id(esp_id)
        token = esp["token"]
        print(f"ESP criado id={esp_id} ip={args.ip_esp}")

    for num in range(1, 9):
        with BaseRepository.get_connection() as conn:
            existe = conn.execute("""
                SELECT id FROM compartimentos
                WHERE armario = ? AND numero = ?
            """, (armario_id, num)).fetchone()

        dados = {
            "armario": armario_id,
            "numero": num,
            "rele": num,
            "esp32_id": esp_id,
            "gpio": GPIO_BANCADA[num - 1],
            "status": "livre",
            "tamanho": "M",
        }

        if existe:
            CompartimentoRepository.atualizar(existe["id"], dados)
            print(f"  Compartimento #{num} atualizado (rele={num}, gpio={GPIO_BANCADA[num-1]})")
        else:
            CompartimentoService.criar(dados)
            print(f"  Compartimento #{num} criado (rele={num}, gpio={GPIO_BANCADA[num-1]})")

    print("\n" + "=" * 60)
    print("BANCADA CONFIGURADA")
    print("=" * 60)
    print(f"\n1. No firmware elevalocker_sync.ino configure:")
    print(f'   SERVIDOR_URL = "http://SEU_IP_PC:15000"')
    print(f'   ESP32_TOKEN  = "{token}"')
    print(f"\n2. Painel: http://localhost:15000/esp32")
    print(f"   IP ESP: {args.ip_esp} | Max portas: 8")
    print(f"\n3. Teste: http://localhost:15000/esp32/bancada")
    print(f"\n4. Token (copie para o .ino):")
    print(f"   {token}")
    print("=" * 60)


if __name__ == "__main__":
    main()
