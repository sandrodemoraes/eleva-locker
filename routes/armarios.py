from flask import Blueprint, render_template, request, redirect, session, flash

import config
from middleware.auth_required import login_required, perfil_required
from middleware.operador_scope import operador_acessa_armario, redirect_home
from services.armario_service import ArmarioService
from services.empresa_service import EmpresaService
from services.esp32_service import Esp32Service
from services.esp32_portas_service import Esp32PortasService
from services.compartimento_service import CompartimentoService
from services.usuario_service import UsuarioService
from services.log_service import LogService
from repositories.esp32_repository import Esp32Repository

armarios_bp = Blueprint("armarios", __name__)


def _ip_cliente():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "")
    if ip and "," in ip:
        ip = ip.split(",")[0].strip()
    return ip


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

    if not operador_acessa_armario(armario_id):
        flash("Você não tem permissão para acessar este armário.", "warning")
        return redirect(redirect_home())

    armario = ArmarioService.buscar_por_id(armario_id)
    Esp32Repository.marcar_offline_expirados()
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
        lgpd_consentimento_usuario=config.LGPD_CONSENTIMENTO_USUARIO,
        lgpd_politica_versao=config.LGPD_POLITICA_VERSAO,
    )


@armarios_bp.route("/armarios/novo", methods=["POST"])
@login_required
@perfil_required("Administrador")
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
@perfil_required("Administrador")
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
@perfil_required("Administrador")
def excluir(armario_id):

    try:
        vinculados = ArmarioService.excluir(armario_id)
        LogService.registrar(None, session.get("usuario"), f"Armário #{armario_id} excluído")
        msg = "Armário excluído."
        if vinculados:
            msg += (
                f" {vinculados} usuário(s) migrados automaticamente para outro armário "
                "(vínculo preservado)."
            )
        flash(msg, "success")
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
        max_armario = config.normalizar_max_portas(armario["max_portas"] or 16)
        porta_inicial = Esp32PortasService.proxima_porta_inicial_armario(armario_id)
        restantes = max(0, max_armario - porta_inicial + 1)
        max_portas_esp = min(8, restantes) if restantes else 8

        Esp32Service.criar({
            "nome": request.form.get("nome", f"ESP Armário {armario_id}"),
            "ip": request.form.get("ip", ""),
            "mac": request.form.get("mac", ""),
            "armario": armario_id,
            "porta": int(request.form.get("porta", 80)),
            "max_portas": max_portas_esp,
            "porta_inicial": porta_inicial,
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
        ArmarioService.buscar_por_id(armario_id)
        esp = Esp32Repository.buscar_por_id(esp32_id)
        porta_inicial = Esp32PortasService.resolver_porta_inicial(esp32_id)
        max_portas_esp = config.normalizar_max_portas(
            esp["max_portas"] if esp and esp["max_portas"] else 8
        )

        Esp32Service.atualizar(esp32_id, {
            "nome": request.form.get("nome", ""),
            "ip": request.form.get("ip", ""),
            "mac": request.form.get("mac", ""),
            "armario": armario_id,
            "porta": int(request.form.get("porta", 80)),
            "max_portas": max_portas_esp,
            "porta_inicial": porta_inicial,
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
            lgpd_consentimento=request.form.get("lgpd_consentimento") == "1",
            ip=_ip_cliente(),
            user_agent=(request.headers.get("User-Agent") or "")[:500],
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
