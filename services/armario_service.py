from repositories.armario_repository import ArmarioRepository


class ArmarioService:

    @staticmethod
    def listar():
        return ArmarioRepository.listar()

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

        return ArmarioRepository.criar(dados)

    @staticmethod
    def atualizar(armario_id, dados):

        ArmarioService.buscar_por_id(armario_id)

        nome = dados.get("nome", "").strip()

        if not nome:
            raise ValueError("Nome do armário é obrigatório.")

        dados["nome"] = nome

        ArmarioRepository.atualizar(armario_id, dados)

    @staticmethod
    def excluir(armario_id):

        ArmarioService.buscar_por_id(armario_id)

        ArmarioRepository.excluir(armario_id)

    @staticmethod
    def contar():
        return ArmarioRepository.contar()
