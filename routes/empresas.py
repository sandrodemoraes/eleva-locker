from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from flask import jsonify

from services.empresa_service import EmpresaService

empresas_bp = Blueprint("empresas", __name__)


# ==========================
# LISTAR EMPRESAS
# ==========================

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
        return jsonify({
            "sucesso": False,
            "mensagem": "Sessão expirada."
        }), 401

    dados = {

        "razao_social": request.form.get("razao_social", "").strip(),
        "nome_fantasia": request.form.get("nome_fantasia", "").strip(),
        "cnpj": request.form.get("cnpj", "").strip(),
        "inscricao_estadual": request.form.get("inscricao_estadual", "").strip(),
        "responsavel": request.form.get("responsavel", "").strip(),
        "telefone": request.form.get("telefone", "").strip(),
        "whatsapp": request.form.get("whatsapp", "").strip(),
        "email": request.form.get("email", "").strip(),
        "cep": request.form.get("cep", "").strip(),
        "endereco": request.form.get("endereco", "").strip(),
        "numero": request.form.get("numero", "").strip(),
        "bairro": request.form.get("bairro", "").strip(),
        "cidade": request.form.get("cidade", "").strip(),
        "estado": request.form.get("estado", "").strip(),
        "status": request.form.get("status", 1)

    }

    if EmpresaService.cnpj_existe(dados["cnpj"]):

        return jsonify({
            "sucesso": False,
            "mensagem": "Já existe uma empresa cadastrada com este CNPJ."
        })

    EmpresaService.inserir(dados)

    return jsonify({
        "sucesso": True,
        "mensagem": "Empresa cadastrada com sucesso."
    })


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


# ==========================
# EXCLUIR EMPRESA
# ==========================

@empresas_bp.route("/empresas/excluir/<int:id>", methods=["POST"])
def excluir_empresa(id):

    if "usuario" not in session:
        return redirect("/")

    EmpresaService.excluir(id)

    return redirect("/empresas")