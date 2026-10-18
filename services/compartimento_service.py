from repositories.compartimento_repository import CompartimentoRepository
from repositories.armario_repository import ArmarioRepository
from services.limite_plano_service import LimitePlanoService


class CompartimentoService:

    @staticmethod
    def listar(armario_id=None):
        return CompartimentoRepository.listar(armario_id)

    @staticmethod
    def buscar_por_id(compartimento_id):

        compartimento = CompartimentoRepository.buscar_por_id(compartimento_id)

        if not compartimento:
            raise ValueError("Compartimento não encontrado.")

        return compartimento

    @staticmethod
    def listar_livres(armario_id):
        return CompartimentoRepository.listar_livres(armario_id)

    @staticmethod
    def criar(dados):

        armario_id = dados.get("armario")

        if not armario_id:
            raise ValueError("Selecione um armário.")

        if not ArmarioRepository.buscar_por_id(armario_id):
            raise ValueError("Armário não encontrado.")

        numero = int(dados.get("numero", 0))

        if numero <= 0:
            raise ValueError("Número do compartimento inválido.")

        if CompartimentoRepository.numero_existe(armario_id, numero):
            raise ValueError("Este número já existe neste armário.")

        empresa_id = LimitePlanoService.empresa_id_do_armario(armario_id)
        if empresa_id:
            LimitePlanoService.verificar_compartimento(empresa_id)

        dados["numero"] = numero
        dados["status"] = dados.get("status", "livre")

        return CompartimentoRepository.criar(dados)

    @staticmethod
    def atualizar(compartimento_id, dados):

        CompartimentoService.buscar_por_id(compartimento_id)

        armario_id = dados.get("armario")
        numero = int(dados.get("numero", 0))

        if numero <= 0:
            raise ValueError("Número do compartimento inválido.")

        if CompartimentoRepository.numero_existe(armario_id, numero, compartimento_id):
            raise ValueError("Este número já existe neste armário.")

        empresa_id = LimitePlanoService.empresa_id_do_armario(armario_id)
        if empresa_id:
            LimitePlanoService.verificar_compartimento(empresa_id)

        dados["numero"] = numero

        CompartimentoRepository.atualizar(compartimento_id, dados)

    @staticmethod
    def excluir(compartimento_id):

        compartimento = CompartimentoService.buscar_por_id(compartimento_id)

        if compartimento["status"] == "ocupado":
            raise ValueError("Não é possível excluir compartimento ocupado.")

        CompartimentoRepository.excluir(compartimento_id)

    @staticmethod
    def contar():
        return CompartimentoRepository.contar()
