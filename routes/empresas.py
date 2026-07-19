from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import session

from services.empresa_service import EmpresaService

empresas_bp = Blueprint("empresas", __name__)


@empresas_bp.route("/empresas")
def empresas():

    if "usuario" not in session:
        return redirect("/")

    lista = EmpresaService.listar()

    return render_template(
        "empresas.html",
        usuario=session["usuario"],
        perfil=session["perfil"],
        empresas=lista
    )


# ==========================
# NOVA EMPRESA
# ==========================

@empresas_bp.route("/empresas/nova", methods=["POST"])
def nova_empresa():

    if "usuario" not in session:
        return redirect("/")

    dados = {

        "razao_social": request.form.get("razao_social", ""),
        "nome_fantasia": request.form.get("nome_fantasia", ""),
        "cnpj": request.form.get("cnpj", ""),
        "inscricao_estadual": request.form.get("inscricao_estadual", ""),
        "responsavel": request.form.get("responsavel", ""),
        "telefone": request.form.get("telefone", ""),
        "whatsapp": request.form.get("whatsapp", ""),
        "email": request.form.get("email", ""),
        "cep": request.form.get("cep", ""),
        "endereco": request.form.get("endereco", ""),
        "numero": request.form.get("numero", ""),
        "bairro": request.form.get("bairro", ""),
        "cidade": request.form.get("cidade", ""),
        "estado": request.form.get("estado", ""),
        "status": request.form.get("status", 1)

    }

    EmpresaService.inserir(dados)

    return redirect("/empresas")


# ==========================
# EDITAR EMPRESA
# ==========================

@empresas_bp.route("/empresas/editar/<int:id>", methods=["POST"])
def editar_empresa(id):

    if "usuario" not in session:
        return redirect("/")

    dados = {

        "razao_social": request.form.get("razao_social", ""),
        "nome_fantasia": request.form.get("nome_fantasia", ""),
        "cnpj": request.form.get("cnpj", ""),
        "inscricao_estadual": request.form.get("inscricao_estadual", ""),
        "responsavel": request.form.get("responsavel", ""),
        "telefone": request.form.get("telefone", ""),
        "whatsapp": request.form.get("whatsapp", ""),
        "email": request.form.get("email", ""),
        "cep": request.form.get("cep", ""),
        "endereco": request.form.get("endereco", ""),
        "numero": request.form.get("numero", ""),
        "bairro": request.form.get("bairro", ""),
        "cidade": request.form.get("cidade", ""),
        "estado": request.form.get("estado", ""),
        "status": request.form.get("status", 1)

    }

    EmpresaService.atualizar(id, dados)

    return redirect("/empresas")