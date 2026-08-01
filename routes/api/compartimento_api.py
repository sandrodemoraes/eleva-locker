from flask import Blueprint, request, jsonify, session

from middleware.auth_required import login_required
from services.esp32_service import Esp32Service

compartimento_api_bp = Blueprint("compartimento_api", __name__, url_prefix="/api/compartimento")


@compartimento_api_bp.route("/abrir/<int:compartimento_id>", methods=["POST"])
@login_required
def abrir(compartimento_id):

    resultado = Esp32Service.abrir_compartimento(
        compartimento_id,
        operador=session.get("usuario", "Admin"),
    )

    status = 200 if resultado["sucesso"] else 503

    return jsonify(resultado), status
