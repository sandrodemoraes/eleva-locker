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
    def sincronizar_compartimentos(esp32_id, max_portas=None):
        """Cria/atualiza compartimentos 1..N vinculados ao ESP."""

        esp = Esp32Repository.buscar_por_id(esp32_id)
        if not esp:
            raise ValueError("ESP32 não encontrado.")

        armario_id = esp["armario"]
        if not armario_id:
            raise ValueError("ESP32 sem armário vinculado.")

        if max_portas is None:
            arm = ArmarioRepository.buscar_por_id(armario_id)
            max_portas = config.normalizar_max_portas(
                (arm["max_portas"] if arm else None) or esp["max_portas"] or 16
            )
        else:
            max_portas = config.normalizar_max_portas(max_portas)

        criados = 0
        atualizados = 0

        for num in range(1, max_portas + 1):
            existe = CompartimentoRepository.buscar_por_armario_numero(armario_id, num)

            dados = {
                "armario": armario_id,
                "numero": num,
                "rele": num,
                "esp32_id": esp32_id,
                "gpio": gpio_para_rele(num),
                "status": "livre",
                "tamanho": tamanho_para_numero(num),
            }

            if existe:
                CompartimentoRepository.atualizar(existe["id"], dados)
                atualizados += 1
            else:
                CompartimentoRepository.criar(dados)
                criados += 1

        removidos = CompartimentoRepository.remover_acima_porta(
            armario_id, esp32_id, max_portas
        )

        Esp32SyncService.incrementar_versao(esp32_id)

        return {
            "esp32_id": esp32_id,
            "max_portas": max_portas,
            "criados": criados,
            "atualizados": atualizados,
            "removidos": removidos,
        }
