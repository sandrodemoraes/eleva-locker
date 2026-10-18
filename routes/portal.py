from flask import Blueprint, render_template, session, redirect

from middleware.auth_required import login_required
from services.empresa_service import EmpresaService
from services.limite_plano_service import LimitePlanoService
from services.faturamento_service import FaturamentoService
from services.contrato_service import ContratoService

portal_bp = Blueprint("portal", __name__)


@portal_bp.route("/portal")
@login_required
def index():

    empresas = EmpresaService.listar_ativas()

    return render_template(
        "portal_index.html",
        usuario=session.get("usuario"),
        perfil=session.get("perfil"),
        empresas=empresas,
    )


@portal_bp.route("/portal/empresa/<int:empresa_id>")
@login_required
def empresa(empresa_id):

    try:

        empresa = EmpresaService.buscar_por_id(empresa_id)

    except ValueError:

        return redirect("/portal")

    uso = LimitePlanoService.obter_uso(empresa_id)
    contratos = ContratoService.listar(empresa_id)
    faturas = FaturamentoService.listar_faturas(contrato_id=None)

    faturas_empresa = [
        f for f in faturas
        if f["empresa_id"] == empresa_id
    ][:12]

    return render_template(
        "portal.html",
        usuario=session.get("usuario"),
        perfil=session.get("perfil"),
        empresa=empresa,
        uso=uso,
        contratos=contratos,
        faturas=faturas_empresa,
    )
