import random
from datetime import datetime, timedelta

import config
from repositories.encomenda_repository import EncomendaRepository
from repositories.compartimento_repository import CompartimentoRepository
from repositories.base_repository import BaseRepository
from services.log_service import LogService
from services.esp32_service import Esp32Service
from services.notificacao_service import NotificacaoService
from services.limite_plano_service import LimitePlanoService
from middleware.operador_scope import operador_acessa_armario


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
                EncomendaRepository.marcar_lembrete_enviado(encomenda["id"])
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
        notificar=True,
        reverter_se_falhar_abertura=False,
    ):

        cliente = cliente.strip()

        if not cliente:
            raise ValueError("Nome do destinatário é obrigatório.")

        telefone = telefone.strip() if telefone else ""

        if config.NOTIF_WHATSAPP_ATIVO and notificar:
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
        expira = (agora + timedelta(days=config.ENCOMENDA_DIAS_VALIDADE)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        encomenda_id, compartimento = EncomendaRepository.criar_deposito_atomico(
            compartimento_id,
            {
                "codigo": codigo,
                "cliente": cliente,
                "telefone": telefone or None,
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

        if (
            reverter_se_falhar_abertura
            and not abertura.get("sucesso")
            and not abertura.get("simulado")
            and not abertura.get("manual")
        ):
            EncomendaService.cancelar_deposito_totem(encomenda_id, operador)
            raise ValueError(
                abertura.get("mensagem") or "ESP32 offline — depósito cancelado."
            )

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

        try:
            from services.esp32_sync_service import Esp32SyncService
            Esp32SyncService.incrementar_por_compartimento(compartimento_id)
        except Exception:
            pass

        return {
            "id": encomenda_id,
            "codigo": codigo,
            "compartimento": compartimento["numero"],
            "compartimento_id": compartimento_id,
            "armario": compartimento["armario_nome"],
            "expira_em": expira,
            "esp32": abertura,
            "notificacoes": notificacoes,
            "notificado": bool(notificacoes),
        }

    @staticmethod
    def cancelar_deposito_totem(encomenda_id, operador):
        encomenda = EncomendaRepository.buscar_por_id(encomenda_id)

        if not encomenda:
            raise ValueError("Encomenda não encontrada.")

        if encomenda["status"] != "aguardando_retirada":
            raise ValueError("Encomenda não está pendente.")

        if EncomendaService._valor(encomenda, "notificado_em"):
            raise ValueError("Encomenda já notificada — não pode cancelar.")

        comp = CompartimentoRepository.buscar_por_id(encomenda["compartimento"])
        if comp and not operador_acessa_armario(comp["armario"]):
            raise ValueError("Sem permissão para este armário.")

        with BaseRepository.get_connection() as conn:
            conn.execute(
                "DELETE FROM encomendas WHERE id = ? AND notificado_em IS NULL",
                (encomenda_id,),
            )
            if comp:
                conn.execute(
                    "UPDATE compartimentos SET status = 'livre' WHERE id = ?",
                    (encomenda["compartimento"],),
                )
            conn.commit()

        if comp:
            LogService.registrar(
                encomenda["compartimento"],
                operador,
                f"Depósito totem cancelado #{encomenda_id} — {encomenda['cliente']}",
            )

        return {"id": encomenda_id, "cancelado": True}

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

        if EncomendaService._valor(encomenda, "notificado_em"):
            from repositories.notificacao_repository import NotificacaoRepository

            ultimo_wa = NotificacaoRepository.ultimo_whatsapp_encomenda(encomenda_id)
            if ultimo_wa and ultimo_wa["status"] == "enviado":
                return {
                    "id": encomenda_id,
                    "compartimento": encomenda["compartimento_numero"],
                    "cliente": encomenda["cliente"],
                    "ja_notificado": True,
                    "notificacoes": [],
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
            expira_em=EncomendaService._valor(encomenda, "expira_em"),
        )

        # Totem: porta fechada = depósito concluído mesmo se WhatsApp falhar
        if not EncomendaService._valor(encomenda, "notificado_em"):
            enc_atual = EncomendaRepository.buscar_por_id(encomenda_id)
            if not EncomendaService._valor(enc_atual, "notificado_em"):
                EncomendaRepository.marcar_notificado(encomenda_id)

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

        comp = CompartimentoRepository.buscar_por_id(encomenda["compartimento"])
        if armario_id is not None and comp and int(comp["armario"]) != int(armario_id):
            raise ValueError("Este código não é deste armário.")

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
