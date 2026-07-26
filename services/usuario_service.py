from werkzeug.security import generate_password_hash

from repositories.usuario_repository import UsuarioRepository


class UsuarioService:

    @staticmethod
    def listar():
        return UsuarioRepository.listar()

    @staticmethod
    def buscar_por_id(usuario_id):
        """
        Retorna um usuário pelo ID.
        """

        usuario = UsuarioRepository.buscar_por_id(usuario_id)

        if not usuario:
            raise ValueError("Usuário não encontrado.")

        return usuario

    @staticmethod
    def criar(
        nome,
        email,
        telefone,
        senha,
        confirmar,
        perfil,
        status
    ):

        nome = nome.strip()
        email = email.strip().lower()
        telefone = telefone.strip()

        if not nome or not email or not senha:
            raise ValueError("Preencha todos os campos obrigatórios.")

        if senha != confirmar:
            raise ValueError("As senhas não conferem.")

        if UsuarioRepository.buscar_por_email(email):
            raise ValueError("Este e-mail já está cadastrado.")

        senha_hash = generate_password_hash(senha)

        UsuarioRepository.criar(
            nome,
            email,
            telefone,
            senha_hash,
            perfil,
            status
        )

    @staticmethod
    def atualizar(
        usuario_id,
        nome,
        email,
        telefone,
        perfil,
        status
    ):
        """
        Atualiza os dados de um usuário.
        """

        nome = nome.strip()
        email = email.strip().lower()
        telefone = telefone.strip()

        if not nome or not email:
            raise ValueError("Nome e e-mail são obrigatórios.")

        usuario = UsuarioRepository.buscar_por_id(usuario_id)

        if not usuario:
            raise ValueError("Usuário não encontrado.")

        usuario_email = UsuarioRepository.buscar_por_email(email)

        if usuario_email and usuario_email["id"] != usuario_id:
            raise ValueError("Este e-mail já está cadastrado.")

        UsuarioRepository.atualizar(
            usuario_id,
            nome,
            email,
            telefone,
            perfil,
            status
        )

    @staticmethod
    def alterar_senha(
        usuario_id,
        senha,
        confirmar
    ):
        """
        Altera a senha do usuário.
        """

        if not senha:
            raise ValueError("Informe a nova senha.")

        if senha != confirmar:
            raise ValueError("As senhas não conferem.")

        senha_hash = generate_password_hash(senha)

        UsuarioRepository.alterar_senha(
            usuario_id,
            senha_hash
        )

    @staticmethod
    def excluir(usuario_id):
        """
        Exclui um usuário.
        """

        usuario = UsuarioRepository.buscar_por_id(usuario_id)

        if not usuario:
            raise ValueError("Usuário não encontrado.")

        UsuarioRepository.excluir(usuario_id)