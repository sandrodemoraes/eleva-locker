import random
from datetime import datetime, timedelta

import config
from repositories.encomenda_repository import EncomendaRepository
from repositories.compartimento_repository import CompartimentoRepository
from services.log_service import LogService
from services.esp32_service import Esp32Service
from services.notificacao_service import NotificacaoService
from services.limite_plano_service import LimitePlanoService


class EncomendaService:

    @staticmethod
    def _parse_data(valor):
        if not valor:
            return None
        try:
            return datetime.strptime(str(valor)[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None

    @staticmethod
    def _valor(encomenda, chave, default=None):
        try:
            val = encomenda[chave]
        except (KeyError, IndexError, TypeError):
            return default
        return default if val is None else val

    @staticmethod
    def _precisa_lembrete_automatico(encomenda):
        if not config.ENCOMENDA_LEMBRETE_AUTOMATICO:
            return False

        if encomenda["status"] != "aguardando_retirada":
            return False

        if not (
            EncomendaService._valor(encomenda, "telefone")
            or EncomendaService._valor(encomenda, "email")
        ):
            return False

        horas = config.ENCOMENDA_HORAS_REENVIO
        agora = datetime.now()
        entrada = EncomendaService._parse_data(
            EncomendaService._valor(encomenda, "data_entrada")
        )

        if not entrada:
            return False

        if (agora - entrada).total_seconds() < horas * 3600:
            return False

        ref = (
            EncomendaService._valor(encomenda, "ultimo_lembrete_em")
            or EncomendaService._valor(encomenda, "notificado_em")
            or EncomendaService._valor(encomenda, "data_entrada")
        )
        ref_dt = EncomendaService._parse_data(ref) or entrada

        return (agora - ref_dt).total_seconds() >= horas * 3600

    @staticmethod
    def processar_lembretes_automaticos():
        """Reenvia notificação para encomendas há mais de 24h no armário (a cada 24h)."""
        EncomendaService.sincronizar_retidas()
        enviados = 0
        erros = 0

        for encomenda in EncomendaRepository.listar_aguardando_retirada():
            if not EncomendaService._precisa_lembrete_automatico(encomenda):
                continue
            try:
                NotificacaoService.lembrete_automatico(encomenda["id"])
                enviados += 1
            except Exception as erro:
                erros += 1
                print(f"[LEMBRETE] Falha encomenda #{encomenda['id']}: {erro}")

        return {"enviados": enviados, "erros": erros}

    @staticmethod
    def sincronizar_retidas():
        return EncomendaRepository.marcar_retidas()

    @staticmethod
    def listar(status=None):
        EncomendaService.processar_lembretes_automaticos()
        EncomendaService.sincronizar_retidas()
        return EncomendaRepository.listar(status)

    @staticmethod
    def contar_retidas():
        EncomendaService.sincronizar_retidas()
        return EncomendaRepository.contar_retidas()

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
    def _codigo_expirado(encomenda):
        expira_em = encomenda["expira_em"] if encomenda["expira_em"] else None
        if not expira_em:
            return False
        try:
            expira = datetime.strptime(str(expira_em)[:19], "%Y-%m-%d %H:%M:%S")
            return datetime.now() > expira
        except ValueError:
            return False

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

        empresa_id = LimitePlanoService.empresa_id_do_compartimento(compartimento_id)

        if empresa_id:
            LimitePlanoService.verificar_encomenda(empresa_id)

        codigo = EncomendaService._gerar_codigo()
        agora = datetime.now()
        agora_str = agora.strftime("%Y-%m-%d %H:%M:%S")
        expira = (agora + timedelta(days=config.ENCOMENDA_DIAS_VALIDADE)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        encomenda_id = EncomendaRepository.criar({
            "codigo": codigo,
            "cliente": cliente,
            "telefone": telefone.strip() if telefone else None,
            "email": email.strip() if email else None,
            "compartimento": compartimento_id,
            "data_entrada": agora_str,
            "expira_em": expira,
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

        abertura = Esp32Service.abrir_compartimento(compartimento_id, operador)

        notificacoes = NotificacaoService.notificar_encomenda_chegou(
            encomenda_id=encomenda_id,
            codigo=codigo,
            cliente=cliente,
            telefone=telefone,
            email=email,
            armario=compartimento["armario_nome"] or "Armário",
            compartimento=compartimento["numero"],
            expira_em=expira,
        )

        return {
            "id": encomenda_id,
            "codigo": codigo,
            "compartimento": compartimento["numero"],
            "armario": compartimento["armario_nome"],
            "expira_em": expira,
            "esp32": abertura,
            "notificacoes": notificacoes,
        }

    @staticmethod
    def retirar(codigo, operador):

        codigo = codigo.strip()

        if not codigo:
            raise ValueError("Informe o código de retirada.")

        EncomendaService.sincronizar_retidas()

        encomenda = EncomendaRepository.buscar_por_codigo(codigo)

        if not encomenda:
            existente = EncomendaRepository.buscar_por_codigo_any(codigo)
            if existente and existente["status"] == "retida":
                raise ValueError(
                    "Prazo de retirada expirado. Dirija-se à portaria para retirar o pacote."
                )
            if existente and existente["status"] == "retirada":
                raise ValueError("Encomenda já retirada.")
            raise ValueError("Código inválido ou encomenda já retirada.")

        if EncomendaService._codigo_expirado(encomenda):
            EncomendaRepository.marcar_retidas()
            raise ValueError(
                "Prazo de retirada expirado. Dirija-se à portaria para retirar o pacote."
            )

        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        EncomendaRepository.atualizar_retirada(encomenda["id"], agora)
        CompartimentoRepository.atualizar_status(encomenda["compartimento"], "livre")

        LogService.registrar(
            encomenda["compartimento"],
            operador,
            f"Retirada encomenda #{encomenda['id']} - código {codigo} - {encomenda['cliente']}",
        )

        abertura = Esp32Service.abrir_compartimento(encomenda["compartimento"], operador)

        return {
            "id": encomenda["id"],
            "cliente": encomenda["cliente"],
            "compartimento": encomenda["compartimento_numero"],
            "armario": encomenda["armario_nome"],
            "esp32": abertura,
        }

    @staticmethod
    def retirar_retida(encomenda_id, operador, observacao=None):

        EncomendaService.sincronizar_retidas()

        encomenda = EncomendaRepository.buscar_por_id(encomenda_id)

        if not encomenda:
            raise ValueError("Encomenda não encontrada.")

        if encomenda["status"] not in ("retida", "aguardando_retirada"):
            raise ValueError("Encomenda não está retida ou aguardando retirada.")

        if encomenda["status"] == "aguardando_retirada":
            if not EncomendaService._codigo_expirado(encomenda):
                raise ValueError(
                    "Encomenda ainda dentro do prazo. Use retirada normal com o código."
                )
            EncomendaRepository.marcar_retidas()
            encomenda = EncomendaRepository.buscar_por_id(encomenda_id)

        if encomenda["status"] != "retida":
            raise ValueError("Encomenda não está retida.")

        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        obs = observacao.strip() if observacao else "Pacote retido — retirada administrativa"

        abertura = Esp32Service.abrir_compartimento(encomenda["compartimento"], operador)

        EncomendaRepository.atualizar_retirada(encomenda["id"], agora, observacao=obs)
        CompartimentoRepository.atualizar_status(encomenda["compartimento"], "livre")

        LogService.registrar(
            encomenda["compartimento"],
            operador,
            f"Retirada administrativa encomenda retida #{encomenda['id']} "
            f"— compartimento #{encomenda['compartimento_numero']} — {encomenda['cliente']}",
        )

        return {
            "id": encomenda["id"],
            "cliente": encomenda["cliente"],
            "compartimento": encomenda["compartimento_numero"],
            "armario": encomenda["armario_nome"],
            "esp32": abertura,
        }

    @staticmethod
    def contar():
        return EncomendaRepository.contar()

    @staticmethod
    def contar_pendentes():
        return EncomendaRepository.contar_pendentes()
