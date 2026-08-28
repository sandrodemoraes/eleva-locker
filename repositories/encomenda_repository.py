from repositories.base_repository import BaseRepository


class EncomendaRepository:

    @staticmethod
    def listar(status=None):

        with BaseRepository.get_connection() as conn:

            if status:

                return conn.execute("""
                    SELECT
                        e.*,
                        c.numero AS compartimento_numero,
                        a.nome AS armario_nome
                    FROM encomendas e
                    LEFT JOIN compartimentos c ON c.id = e.compartimento
                    LEFT JOIN armarios a ON a.id = c.armario
                    WHERE e.status = ?
                    ORDER BY e.id DESC
                """, (status,)).fetchall()

            return conn.execute("""
                SELECT
                    e.*,
                    c.numero AS compartimento_numero,
                    a.nome AS armario_nome
                FROM encomendas e
                LEFT JOIN compartimentos c ON c.id = e.compartimento
                LEFT JOIN armarios a ON a.id = c.armario
                ORDER BY e.id DESC
            """).fetchall()

    @staticmethod
    def buscar_por_id(encomenda_id):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT
                    e.*,
                    c.numero AS compartimento_numero,
                    a.nome AS armario_nome
                FROM encomendas e
                LEFT JOIN compartimentos c ON c.id = e.compartimento
                LEFT JOIN armarios a ON a.id = c.armario
                WHERE e.id = ?
            """, (encomenda_id,)).fetchone()

    @staticmethod
    def buscar_por_codigo(codigo):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT
                    e.*,
                    c.numero AS compartimento_numero,
                    a.nome AS armario_nome
                FROM encomendas e
                LEFT JOIN compartimentos c ON c.id = e.compartimento
                LEFT JOIN armarios a ON a.id = c.armario
                WHERE e.codigo = ? AND e.status = 'aguardando_retirada'
            """, (codigo,)).fetchone()

    @staticmethod
    def codigo_existe(codigo):

        with BaseRepository.get_connection() as conn:

            row = conn.execute("""
                SELECT id FROM encomendas
                WHERE codigo = ? AND status = 'aguardando_retirada'
            """, (codigo,)).fetchone()

            return row is not None

    @staticmethod
    def criar(dados):

        with BaseRepository.get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO encomendas (
                    codigo, cliente, telefone, email, compartimento,
                    data_entrada, expira_em, status, operador, transportadora, observacao
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dados["codigo"],
                dados["cliente"],
                dados.get("telefone"),
                dados.get("email"),
                dados["compartimento"],
                dados["data_entrada"],
                dados.get("expira_em"),
                dados.get("status", "aguardando_retirada"),
                dados.get("operador"),
                dados.get("transportadora"),
                dados.get("observacao"),
            ))

            conn.commit()

            return cursor.lastrowid

    @staticmethod
    def atualizar_retirada(encomenda_id, data_retirada, observacao=None):

        with BaseRepository.get_connection() as conn:

            if observacao:
                conn.execute("""
                    UPDATE encomendas
                    SET status = 'retirada', data_retirada = ?,
                        observacao = COALESCE(observacao || ' | ', '') || ?
                    WHERE id = ?
                """, (data_retirada, observacao, encomenda_id))
            else:
                conn.execute("""
                    UPDATE encomendas
                    SET status = 'retirada', data_retirada = ?
                    WHERE id = ?
                """, (data_retirada, encomenda_id))

            conn.commit()

    @staticmethod
    def buscar_por_codigo_any(codigo):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT
                    e.*,
                    c.numero AS compartimento_numero,
                    a.nome AS armario_nome
                FROM encomendas e
                LEFT JOIN compartimentos c ON c.id = e.compartimento
                LEFT JOIN armarios a ON a.id = c.armario
                WHERE e.codigo = ?
                ORDER BY e.id DESC
                LIMIT 1
            """, (codigo,)).fetchone()

    @staticmethod
    def marcar_retidas():

        from datetime import datetime

        agora = datetime.now()
        agora_str = agora.strftime("%Y-%m-%d %H:%M:%S")
        count = 0

        with BaseRepository.get_connection() as conn:

            rows = conn.execute("""
                SELECT id, expira_em FROM encomendas
                WHERE status = 'aguardando_retirada'
                  AND expira_em IS NOT NULL
                  AND expira_em != ''
            """).fetchall()

            for row in rows:
                try:
                    expira = datetime.strptime(str(row["expira_em"])[:19], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue
                if agora <= expira:
                    continue
                conn.execute("""
                    UPDATE encomendas
                    SET status = 'retida', retida_em = ?
                    WHERE id = ?
                """, (agora_str, row["id"]))
                count += 1

            conn.commit()

        return count

    @staticmethod
    def contar_retidas(site_id=None):

        return EncomendaRepository.contar(status="retida", site_id=site_id)

    @staticmethod
    def marcar_lembrete_enviado(encomenda_id):

        from datetime import datetime

        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                UPDATE encomendas
                SET ultimo_lembrete_em = ?, notificado_em = ?
                WHERE id = ?
            """, (agora, agora, encomenda_id))

            conn.commit()

    @staticmethod
    def listar_aguardando_retirada():

        return EncomendaRepository.listar(status="aguardando_retirada")

    @staticmethod
    def marcar_notificado(encomenda_id):

        from datetime import datetime

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                UPDATE encomendas
                SET notificado_em = ?
                WHERE id = ?
            """, (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                encomenda_id,
            ))

            conn.commit()

    @staticmethod
    def contar(status=None, site_id=None):

        with BaseRepository.get_connection() as conn:

            filtro = ""
            params = []

            if status:
                filtro += " AND e.status = ?"
                params.append(status)

            if site_id is not None:
                filtro += " AND a.site_id = ?"
                params.append(site_id)

            if status or site_id is not None:
                return conn.execute(f"""
                    SELECT COUNT(*) AS total
                    FROM encomendas e
                    JOIN compartimentos c ON c.id = e.compartimento
                    JOIN armarios a ON a.id = c.armario
                    WHERE 1=1 {filtro}
                """, tuple(params)).fetchone()["total"]

            return conn.execute("""
                SELECT COUNT(*) AS total FROM encomendas
            """).fetchone()["total"]

    @staticmethod
    def contar_pendentes(site_id=None):

        return EncomendaRepository.contar(
            status="aguardando_retirada",
            site_id=site_id,
        )
