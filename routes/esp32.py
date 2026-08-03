from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash,
)

from services.esp32_service import Esp32Service
from services.armario_service import ArmarioService

esp32_bp = Blueprint("esp32", __name__)


@esp32_bp.route("/esp32")
def esp32():

    if "usuario" not in session:
        return redirect("/")

    return render_template(
        "esp32.html",
        usuario=session["usuario"],
        perfil=session["perfil"],
        dispositivos=Esp32Service.listar(),
        armarios=ArmarioService.listar(),
    )


@esp32_bp.route("/esp32/novo", methods=["POST"])
def novo_esp32():

    if "usuario" not in session:
        return redirect("/")

    try:
        Esp32Service.inserir({
            "nome": request.form.get("nome", ""),
            "ip": request.form.get("ip", ""),
            "mac": request.form.get("mac", ""),
            "armario": request.form.get("armario", ""),
            "status": request.form.get("status", "Ativo"),
        })
        flash("ESP32 cadastrado com sucesso!", "success")

    except ValueError as erro:
        flash(str(erro), "warning")

    except Exception:
        flash("Erro interno ao cadastrar ESP32.", "danger")

    return redirect("/esp32")


@esp32_bp.route("/esp32/editar/<int:esp32_id>", methods=["POST"])
def editar_esp32(esp32_id):

    if "usuario" not in session:
        return redirect("/")

    try:
        Esp32Service.atualizar(esp32_id, {
            "nome": request.form.get("nome", ""),
            "ip": request.form.get("ip", ""),
            "mac": request.form.get("mac", ""),
            "armario": request.form.get("armario", ""),
            "status": request.form.get("status", "Ativo"),
        })
        flash("ESP32 atualizado com sucesso!", "success")

    except ValueError as erro:
        flash(str(erro), "warning")

    except Exception:
        flash("Erro interno ao atualizar ESP32.", "danger")

    return redirect("/esp32")


@esp32_bp.route("/esp32/excluir/<int:esp32_id>", methods=["POST"])
def excluir_esp32(esp32_id):

    if "usuario" not in session:
        return redirect("/")

    try:
        Esp32Service.excluir(esp32_id)
        flash("ESP32 excluído com sucesso!", "success")

    except Exception:
        flash("Erro interno ao excluir ESP32.", "danger")

    return redirect("/esp32")
