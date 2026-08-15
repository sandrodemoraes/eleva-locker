import config
from repositories.armario_repository import ArmarioRepository
from repositories.esp32_repository import Esp32Repository
from services.limite_plano_service import LimitePlanoService
from middleware.site_scope import get_site_id
from middleware.operador_scope import get_armario_restrito


class ArmarioService:

    @staticmethod
    def _filtrar_operador(armarios):
        restrito = get_armario_restrito()
        if restrito is None:
            return armarios
        return [a for a in armarios if a["id"] == restrito]

    @staticmethod
    def listar():
        armarios = ArmarioRepository.listar(site_id=get_site_id())
        return ArmarioService._filtrar_operador(armarios)

    @staticmethod
    def listar_ativos():
        armarios = ArmarioRepository.listar_ativos()
        restrito = get_armario_restrito()
        if restrito is None:
            return armarios
        return [a for a in armarios if a["id"] == restrito]

    @staticmethod
    def buscar_por_id(armario_id):

        armario = ArmarioRepository.buscar_por_id(armario_id)

        if not armario:
            raise ValueError("Armário não encontrado.")

        return armario

    @staticmethod
    def criar(dados):

        nome = dados.get("nome", "").strip()

        if not nome:
            raise ValueError("Nome do armário é obrigatório.")

        dados["nome"] = nome
        dados["status"] = dados.get("status", "ativo")
        dados["max_portas"] = config.normalizar_max_portas(dados.get("max_portas") or 16)

        empresa_id = dados.get("empresa_id")

        if empresa_id:
            LimitePlanoService.verificar_armario(int(empresa_id))

        if not dados.get("site_id"):
            dados["site_id"] = get_site_id() or 1

        return ArmarioRepository.criar(dados)

    @staticmethod
    def atualizar(armario_id, dados):

        armario = ArmarioService.buscar_por_id(armario_id)

        nome = dados.get("nome", "").strip()

        if not nome:
            raise ValueError("Nome do armário é obrigatório.")

        dados["nome"] = nome

        if dados.get("site_id") is None:
            dados["site_id"] = armario["site_id"] if armario["site_id"] is not None else (get_site_id() or 1)

        if "max_portas" in dados:
            dados["max_portas"] = config.normalizar_max_portas(dados.get("max_portas") or armario["max_portas"] or 16)

        ArmarioRepository.atualizar(armario_id, dados)

        if "max_portas" in dados:
            removidos = ArmarioService._sincronizar_portas_armario(armario_id, dados["max_portas"])
            dados["_sync_removidos"] = removidos

        return dados.get("_sync_removidos", 0)

    @staticmethod
    def _sincronizar_portas_armario(armario_id, max_portas):
        from services.esp32_portas_service import Esp32PortasService

        total_removidos = 0
        esps = Esp32Repository.listar_por_armario(armario_id)
        for esp in esps:
            Esp32Repository.atualizar(esp["id"], {
                "nome": esp["nome"],
                "ip": esp["ip"],
                "mac": esp["mac"] or "",
                "armario": armario_id,
                "status": esp["status"],
                "token": esp["token"],
                "porta": esp["porta"] or 80,
                "max_portas": max_portas,
            })
            resultado = Esp32PortasService.sincronizar_compartimentos(esp["id"], max_portas)
            total_removidos += resultado.get("removidos", 0)

        return total_removidos

    NOME_ARMARIO_MIGRACAO = "ELEVA Locker Matriz"

    @staticmethod
    def _resolver_destino_migracao(conn, armario_id, migrar_usuarios_para=None):
        """Define para onde mover usuários ao excluir armário (nunca NULL silencioso)."""
        if migrar_usuarios_para is not None:
            return migrar_usuarios_para

        vinculados = conn.execute(
            "SELECT COUNT(*) AS n FROM usuarios WHERE armario_id = ?",
            (armario_id,),
        ).fetchone()["n"]
        if vinculados == 0:
            return None

        row = conn.execute(
            """
            SELECT id FROM armarios
            WHERE nome = ? AND id != ?
            LIMIT 1
            """,
            (ArmarioService.NOME_ARMARIO_MIGRACAO, armario_id),
        ).fetchone()
        if row:
            return row["id"]

        row = conn.execute(
            "SELECT id FROM armarios WHERE id != ? ORDER BY id LIMIT 1",
            (armario_id,),
        ).fetchone()
        return row["id"] if row else None

    @staticmethod
    def excluir(armario_id, migrar_usuarios_para=None, desvincular_usuarios=False):

        ArmarioService.buscar_por_id(armario_id)

        from repositories.base_repository import BaseRepository

        with BaseRepository.get_connection() as conn:
            pendentes = conn.execute("""
                SELECT COUNT(*) AS n FROM encomendas e
                JOIN compartimentos c ON c.id = e.compartimento
                WHERE c.armario = ? AND e.status != 'retirada'
            """, (armario_id,)).fetchone()["n"]

            if pendentes:
                raise ValueError(
                    f"Armário tem {pendentes} encomenda(s) ativa(s). "
                    "Retire ou cancele antes de excluir."
                )

            vinculados = conn.execute("""
                SELECT COUNT(*) AS n FROM usuarios WHERE armario_id = ?
            """, (armario_id,)).fetchone()["n"]

            destino = ArmarioService._resolver_destino_migracao(
                conn, armario_id, migrar_usuarios_para
            )

            if vinculados and destino is None and not desvincular_usuarios:
                raise ValueError(
                    f"Armário tem {vinculados} usuário(s) vinculado(s) e não há "
                    "outro armário para migrar. Cadastre outro armário ou remova "
                    "os vínculos manualmente antes de excluir."
                )

            if destino is not None:
                ArmarioService.buscar_por_id(destino)
                conn.execute(
                    "UPDATE usuarios SET armario_id = ? WHERE armario_id = ?",
                    (destino, armario_id),
                )
            elif vinculados and desvincular_usuarios:
                conn.execute(
                    "UPDATE usuarios SET armario_id = NULL WHERE armario_id = ?",
                    (armario_id,),
                )
            conn.execute(
                "DELETE FROM compartimentos WHERE armario = ?",
                (armario_id,),
            )
            conn.execute(
                "DELETE FROM esp32 WHERE armario = ?",
                (armario_id,),
            )
            conn.execute(
                "DELETE FROM armarios WHERE id = ?",
                (armario_id,),
            )
            conn.commit()

        return vinculados

    @staticmethod
    def contar():
        return ArmarioRepository.contar()
