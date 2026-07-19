import sqlite3

DB = "database/elevalocker.db"


class EmpresaService:

    @staticmethod
    def listar():

        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row

        empresas = conn.execute("""
            SELECT *
            FROM empresas
            ORDER BY razao_social
        """).fetchall()

        conn.close()

        return empresas


    @staticmethod
    def inserir(dados):

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO empresas (
                razao_social,
                nome_fantasia,
                cnpj,
                inscricao_estadual,
                responsavel,
                telefone,
                whatsapp,
                email,
                cep,
                endereco,
                numero,
                bairro,
                cidade,
                estado,
                status
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
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
            dados["status"]

        ))

        conn.commit()
        conn.close()


    @staticmethod
    def atualizar(id, dados):

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE empresas
            SET
                razao_social=?,
                nome_fantasia=?,
                cnpj=?,
                inscricao_estadual=?,
                responsavel=?,
                telefone=?,
                whatsapp=?,
                email=?,
                cep=?,
                endereco=?,
                numero=?,
                bairro=?,
                cidade=?,
                estado=?,
                status=?
            WHERE id=?
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
            id

        ))

        conn.commit()
        conn.close()