from flask import Blueprint, render_template, session, redirect, url_for, flash

from middleware.auth_required import login_required
from services.notificacao_service import NotificacaoService
from services.totem_ajuda_service import TotemAjudaService
import config

notificacoes_bp = Blueprint("notificacoes", __name__)


@notificacoes_bp.route("/notificacoes")
@login_required
def listar():

    return render_template(
        "notificacoes.html",
        usuario=session.get("usuario"),
        perfil=session.get("perfil"),
        notificacoes=NotificacaoService.listar(),
        ajuda_pedidos=TotemAjudaService.listar(status="pendente", limite=20),
        config=config,
    )


@notificacoes_bp.route("/notificacoes/ajuda-totem/<int:pedido_id>/atendido", methods=["POST"])
@login_required
def ajuda_totem_atendido(pedido_id):
    try:
        TotemAjudaService.marcar_atendido(
            pedido_id,
            session.get("usuario") or session.get("nome") or "admin",
        )
        flash("Pedido de ajuda marcado como atendido.", "success")
    except ValueError as erro:
        flash(str(erro), "warning")
    return redirect(url_for("notificacoes.listar", _anchor="ajuda-totem"))


@notificacoes_bp.route("/notificacoes/ajuda-totem/<int:pedido_id>/atendido", methods=["GET"])
@login_required
def ajuda_totem_atendido_get(pedido_id):
    """Evita página em branco/erro se o navegador abrir o link do POST."""
    return redirect(url_for("notificacoes.listar", _anchor="ajuda-totem"))
