import config
from repositories.armario_repository import ArmarioRepository
from repositories.esp32_repository import Esp32Repository
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
        dados["max_portas"] = config.normalizar_max_portas(dados.get("max_portas") or 16)

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

        if "max_portas" in dados:
            dados["max_portas"] = config.normalizar_max_portas(dados.get("max_portas") or armario["max_portas"] or 16)

        ArmarioRepository.atualizar(armario_id, dados)

        if "max_portas" in dados:
            ArmarioService._sincronizar_portas_armario(armario_id, dados["max_portas"])

    @staticmethod
    def _sincronizar_portas_armario(armario_id, max_portas):
        from services.esp32_portas_service import Esp32PortasService

        esps = Esp32Repository.listar_por_armario(armario_id)
        for esp in esps:
            Esp32Repository.atualizar(esp["id"], {
                "nome": esp["nome"],
                "ip": esp["ip"],
                "mac": esp["mac"] or "",
                "armario": armario_id,
                "status": esp["status"],
                "token": esp["token"],
                "porta": esp["porta"] or 80,
                "max_portas": max_portas,
            })
            Esp32PortasService.sincronizar_compartimentos(esp["id"], max_portas)

    @staticmethod
    def excluir(armario_id):

        ArmarioService.buscar_por_id(armario_id)

        ArmarioRepository.excluir(armario_id)

    @staticmethod
    def contar():
        return ArmarioRepository.contar()
