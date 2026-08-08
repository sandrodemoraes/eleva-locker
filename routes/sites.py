from flask import Blueprint, render_template, request, redirect, session, flash, jsonify

from middleware.auth_required import login_required, perfil_required
from middleware.site_scope import set_site_id, get_site_id
from services.site_service import SiteService
from services.api_key_service import ApiKeyService
from services.log_service import LogService

sites_bp = Blueprint("sites", __name__)


@sites_bp.route("/sites")
@login_required
@perfil_required("Administrador")
def listar():

    return render_template(
        "sites.html",
        usuario=session.get("usuario"),
        perfil=session.get("perfil"),
        sites=SiteService.listar(),
        api_keys=ApiKeyService.listar(),
        site_atual=get_site_id(),
    )


@sites_bp.route("/sites/novo", methods=["POST"])
@login_required
@perfil_required("Administrador")
def novo():

    try:
        SiteService.criar({
            "nome": request.form.get("nome", ""),
            "codigo": request.form.get("codigo", ""),
            "endereco": request.form.get("endereco", ""),
            "cidade": request.form.get("cidade", ""),
            "estado": request.form.get("estado", ""),
            "status": int(request.form.get("status", 1)),
        })
        LogService.registrar(None, session.get("usuario"), "Site cadastrado")
        flash("Site cadastrado com sucesso!", "success")
    except ValueError as erro:
        flash(str(erro), "warning")
    except Exception:
        flash("Erro ao cadastrar site.", "danger")

    return redirect("/sites")


@sites_bp.route("/sites/editar/<int:site_id>", methods=["POST"])
@login_required
@perfil_required("Administrador")
def editar(site_id):

    try:
        SiteService.atualizar(site_id, {
            "nome": request.form.get("nome", ""),
            "codigo": request.form.get("codigo", ""),
            "endereco": request.form.get("endereco", ""),
            "cidade": request.form.get("cidade", ""),
            "estado": request.form.get("estado", ""),
            "status": int(request.form.get("status", 1)),
        })
        flash("Site atualizado!", "success")
    except ValueError as erro:
        flash(str(erro), "warning")

    return redirect("/sites")


@sites_bp.route("/sites/excluir/<int:site_id>", methods=["POST"])
@login_required
@perfil_required("Administrador")
def excluir(site_id):

    try:
        SiteService.excluir(site_id)
        flash("Site excluído.", "success")
    except ValueError as erro:
        flash(str(erro), "warning")

    return redirect("/sites")


@sites_bp.route("/sites/selecionar", methods=["POST"])
@login_required
def selecionar():

    set_site_id(request.form.get("site_id"))
    return redirect(request.referrer or "/dashboard")


@sites_bp.route("/sites/api-key/nova", methods=["POST"])
@login_required
@perfil_required("Administrador")
def nova_api_key():

    try:
        site_id = request.form.get("site_id") or None
        _, chave = ApiKeyService.criar(
            request.form.get("nome", ""),
            site_id=site_id,
            permissoes=request.form.get("permissoes", "read"),
        )
        flash(f"Chave criada: {chave} (copie agora — não será exibida novamente)", "success")
    except ValueError as erro:
        flash(str(erro), "warning")

    return redirect("/sites")


@sites_bp.route("/sites/api-key/toggle/<int:key_id>", methods=["POST"])
@login_required
@perfil_required("Administrador")
def toggle_api_key(key_id):

    ativo = request.form.get("ativo", "0") == "1"
    ApiKeyService.alternar_ativo(key_id, ativo)
    flash("Status da chave atualizado.", "success")
    return redirect("/sites")


@sites_bp.route("/sites/api-key/excluir/<int:key_id>", methods=["POST"])
@login_required
@perfil_required("Administrador")
def excluir_api_key(key_id):

    ApiKeyService.excluir(key_id)
    flash("Chave removida.", "success")
    return redirect("/sites")
