from datetime import datetime

from repositories.base_repository import BaseRepository


class LgpdConsentimentoRepository:

    @staticmethod
    def criar(dados):
        with BaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO lgpd_consentimentos (
                    titular_tipo, titular_id, telefone, email,
                    finalidade, versao_politica, ip, user_agent, criado_em
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dados["titular_tipo"],
                dados.get("titular_id"),
                dados.get("telefone"),
                dados.get("email"),
                dados["finalidade"],
                dados.get("versao_politica"),
                dados.get("ip"),
                dados.get("user_agent"),
                dados.get("criado_em") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def contar():
        with BaseRepository.get_connection() as conn:
            row = conn.execute("SELECT COUNT(*) AS n FROM lgpd_consentimentos").fetchone()
            return row["n"] if row else 0
