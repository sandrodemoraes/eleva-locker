from flask import Blueprint, request, jsonify

from middleware.api_key_required import api_key_required
from services.armario_service import ArmarioService
from services.encomenda_service import EncomendaService
from repositories.encomenda_repository import EncomendaRepository
from repositories.armario_repository import ArmarioRepository
from repositories.compartimento_repository import CompartimentoRepository
from repositories.base_repository import BaseRepository

v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")


def _site_id_api():
    reg = getattr(request, "api_key", None)
    return reg["site_id"] if reg else None


def _filtrar_armarios_por_site(armarios, site_id):

    if not site_id:
        return armarios

    return [a for a in armarios if a.get("site_id") == site_id]


@v1_bp.route("/status", methods=["GET"])
@api_key_required("read")
def status():

    site_id = _site_id_api()

    with BaseRepository.get_connection() as conn:

        if site_id:
            armarios = conn.execute("""
                SELECT COUNT(*) AS total FROM armarios WHERE site_id = ?
            """, (site_id,)).fetchone()["total"]
            pendentes = conn.execute("""
                SELECT COUNT(*) AS total
                FROM encomendas e
                JOIN compartimentos c ON c.id = e.compartimento
                JOIN armarios a ON a.id = c.armario
                WHERE e.status = 'aguardando_retirada' AND a.site_id = ?
            """, (site_id,)).fetchone()["total"]
        else:
            armarios = ArmarioRepository.contar()
            pendentes = EncomendaRepository.contar_pendentes()

    return jsonify({
        "sucesso": True,
        "versao": "1.0",
        "site_id": site_id,
        "armarios": armarios,
        "encomendas_pendentes": pendentes,
    })


@v1_bp.route("/armarios", methods=["GET"])
@api_key_required("read")
def armarios():

    site_id = _site_id_api()
    lista = ArmarioRepository.listar(site_id=site_id)

    return jsonify({
        "sucesso": True,
        "armarios": [
            {
                "id": a["id"],
                "nome": a["nome"],
                "cidade": a["cidade"],
                "estado": a["estado"],
                "status": a["status"],
                "compartimentos": a["total_compartimentos"],
                "ocupados": a["compartimentos_ocupados"],
            }
            for a in lista
        ],
    })


@v1_bp.route("/compartimentos", methods=["GET"])
@api_key_required("read")
def compartimentos():

    armario_id = request.args.get("armario_id", type=int)
    site_id = _site_id_api()

    if armario_id:
        arm = ArmarioService.buscar_por_id(armario_id)
        if site_id and arm.get("site_id") != site_id:
            return jsonify({"sucesso": False, "mensagem": "Armário não pertence ao site."}), 403
        lista = CompartimentoRepository.listar(armario_id)
    else:
        lista = CompartimentoRepository.listar()
        if site_id:
            ids = {a["id"] for a in ArmarioRepository.listar(site_id=site_id)}
            lista = [c for c in lista if c["armario"] in ids]

    return jsonify({
        "sucesso": True,
        "compartimentos": [
            {
                "id": c["id"],
                "armario_id": c["armario"],
                "numero": c["numero"],
                "status": c["status"],
                "tamanho": c.get("tamanho"),
            }
            for c in lista
        ],
    })


@v1_bp.route("/encomendas", methods=["GET"])
@api_key_required("read")
def listar_encomendas():

    status = request.args.get("status")
    site_id = _site_id_api()

    with BaseRepository.get_connection() as conn:

        sql = """
            SELECT e.id, e.codigo, e.cliente, e.status, e.data_entrada,
                   a.nome AS armario, c.numero AS compartimento
            FROM encomendas e
            JOIN compartimentos c ON c.id = e.compartimento
            JOIN armarios a ON a.id = c.armario
            WHERE 1=1
        """
        params = []

        if status:
            sql += " AND e.status = ?"
            params.append(status)

        if site_id:
            sql += " AND a.site_id = ?"
            params.append(site_id)

        sql += " ORDER BY e.id DESC LIMIT 100"

        rows = conn.execute(sql, tuple(params)).fetchall()

    return jsonify({
        "sucesso": True,
        "encomendas": [dict(r) for r in rows],
    })


@v1_bp.route("/encomendas/<codigo>", methods=["GET"])
@api_key_required("read")
def buscar_encomenda(codigo):

    try:
        enc = EncomendaRepository.buscar_por_codigo(codigo)
        if not enc:
            enc = EncomendaService.buscar_por_id(int(codigo)) if codigo.isdigit() else None
    except (ValueError, TypeError):
        enc = EncomendaRepository.buscar_por_codigo(codigo)

    if not enc:
        return jsonify({"sucesso": False, "mensagem": "Encomenda não encontrada."}), 404

    site_id = _site_id_api()
    if site_id:
        arm = ArmarioRepository.buscar_por_id(
            CompartimentoRepository.buscar_por_id(enc["compartimento"])["armario"]
        )
        if arm.get("site_id") != site_id:
            return jsonify({"sucesso": False, "mensagem": "Encomenda não encontrada."}), 404

    return jsonify({"sucesso": True, "encomenda": dict(enc)})


@v1_bp.route("/encomendas", methods=["POST"])
@api_key_required("write")
def criar_encomenda():

    dados = request.get_json(silent=True) or {}

    compartimento_id = dados.get("compartimento_id")

    if not compartimento_id:
        return jsonify({
            "sucesso": False,
            "mensagem": "compartimento_id é obrigatório.",
        }), 400

    site_id = _site_id_api()

    if site_id:
        comp = CompartimentoRepository.buscar_por_id(compartimento_id)
        arm = ArmarioRepository.buscar_por_id(comp["armario"])
        if arm.get("site_id") != site_id:
            return jsonify({
                "sucesso": False,
                "mensagem": "Compartimento não pertence ao site da chave.",
            }), 403

    try:
        resultado = EncomendaService.depositar(
            compartimento_id=int(compartimento_id),
            cliente=dados.get("cliente", ""),
            telefone=dados.get("telefone"),
            email=dados.get("email"),
            operador=f"API:{request.api_key['nome']}",
            transportadora=dados.get("transportadora"),
            observacao=dados.get("observacao"),
        )
        return jsonify({"sucesso": True, "encomenda": resultado}), 201
    except ValueError as erro:
        return jsonify({"sucesso": False, "mensagem": str(erro)}), 400
