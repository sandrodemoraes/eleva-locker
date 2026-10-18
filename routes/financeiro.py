from flask import Blueprint, render_template, session, redirect, flash

from middleware.auth_required import login_required, perfil_required
from services.faturamento_service import FaturamentoService
from services.contrato_service import ContratoService
from services.plano_service import PlanoService

financeiro_bp = Blueprint("financeiro", __name__)


@financeiro_bp.route("/financeiro")
@login_required
@perfil_required("Administrador")
def dashboard():

    metricas = FaturamentoService.obter_metricas()

    return render_template(
        "financeiro.html",
        usuario=session.get("usuario"),
        perfil=session.get("perfil"),
        metricas=metricas,
        contratos=ContratoService.listar(),
        faturas=FaturamentoService.listar_faturas()[:10],
    )
