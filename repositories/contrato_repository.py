from repositories.base_repository import BaseRepository


class ContratoRepository:

    @staticmethod
    def listar(empresa_id=None):

        with BaseRepository.get_connection() as conn:

            if empresa_id:

                return conn.execute("""
                    SELECT
                        c.*,
                        e.razao_social AS empresa_nome,
                        p.nome AS plano_nome,
                        p.max_armarios, p.max_compartimentos, p.max_encomendas_mes
                    FROM contratos c
                    JOIN empresas e ON e.id = c.empresa_id
                    JOIN planos p ON p.id = c.plano_id
                    WHERE c.empresa_id = ?
                    ORDER BY c.id DESC
                """, (empresa_id,)).fetchall()

            return conn.execute("""
                SELECT
                    c.*,
                    e.razao_social AS empresa_nome,
                    p.nome AS plano_nome,
                    p.max_armarios, p.max_compartimentos, p.max_encomendas_mes
                FROM contratos c
                JOIN empresas e ON e.id = c.empresa_id
                JOIN planos p ON p.id = c.plano_id
                ORDER BY c.id DESC
            """).fetchall()

    @staticmethod
    def buscar_por_id(contrato_id):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT
                    c.*,
                    e.razao_social AS empresa_nome,
                    p.nome AS plano_nome,
                    p.max_armarios, p.max_compartimentos, p.max_encomendas_mes
                FROM contratos c
                JOIN empresas e ON e.id = c.empresa_id
                JOIN planos p ON p.id = c.plano_id
                WHERE c.id = ?
            """, (contrato_id,)).fetchone()

    @staticmethod
    def buscar_ativo_por_empresa(empresa_id):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT
                    c.*,
                    p.nome AS plano_nome,
                    p.max_armarios, p.max_compartimentos, p.max_encomendas_mes,
                    p.inclui_whatsapp, p.inclui_relatorios
                FROM contratos c
                JOIN planos p ON p.id = c.plano_id
                WHERE c.empresa_id = ? AND c.status = 'ativo'
                ORDER BY c.id DESC
                LIMIT 1
            """, (empresa_id,)).fetchone()

    @staticmethod
    def criar(dados):

        with BaseRepository.get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO contratos (
                    empresa_id, plano_id, data_inicio, data_fim,
                    status, valor_mensal, renovacao_automatica
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                dados["empresa_id"], dados["plano_id"], dados["data_inicio"],
                dados.get("data_fim"), dados.get("status", "ativo"),
                dados["valor_mensal"], dados.get("renovacao_automatica", 1),
            ))

            conn.commit()

            return cursor.lastrowid

    @staticmethod
    def atualizar(contrato_id, dados):

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                UPDATE contratos SET
                    empresa_id=?, plano_id=?, data_inicio=?, data_fim=?,
                    status=?, valor_mensal=?, renovacao_automatica=?
                WHERE id=?
            """, (
                dados["empresa_id"], dados["plano_id"], dados["data_inicio"],
                dados.get("data_fim"), dados["status"], dados["valor_mensal"],
                dados.get("renovacao_automatica", 1), contrato_id,
            ))

            conn.commit()

    @staticmethod
    def atualizar_status(contrato_id, status):

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                UPDATE contratos SET status = ? WHERE id = ?
            """, (status, contrato_id))

            conn.commit()

    @staticmethod
    def listar_ativos():

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT c.*, e.razao_social AS empresa_nome
                FROM contratos c
                JOIN empresas e ON e.id = c.empresa_id
                WHERE c.status = 'ativo'
            """).fetchall()

    @staticmethod
    def contar_ativos():

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT COUNT(*) AS total FROM contratos WHERE status = 'ativo'
            """).fetchone()["total"]
