from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash,
)

from services.armario_service import ArmarioService

armarios_bp = Blueprint("armarios", __name__)


@armarios_bp.route("/armarios")
def armarios():

    if "usuario" not in session:
        return redirect("/")

    lista = ArmarioService.listar()

    return render_template(
        "armarios.html",
        usuario=session["usuario"],
        perfil=session["perfil"],
        armarios=lista,
    )


@armarios_bp.route("/armarios/novo", methods=["POST"])
def novo_armario():

    if "usuario" not in session:
        return redirect("/")

    try:
        ArmarioService.inserir({
            "nome": request.form.get("nome", ""),
            "endereco": request.form.get("endereco", ""),
            "cidade": request.form.get("cidade", ""),
            "estado": request.form.get("estado", ""),
            "status": request.form.get("status", "Ativo"),
        })
        flash("Armário cadastrado com sucesso!", "success")

    except ValueError as erro:
        flash(str(erro), "warning")

    except Exception:
        flash("Erro interno ao cadastrar armário.", "danger")

    return redirect("/armarios")


@armarios_bp.route("/armarios/editar/<int:armario_id>", methods=["POST"])
def editar_armario(armario_id):

    if "usuario" not in session:
        return redirect("/")

    try:
        ArmarioService.atualizar(armario_id, {
            "nome": request.form.get("nome", ""),
            "endereco": request.form.get("endereco", ""),
            "cidade": request.form.get("cidade", ""),
            "estado": request.form.get("estado", ""),
            "status": request.form.get("status", "Ativo"),
        })
        flash("Armário atualizado com sucesso!", "success")

    except ValueError as erro:
        flash(str(erro), "warning")

    except Exception:
        flash("Erro interno ao atualizar armário.", "danger")

    return redirect("/armarios")


@armarios_bp.route("/armarios/excluir/<int:armario_id>", methods=["POST"])
def excluir_armario(armario_id):

    if "usuario" not in session:
        return redirect("/")

    try:
        ArmarioService.excluir(armario_id)
        flash("Armário excluído com sucesso!", "success")

    except Exception:
        flash("Erro interno ao excluir armário.", "danger")

    return redirect("/armarios")
