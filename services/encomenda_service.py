import random
from datetime import datetime

from repositories.encomenda_repository import EncomendaRepository
from repositories.compartimento_repository import CompartimentoRepository
from services.log_service import LogService


class EncomendaService:

    @staticmethod
    def listar(status=None):
        return EncomendaRepository.listar(status)

    @staticmethod
    def buscar_por_id(encomenda_id):

        encomenda = EncomendaRepository.buscar_por_id(encomenda_id)

        if not encomenda:
            raise ValueError("Encomenda não encontrada.")

        return encomenda

    @staticmethod
    def _gerar_codigo():

        for _ in range(20):

            codigo = f"{random.randint(100000, 999999)}"

            if not EncomendaRepository.codigo_existe(codigo):
                return codigo

        raise ValueError("Não foi possível gerar código único. Tente novamente.")

    @staticmethod
    def depositar(
        compartimento_id,
        cliente,
        telefone,
        email,
        operador,
        transportadora=None,
        observacao=None,
    ):

        cliente = cliente.strip()

        if not cliente:
            raise ValueError("Nome do destinatário é obrigatório.")

        compartimento = CompartimentoRepository.buscar_por_id(compartimento_id)

        if not compartimento:
            raise ValueError("Compartimento não encontrado.")

        if compartimento["status"] != "livre":
            raise ValueError("Compartimento não está livre.")

        codigo = EncomendaService._gerar_codigo()
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        encomenda_id = EncomendaRepository.criar({
            "codigo": codigo,
            "cliente": cliente,
            "telefone": telefone.strip() if telefone else None,
            "email": email.strip() if email else None,
            "compartimento": compartimento_id,
            "data_entrada": agora,
            "status": "aguardando_retirada",
            "operador": operador,
            "transportadora": transportadora,
            "observacao": observacao,
        })

        CompartimentoRepository.atualizar_status(compartimento_id, "ocupado")

        LogService.registrar(
            compartimento_id,
            operador,
            f"Depósito encomenda #{encomenda_id} - código {codigo} - {cliente}",
        )

        return {
            "id": encomenda_id,
            "codigo": codigo,
            "compartimento": compartimento["numero"],
            "armario": compartimento["armario_nome"],
        }

    @staticmethod
    def retirar(codigo, operador):

        codigo = codigo.strip()

        if not codigo:
            raise ValueError("Informe o código de retirada.")

        encomenda = EncomendaRepository.buscar_por_codigo(codigo)

        if not encomenda:
            raise ValueError("Código inválido ou encomenda já retirada.")

        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        EncomendaRepository.atualizar_retirada(encomenda["id"], agora)
        CompartimentoRepository.atualizar_status(encomenda["compartimento"], "livre")

        LogService.registrar(
            encomenda["compartimento"],
            operador,
            f"Retirada encomenda #{encomenda['id']} - código {codigo} - {encomenda['cliente']}",
        )

        return {
            "id": encomenda["id"],
            "cliente": encomenda["cliente"],
            "compartimento": encomenda["compartimento_numero"],
            "armario": encomenda["armario_nome"],
        }

    @staticmethod
    def contar():
        return EncomendaRepository.contar()

    @staticmethod
    def contar_pendentes():
        return EncomendaRepository.contar_pendentes()
