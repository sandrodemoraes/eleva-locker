from datetime import datetime

from repositories.contrato_repository import ContratoRepository
from repositories.plano_repository import PlanoRepository
from services.faturamento_service import FaturamentoService


class ContratoService:

    @staticmethod
    def listar(empresa_id=None):
        return ContratoRepository.listar(empresa_id)

    @staticmethod
    def buscar_por_id(contrato_id):

        contrato = ContratoRepository.buscar_por_id(contrato_id)

        if not contrato:
            raise ValueError("Contrato não encontrado.")

        return contrato

    @staticmethod
    def criar(dados):

        empresa_id = int(dados["empresa_id"])
        plano_id = int(dados["plano_id"])

        plano = PlanoRepository.buscar_por_id(plano_id)

        if not plano:
            raise ValueError("Plano não encontrado.")

        ativo = ContratoRepository.buscar_ativo_por_empresa(empresa_id)

        if ativo:
            raise ValueError(
                "Esta empresa já possui contrato ativo. "
                "Suspenda ou cancele o contrato atual antes de criar outro."
            )

        valor = dados.get("valor_mensal")

        if not valor:
            valor = plano["preco_mensal"]

        dados["valor_mensal"] = float(valor)
        dados["data_inicio"] = dados.get("data_inicio") or datetime.now().strftime("%Y-%m-%d")

        contrato_id = ContratoRepository.criar(dados)

        FaturamentoService.gerar_fatura_contrato(contrato_id)

        return contrato_id

    @staticmethod
    def atualizar(contrato_id, dados):

        ContratoService.buscar_por_id(contrato_id)
        dados["valor_mensal"] = float(dados.get("valor_mensal", 0))
        ContratoRepository.atualizar(contrato_id, dados)

    @staticmethod
    def suspender(contrato_id):

        ContratoService.buscar_por_id(contrato_id)
        ContratoRepository.atualizar_status(contrato_id, "suspenso")

    @staticmethod
    def reativar(contrato_id):

        ContratoService.buscar_por_id(contrato_id)
        ContratoRepository.atualizar_status(contrato_id, "ativo")

    @staticmethod
    def cancelar(contrato_id):

        ContratoService.buscar_por_id(contrato_id)
        ContratoRepository.atualizar_status(contrato_id, "cancelado")
