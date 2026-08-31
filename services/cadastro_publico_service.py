import re

import config
from repositories.fatura_repository import FaturaRepository
from services.contrato_service import ContratoService
from services.empresa_service import EmpresaService
from services.plano_service import PlanoService
from services.usuario_service import UsuarioService


class CadastroPublicoService:

    @staticmethod
    def url_cadastro(plano_id=None):
        base = config.APP_URL_BASE.rstrip("/")
        if plano_id:
            return f"{base}/cadastro?plano={int(plano_id)}"
        return f"{base}/cadastro"

    @staticmethod
    def _limpar_cnpj(cnpj):
        return re.sub(r"\D", "", (cnpj or "").strip())

    @staticmethod
    def _validar_cnpj(cnpj):
        cnpj = CadastroPublicoService._limpar_cnpj(cnpj)
        if len(cnpj) != 14:
            raise ValueError("Informe um CNPJ válido com 14 dígitos.")
        if cnpj == cnpj[0] * 14:
            raise ValueError("CNPJ inválido.")
        return cnpj

    @staticmethod
    def processar(dados, ip=None, user_agent=None):
        if not config.CADASTRO_PUBLICO_ATIVO:
            raise ValueError("Cadastro público temporariamente indisponível.")

        razao_social = (dados.get("razao_social") or "").strip()
        nome_fantasia = (dados.get("nome_fantasia") or "").strip()
        cnpj = CadastroPublicoService._validar_cnpj(dados.get("cnpj"))
        responsavel = (dados.get("responsavel") or "").strip()
        telefone = (dados.get("telefone") or "").strip()
        email_empresa = (dados.get("email_empresa") or "").strip().lower()

        nome = (dados.get("nome") or responsavel).strip()
        email = (dados.get("email") or email_empresa).strip().lower()
        senha = dados.get("senha") or ""
        confirmar = dados.get("confirmar") or ""
        plano_id = dados.get("plano_id")
        lgpd = dados.get("lgpd_consentimento") in (True, "1", "on", 1)

        if not razao_social:
            raise ValueError("Razão social é obrigatória.")
        if not responsavel:
            raise ValueError("Informe o responsável pelo condomínio/empresa.")
        if not telefone:
            raise ValueError("Telefone de contato é obrigatório.")
        if not email_empresa:
            raise ValueError("E-mail da empresa é obrigatório.")
        if not plano_id:
            raise ValueError("Selecione um plano.")

        plano = PlanoService.buscar_por_id(int(plano_id))
        if not plano or not plano["status"]:
            raise ValueError("Plano indisponível.")

        if EmpresaService.cnpj_existe(cnpj):
            raise ValueError("Já existe cadastro com este CNPJ.")

        empresa_id = EmpresaService.inserir({
            "razao_social": razao_social,
            "nome_fantasia": nome_fantasia or razao_social,
            "cnpj": cnpj,
            "inscricao_estadual": "",
            "responsavel": responsavel,
            "telefone": telefone,
            "whatsapp": telefone,
            "email": email_empresa,
            "cep": "",
            "endereco": "",
            "numero": "",
            "bairro": "",
            "cidade": "",
            "estado": "",
            "status": 1,
        })

        usuario_id = UsuarioService.criar(
            nome=nome,
            email=email,
            telefone=telefone,
            senha=senha,
            confirmar=confirmar,
            perfil="Operador",
            status=1,
            armario_id=None,
            empresa_id=empresa_id,
            lgpd_consentimento=lgpd,
            ip=ip,
            user_agent=user_agent,
        )

        contrato_id = ContratoService.criar({
            "empresa_id": empresa_id,
            "plano_id": int(plano_id),
        })

        faturas = FaturaRepository.listar(contrato_id=contrato_id)
        link_pagamento = faturas[0]["link_pagamento"] if faturas else None

        return {
            "empresa_id": empresa_id,
            "usuario_id": usuario_id,
            "contrato_id": contrato_id,
            "plano_nome": plano["nome"],
            "link_pagamento": link_pagamento,
            "email": email,
        }
