from repositories.empresa_repository import EmpresaRepository


class EmpresaService:

    @staticmethod
    def listar():
        return EmpresaRepository.listar()

    @staticmethod
    def listar_ativas():
        return EmpresaRepository.listar_ativas()

    @staticmethod
    def buscar_por_id(empresa_id):

        empresa = EmpresaRepository.buscar_por_id(empresa_id)

        if not empresa:
            raise ValueError("Empresa não encontrada.")

        return empresa

    @staticmethod
    def cnpj_existe(cnpj):
        return EmpresaRepository.buscar_por_cnpj(cnpj) is not None

    @staticmethod
    def inserir(dados):

        if not dados.get("razao_social"):
            raise ValueError("Razão social é obrigatória.")

        EmpresaRepository.inserir(dados)

    @staticmethod
    def atualizar(empresa_id, dados):

        if not EmpresaRepository.buscar_por_id(empresa_id):
            raise ValueError("Empresa não encontrada.")

        EmpresaRepository.atualizar(empresa_id, dados)

    @staticmethod
    def excluir(empresa_id):

        if not EmpresaRepository.buscar_por_id(empresa_id):
            raise ValueError("Empresa não encontrada.")

        EmpresaRepository.excluir(empresa_id)
