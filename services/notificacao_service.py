import json
import re
import smtplib
import urllib.request
import urllib.error
from email.mime.text import MIMEText

import config
from repositories.notificacao_repository import NotificacaoRepository
from repositories.encomenda_repository import EncomendaRepository


class NotificacaoService:

    @staticmethod
    def _normalizar_telefone(telefone):

        numeros = re.sub(r"\D", "", telefone or "")

        if not numeros:
            return None

        if len(numeros) <= 11:
            numeros = "55" + numeros

        return numeros

    @staticmethod
    def _montar_mensagem(cliente, armario, compartimento, codigo):

        return (
            f"Olá {cliente}!\n\n"
            f"Sua encomenda chegou no *ELEVA LOCKER*.\n"
            f"📍 Local: {armario}\n"
            f"📦 Compartimento: #{compartimento}\n"
            f"🔑 Código de retirada: *{codigo}*\n\n"
            f"Apresente este código no totem ou informe à portaria."
        )

    @staticmethod
    def _registrar(encomenda_id, canal, destinatario, mensagem, status, detalhe=None):

        NotificacaoRepository.registrar(
            encomenda_id, canal, destinatario, mensagem, status, detalhe
        )

    @staticmethod
    def _enviar_email(destinatario, assunto, mensagem):

        if not destinatario:
            return {"sucesso": False, "mensagem": "E-mail não informado."}

        if config.NOTIF_MODO == "console" or not config.SMTP_HOST:

            print(f"\n📧 [EMAIL → {destinatario}]\n{assunto}\n{mensagem}\n")
            return {"sucesso": True, "mensagem": "E-mail registrado (modo console).", "simulado": True}

        try:

            msg = MIMEText(mensagem, "plain", "utf-8")
            msg["Subject"] = assunto
            msg["From"] = config.SMTP_FROM
            msg["To"] = destinatario

            with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:

                server.starttls()
                server.login(config.SMTP_USER, config.SMTP_PASS)
                server.send_message(msg)

            return {"sucesso": True, "mensagem": "E-mail enviado."}

        except Exception as erro:

            return {"sucesso": False, "mensagem": str(erro)}

    @staticmethod
    def _enviar_whatsapp(telefone, mensagem):

        numero = NotificacaoService._normalizar_telefone(telefone)

        if not numero:
            return {"sucesso": False, "mensagem": "Telefone inválido."}

        if config.NOTIF_MODO == "console" or not config.WHATSAPP_API_URL:

            print(f"\n💬 [WHATSAPP → {numero}]\n{mensagem}\n")
            return {"sucesso": True, "mensagem": "WhatsApp registrado (modo console).", "simulado": True}

        try:

            url = (
                f"{config.WHATSAPP_API_URL.rstrip('/')}/message/sendText/"
                f"{config.WHATSAPP_INSTANCIA}"
            )

            payload = json.dumps({
                "number": numero,
                "text": mensagem,
            }).encode("utf-8")

            req = urllib.request.Request(
                url,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "apikey": config.WHATSAPP_API_KEY,
                },
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=10) as resp:
                dados = json.loads(resp.read().decode("utf-8"))

            return {"sucesso": True, "mensagem": "WhatsApp enviado.", "dados": dados}

        except Exception as erro:

            return {"sucesso": False, "mensagem": str(erro)}

    @staticmethod
    def _enviar_sms(telefone, mensagem):

        numero = NotificacaoService._normalizar_telefone(telefone)

        if not numero:
            return {"sucesso": False, "mensagem": "Telefone inválido."}

        if config.NOTIF_MODO == "console" or not config.SMS_API_URL:

            print(f"\n📱 [SMS → {numero}]\n{mensagem}\n")
            return {"sucesso": True, "mensagem": "SMS registrado (modo console).", "simulado": True}

        try:

            payload = json.dumps({
                "to": numero,
                "message": mensagem,
            }).encode("utf-8")

            req = urllib.request.Request(
                config.SMS_API_URL,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {config.SMS_API_KEY}",
                },
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=10) as resp:
                dados = json.loads(resp.read().decode("utf-8"))

            return {"sucesso": True, "mensagem": "SMS enviado.", "dados": dados}

        except Exception as erro:

            return {"sucesso": False, "mensagem": str(erro)}

    @staticmethod
    def notificar_encomenda_chegou(
        encomenda_id,
        codigo,
        cliente,
        telefone,
        email,
        armario,
        compartimento,
    ):

        mensagem = NotificacaoService._montar_mensagem(
            cliente, armario, compartimento, codigo
        )

        assunto = f"ELEVA LOCKER — Encomenda disponível (código {codigo})"
        resultados = []

        if config.NOTIF_EMAIL_ATIVO and email:

            r = NotificacaoService._enviar_email(email, assunto, mensagem)
            NotificacaoService._registrar(
                encomenda_id, "email", email, mensagem,
                "enviado" if r["sucesso"] else "erro",
                r.get("mensagem"),
            )
            resultados.append({"canal": "email", **r})

        if config.NOTIF_WHATSAPP_ATIVO and telefone:

            r = NotificacaoService._enviar_whatsapp(telefone, mensagem)
            NotificacaoService._registrar(
                encomenda_id, "whatsapp", telefone, mensagem,
                "enviado" if r["sucesso"] else "erro",
                r.get("mensagem"),
            )
            resultados.append({"canal": "whatsapp", **r})

        if config.NOTIF_SMS_ATIVO and telefone:

            r = NotificacaoService._enviar_sms(telefone, mensagem)
            NotificacaoService._registrar(
                encomenda_id, "sms", telefone, mensagem,
                "enviado" if r["sucesso"] else "erro",
                r.get("mensagem"),
            )
            resultados.append({"canal": "sms", **r})

        if not resultados:

            NotificacaoService._registrar(
                encomenda_id, "console", telefone or email or "—",
                mensagem, "enviado", "Nenhum canal ativo — modo console",
            )
            print(f"\n🔔 [NOTIFICAÇÃO — encomenda #{encomenda_id}]\n{mensagem}\n")
            resultados.append({
                "canal": "console",
                "sucesso": True,
                "mensagem": "Notificação registrada no console.",
            })

        EncomendaRepository.marcar_notificado(encomenda_id)

        return resultados

    @staticmethod
    def reenviar(encomenda_id):

        encomenda = EncomendaRepository.buscar_por_id(encomenda_id)

        if not encomenda:
            raise ValueError("Encomenda não encontrada.")

        if encomenda["status"] != "aguardando_retirada":
            raise ValueError("Só é possível reenviar notificação de encomendas pendentes.")

        return NotificacaoService.notificar_encomenda_chegou(
            encomenda_id=encomenda_id,
            codigo=encomenda["codigo"],
            cliente=encomenda["cliente"],
            telefone=encomenda["telefone"],
            email=encomenda["email"],
            armario=encomenda["armario_nome"] or "Armário",
            compartimento=encomenda["compartimento_numero"] or "—",
        )

    @staticmethod
    def listar():
        return NotificacaoRepository.listar()

    @staticmethod
    def contar_hoje():
        return NotificacaoRepository.contar_hoje()
