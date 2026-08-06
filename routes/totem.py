from flask import Blueprint, render_template, request, jsonify

import config
from middleware.rate_limit import rate_limit
from services.encomenda_service import EncomendaService
from services.armario_service import ArmarioService
from services.qrcode_service import QrcodeService

totem_bp = Blueprint("totem", __name__)


@totem_bp.route("/totem")
@totem_bp.route("/totem/<int:armario_id>")
def index(armario_id=None):

    armario = None

    if armario_id:
        try:
            armario = ArmarioService.buscar_por_id(armario_id)
        except ValueError:
            armario = None

    return render_template(
        "totem.html",
        armario=armario,
        armarios=ArmarioService.listar_ativos() if not armario else None,
        max_portas=(armario.get("max_portas") or 8) if armario else 8,
        ajuda_telefone=config.TOTEM_AJUDA_TELEFONE,
    )


@totem_bp.route("/totem/retirar", methods=["POST"])
@rate_limit("totem-retirar", max_tentativas=config.TOTEM_RATE_LIMIT, janela_seg=config.TOTEM_RATE_JANELA)
def retirar():

    codigo = request.form.get("codigo", "").strip()
    armario_raw = request.form.get("armario_id", "").strip()
    armario_id = int(armario_raw) if armario_raw.isdigit() else None

    try:

        resultado = EncomendaService.retirar(
            codigo,
            operador="Totem",
            armario_id=armario_id,
        )

        return jsonify({
            "sucesso": True,
            "mensagem": "Retirada confirmada!",
            "cliente": resultado["cliente"],
            "compartimento": resultado["compartimento"],
            "armario": resultado["armario"],
        })

    except ValueError as erro:

        return jsonify({"sucesso": False, "mensagem": str(erro)}), 400

    except Exception:

        return jsonify({"sucesso": False, "mensagem": "Erro interno."}), 500


@totem_bp.route("/totem/scan", methods=["POST"])
@rate_limit("totem-scan", max_tentativas=config.TOTEM_RATE_LIMIT, janela_seg=config.TOTEM_RATE_JANELA)
def scan_qrcode():

    dados = request.get_json(silent=True) or {}
    conteudo = dados.get("conteudo", "")
    armario_raw = dados.get("armario_id")
    armario_id = int(armario_raw) if armario_raw else None

    parsed = QrcodeService.parse_conteudo(conteudo)

    if not parsed:

        return jsonify({"sucesso": False, "mensagem": "QR Code inválido."}), 400

    try:

        resultado = EncomendaService.retirar(
            parsed["codigo"],
            operador="Totem-QR",
            armario_id=armario_id,
        )

        return jsonify({
            "sucesso": True,
            "mensagem": "Retirada confirmada!",
            "cliente": resultado["cliente"],
            "compartimento": resultado["compartimento"],
            "armario": resultado["armario"],
        })

    except ValueError as erro:

        return jsonify({"sucesso": False, "mensagem": str(erro)}), 400
