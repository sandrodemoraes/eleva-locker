from flask import Blueprint, render_template, session

from middleware.auth_required import login_required
from services.log_service import LogService

logs_bp = Blueprint("logs", __name__)


@logs_bp.route("/logs")
@login_required
def listar():

    return render_template(
        "logs.html",
        usuario=session.get("usuario"),
        perfil=session.get("perfil"),
        logs=LogService.listar(),
    )
