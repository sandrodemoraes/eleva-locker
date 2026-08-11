import json
import urllib.request
from datetime import datetime, timedelta

import config
from repositories.contrato_repository import ContratoRepository
from repositories.fatura_repository import FaturaRepository


class FaturamentoService:

    @staticmethod
    def _referencia_atual():
        return datetime.now().strftime("%Y-%m")

    @staticmethod
    def _data_vencimento(referencia):

        ano, mes = map(int, referencia.split("-"))
        dia = min(config.PAGAMENTO_DIAS_VENCIMENTO, 28)

        return f"{ano}-{mes:02d}-{dia:02d}"

    @staticmethod
    def gerar_fatura_contrato(contrato_id, referencia=None):

        contrato = ContratoRepository.buscar_por_id(contrato_id)

        if not contrato:
            raise ValueError("Contrato não encontrado.")

        referencia = referencia or FaturamentoService._referencia_atual()

        if FaturaRepository.buscar_por_referencia(contrato_id, referencia):
            return None

        link, gateway_id = FaturamentoService._criar_cobranca_gateway(
            contrato, referencia
        )

        return FaturaRepository.criar({
            "contrato_id": contrato_id,
            "referencia": referencia,
            "valor": contrato["valor_mensal"],
            "status": "pendente",
            "data_vencimento": FaturamentoService._data_vencimento(referencia),
            "link_pagamento": link,
            "gateway_id": gateway_id,
        })

    @staticmethod
    def gerar_faturas_mes(referencia=None):

        referencia = referencia or FaturamentoService._referencia_atual()
        geradas = 0

        for contrato in ContratoRepository.listar_ativos():

            if contrato["renovacao_automatica"]:

                fatura_id = FaturamentoService.gerar_fatura_contrato(
                    contrato["id"], referencia
                )

                if fatura_id:
                    geradas += 1

        return geradas

    @staticmethod
    def _criar_cobranca_gateway(contrato, referencia):

        valor = contrato["valor_mensal"]
        descricao = (
            f"ELEVA LOCKER — {contrato['plano_nome']} — "
            f"{contrato['empresa_nome']} — {referencia}"
        )

        if config.PAGAMENTO_MODO == "console" or not config.PAGAMENTO_API_URL:

            gateway_id = f"sim_{contrato['id']}_{referencia}"
            link = f"{config.APP_URL_BASE}/faturas/pagar/{gateway_id}"

            print(f"\n💳 [COBRANÇA] {descricao}")
            print(f"   Valor: R$ {valor:.2f}")
            print(f"   Link: {link}\n")

            return link, gateway_id

        try:

            payload = json.dumps({
                "customer": contrato["empresa_nome"],
                "value": valor,
                "description": descricao,
                "dueDate": FaturamentoService._data_vencimento(referencia),
            }).encode("utf-8")

            req = urllib.request.Request(
                f"{config.PAGAMENTO_API_URL.rstrip('/')}/payments",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {config.PAGAMENTO_API_KEY}",
                },
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=15) as resp:
                dados = json.loads(resp.read().decode("utf-8"))

            return dados.get("invoiceUrl", ""), dados.get("id", "")

        except Exception as erro:

            gateway_id = f"err_{contrato['id']}_{referencia}"
            link = f"{config.APP_URL_BASE}/faturas/pagar/{gateway_id}"

            print(f"⚠ Gateway erro: {erro}")

            return link, gateway_id

    @staticmethod
    def marcar_pago(fatura_id):

        fatura = FaturaRepository.buscar_por_id(fatura_id)

        if not fatura:
            raise ValueError("Fatura não encontrada.")

        if fatura["status"] == "pago":
            raise ValueError("Fatura já está paga.")

        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        FaturaRepository.marcar_pago(fatura_id, agora)

        contrato = ContratoRepository.buscar_por_id(fatura["contrato_id"])

        if contrato and contrato["status"] == "suspenso":
            ContratoRepository.atualizar_status(fatura["contrato_id"], "ativo")

        return fatura

    @staticmethod
    def pagar_por_gateway(gateway_id):

        fatura = FaturaRepository.buscar_por_gateway(gateway_id)

        if not fatura:
            raise ValueError("Cobrança não encontrada.")

        return FaturamentoService.marcar_pago(fatura["id"])

    @staticmethod
    def verificar_inadimplencia():

        hoje = datetime.now().strftime("%Y-%m-%d")

        FaturaRepository.marcar_vencidas(hoje)

        with __import__(
            "repositories.base_repository", fromlist=["BaseRepository"]
        ).BaseRepository.get_connection() as conn:

            vencidas = conn.execute("""
                SELECT DISTINCT contrato_id FROM faturas
                WHERE status = 'vencido'
            """).fetchall()

        for row in vencidas:
            ContratoRepository.atualizar_status(row["contrato_id"], "suspenso")

        return len(vencidas)

    @staticmethod
    def obter_metricas():

        referencia = FaturamentoService._referencia_atual()

        FaturamentoService.verificar_inadimplencia()

        return {
            "mrr": FaturaRepository.calcular_mrr(),
            "contratos_ativos": ContratoRepository.contar_ativos(),
            "faturas_pendentes": FaturaRepository.contar_pendentes(),
            "recebido_mes": FaturaRepository.total_recebido_mes(referencia),
            "referencia": referencia,
        }

    @staticmethod
    def listar_faturas(status=None, contrato_id=None):
        return FaturaRepository.listar(status, contrato_id)
