from repositories.base_repository import BaseRepository


class EncomendaRepository:

    @staticmethod
    def listar(status=None, armario_id=None):

        with BaseRepository.get_connection() as conn:

            filtros = []
            params = []

            if status:
                filtros.append("e.status = ?")
                params.append(status)

            if armario_id is not None:
                filtros.append("c.armario = ?")
                params.append(armario_id)

            where = f"WHERE {' AND '.join(filtros)}" if filtros else ""

            return conn.execute(f"""
                SELECT
                    e.*,
                    c.numero AS compartimento_numero,
                    c.tamanho AS compartimento_tamanho,
                    c.armario AS compartimento_armario,
                    a.nome AS armario_nome
                FROM encomendas e
                LEFT JOIN compartimentos c ON c.id = e.compartimento
                LEFT JOIN armarios a ON a.id = c.armario
                {where}
                ORDER BY e.id DESC
            """, tuple(params)).fetchall()

    @staticmethod
    def buscar_por_id(encomenda_id):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT
                    e.*,
                    c.numero AS compartimento_numero,
                    c.tamanho AS compartimento_tamanho,
                    c.armario AS compartimento_armario,
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
                    c.tamanho AS compartimento_tamanho,
                    c.armario AS compartimento_armario,
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
    def tem_pendente_no_compartimento(compartimento_id):

        with BaseRepository.get_connection() as conn:

            row = conn.execute("""
                SELECT id FROM encomendas
                WHERE compartimento = ? AND status = 'aguardando_retirada'
                LIMIT 1
            """, (compartimento_id,)).fetchone()

            return row is not None

    @staticmethod
    def criar(dados):

        with BaseRepository.get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO encomendas (
                    codigo, cliente, telefone, email, compartimento,
                    data_entrada, status, operador, transportadora, observacao
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dados["codigo"],
                dados["cliente"],
                dados.get("telefone"),
                dados.get("email"),
                dados["compartimento"],
                dados["data_entrada"],
                dados.get("status", "aguardando_retirada"),
                dados.get("operador"),
                dados.get("transportadora"),
                dados.get("observacao"),
            ))

            conn.commit()

            return cursor.lastrowid

    @staticmethod
    def criar_deposito_atomico(compartimento_id, dados):
        """Cria encomenda e marca compartimento ocupado na mesma transação."""

        with BaseRepository.get_connection() as conn:

            if conn._engine == "sqlite":
                conn._conn.execute("BEGIN IMMEDIATE")

            try:
                comp = conn.execute("""
                    SELECT
                        c.*,
                        a.nome AS armario_nome
                    FROM compartimentos c
                    JOIN armarios a ON a.id = c.armario
                    WHERE c.id = ?
                """, (compartimento_id,)).fetchone()

                if not comp:
                    raise ValueError("Compartimento não encontrado.")

                pendente = conn.execute("""
                    SELECT id FROM encomendas
                    WHERE compartimento = ? AND status = 'aguardando_retirada'
                    LIMIT 1
                """, (compartimento_id,)).fetchone()

                if pendente or comp["status"] != "livre":
                    raise ValueError(
                        f"Compartimento #{comp['numero']} já está ocupado. "
                        "Escolha outro compartimento livre."
                    )

                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO encomendas (
                        codigo, cliente, telefone, email, compartimento,
                        data_entrada, status, operador, transportadora, observacao, expira_em
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    dados["codigo"],
                    dados["cliente"],
                    dados.get("telefone"),
                    dados.get("email"),
                    compartimento_id,
                    dados["data_entrada"],
                    dados.get("status", "aguardando_retirada"),
                    dados.get("operador"),
                    dados.get("transportadora"),
                    dados.get("observacao"),
                    dados.get("expira_em"),
                ))

                encomenda_id = cursor.lastrowid

                conn.execute("""
                    UPDATE compartimentos SET status = 'ocupado' WHERE id = ?
                """, (compartimento_id,))

                conn.commit()
                return encomenda_id, comp

            except Exception:
                if conn._engine == "sqlite":
                    conn._conn.rollback()
                else:
                    conn._conn.rollback()
                raise

    @staticmethod
    def atualizar_retirada(encomenda_id, data_retirada):

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                UPDATE encomendas
                SET status = 'retirada', data_retirada = ?
                WHERE id = ?
            """, (data_retirada, encomenda_id))

            conn.commit()

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
