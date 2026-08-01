from flask import Blueprint, render_template, session

from middleware.auth_required import login_required
from services.notificacao_service import NotificacaoService
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
        config=config,
    )
