from datetime import datetime

from repositories.base_repository import BaseRepository
from repositories.contrato_repository import ContratoRepository


class LimitePlanoService:
    """
    Verifica limites do plano contratado por empresa.
    -1 = ilimitado
    """

    @staticmethod
    def obter_contrato(empresa_id):

        if not empresa_id:
            return None

        return ContratoRepository.buscar_ativo_por_empresa(empresa_id)

    @staticmethod
    def _ilimitado(valor):
        return valor is None or int(valor) < 0

    @staticmethod
    def contar_armarios_empresa(empresa_id):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT COUNT(*) AS total FROM armarios
                WHERE empresa_id = ?
            """, (empresa_id,)).fetchone()["total"]

    @staticmethod
    def contar_compartimentos_empresa(empresa_id):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT COUNT(*) AS total
                FROM compartimentos c
                JOIN armarios a ON a.id = c.armario
                WHERE a.empresa_id = ?
            """, (empresa_id,)).fetchone()["total"]

    @staticmethod
    def contar_encomendas_mes_empresa(empresa_id):

        mes = datetime.now().strftime("%Y-%m")

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT COUNT(*) AS total
                FROM encomendas e
                JOIN compartimentos c ON c.id = e.compartimento
                JOIN armarios a ON a.id = c.armario
                WHERE a.empresa_id = ?
                  AND e.data_entrada LIKE ?
            """, (empresa_id, f"{mes}%")).fetchone()["total"]

    @staticmethod
    def obter_uso(empresa_id):

        contrato = LimitePlanoService.obter_contrato(empresa_id)

        uso = {
            "contrato": contrato,
            "armarios": LimitePlanoService.contar_armarios_empresa(empresa_id),
            "compartimentos": LimitePlanoService.contar_compartimentos_empresa(empresa_id),
            "encomendas_mes": LimitePlanoService.contar_encomendas_mes_empresa(empresa_id),
        }

        if contrato:

            uso["limites"] = {
                "armarios": contrato["max_armarios"],
                "compartimentos": contrato["max_compartimentos"],
                "encomendas_mes": contrato["max_encomendas_mes"],
            }
            uso["plano_nome"] = contrato["plano_nome"]

        return uso

    @staticmethod
    def verificar_armario(empresa_id):

        if not empresa_id:
            return

        contrato = LimitePlanoService.obter_contrato(empresa_id)

        if not contrato:
            return

        if LimitePlanoService._ilimitado(contrato["max_armarios"]):
            return

        atual = LimitePlanoService.contar_armarios_empresa(empresa_id)

        if atual >= contrato["max_armarios"]:
            raise ValueError(
                f"Limite de armários atingido ({atual}/{contrato['max_armarios']}). "
                f"Plano: {contrato['plano_nome']}. Faça upgrade do contrato."
            )

    @staticmethod
    def verificar_compartimento(empresa_id):

        if not empresa_id:
            return

        contrato = LimitePlanoService.obter_contrato(empresa_id)

        if not contrato:
            return

        if LimitePlanoService._ilimitado(contrato["max_compartimentos"]):
            return

        atual = LimitePlanoService.contar_compartimentos_empresa(empresa_id)

        if atual >= contrato["max_compartimentos"]:
            raise ValueError(
                f"Limite de compartimentos atingido ({atual}/{contrato['max_compartimentos']}). "
                f"Plano: {contrato['plano_nome']}."
            )

    @staticmethod
    def verificar_encomenda(empresa_id):

        if not empresa_id:
            return

        contrato = LimitePlanoService.obter_contrato(empresa_id)

        if not contrato:
            return

        if contrato["status"] == "suspenso":
            raise ValueError(
                "Contrato suspenso por inadimplência. Regularize o pagamento para continuar."
            )

        if LimitePlanoService._ilimitado(contrato["max_encomendas_mes"]):
            return

        atual = LimitePlanoService.contar_encomendas_mes_empresa(empresa_id)

        if atual >= contrato["max_encomendas_mes"]:
            raise ValueError(
                f"Limite de encomendas/mês atingido ({atual}/{contrato['max_encomendas_mes']}). "
                f"Plano: {contrato['plano_nome']}."
            )

    @staticmethod
    def empresa_id_do_armario(armario_id):

        with BaseRepository.get_connection() as conn:

            row = conn.execute("""
                SELECT empresa_id FROM armarios WHERE id = ?
            """, (armario_id,)).fetchone()

            return row["empresa_id"] if row else None

    @staticmethod
    def empresa_id_do_compartimento(compartimento_id):

        with BaseRepository.get_connection() as conn:

            row = conn.execute("""
                SELECT a.empresa_id
                FROM compartimentos c
                JOIN armarios a ON a.id = c.armario
                WHERE c.id = ?
            """, (compartimento_id,)).fetchone()

            return row["empresa_id"] if row else None
