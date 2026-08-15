from flask import Blueprint, render_template, request, redirect, session, flash

import config
from middleware.auth_required import login_required, perfil_required
from services.notificacao_service import NotificacaoService

notificacoes_bp = Blueprint("notificacoes", __name__)


@notificacoes_bp.route("/notificacoes")
@login_required
def listar():

    return render_template(
        "notificacoes.html",
        usuario=session.get("usuario"),
        perfil=session.get("perfil"),
        notificacoes=NotificacaoService.listar(),
        config=config,
        whatsapp_configurado=NotificacaoService.whatsapp_configurado(),
        whatsapp_status=NotificacaoService.status_whatsapp(),
    )


@notificacoes_bp.route("/notificacoes/testar-whatsapp", methods=["POST"])
@login_required
@perfil_required("Administrador")
def testar_whatsapp():

    try:
        NotificacaoService.testar_whatsapp(request.form.get("telefone", ""))
        flash("WhatsApp de teste enviado com sucesso!", "success")
    except ValueError as erro:
        flash(str(erro), "warning")
    except Exception:
        flash("Erro ao enviar WhatsApp de teste.", "danger")

    return redirect("/notificacoes")
