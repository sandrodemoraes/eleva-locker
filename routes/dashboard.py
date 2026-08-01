from flask import Blueprint, render_template, session

from middleware.auth_required import login_required
from services.dashboard_service import DashboardService
from services.encomenda_service import EncomendaService

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():

    stats = DashboardService.obter_estatisticas()
    encomendas_recentes = EncomendaService.listar()[:5]

    return render_template(
        "dashboard.html",
        usuario=session.get("usuario"),
        perfil=session.get("perfil"),
        stats=stats,
        encomendas_recentes=encomendas_recentes,
    )
