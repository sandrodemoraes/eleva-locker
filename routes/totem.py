from flask import Blueprint, render_template, request, jsonify, Response
import json

import config
from middleware.rate_limit import rate_limit
from services.encomenda_service import EncomendaService
from services.armario_service import ArmarioService
from services.compartimento_service import CompartimentoService
from services.qrcode_service import QrcodeService
from services.totem_auth_service import autorizar_deposito_totem, deposito_totem_habilitado

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
        max_portas=(armario["max_portas"] or 8) if armario else 8,
        ajuda_telefone=config.TOTEM_AJUDA_TELEFONE,
        armario_id=armario_id,
        deposito_habilitado=deposito_totem_habilitado(),
        whatsapp_ativo=config.NOTIF_WHATSAPP_ATIVO,
        usa_pin_deposito=bool(config.TOTEM_DEPOSITO_PIN),
    )


@totem_bp.route("/totem/<int:armario_id>/manifest.json")
def manifest_armario(armario_id):

    start = f"/totem/{armario_id}"
    nome = "ELEVA Totem"
    try:
        arm = ArmarioService.buscar_por_id(armario_id)
        nome = f"ELEVA — {arm['nome']}"
    except ValueError:
        pass

    dados = {
        "name": nome,
        "short_name": "Totem",
        "description": "Totem de retirada ELEVA LOCKER",
        "start_url": start,
        "scope": start,
        "display": "fullscreen",
        "orientation": "any",
        "background_color": "#0f3d75",
        "theme_color": "#0f3d75",
        "icons": [{
            "src": "/static/icons/icon.svg",
            "sizes": "any",
            "type": "image/svg+xml",
            "purpose": "any maskable",
        }],
    }
    return Response(
        json.dumps(dados),
        mimetype="application/manifest+json",
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


def _dados_form():
    if request.is_json:
        return request.get_json(silent=True) or {}
    return request.form.to_dict()


def _auth_deposito(dados):
    return autorizar_deposito_totem({
        "pin": dados.get("pin"),
        "email": dados.get("operador_email"),
        "senha": dados.get("operador_senha"),
    })


@totem_bp.route("/totem/compartimentos-livres", methods=["POST"])
def compartimentos_livres_totem():

    dados = _dados_form()

    if not _auth_deposito(dados):
        return jsonify({"erro": "PIN ou login inválido."}), 403

    try:
        armario_id = int(dados.get("armario_id"))
        ArmarioService.buscar_por_id(armario_id)
    except (TypeError, ValueError):
        return jsonify({"erro": "Armário inválido."}), 400

    livres = CompartimentoService.listar_livres(armario_id)

    return jsonify([
        {"id": c["id"], "numero": c["numero"], "tamanho": c["tamanho"] or "M"}
        for c in livres
    ])


@totem_bp.route("/totem/depositar", methods=["POST"])
@rate_limit("totem-depositar", max_tentativas=20, janela_seg=300)
def depositar():

    dados = _dados_form()
    operador = _auth_deposito(dados)

    if not operador:
        return jsonify({"sucesso": False, "mensagem": "PIN ou login inválido."}), 403

    try:
        armario_id = int(dados.get("armario_id"))
        compartimento_id = int(dados.get("compartimento_id"))
    except (TypeError, ValueError):
        return jsonify({"sucesso": False, "mensagem": "Dados inválidos."}), 400

    comp = CompartimentoService.buscar_por_id(compartimento_id)
    if int(comp["armario"]) != armario_id:
        return jsonify({"sucesso": False, "mensagem": "Compartimento inválido."}), 400

    try:
        resultado = EncomendaService.depositar(
            compartimento_id=compartimento_id,
            cliente=dados.get("cliente", ""),
            telefone=dados.get("telefone", ""),
            email=dados.get("email_morador", ""),
            operador=f"Totem ({operador})",
            transportadora=dados.get("transportadora", ""),
            observacao=dados.get("observacao", ""),
        )

        return jsonify({
            "sucesso": True,
            "mensagem": "Morador notificado por WhatsApp.",
            "compartimento": resultado["compartimento"],
            "cliente": dados.get("cliente", ""),
            "modo": "deposito",
        })

    except ValueError as erro:
        return jsonify({"sucesso": False, "mensagem": str(erro)}), 400

    except Exception:
        return jsonify({"sucesso": False, "mensagem": "Erro ao depositar."}), 500
