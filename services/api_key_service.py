import secrets

from repositories.api_key_repository import ApiKeyRepository
from services.site_service import SiteService


class ApiKeyService:

    @staticmethod
    def listar(site_id=None):
        return ApiKeyRepository.listar(site_id)

    @staticmethod
    def gerar_chave():
        return f"elk_{secrets.token_urlsafe(24)}"

    @staticmethod
    def criar(nome, site_id=None, permissoes="read"):

        nome = nome.strip()

        if not nome:
            raise ValueError("Nome da chave é obrigatório.")

        if site_id:
            SiteService.buscar_por_id(int(site_id))

        if permissoes not in ("read", "write", "admin"):
            raise ValueError("Permissão inválida.")

        chave = ApiKeyService.gerar_chave()

        return ApiKeyRepository.criar({
            "nome": nome,
            "site_id": int(site_id) if site_id else None,
            "chave": chave,
            "permissoes": permissoes,
            "ativo": 1,
        }), chave

    @staticmethod
    def alternar_ativo(key_id, ativo):
        ApiKeyRepository.alternar_ativo(key_id, 1 if ativo else 0)

    @staticmethod
    def excluir(key_id):
        ApiKeyRepository.excluir(key_id)
