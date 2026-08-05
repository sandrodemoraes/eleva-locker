import json
import re
import smtplib
import time
import urllib.error
import urllib.request
from email.mime.text import MIMEText

import config
from repositories.encomenda_repository import EncomendaRepository
from repositories.notificacao_repository import NotificacaoRepository


class NotificacaoService:

    @staticmethod
    def whatsapp_configurado():
        if config.NOTIF_MODO == "console":
            return False
        if config.WHATSAPP_PROVIDER == "meta":
            return bool(config.WHATSAPP_META_TOKEN and config.WHATSAPP_META_PHONE_ID)
        return bool(config.WHATSAPP_API_URL and config.WHATSAPP_INSTANCIA)

    @staticmethod
    def _evolution_request(method, path, payload=None):
        url = f"{config.WHATSAPP_API_URL.rstrip('/')}{path}"
        headers = {
            "apikey": config.WHATSAPP_API_KEY,
            "Content-Type": "application/json",
        }
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))

    @staticmethod
    def _extrair_status_instancia(instancia):
        if isinstance(instancia, dict):
            for chave in ("connectionStatus", "status", "state"):
                if instancia.get(chave):
                    return str(instancia[chave]).lower()
            inner = instancia.get("instance") or instancia.get("data") or {}
            if isinstance(inner, dict):
                for chave in ("connectionStatus", "status", "state"):
                    if inner.get(chave):
                        return str(inner[chave]).lower()
        return None

    @staticmethod
    def _buscar_instancia_evolution():
        dados = NotificacaoService._evolution_request("GET", "/instance/fetchInstances")
        alvo = config.WHATSAPP_INSTANCIA
        lista = dados if isinstance(dados, list) else dados.get("instances", [])

        for item in lista:
            nome = (
                item.get("name")
                or item.get("instanceName")
                or (item.get("instance") or {}).get("instanceName")
            )
            if nome == alvo:
                return item
        return None

    @staticmethod
    def status_whatsapp():
        info = {
            "ativo": config.NOTIF_WHATSAPP_ATIVO,
            "modo": config.NOTIF_MODO,
            "configurado": NotificacaoService.whatsapp_configurado(),
            "instancia": config.WHATSAPP_INSTANCIA,
            "conexao": None,
            "pronto": False,
            "mensagem": "",
        }

        if not config.NOTIF_WHATSAPP_ATIVO:
            info["mensagem"] = "WhatsApp desativado (NOTIF_WHATSAPP_ATIVO=0)."
            return info

        if config.NOTIF_MODO == "console":
            info["mensagem"] = (
                "NOTIF_MODO=console — não envia de verdade. "
                "Altere para producao no .env e reinicie py app.py"
            )
            return info

        if not NotificacaoService.whatsapp_configurado():
            info["mensagem"] = "WHATSAPP_API_URL ou WHATSAPP_INSTANCIA não configurados."
            return info

        try:
            inst = NotificacaoService._buscar_instancia_evolution()
            if not inst:
                info["mensagem"] = (
                    f'Instância "{config.WHATSAPP_INSTANCIA}" não encontrada no manager.'
                )
                return info

            conexao = NotificacaoService._extrair_status_instancia(inst)
            info["conexao"] = conexao

            if conexao in ("open", "connected"):
                info["pronto"] = True
                info["mensagem"] = "WhatsApp conectado e pronto para enviar."
            else:
                info["mensagem"] = (
                    f'WhatsApp desconectado (status: {conexao or "desconhecido"}). '
                    "Abra o manager e escaneie o QR novamente."
                )
        except Exception as erro:
            info["mensagem"] = f"Evolution API inacessível: {erro}"

        return info

    @staticmethod
    def validar_telefone_br(telefone):
        numeros = re.sub(r"\D", "", telefone or "")

        if not numeros:
            return None, "Telefone não informado."

        if numeros.startswith("55") and len(numeros) > 11:
            numeros = numeros[2:]

        if len(numeros) == 10:
            ddd = numeros[:2]
            if ddd[0] == "0" or int(ddd) < 11:
                return None, "DDD inválido. Use DDD + número (ex: 11 99999-9999)."
        elif len(numeros) == 11:
            ddd = numeros[:2]
            nono = numeros[2]
            if ddd[0] == "0" or int(ddd) < 11:
                return None, "DDD inválido. Use DDD + número (ex: 11 99999-9999)."
            if nono != "9":
                return None, "Celular deve ter 9 dígitos após o DDD (ex: 11 99999-9999)."
        else:
            return None, "Telefone inválido. Use DDD + número com 10 ou 11 dígitos."

        return "55" + numeros, None

    @staticmethod
    def _normalizar_telefone(telefone):
        numero, erro = NotificacaoService.validar_telefone_br(telefone)
        return numero if not erro else None

    @staticmethod
    def _montar_mensagem_whatsapp(cliente, armario, compartimento, codigo):
        totem = config.APP_URL_BASE.rstrip("/") + "/totem"
        return (
            f"Olá {cliente}! 📦\n\n"
            f"Sua encomenda chegou no *ELEVA LOCKER*.\n\n"
            f"📍 *{armario}*\n"
            f"🚪 Compartimento *#{compartimento}*\n"
            f"🔑 Código de retirada: *{codigo}*\n\n"
            f"Retire no totem:\n→ {totem}\n\n"
            f"Apresente o código no totem ou informe à portaria.\n"
            f"Válido até a retirada."
        )

    @staticmethod
    def _montar_mensagem_email(cliente, armario, compartimento, codigo):
        totem = config.APP_URL_BASE.rstrip("/") + "/totem"
        return (
            f"Olá {cliente}!\n\n"
            f"Sua encomenda chegou no ELEVA LOCKER.\n\n"
            f"Local: {armario}\n"
            f"Compartimento: #{compartimento}\n"
            f"Código de retirada: {codigo}\n\n"
            f"Retire no totem: {totem}\n\n"
            f"Apresente este código no totem ou informe à portaria."
        )

    @staticmethod
    def formatar_resultado_notificacoes(resultados):
        if not resultados:
            return ""

        partes = []
        for item in resultados:
            canal = item.get("canal", "?")
            if item.get("sucesso"):
                sufixo = " (simulado)" if item.get("simulado") else ""
                partes.append(f"{canal}: OK{sufixo}")
            else:
                partes.append(f"{canal}: {item.get('mensagem', 'falhou')}")
        return " — ".join(partes)

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
    def _parse_erro_whatsapp(erro):
        if isinstance(erro, urllib.error.HTTPError):
            try:
                corpo = erro.read().decode("utf-8")
                dados = json.loads(corpo)
                if isinstance(dados, dict):
                    return dados.get("message") or dados.get("error") or corpo[:200]
            except Exception:
                pass
            return f"HTTP {erro.code}: {erro.reason}"
        return str(erro)

    @staticmethod
    def _enviar_whatsapp_evolution(numero, mensagem):
        status = NotificacaoService.status_whatsapp()
        if not status["pronto"]:
            raise ValueError(status["mensagem"] or "WhatsApp não está pronto.")

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

        with urllib.request.urlopen(req, timeout=15) as resp:
            dados = json.loads(resp.read().decode("utf-8"))

        if isinstance(dados, dict):
            erro = dados.get("error") or dados.get("message")
            if isinstance(erro, list) and erro:
                erro = erro[0]
            if dados.get("status") in (400, 404, 500) or (
                isinstance(erro, str) and "exist" in erro.lower()
            ):
                raise ValueError(str(erro))

        return dados

    @staticmethod
    def _enviar_whatsapp_meta(numero, mensagem):
        url = f"https://graph.facebook.com/v18.0/{config.WHATSAPP_META_PHONE_ID}/messages"
        payload = json.dumps({
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "text",
            "text": {"body": mensagem},
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config.WHATSAPP_META_TOKEN}",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))

    @staticmethod
    def _enviar_whatsapp(telefone, mensagem):
        numero, erro = NotificacaoService.validar_telefone_br(telefone)
        if erro:
            return {"sucesso": False, "mensagem": erro}

        if config.NOTIF_MODO == "console" or not NotificacaoService.whatsapp_configurado():
            print(f"\n💬 [WHATSAPP → {numero}]\n{mensagem}\n")
            return {"sucesso": True, "mensagem": "WhatsApp registrado (modo console).", "simulado": True}

        ultimo_erro = "Falha ao enviar WhatsApp."
        for tentativa in range(1, config.WHATSAPP_RETRY_MAX + 1):
            try:
                if config.WHATSAPP_PROVIDER == "meta":
                    dados = NotificacaoService._enviar_whatsapp_meta(numero, mensagem)
                else:
                    dados = NotificacaoService._enviar_whatsapp_evolution(numero, mensagem)

                return {
                    "sucesso": True,
                    "mensagem": "WhatsApp enviado.",
                    "dados": dados,
                    "tentativa": tentativa,
                }

            except Exception as erro:
                ultimo_erro = NotificacaoService._parse_erro_whatsapp(erro)
                if tentativa < config.WHATSAPP_RETRY_MAX:
                    time.sleep(config.WHATSAPP_RETRY_DELAY)

        return {"sucesso": False, "mensagem": ultimo_erro}

    @staticmethod
    def testar_whatsapp(telefone):
        numero, erro = NotificacaoService.validar_telefone_br(telefone)
        if erro:
            raise ValueError(erro)

        mensagem = (
            "✅ *ELEVA LOCKER* — teste de WhatsApp\n\n"
            "Se você recebeu esta mensagem, a integração está funcionando!"
        )
        resultado = NotificacaoService._enviar_whatsapp(telefone, mensagem)

        NotificacaoService._registrar(
            None,
            "whatsapp",
            numero,
            mensagem,
            "enviado" if resultado["sucesso"] else "erro",
            resultado.get("mensagem"),
        )

        if not resultado["sucesso"]:
            raise ValueError(resultado["mensagem"])

        return resultado

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
        mensagem_whatsapp = NotificacaoService._montar_mensagem_whatsapp(
            cliente, armario, compartimento, codigo
        )
        mensagem_email = NotificacaoService._montar_mensagem_email(
            cliente, armario, compartimento, codigo
        )
        assunto = f"ELEVA LOCKER — Encomenda disponível (código {codigo})"
        resultados = []

        if config.NOTIF_EMAIL_ATIVO and email:
            r = NotificacaoService._enviar_email(email, assunto, mensagem_email)
            NotificacaoService._registrar(
                encomenda_id, "email", email, mensagem_email,
                "enviado" if r["sucesso"] else "erro",
                r.get("mensagem"),
            )
            resultados.append({"canal": "email", **r})

        if config.NOTIF_WHATSAPP_ATIVO and telefone:
            r = NotificacaoService._enviar_whatsapp(telefone, mensagem_whatsapp)
            NotificacaoService._registrar(
                encomenda_id, "whatsapp", telefone, mensagem_whatsapp,
                "enviado" if r["sucesso"] else "erro",
                r.get("mensagem"),
            )
            resultados.append({"canal": "whatsapp", **r})

        if config.NOTIF_SMS_ATIVO and telefone:
            r = NotificacaoService._enviar_sms(telefone, mensagem_whatsapp)
            NotificacaoService._registrar(
                encomenda_id, "sms", telefone, mensagem_whatsapp,
                "enviado" if r["sucesso"] else "erro",
                r.get("mensagem"),
            )
            resultados.append({"canal": "sms", **r})

        if not resultados:
            NotificacaoService._registrar(
                encomenda_id, "console", telefone or email or "—",
                mensagem_whatsapp, "enviado", "Nenhum canal ativo — modo console",
            )
            print(f"\n🔔 [NOTIFICAÇÃO — encomenda #{encomenda_id}]\n{mensagem_whatsapp}\n")
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
