import re

from repositories.site_repository import SiteRepository


class SiteService:

    @staticmethod
    def listar():
        return SiteRepository.listar()

    @staticmethod
    def listar_ativos():
        return SiteRepository.listar_ativos()

    @staticmethod
    def buscar_por_id(site_id):

        site = SiteRepository.buscar_por_id(site_id)

        if not site:
            raise ValueError("Site não encontrado.")

        return site

    @staticmethod
    def _normalizar_codigo(codigo):

        codigo = re.sub(r"[^a-z0-9-]", "", codigo.lower().strip())

        if not codigo:
            raise ValueError("Código do site é obrigatório (letras, números e hífen).")

        return codigo

    @staticmethod
    def criar(dados):

        nome = dados.get("nome", "").strip()

        if not nome:
            raise ValueError("Nome do site é obrigatório.")

        codigo = SiteService._normalizar_codigo(dados.get("codigo", nome))

        if SiteRepository.buscar_por_codigo(codigo):
            raise ValueError("Já existe um site com este código.")

        dados["nome"] = nome
        dados["codigo"] = codigo

        return SiteRepository.criar(dados)

    @staticmethod
    def atualizar(site_id, dados):

        SiteService.buscar_por_id(site_id)

        nome = dados.get("nome", "").strip()

        if not nome:
            raise ValueError("Nome do site é obrigatório.")

        codigo = SiteService._normalizar_codigo(dados.get("codigo", nome))

        existente = SiteRepository.buscar_por_codigo(codigo)

        if existente and existente["id"] != site_id:
            raise ValueError("Já existe um site com este código.")

        dados["nome"] = nome
        dados["codigo"] = codigo

        SiteRepository.atualizar(site_id, dados)

    @staticmethod
    def excluir(site_id):

        if site_id == 1:
            raise ValueError("Não é possível excluir o site matriz.")

        SiteService.buscar_por_id(site_id)
        SiteRepository.excluir(site_id)
