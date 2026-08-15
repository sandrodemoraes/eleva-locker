from flask import Blueprint, render_template, session, jsonify

from middleware.auth_required import login_required
from services.relatorio_service import RelatorioService

relatorios_bp = Blueprint("relatorios", __name__)


@relatorios_bp.route("/relatorios")
@login_required
def index():

    dados = RelatorioService.dados_completos()

    return render_template(
        "relatorios.html",
        usuario=session.get("usuario"),
        perfil=session.get("perfil"),
        dados=dados,
    )


@relatorios_bp.route("/relatorios/api/dados")
@login_required
def api_dados():

    return jsonify(RelatorioService.dados_completos())
