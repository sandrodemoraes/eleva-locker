from flask import Blueprint, render_template, request, redirect, session, flash, jsonify

from middleware.auth_required import login_required
from services.armario_service import ArmarioService
from services.empresa_service import EmpresaService
from services.log_service import LogService

armarios_bp = Blueprint("armarios", __name__)


@armarios_bp.route("/armarios")
@login_required
def listar():

    return render_template(
        "armarios.html",
        usuario=session.get("usuario"),
        perfil=session.get("perfil"),
        armarios=ArmarioService.listar(),
        empresas=EmpresaService.listar_ativas(),
    )


@armarios_bp.route("/armarios/novo", methods=["POST"])
@login_required
def novo():

    try:

        empresa_id = request.form.get("empresa_id")

        ArmarioService.criar({
            "nome": request.form.get("nome", ""),
            "endereco": request.form.get("endereco", ""),
            "cidade": request.form.get("cidade", ""),
            "estado": request.form.get("estado", ""),
            "status": request.form.get("status", "ativo"),
            "empresa_id": int(empresa_id) if empresa_id else None,
        })

        LogService.registrar(None, session.get("usuario"), "Armário cadastrado")
        flash("Armário cadastrado com sucesso!", "success")

    except ValueError as erro:
        flash(str(erro), "warning")
    except Exception:
        flash("Erro ao cadastrar armário.", "danger")

    return redirect("/armarios")


@armarios_bp.route("/armarios/editar/<int:armario_id>", methods=["POST"])
@login_required
def editar(armario_id):

    try:

        empresa_id = request.form.get("empresa_id")

        ArmarioService.atualizar(armario_id, {
            "nome": request.form.get("nome", ""),
            "endereco": request.form.get("endereco", ""),
            "cidade": request.form.get("cidade", ""),
            "estado": request.form.get("estado", ""),
            "status": request.form.get("status", "ativo"),
            "empresa_id": int(empresa_id) if empresa_id else None,
        })

        LogService.registrar(None, session.get("usuario"), f"Armário #{armario_id} atualizado")
        flash("Armário atualizado com sucesso!", "success")

    except ValueError as erro:
        flash(str(erro), "warning")
    except Exception:
        flash("Erro ao atualizar armário.", "danger")

    return redirect("/armarios")


@armarios_bp.route("/armarios/excluir/<int:armario_id>", methods=["POST"])
@login_required
def excluir(armario_id):

    try:

        ArmarioService.excluir(armario_id)
        LogService.registrar(None, session.get("usuario"), f"Armário #{armario_id} excluído")
        flash("Armário excluído com sucesso!", "success")

    except ValueError as erro:
        flash(str(erro), "warning")
    except Exception:
        flash("Erro ao excluir armário.", "danger")

    return redirect("/armarios")
