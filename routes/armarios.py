from flask import Blueprint, render_template, request, redirect, session, flash

import config
from middleware.auth_required import login_required, perfil_required
from services.armario_service import ArmarioService
from services.empresa_service import EmpresaService
from services.esp32_service import Esp32Service
from services.compartimento_service import CompartimentoService
from services.usuario_service import UsuarioService
from services.log_service import LogService
from repositories.esp32_repository import Esp32Repository

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
        portas_opcoes=config.ESP32_PORTAS_OPCOES,
    )


@armarios_bp.route("/armarios/<int:armario_id>")
@login_required
def detalhe(armario_id):

    armario = ArmarioService.buscar_por_id(armario_id)
    esps = Esp32Repository.listar_por_armario(armario_id)
    compartimentos = CompartimentoService.listar(armario_id)
    usuarios = UsuarioService.listar(armario_id)

    return render_template(
        "armarios_detalhe.html",
        usuario=session.get("usuario"),
        perfil=session.get("perfil"),
        armario=armario,
        esps=esps,
        compartimentos=compartimentos,
        usuarios=usuarios,
        empresas=EmpresaService.listar_ativas(),
        portas_opcoes=config.ESP32_PORTAS_OPCOES,
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
            "max_portas": request.form.get("max_portas", 16),
        })
        LogService.registrar(None, session.get("usuario"), "Armário cadastrado")
        flash("Armário cadastrado! Abra-o para adicionar placa ESP e usuários.", "success")
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
        removidos = ArmarioService.atualizar(armario_id, {
            "nome": request.form.get("nome", ""),
            "endereco": request.form.get("endereco", ""),
            "cidade": request.form.get("cidade", ""),
            "estado": request.form.get("estado", ""),
            "status": request.form.get("status", "ativo"),
            "empresa_id": int(empresa_id) if empresa_id else None,
            "max_portas": request.form.get("max_portas", 16),
        })
        LogService.registrar(None, session.get("usuario"), f"Armário #{armario_id} atualizado")
        msg = "Armário atualizado!"
        if removidos:
            msg += f" {removidos} compartimento(s) extra removido(s)."
        flash(msg, "success")
    except ValueError as erro:
        flash(str(erro), "warning")
    except Exception:
        flash("Erro ao atualizar armário.", "danger")

    destino = request.form.get("redirect") or f"/armarios/{armario_id}"
    return redirect(destino)


@armarios_bp.route("/armarios/excluir/<int:armario_id>", methods=["POST"])
@login_required
def excluir(armario_id):

    try:
        ArmarioService.excluir(armario_id)
        LogService.registrar(None, session.get("usuario"), f"Armário #{armario_id} excluído")
        flash("Armário excluído.", "success")
    except ValueError as erro:
        flash(str(erro), "warning")
    except Exception:
        flash("Erro ao excluir armário.", "danger")

    return redirect("/armarios")


@armarios_bp.route("/armarios/<int:armario_id>/esp32/novo", methods=["POST"])
@login_required
@perfil_required("Administrador")
def esp32_novo(armario_id):

    try:
        armario = ArmarioService.buscar_por_id(armario_id)
        Esp32Service.criar({
            "nome": request.form.get("nome", f"ESP Armário {armario_id}"),
            "ip": request.form.get("ip", ""),
            "mac": request.form.get("mac", ""),
            "armario": armario_id,
            "porta": int(request.form.get("porta", 80)),
            "max_portas": armario["max_portas"] or 16,
            "status": "offline",
        })
        flash("Placa ESP adicionada ao armário!", "success")
    except (ValueError, TypeError) as erro:
        flash(str(erro), "warning")
    except Exception:
        flash("Erro ao cadastrar ESP.", "danger")

    return redirect(f"/armarios/{armario_id}")


@armarios_bp.route("/armarios/<int:armario_id>/esp32/editar/<int:esp32_id>", methods=["POST"])
@login_required
@perfil_required("Administrador")
def esp32_editar(armario_id, esp32_id):

    try:
        armario = ArmarioService.buscar_por_id(armario_id)
        Esp32Service.atualizar(esp32_id, {
            "nome": request.form.get("nome", ""),
            "ip": request.form.get("ip", ""),
            "mac": request.form.get("mac", ""),
            "armario": armario_id,
            "porta": int(request.form.get("porta", 80)),
            "max_portas": armario["max_portas"] or 16,
            "status": request.form.get("status", "offline"),
            "token": request.form.get("token", ""),
        })
        flash("ESP atualizado!", "success")
    except (ValueError, TypeError) as erro:
        flash(str(erro), "warning")
    except Exception:
        flash("Erro ao atualizar ESP.", "danger")

    return redirect(f"/armarios/{armario_id}")


@armarios_bp.route("/armarios/<int:armario_id>/esp32/excluir/<int:esp32_id>", methods=["POST"])
@login_required
@perfil_required("Administrador")
def esp32_excluir(armario_id, esp32_id):

    try:
        Esp32Service.excluir(esp32_id)
        flash("ESP removido.", "success")
    except ValueError as erro:
        flash(str(erro), "warning")
    except Exception:
        flash("Erro ao excluir ESP.", "danger")

    return redirect(f"/armarios/{armario_id}")


@armarios_bp.route("/armarios/<int:armario_id>/usuarios/novo", methods=["POST"])
@login_required
@perfil_required("Administrador")
def usuario_novo(armario_id):

    try:
        ArmarioService.buscar_por_id(armario_id)
        usuario_id = UsuarioService.criar(
            nome=request.form.get("nome", ""),
            email=request.form.get("email", ""),
            telefone=request.form.get("telefone", ""),
            senha=request.form.get("senha", ""),
            confirmar=request.form.get("confirmar", ""),
            perfil=request.form.get("perfil", "Operador"),
            status=int(request.form.get("status", 1)),
            armario_id=armario_id,
        )
        LogService.registrar(None, session.get("usuario"), f"Usuário #{usuario_id} cadastrado no armário #{armario_id}")
        flash("Usuário cadastrado neste armário!", "success")
    except ValueError as erro:
        flash(str(erro), "warning")
    except Exception as erro:
        import traceback
        traceback.print_exc()
        flash(f"Erro ao cadastrar usuário: {erro}", "danger")

    return redirect(f"/armarios/{armario_id}")


@armarios_bp.route("/armarios/<int:armario_id>/usuarios/excluir/<int:usuario_id>", methods=["POST"])
@login_required
@perfil_required("Administrador")
def usuario_excluir(armario_id, usuario_id):

    try:
        UsuarioService.excluir(usuario_id)
        flash("Usuário excluído.", "success")
    except ValueError as erro:
        flash(str(erro), "warning")
    except Exception:
        flash("Erro ao excluir usuário.", "danger")

    return redirect(f"/armarios/{armario_id}")
