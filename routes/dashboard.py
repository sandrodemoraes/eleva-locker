from flask import Blueprint, render_template, session, redirect

from middleware.auth_required import login_required
from middleware.operador_scope import get_armario_restrito
from services.dashboard_service import DashboardService
from services.encomenda_service import EncomendaService
from services.site_service import SiteService
from middleware.site_scope import get_site_id

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():

    restrito = get_armario_restrito()
    if restrito:
        return redirect(f"/armarios/{restrito}")

    stats = DashboardService.obter_estatisticas()
    encomendas_recentes = EncomendaService.listar()[:5]

    return render_template(
        "dashboard.html",
        usuario=session.get("usuario"),
        perfil=session.get("perfil"),
        stats=stats,
        encomendas_recentes=encomendas_recentes,
        sites=SiteService.listar_ativos(),
        site_atual=get_site_id(),
    )
