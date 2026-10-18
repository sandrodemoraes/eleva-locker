from repositories.plano_repository import PlanoRepository


class PlanoService:

    @staticmethod
    def listar():
        return PlanoRepository.listar()

    @staticmethod
    def listar_todos():
        return PlanoRepository.listar_todos()

    @staticmethod
    def buscar_por_id(plano_id):

        plano = PlanoRepository.buscar_por_id(plano_id)

        if not plano:
            raise ValueError("Plano não encontrado.")

        return plano

    @staticmethod
    def criar(dados):

        nome = dados.get("nome", "").strip()

        if not nome:
            raise ValueError("Nome do plano é obrigatório.")

        dados["nome"] = nome
        dados["preco_mensal"] = float(dados.get("preco_mensal", 0))

        return PlanoRepository.criar(dados)

    @staticmethod
    def atualizar(plano_id, dados):

        PlanoService.buscar_por_id(plano_id)

        dados["nome"] = dados.get("nome", "").strip()
        dados["preco_mensal"] = float(dados.get("preco_mensal", 0))

        PlanoRepository.atualizar(plano_id, dados)

    @staticmethod
    def excluir(plano_id):

        PlanoService.buscar_por_id(plano_id)
        PlanoRepository.excluir(plano_id)

    @staticmethod
    def formatar_limite(valor):

        if valor is None or int(valor) < 0:
            return "Ilimitado"

        return str(valor)
