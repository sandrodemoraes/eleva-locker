from repositories.armario_repository import ArmarioRepository
from services.limite_plano_service import LimitePlanoService
from middleware.site_scope import get_site_id


class ArmarioService:

    @staticmethod
    def listar():
        return ArmarioRepository.listar(site_id=get_site_id())

    @staticmethod
    def listar_ativos():
        return ArmarioRepository.listar_ativos()

    @staticmethod
    def buscar_por_id(armario_id):

        armario = ArmarioRepository.buscar_por_id(armario_id)

        if not armario:
            raise ValueError("Armário não encontrado.")

        return armario

    @staticmethod
    def criar(dados):

        nome = dados.get("nome", "").strip()

        if not nome:
            raise ValueError("Nome do armário é obrigatório.")

        dados["nome"] = nome
        dados["status"] = dados.get("status", "ativo")

        empresa_id = dados.get("empresa_id")

        if empresa_id:
            LimitePlanoService.verificar_armario(int(empresa_id))

        if not dados.get("site_id"):
            dados["site_id"] = get_site_id() or 1

        return ArmarioRepository.criar(dados)

    @staticmethod
    def atualizar(armario_id, dados):

        armario = ArmarioService.buscar_por_id(armario_id)

        nome = dados.get("nome", "").strip()

        if not nome:
            raise ValueError("Nome do armário é obrigatório.")

        dados["nome"] = nome

        if dados.get("site_id") is None:
            dados["site_id"] = armario["site_id"] if armario["site_id"] is not None else (get_site_id() or 1)

        ArmarioRepository.atualizar(armario_id, dados)

    @staticmethod
    def excluir(armario_id):

        ArmarioService.buscar_por_id(armario_id)

        ArmarioRepository.excluir(armario_id)

    @staticmethod
    def contar():
        return ArmarioRepository.contar()
