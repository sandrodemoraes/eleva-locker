import csv
import io
import json
from datetime import datetime

import config
from repositories.base_repository import BaseRepository
from repositories.encomenda_repository import EncomendaRepository
from repositories.lgpd_solicitacao_repository import LgpdSolicitacaoRepository
from repositories.lgpd_titular_repository import LgpdTitularRepository, ANONIMIZADO
from repositories.usuario_repository import UsuarioRepository
from services.log_service import LogService


class LgpdTitularService:

    TIPOS_VALIDOS = ("usuario", "encomenda")

    @staticmethod
    def ativo():
        return config.LGPD_TITULAR_ATIVO

    @staticmethod
    def _row_dict(row):
        if row is None:
            return None
        return dict(row)

    @staticmethod
    def _validar_tipo(titular_tipo):
        if titular_tipo not in LgpdTitularService.TIPOS_VALIDOS:
            raise ValueError("Tipo de titular inválido. Use usuario ou encomenda.")

    @staticmethod
    def coletar_dados(titular_tipo, titular_id):
        LgpdTitularService._validar_tipo(titular_tipo)

        if titular_tipo == "usuario":
            usuario = UsuarioRepository.buscar_por_id(titular_id)
            if not usuario:
                raise ValueError("Usuário não encontrado.")
            u = LgpdTitularService._row_dict(usuario)
            u.pop("senha", None)
            encomendas = LgpdTitularRepository.listar_encomendas_por_contato(
                usuario["telefone"], usuario["email"],
            )
            consentimentos = LgpdTitularRepository.listar_consentimentos(
                "usuario", titular_id, usuario["telefone"], usuario["email"],
            )
            enc_ids = [e["id"] for e in encomendas]
            notificacoes = LgpdTitularRepository.listar_notificacoes_por_encomendas(enc_ids)
            solicitacoes = LgpdSolicitacaoRepository.listar_por_titular("usuario", titular_id)
            return {
                "titular_tipo": "usuario",
                "titular_id": titular_id,
                "exportado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "politica_versao": config.LGPD_POLITICA_VERSAO,
                "usuario": u,
                "encomendas": [dict(e) for e in encomendas],
                "consentimentos": [dict(c) for c in consentimentos],
                "notificacoes": [dict(n) for n in notificacoes],
                "solicitacoes": [dict(s) for s in solicitacoes],
            }

        encomenda = EncomendaRepository.buscar_por_id(titular_id)
        if not encomenda:
            raise ValueError("Encomenda não encontrada.")
        enc = LgpdTitularService._row_dict(encomenda)
        notificacoes = LgpdTitularRepository.listar_notificacoes_por_encomendas([titular_id])
        consentimentos = LgpdTitularRepository.listar_consentimentos(
            "encomenda", titular_id, enc.get("telefone"), enc.get("email"),
        )
        solicitacoes = LgpdSolicitacaoRepository.listar_por_titular("encomenda", titular_id)
        return {
            "titular_tipo": "encomenda",
            "titular_id": titular_id,
            "exportado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "politica_versao": config.LGPD_POLITICA_VERSAO,
            "encomenda": enc,
            "consentimentos": [dict(c) for c in consentimentos],
            "notificacoes": [dict(n) for n in notificacoes],
            "solicitacoes": [dict(s) for s in solicitacoes],
        }

    @staticmethod
    def exportar_json(titular_tipo, titular_id):
        dados = LgpdTitularService.coletar_dados(titular_tipo, titular_id)
        return json.dumps(dados, ensure_ascii=False, indent=2, default=str)

    @staticmethod
    def exportar_csv(titular_tipo, titular_id):
        dados = LgpdTitularService.coletar_dados(titular_tipo, titular_id)
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["secao", "campo", "valor"])

        def _escrever(secao, registro):
            if not registro:
                return
            for chave, valor in registro.items():
                writer.writerow([secao, chave, valor])

        if dados.get("usuario"):
            _escrever("usuario", dados["usuario"])
        if dados.get("encomenda"):
            _escrever("encomenda", dados["encomenda"])
        for enc in dados.get("encomendas", []):
            _escrever("encomenda", enc)
        for item in dados.get("consentimentos", []):
            _escrever("consentimento", item)
        for item in dados.get("notificacoes", []):
            _escrever("notificacao", item)
        for item in dados.get("solicitacoes", []):
            _escrever("solicitacao", item)

        return buf.getvalue()

    @staticmethod
    def _registrar(acao, titular_tipo, titular_id, operador, detalhe=None):
        LgpdSolicitacaoRepository.criar(
            tipo=acao,
            titular_tipo=titular_tipo,
            titular_id=titular_id,
            operador=operador,
            detalhe=detalhe,
        )
        LogService.registrar(
            None,
            operador,
            f"LGPD {acao}: {titular_tipo} #{titular_id}" + (f" — {detalhe}" if detalhe else ""),
        )

    @staticmethod
    def registrar_acesso(titular_tipo, titular_id, operador, formato):
        LgpdTitularService._registrar(
            "acesso", titular_tipo, titular_id, operador,
            detalhe=f"export_{formato}",
        )

    @staticmethod
    def anonimizar(titular_tipo, titular_id, operador):
        LgpdTitularService._validar_tipo(titular_tipo)

        if titular_tipo == "usuario":
            usuario = UsuarioRepository.buscar_por_id(titular_id)
            if not usuario:
                raise ValueError("Usuário não encontrado.")
            usuario = LgpdTitularService._row_dict(usuario)
            if usuario.get("lgpd_anonimizado_em"):
                raise ValueError("Usuário já anonimizado.")
            if usuario.get("perfil") == "Administrador":
                raise ValueError("Não é permitido anonimizar administrador.")

            tel = usuario.get("telefone")
            em = usuario.get("email")
            enc_ids = LgpdTitularRepository.anonimizar_encomendas_por_contato(tel, em)
            LgpdTitularRepository.anonimizar_usuario(titular_id)
            detalhe = f"encomendas_anonimizadas={len(enc_ids)}"
            LgpdTitularService._registrar("exclusao", titular_tipo, titular_id, operador, detalhe)
            return {
                "titular_tipo": titular_tipo,
                "titular_id": titular_id,
                "anonimizado": True,
                "encomendas_anonimizadas": enc_ids,
            }

        encomenda = EncomendaRepository.buscar_por_id(titular_id)
        if not encomenda:
            raise ValueError("Encomenda não encontrada.")
        encomenda = LgpdTitularService._row_dict(encomenda)
        if encomenda.get("lgpd_anonimizado_em"):
            raise ValueError("Encomenda já anonimizada.")
        if encomenda.get("status") == "aguardando_retirada":
            raise ValueError(
                "Encomenda aguardando retirada — conclua ou retira antes de anonimizar."
            )

        LgpdTitularRepository.anonimizar_encomenda(titular_id)
        LgpdTitularService._registrar("exclusao", titular_tipo, titular_id, operador)
        return {
            "titular_tipo": titular_tipo,
            "titular_id": titular_id,
            "anonimizado": True,
            "encomendas_anonimizadas": [titular_id],
        }

    @staticmethod
    def definir_oposicao_marketing(usuario_id, operador, opt_out=True):
        usuario = UsuarioRepository.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado.")
        with BaseRepository.get_connection() as conn:
            conn.execute(
                "UPDATE usuarios SET marketing_opt_out = ? WHERE id = ?",
                (1 if opt_out else 0, usuario_id),
            )
            conn.commit()
        acao = "oposicao" if opt_out else "oposicao_revogada"
        LgpdTitularService._registrar(acao, "usuario", usuario_id, operador)
