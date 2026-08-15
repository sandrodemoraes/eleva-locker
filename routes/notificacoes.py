from flask import Blueprint, render_template, request, redirect, session, flash

import config
from middleware.auth_required import login_required, perfil_required
from services.notificacao_service import NotificacaoService
from services.totem_ajuda_service import TotemAjudaService

notificacoes_bp = Blueprint("notificacoes", __name__)


@notificacoes_bp.route("/notificacoes")
@login_required
def listar():

    return render_template(
        "notificacoes.html",
        usuario=session.get("usuario"),
        perfil=session.get("perfil"),
        notificacoes=NotificacaoService.listar(),
        pedidos_ajuda=TotemAjudaService.listar(limite=30),
        ajuda_pendentes=TotemAjudaService.contar_pendentes(),
        config=config,
        whatsapp_configurado=NotificacaoService.whatsapp_configurado(),
        whatsapp_status=NotificacaoService.status_whatsapp(),
    )


@notificacoes_bp.route("/notificacoes/ajuda/<int:pedido_id>/atender", methods=["POST"])
@login_required
def atender_ajuda(pedido_id):

    try:
        TotemAjudaService.marcar_atendido(pedido_id, session.get("usuario") or session.get("nome"))
        flash("Pedido de ajuda marcado como atendido.", "success")
    except ValueError as erro:
        flash(str(erro), "warning")
    except Exception:
        flash("Erro ao atualizar pedido de ajuda.", "danger")

    return redirect("/notificacoes#ajuda-totem")


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
