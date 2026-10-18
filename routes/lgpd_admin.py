"""Rotas admin LGPD Fase 3 — direitos do titular (exportar / anonimizar)."""

from flask import (
    Blueprint, render_template, redirect, session, flash, Response, abort, request,
)

import config
from middleware.auth_required import login_required, perfil_required
from repositories.lgpd_solicitacao_repository import LgpdSolicitacaoRepository
from services.lgpd_titular_service import LgpdTitularService

lgpd_admin_bp = Blueprint("lgpd_admin", __name__)


def _requer_titular_ativo():
    if not config.LGPD_TITULAR_ATIVO:
        abort(404)


@lgpd_admin_bp.route("/lgpd/admin/titular")
@login_required
@perfil_required("Administrador")
def titular_index():
    _requer_titular_ativo()
    titular_tipo = request.args.get("tipo", "usuario")
    titular_id = request.args.get("id", "").strip()
    preview = None

    if titular_id.isdigit():
        try:
            preview = LgpdTitularService.coletar_dados(titular_tipo, int(titular_id))
        except ValueError as erro:
            flash(str(erro), "warning")

    return render_template(
        "lgpd/admin_titular.html",
        usuario=session.get("usuario"),
        titular_tipo=titular_tipo,
        titular_id=titular_id,
        preview=preview,
        solicitacoes=LgpdSolicitacaoRepository.listar(30),
        lgpd_politica_versao=config.LGPD_POLITICA_VERSAO,
    )


@lgpd_admin_bp.route("/lgpd/admin/export/<titular_tipo>/<int:titular_id>.json")
@login_required
@perfil_required("Administrador")
def exportar_json(titular_tipo, titular_id):
    _requer_titular_ativo()
    try:
        conteudo = LgpdTitularService.exportar_json(titular_tipo, titular_id)
        LgpdTitularService.registrar_acesso(
            titular_tipo, titular_id, session.get("usuario"), "json",
        )
    except ValueError as erro:
        flash(str(erro), "warning")
        return redirect(f"/lgpd/admin/titular?tipo={titular_tipo}&id={titular_id}")

    nome = f"lgpd_{titular_tipo}_{titular_id}.json"
    return Response(
        conteudo,
        mimetype="application/json; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{nome}"'},
    )


@lgpd_admin_bp.route("/lgpd/admin/export/<titular_tipo>/<int:titular_id>.csv")
@login_required
@perfil_required("Administrador")
def exportar_csv(titular_tipo, titular_id):
    _requer_titular_ativo()
    try:
        conteudo = LgpdTitularService.exportar_csv(titular_tipo, titular_id)
        LgpdTitularService.registrar_acesso(
            titular_tipo, titular_id, session.get("usuario"), "csv",
        )
    except ValueError as erro:
        flash(str(erro), "warning")
        return redirect(f"/lgpd/admin/titular?tipo={titular_tipo}&id={titular_id}")

    nome = f"lgpd_{titular_tipo}_{titular_id}.csv"
    return Response(
        conteudo,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{nome}"'},
    )


@lgpd_admin_bp.route("/lgpd/admin/anonimizar/<titular_tipo>/<int:titular_id>", methods=["POST"])
@login_required
@perfil_required("Administrador")
def anonimizar(titular_tipo, titular_id):
    _requer_titular_ativo()
    try:
        resultado = LgpdTitularService.anonimizar(
            titular_tipo, titular_id, session.get("usuario"),
        )
        n = len(resultado.get("encomendas_anonimizadas", []))
        flash(f"Titular anonimizado. {n} encomenda(s) atualizada(s).", "success")
    except ValueError as erro:
        flash(str(erro), "warning")

    return redirect(f"/lgpd/admin/titular?tipo={titular_tipo}&id={titular_id}")


@lgpd_admin_bp.route("/lgpd/admin/oposicao/<int:usuario_id>", methods=["POST"])
@login_required
@perfil_required("Administrador")
def oposicao_marketing(usuario_id):
    _requer_titular_ativo()
    try:
        LgpdTitularService.definir_oposicao_marketing(
            usuario_id, session.get("usuario"), opt_out=True,
        )
        flash("Oposição a marketing registrada.", "success")
    except ValueError as erro:
        flash(str(erro), "warning")
    return redirect(f"/lgpd/admin/titular?tipo=usuario&id={usuario_id}")
