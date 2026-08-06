from pathlib import Path

from flask import Blueprint, render_template, request, jsonify, Response, make_response, redirect
import json

import config

TOTEM_VERSAO = "2.3.3"
from middleware.rate_limit import rate_limit
from services.encomenda_service import EncomendaService
from services.armario_service import ArmarioService
from services.compartimento_service import CompartimentoService
from services.qrcode_service import QrcodeService
from services.totem_auth_service import autorizar_deposito_totem, deposito_totem_habilitado
from services.totem_destinatario_service import TotemDestinatarioService

totem_bp = Blueprint("totem", __name__)


def _totem_template_info():
    path = Path(__file__).resolve().parent.parent / "templates" / "totem.html"
    texto = path.read_text(encoding="utf-8") if path.exists() else ""
    return {
        "versao": TOTEM_VERSAO,
        "deposito": "Depositar encomenda" in texto,
        "home_botoes": "Retirar encomenda" in texto,
        "layout_antigo": "Abrir compartimento" in texto or "Totem de retirada" in texto,
    }


@totem_bp.route("/totem/versao")
def versao():
    info = _totem_template_info()
    info["ok"] = info["deposito"] and info["home_botoes"] and not info["layout_antigo"]
    return jsonify(info)


@totem_bp.route("/totem")
@totem_bp.route("/totem/<int:armario_id>")
def index(armario_id=None):

    if armario_id is None and config.TOTEM_ARMARIO_ID:
        return redirect(f"/totem/{config.TOTEM_ARMARIO_ID}")

    armario = None

    if armario_id:
        try:
            armario = ArmarioService.buscar_por_id(armario_id)
        except ValueError:
            armario = None

    armarios_lista = None
    if not armario and not config.TOTEM_ARMARIO_ID:
        armarios_lista = ArmarioService.listar_ativos()

    resp = make_response(render_template(
        "totem.html",
        armario=armario,
        armarios=armarios_lista,
        max_portas=(armario["max_portas"] or 8) if armario else 8,
        ajuda_telefone=config.TOTEM_AJUDA_TELEFONE,
        armario_id=armario_id,
        deposito_habilitado=deposito_totem_habilitado(),
        whatsapp_ativo=config.NOTIF_WHATSAPP_ATIVO,
        usa_pin_deposito=bool(config.TOTEM_DEPOSITO_PIN) and not config.TOTEM_DEPOSITO_SEM_PIN,
        deposito_sem_pin=config.TOTEM_DEPOSITO_SEM_PIN,
        totem_versao=TOTEM_VERSAO,
    ))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    return resp


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
            "porta_aberta": resultado.get("porta_aberta", True),
            "aviso": resultado["esp32"].get("mensagem") if not resultado.get("porta_aberta") else "",
        })

    except ValueError as erro:

        return jsonify({"sucesso": False, "mensagem": str(erro)}), 400

    except Exception as erro:
        import traceback
        traceback.print_exc()
        return jsonify({"sucesso": False, "mensagem": "Erro interno. Tente de novo ou fale com a portaria."}), 500


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
    if config.TOTEM_DEPOSITO_SEM_PIN:
        return "Totem"
    return autorizar_deposito_totem({
        "pin": dados.get("pin"),
        "email": dados.get("operador_email"),
        "senha": dados.get("operador_senha"),
    })


@totem_bp.route("/totem/destinatarios")
@rate_limit("totem-destinatarios", max_tentativas=60, janela_seg=60)
def destinatarios_totem():

    termo = request.args.get("q", "").strip()
    armario_raw = request.args.get("armario_id", "").strip()
    armario_id = int(armario_raw) if armario_raw.isdigit() else None

    return jsonify(TotemDestinatarioService.buscar(termo, armario_id))


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
    todos = CompartimentoService.listar(armario_id)

    return jsonify({
        "livres": [
            {"id": c["id"], "numero": c["numero"], "tamanho": (c["tamanho"] or "M").upper()}
            for c in livres
        ],
        "mapa": [
            {
                "id": c["id"],
                "numero": c["numero"],
                "tamanho": (c["tamanho"] or "M").upper(),
                "livre": c["status"] == "livre",
            }
            for c in sorted(todos, key=lambda x: x["numero"])
        ],
    })


@totem_bp.route("/totem/depositar", methods=["POST"])
@rate_limit("totem-depositar", max_tentativas=20, janela_seg=300)
def depositar():

    dados = _dados_form()
    operador = _auth_deposito(dados)

    if not operador:
        return jsonify({"sucesso": False, "mensagem": "PIN ou login inválido."}), 403

    try:
        armario_id = int(dados.get("armario_id"))
        compartimento_id = dados.get("compartimento_id")
        tamanho_pedido = (dados.get("tamanho") or "").strip().upper()
    except (TypeError, ValueError):
        return jsonify({"sucesso": False, "mensagem": "Dados inválidos."}), 400

    if not compartimento_id and tamanho_pedido:
        livres = CompartimentoService.listar_livres(armario_id)
        candidatos = [
            c for c in livres
            if (c["tamanho"] or "M").upper() == tamanho_pedido
        ]
        if not candidatos:
            return jsonify({
                "sucesso": False,
                "mensagem": f"Nenhum compartimento {tamanho_pedido} livre.",
            }), 400
        compartimento_id = candidatos[0]["id"]

    try:
        compartimento_id = int(compartimento_id)
    except (TypeError, ValueError):
        return jsonify({"sucesso": False, "mensagem": "Selecione o tamanho ou compartimento."}), 400

    comp = CompartimentoService.buscar_por_id(compartimento_id)
    if int(comp["armario"]) != armario_id:
        return jsonify({"sucesso": False, "mensagem": "Compartimento inválido."}), 400

    try:
        aguardar_fechamento = str(dados.get("aguardar_fechamento", "1")).lower() in ("1", "true", "sim", "yes")
        resultado = EncomendaService.depositar(
            compartimento_id=compartimento_id,
            cliente=dados.get("cliente", ""),
            telefone=dados.get("telefone", ""),
            email=dados.get("email_morador", ""),
            operador=f"Totem ({operador})",
            transportadora=dados.get("transportadora", ""),
            observacao=dados.get("observacao", ""),
            notificar=not aguardar_fechamento,
        )

        return jsonify({
            "sucesso": True,
            "mensagem": "Porta aberta. Feche para concluir." if aguardar_fechamento else "Morador notificado por WhatsApp.",
            "encomenda_id": resultado["id"],
            "compartimento": resultado["compartimento"],
            "compartimento_id": resultado["compartimento_id"],
            "tamanho": (comp["tamanho"] or "M").upper(),
            "cliente": dados.get("cliente", ""),
            "modo": "deposito",
            "aguardar_fechamento": aguardar_fechamento,
        })

    except ValueError as erro:
        return jsonify({"sucesso": False, "mensagem": str(erro)}), 400

    except Exception:
        return jsonify({"sucesso": False, "mensagem": "Erro ao depositar."}), 500


@totem_bp.route("/totem/depositar/concluir", methods=["POST"])
@rate_limit("totem-depositar-concluir", max_tentativas=30, janela_seg=300)
def concluir_deposito():

    dados = _dados_form()
    operador = _auth_deposito(dados)

    if not operador:
        return jsonify({"sucesso": False, "mensagem": "PIN ou login inválido."}), 403

    try:
        encomenda_id = int(dados.get("encomenda_id"))
    except (TypeError, ValueError):
        return jsonify({"sucesso": False, "mensagem": "Encomenda inválida."}), 400

    try:
        resultado = EncomendaService.concluir_deposito_totem(
            encomenda_id,
            operador=f"Totem ({operador})",
        )

        return jsonify({
            "sucesso": True,
            "mensagem": "Depósito concluído! Morador notificado.",
            "encomenda_id": resultado["id"],
            "compartimento": resultado["compartimento"],
            "cliente": resultado["cliente"],
            "modo": "deposito",
        })

    except ValueError as erro:
        return jsonify({"sucesso": False, "mensagem": str(erro)}), 400

    except Exception:
        return jsonify({"sucesso": False, "mensagem": "Erro ao concluir depósito."}), 500


@totem_bp.route("/totem/porta/<int:compartimento_id>/status")
def status_porta(compartimento_id):
    """Status da porta — sensor ESP32 (fase 2); hoje retorna aberta."""
    try:
        comp = CompartimentoService.buscar_por_id(compartimento_id)
        return jsonify({
            "compartimento_id": compartimento_id,
            "numero": comp["numero"],
            "fechada": False,
            "sensor": False,
        })
    except ValueError:
        return jsonify({"erro": "Compartimento não encontrado."}), 404
