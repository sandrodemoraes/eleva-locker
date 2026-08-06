import random
from datetime import datetime, timedelta

import config
from repositories.encomenda_repository import EncomendaRepository
from repositories.compartimento_repository import CompartimentoRepository
from services.log_service import LogService
from services.esp32_service import Esp32Service
from services.notificacao_service import NotificacaoService
from services.limite_plano_service import LimitePlanoService
from services.esp32_sync_service import Esp32SyncService
from middleware.operador_scope import operador_acessa_armario


class EncomendaService:

    @staticmethod
    def listar(status=None, armario_id=None):
        return EncomendaRepository.listar(status, armario_id=armario_id)

    @staticmethod
    def buscar_por_id(encomenda_id, verificar_acesso=False):

        encomenda = EncomendaRepository.buscar_por_id(encomenda_id)

        if not encomenda:
            raise ValueError("Encomenda não encontrada.")

        if verificar_acesso:
            comp = CompartimentoRepository.buscar_por_id(encomenda["compartimento"])
            if comp and not operador_acessa_armario(comp["armario"]):
                raise ValueError("Sem permissão para acessar esta encomenda.")

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
        notificar=True,
    ):

        cliente = cliente.strip()

        if not cliente:
            raise ValueError("Nome do destinatário é obrigatório.")

        telefone = telefone.strip() if telefone else ""

        if config.NOTIF_WHATSAPP_ATIVO:
            if not telefone:
                raise ValueError("Telefone é obrigatório para enviar WhatsApp ao destinatário.")
            _, erro_tel = NotificacaoService.validar_telefone_br(telefone)
            if erro_tel:
                raise ValueError(erro_tel)

        compartimento = CompartimentoRepository.buscar_por_id(compartimento_id)

        if not compartimento:
            raise ValueError("Compartimento não encontrado.")

        if not operador_acessa_armario(compartimento["armario"]):
            raise ValueError("Sem permissão para depositar neste armário.")

        empresa_id = LimitePlanoService.empresa_id_do_compartimento(compartimento_id)

        if empresa_id:
            LimitePlanoService.verificar_encomenda(empresa_id)

        codigo = EncomendaService._gerar_codigo()
        agora = datetime.now()
        agora_str = agora.strftime("%Y-%m-%d %H:%M:%S")
        expira = (agora + timedelta(days=config.ENCOMENDA_DIAS_VALIDADE)).strftime("%Y-%m-%d %H:%M:%S")

        encomenda_id, compartimento = EncomendaRepository.criar_deposito_atomico(
            compartimento_id,
            {
                "codigo": codigo,
                "cliente": cliente,
                "telefone": telefone.strip() if telefone else None,
                "email": email.strip() if email else None,
                "data_entrada": agora_str,
                "expira_em": expira,
                "status": "aguardando_retirada",
                "operador": operador,
                "transportadora": transportadora,
                "observacao": observacao,
            },
        )

        LogService.registrar(
            compartimento_id,
            operador,
            f"Depósito encomenda #{encomenda_id} - código {codigo} - {cliente}",
        )

        abertura = Esp32Service.abrir_compartimento(compartimento_id, operador)

        notificacoes = []
        if notificar:
            notificacoes = NotificacaoService.notificar_encomenda_chegou(
                encomenda_id=encomenda_id,
                codigo=codigo,
                cliente=cliente,
                telefone=telefone,
                email=email,
                armario=compartimento["armario_nome"] or "Armário",
                armario_id=compartimento["armario"],
                compartimento=compartimento["numero"],
                expira_em=expira,
            )

        Esp32SyncService.incrementar_por_compartimento(compartimento_id)

        return {
            "id": encomenda_id,
            "codigo": codigo,
            "compartimento": compartimento["numero"],
            "compartimento_id": compartimento_id,
            "armario": compartimento["armario_nome"],
            "esp32": abertura,
            "notificacoes": notificacoes,
            "notificado": bool(notificacoes),
        }

    @staticmethod
    def concluir_deposito_totem(encomenda_id, operador):
        encomenda = EncomendaRepository.buscar_por_id(encomenda_id)

        if not encomenda:
            raise ValueError("Encomenda não encontrada.")

        if encomenda["status"] != "aguardando_retirada":
            raise ValueError("Encomenda não está aguardando retirada.")

        comp = CompartimentoRepository.buscar_por_id(encomenda["compartimento"])
        if comp and not operador_acessa_armario(comp["armario"]):
            raise ValueError("Sem permissão para este armário.")

        if encomenda["notificado_em"]:
            return {
                "id": encomenda_id,
                "compartimento": encomenda["compartimento_numero"],
                "cliente": encomenda["cliente"],
                "ja_notificado": True,
            }

        notificacoes = NotificacaoService.notificar_encomenda_chegou(
            encomenda_id=encomenda_id,
            codigo=encomenda["codigo"],
            cliente=encomenda["cliente"],
            telefone=encomenda["telefone"],
            email=encomenda["email"],
            armario=encomenda["armario_nome"] or "Armário",
            armario_id=comp["armario"] if comp else None,
            compartimento=encomenda["compartimento_numero"] or "—",
            expira_em=encomenda["expira_em"] if encomenda["expira_em"] else None,
        )

        LogService.registrar(
            encomenda["compartimento"],
            operador,
            f"Depósito totem concluído #{encomenda_id} — porta fechada",
        )

        return {
            "id": encomenda_id,
            "compartimento": encomenda["compartimento_numero"],
            "cliente": encomenda["cliente"],
            "notificacoes": notificacoes,
            "ja_notificado": False,
        }

    @staticmethod
    def retirar(codigo, operador, armario_id=None):

        codigo = codigo.strip()

        if not codigo:
            raise ValueError("Informe o código de retirada.")

        encomenda = EncomendaRepository.buscar_por_codigo(codigo)

        if not encomenda:
            raise ValueError("Código inválido ou encomenda já retirada.")

        expira_em = encomenda["expira_em"] if encomenda["expira_em"] else None
        if expira_em:
            try:
                expira = datetime.strptime(str(expira_em)[:19], "%Y-%m-%d %H:%M:%S")
                if datetime.now() > expira:
                    raise ValueError("Código expirado. Peça reenvio da notificação à portaria.")
            except ValueError as erro:
                if "expirado" in str(erro).lower():
                    raise

        comp = CompartimentoRepository.buscar_por_id(encomenda["compartimento"])
        if not comp or not operador_acessa_armario(comp["armario"]):
            raise ValueError("Sem permissão para retirar deste armário.")

        if armario_id is not None and int(comp["armario"]) != int(armario_id):
            raise ValueError("Este código não é deste armário.")

        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        EncomendaRepository.atualizar_retirada(encomenda["id"], agora)
        CompartimentoRepository.atualizar_status(encomenda["compartimento"], "livre")

        LogService.registrar(
            encomenda["compartimento"],
            operador,
            f"Retirada encomenda #{encomenda['id']} - código {codigo} - {encomenda['cliente']}",
        )

        abertura = {"sucesso": False, "mensagem": "Porta não acionada."}
        try:
            abertura = Esp32Service.abrir_compartimento(encomenda["compartimento"], operador)
        except Exception:
            abertura = {
                "sucesso": False,
                "mensagem": "Retirada OK, mas falha ao abrir a porta. Peça ajuda na portaria.",
            }

        try:
            Esp32SyncService.incrementar_por_compartimento(encomenda["compartimento"])
        except Exception:
            pass

        return {
            "id": encomenda["id"],
            "cliente": encomenda["cliente"],
            "compartimento": encomenda["compartimento_numero"],
            "armario": encomenda["armario_nome"],
            "esp32": abertura,
            "porta_aberta": abertura.get("sucesso") if isinstance(abertura, dict) else False,
        }

    @staticmethod
    def contar():
        return EncomendaRepository.contar()

    @staticmethod
    def contar_pendentes():
        return EncomendaRepository.contar_pendentes()
