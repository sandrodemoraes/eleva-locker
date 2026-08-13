from db.connection import get_engine
from repositories.usuario_repository import UsuarioRepository
from repositories.armario_repository import ArmarioRepository
from repositories.compartimento_repository import CompartimentoRepository
from repositories.encomenda_repository import EncomendaRepository
from repositories.esp32_repository import Esp32Repository
from repositories.notificacao_repository import NotificacaoRepository
from middleware.site_scope import get_site_id


class DashboardService:

    @staticmethod
    def obter_estatisticas():

        site_id = get_site_id()
        Esp32Repository.marcar_offline_expirados()

        armarios = ArmarioRepository.contar(site_id)
        armarios_global = ArmarioRepository.contar(None)

        return {
            "usuarios": len(UsuarioRepository.listar()),
            "armarios": armarios,
            "armarios_global": armarios_global,
            "compartimentos": CompartimentoRepository.contar(site_id),
            "encomendas": EncomendaRepository.contar(site_id=site_id),
            "encomendas_pendentes": EncomendaRepository.contar_pendentes(site_id),
            "esp32_online": Esp32Repository.contar_online(site_id),
            "esp32_total": Esp32Repository.contar(site_id),
            "notificacoes_hoje": NotificacaoRepository.contar_hoje(),
            "site_id": site_id,
            "db_engine": get_engine(),
        }
