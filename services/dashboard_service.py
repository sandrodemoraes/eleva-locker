from repositories.usuario_repository import UsuarioRepository
from repositories.armario_repository import ArmarioRepository
from repositories.compartimento_repository import CompartimentoRepository
from repositories.encomenda_repository import EncomendaRepository


class DashboardService:

    @staticmethod
    def obter_estatisticas():

        return {
            "usuarios": len(UsuarioRepository.listar()),
            "armarios": ArmarioRepository.contar(),
            "compartimentos": CompartimentoRepository.contar(),
            "encomendas": EncomendaRepository.contar(),
            "encomendas_pendentes": EncomendaRepository.contar_pendentes(),
        }
