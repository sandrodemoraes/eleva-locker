from repositories.usuario_repository import UsuarioRepository
from repositories.armario_repository import ArmarioRepository
from repositories.compartimento_repository import CompartimentoRepository
from repositories.encomenda_repository import EncomendaRepository
from repositories.esp32_repository import Esp32Repository


class DashboardService:

    @staticmethod
    def obter_estatisticas():

        Esp32Repository.marcar_offline_expirados()

        return {
            "usuarios": len(UsuarioRepository.listar()),
            "armarios": ArmarioRepository.contar(),
            "compartimentos": CompartimentoRepository.contar(),
            "encomendas": EncomendaRepository.contar(),
            "encomendas_pendentes": EncomendaRepository.contar_pendentes(),
            "esp32_online": Esp32Repository.contar_online(),
            "esp32_total": len(Esp32Repository.listar()),
        }
