"""Sincroniza compartimentos com max_portas do ESP32 (8/16/24/32/64)."""

import config
from repositories.compartimento_repository import CompartimentoRepository
from repositories.esp32_repository import Esp32Repository
from repositories.armario_repository import ArmarioRepository
from services.esp32_sync_service import Esp32SyncService

GPIO_PADRAO = [16, 17, 18, 19, 21, 22, 23, 27, 26, 32, 33, 12, 13, 14, 15]
TAMANHO_CICLO_8 = ["P", "P", "P", "P", "M", "M", "G", "GG"]


def gpio_para_rele(rele):
    if rele <= 0:
        return None
    return GPIO_PADRAO[(rele - 1) % len(GPIO_PADRAO)]


def tamanho_para_numero(numero):
    pos = (int(numero) - 1) % 8
    return TAMANHO_CICLO_8[pos]


class Esp32PortasService:

    @staticmethod
    def resolver_porta_inicial(esp32_id, porta_inicial=None):
        if porta_inicial is not None:
            return int(porta_inicial)

        esp = Esp32Repository.buscar_por_id(esp32_id)
        if esp and esp["porta_inicial"]:
            return int(esp["porta_inicial"])

        from repositories.base_repository import BaseRepository

        with BaseRepository.get_connection() as conn:
            row = conn.execute("""
                SELECT MIN(numero) AS n
                FROM compartimentos
                WHERE esp32_id = ?
            """, (esp32_id,)).fetchone()

        if row and row["n"]:
            return int(row["n"])

        return 1

    @staticmethod
    def proxima_porta_inicial_armario(armario_id):
        esps = Esp32Repository.listar_por_armario(armario_id)
        if not esps:
            return 1

        ultimo = 0
        for esp in esps:
            porta = Esp32PortasService.resolver_porta_inicial(esp["id"])
            max_esp = config.normalizar_max_portas(esp["max_portas"] or 8)
            ultimo = max(ultimo, porta + max_esp - 1)

        return ultimo + 1

    @staticmethod
    def sincronizar_compartimentos(esp32_id, max_portas=None, porta_inicial=None):
        """
        Cria/atualiza compartimentos vinculados ao ESP.

        Multi-módulo (ex.: armário 24 portas, 3× ESP 8ch):
          ESP A: porta_inicial=1  → compartimentos 1–8,  relés locais 1–8
          ESP B: porta_inicial=9  → compartimentos 9–16, relés locais 1–8
          ESP C: porta_inicial=17 → compartimentos 17–24, relés locais 1–8
        """

        esp = Esp32Repository.buscar_por_id(esp32_id)
        if not esp:
            raise ValueError("ESP32 não encontrado.")

        armario_id = esp["armario"]
        if not armario_id:
            raise ValueError("ESP32 sem armário vinculado.")

        porta_inicial = Esp32PortasService.resolver_porta_inicial(esp32_id, porta_inicial)
        if porta_inicial < 1:
            raise ValueError("porta_inicial deve ser >= 1.")

        if max_portas is None:
            max_portas = config.normalizar_max_portas(esp["max_portas"] or 8)
        else:
            max_portas = config.normalizar_max_portas(max_portas)

        arm = ArmarioRepository.buscar_por_id(armario_id)
        max_armario = config.normalizar_max_portas(
            (arm["max_portas"] if arm else None) or max_portas
        )

        criados = 0
        atualizados = 0

        for i in range(max_portas):
            num = porta_inicial + i
            rele_local = i + 1
            existe = CompartimentoRepository.buscar_por_armario_numero(armario_id, num)

            dados = {
                "armario": armario_id,
                "numero": num,
                "rele": rele_local,
                "esp32_id": esp32_id,
                "gpio": gpio_para_rele(rele_local),
                "status": "livre",
                "tamanho": tamanho_para_numero(num),
            }

            if existe:
                dados["status"] = existe["status"]
                CompartimentoRepository.atualizar(existe["id"], dados)
                atualizados += 1
            else:
                CompartimentoRepository.criar(dados)
                criados += 1

        removidos = 0
        if porta_inicial == 1:
            removidos = CompartimentoRepository.remover_acima_porta(armario_id, max_armario)

        Esp32Repository.atualizar(esp32_id, {
            "nome": esp["nome"],
            "ip": esp["ip"],
            "mac": esp["mac"] or "",
            "armario": armario_id,
            "status": esp["status"],
            "token": esp["token"],
            "porta": esp["porta"] or 80,
            "max_portas": max_portas,
            "porta_inicial": porta_inicial,
        })

        Esp32SyncService.incrementar_versao(esp32_id)

        return {
            "esp32_id": esp32_id,
            "max_portas": max_portas,
            "porta_inicial": porta_inicial,
            "porta_final": porta_inicial + max_portas - 1,
            "criados": criados,
            "atualizados": atualizados,
            "removidos": removidos,
        }
