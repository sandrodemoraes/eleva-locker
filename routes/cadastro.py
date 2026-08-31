"""Cadastro público — QR Code leva para /cadastro."""

from flask import Blueprint, render_template, request, redirect, send_file, session, url_for
import config

from middleware.auth_required import login_required, perfil_required
from services.cadastro_publico_service import CadastroPublicoService
from services.plano_service import PlanoService
from services.qrcode_service import QrcodeService

cadastro_bp = Blueprint("cadastro", __name__)


def _ctx_publico():
    contato_tel = config.LGPD_CONTATO_TELEFONE or config.TOTEM_AJUDA_TELEFONE or ""
    return {
        "lgpd_versao": config.LGPD_POLITICA_VERSAO,
        "lgpd_controlador": config.LGPD_CONTROLADOR_NOME,
        "lgpd_email": config.LGPD_CONTATO_EMAIL,
        "lgpd_telefone": contato_tel,
        "app_url_base": config.APP_URL_BASE.rstrip("/"),
        "lgpd_consentimento_obrigatorio": config.LGPD_CONSENTIMENTO_USUARIO,
        "pagina": "cadastro",
    }


@cadastro_bp.route("/cadastro")
def formulario():
    if not config.CADASTRO_PUBLICO_ATIVO:
        return render_template(
            "cadastro/indisponivel.html",
            **_ctx_publico(),
        )

    plano_pre = request.args.get("plano", type=int)
    planos = PlanoService.listar()

    return render_template(
        "cadastro/form.html",
        planos=planos,
        plano_pre=plano_pre,
        erro=None,
        **_ctx_publico(),
    )


@cadastro_bp.route("/cadastro", methods=["POST"])
def enviar():
    if not config.CADASTRO_PUBLICO_ATIVO:
        return render_template(
            "cadastro/indisponivel.html",
            **_ctx_publico(),
        )

    planos = PlanoService.listar()
    dados = {
        "razao_social": request.form.get("razao_social"),
        "nome_fantasia": request.form.get("nome_fantasia"),
        "cnpj": request.form.get("cnpj"),
        "responsavel": request.form.get("responsavel"),
        "telefone": request.form.get("telefone"),
        "email_empresa": request.form.get("email_empresa"),
        "nome": request.form.get("nome"),
        "email": request.form.get("email"),
        "senha": request.form.get("senha"),
        "confirmar": request.form.get("confirmar"),
        "plano_id": request.form.get("plano_id"),
        "lgpd_consentimento": request.form.get("lgpd_consentimento"),
    }

    try:
        resultado = CadastroPublicoService.processar(
            dados,
            ip=request.remote_addr,
            user_agent=(request.user_agent.string if request.user_agent else None),
        )
    except ValueError as erro:
        return render_template(
            "cadastro/form.html",
            planos=planos,
            plano_pre=dados.get("plano_id"),
            erro=str(erro),
            form=dados,
            **_ctx_publico(),
        )

    return render_template(
        "cadastro/confirmacao.html",
        resultado=resultado,
        **_ctx_publico(),
    )


@cadastro_bp.route("/cadastro/qrcode")
@cadastro_bp.route("/cadastro/qrcode.png")
def qrcode_png():
    plano_id = request.args.get("plano", type=int)
    url = CadastroPublicoService.url_cadastro(plano_id)
    png = QrcodeService.gerar_png_url(url)
    return send_file(
        png,
        mimetype="image/png",
        download_name="eleva-cadastro-qrcode.png",
    )


@cadastro_bp.route("/cadastro/qr")
@login_required
@perfil_required("Administrador")
def qr_admin():
    plano_id = request.args.get("plano", type=int)
    url = CadastroPublicoService.url_cadastro(plano_id)
    planos = PlanoService.listar()
    return render_template(
        "cadastro/qr_admin.html",
        usuario=session.get("usuario"),
        perfil=session.get("perfil"),
        url_cadastro=url,
        plano_id=plano_id,
        planos=planos,
        qrcode_url=url_for("cadastro.qrcode_png", plano=plano_id) if plano_id else url_for("cadastro.qrcode_png"),
    )
