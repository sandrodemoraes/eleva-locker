from flask import Blueprint, render_template, request, redirect, session, flash

from middleware.auth_required import login_required
from services.compartimento_service import CompartimentoService
from services.armario_service import ArmarioService
from services.esp32_service import Esp32Service
from services.log_service import LogService

compartimentos_bp = Blueprint("compartimentos", __name__)


@compartimentos_bp.route("/compartimentos")
@login_required
def listar():

    armario_id = request.args.get("armario_id", type=int)

    return render_template(
        "compartimentos.html",
        usuario=session.get("usuario"),
        perfil=session.get("perfil"),
        compartimentos=CompartimentoService.listar(armario_id),
        armarios=ArmarioService.listar_ativos(),
        dispositivos_esp32=Esp32Service.listar(),
        armario_filtro=armario_id,
    )


@compartimentos_bp.route("/compartimentos/novo", methods=["POST"])
@login_required
def novo():

    try:

        CompartimentoService.criar({
            "armario": int(request.form.get("armario")),
            "numero": request.form.get("numero"),
            "rele": int(request.form["rele"]) if request.form.get("rele") else None,
            "esp32_id": int(request.form["esp32_id"]) if request.form.get("esp32_id") else None,
            "status": request.form.get("status", "livre"),
            "tamanho": request.form.get("tamanho", "M"),
        })

        LogService.registrar(None, session.get("usuario"), "Compartimento cadastrado")
        flash("Compartimento cadastrado com sucesso!", "success")

    except (ValueError, TypeError) as erro:
        flash(str(erro), "warning")
    except Exception:
        flash("Erro ao cadastrar compartimento.", "danger")

    return redirect("/compartimentos")


@compartimentos_bp.route("/compartimentos/editar/<int:compartimento_id>", methods=["POST"])
@login_required
def editar(compartimento_id):

    try:

        CompartimentoService.atualizar(compartimento_id, {
            "armario": int(request.form.get("armario")),
            "numero": request.form.get("numero"),
            "rele": int(request.form["rele"]) if request.form.get("rele") else None,
            "esp32_id": int(request.form["esp32_id"]) if request.form.get("esp32_id") else None,
            "status": request.form.get("status", "livre"),
            "tamanho": request.form.get("tamanho", "M"),
        })

        LogService.registrar(compartimento_id, session.get("usuario"), "Compartimento atualizado")
        flash("Compartimento atualizado com sucesso!", "success")

    except (ValueError, TypeError) as erro:
        flash(str(erro), "warning")
    except Exception:
        flash("Erro ao atualizar compartimento.", "danger")

    return redirect("/compartimentos")


@compartimentos_bp.route("/compartimentos/excluir/<int:compartimento_id>", methods=["POST"])
@login_required
def excluir(compartimento_id):

    try:

        CompartimentoService.excluir(compartimento_id)
        LogService.registrar(compartimento_id, session.get("usuario"), "Compartimento excluído")
        flash("Compartimento excluído com sucesso!", "success")

    except ValueError as erro:
        flash(str(erro), "warning")
    except Exception:
        flash("Erro ao excluir compartimento.", "danger")

    return redirect("/compartimentos")
