from repositories.armario_repository import ArmarioRepository
from services.limite_plano_service import LimitePlanoService
from middleware.site_scope import get_site_id


class ArmarioService:

    @staticmethod
    def _rotulo(row):
        nome = (row["nome"] or "").strip() if row else ""
        if nome:
            return nome
        return f"Armário #{row['id']}"

    @staticmethod
    def _para_totem(row):
        if not row:
            return None
        keys = row.keys() if hasattr(row, "keys") else row
        max_portas = row["max_portas"] if "max_portas" in keys else None
        return {
            "id": row["id"],
            "nome": ArmarioService._rotulo(row),
            "status": row["status"] if "status" in keys else None,
            "max_portas": max_portas,
        }

    @staticmethod
    def listar_para_totem():
        return [
            ArmarioService._para_totem(row)
            for row in ArmarioRepository.listar_para_totem()
        ]

    @staticmethod
    def listar():
        return ArmarioRepository.listar(site_id=get_site_id())

    @staticmethod
    def listar_ativos():
        rows = ArmarioRepository.listar_ativos()
        if not rows:
            rows = ArmarioRepository.listar_para_totem()
        return [ArmarioService._para_totem(row) for row in rows]

    @staticmethod
    def buscar_por_id(armario_id):

        armario = ArmarioRepository.buscar_por_id(armario_id)

        if not armario:
            raise ValueError("Armário não encontrado.")

        return armario

    @staticmethod
    def buscar_para_totem(armario_id):
        row = ArmarioRepository.buscar_por_id(armario_id)
        if not row:
            raise ValueError("Armário não encontrado.")
        return ArmarioService._para_totem(row)

    @staticmethod
    def criar(dados):

        nome = dados.get("nome", "").strip()

        if not nome:
            raise ValueError("Nome do armário é obrigatório.")

        dados["nome"] = nome
        dados["status"] = dados.get("status", "ativo")

        empresa_id = dados.get("empresa_id")

        if empresa_id:
            LimitePlanoService.verificar_armario(int(empresa_id))

        if not dados.get("site_id"):
            dados["site_id"] = get_site_id() or 1

        return ArmarioRepository.criar(dados)

    @staticmethod
    def atualizar(armario_id, dados):

        ArmarioService.buscar_por_id(armario_id)

        nome = dados.get("nome", "").strip()

        if not nome:
            raise ValueError("Nome do armário é obrigatório.")

        dados["nome"] = nome

        ArmarioRepository.atualizar(armario_id, dados)

    @staticmethod
    def excluir(armario_id):

        ArmarioService.buscar_por_id(armario_id)

        ArmarioRepository.excluir(armario_id)

    @staticmethod
    def contar():
        return ArmarioRepository.contar()
