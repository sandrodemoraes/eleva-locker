from repositories.base_repository import BaseRepository


class EmpresaRepository:

    @staticmethod
    def listar():

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT *
                FROM empresas
                ORDER BY razao_social
            """).fetchall()

    @staticmethod
    def listar_ativas():

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT id, razao_social, nome_fantasia
                FROM empresas
                WHERE status = 1
                ORDER BY razao_social
            """).fetchall()

    @staticmethod
    def buscar_por_id(empresa_id):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT *
                FROM empresas
                WHERE id = ?
            """, (empresa_id,)).fetchone()

    @staticmethod
    def buscar_por_cnpj(cnpj):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT id
                FROM empresas
                WHERE cnpj = ?
            """, (cnpj,)).fetchone()

    @staticmethod
    def inserir(dados):

        with BaseRepository.get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO empresas (
                    razao_social, nome_fantasia, cnpj, inscricao_estadual,
                    responsavel, telefone, whatsapp, email, cep, endereco,
                    numero, bairro, cidade, estado, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dados["razao_social"],
                dados["nome_fantasia"],
                dados["cnpj"],
                dados["inscricao_estadual"],
                dados["responsavel"],
                dados["telefone"],
                dados["whatsapp"],
                dados["email"],
                dados["cep"],
                dados["endereco"],
                dados["numero"],
                dados["bairro"],
                dados["cidade"],
                dados["estado"],
                dados["status"],
            ))

            conn.commit()

            return cursor.lastrowid

    @staticmethod
    def atualizar(empresa_id, dados):

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                UPDATE empresas
                SET
                    razao_social = ?,
                    nome_fantasia = ?,
                    cnpj = ?,
                    inscricao_estadual = ?,
                    responsavel = ?,
                    telefone = ?,
                    whatsapp = ?,
                    email = ?,
                    cep = ?,
                    endereco = ?,
                    numero = ?,
                    bairro = ?,
                    cidade = ?,
                    estado = ?,
                    status = ?
                WHERE id = ?
            """, (
                dados["razao_social"],
                dados["nome_fantasia"],
                dados["cnpj"],
                dados["inscricao_estadual"],
                dados["responsavel"],
                dados["telefone"],
                dados["whatsapp"],
                dados["email"],
                dados["cep"],
                dados["endereco"],
                dados["numero"],
                dados["bairro"],
                dados["cidade"],
                dados["estado"],
                dados["status"],
                empresa_id,
            ))

            conn.commit()

    @staticmethod
    def excluir(empresa_id):

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                DELETE FROM empresas
                WHERE id = ?
            """, (empresa_id,))

            conn.commit()
