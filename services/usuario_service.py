from werkzeug.security import generate_password_hash

from repositories.usuario_repository import UsuarioRepository


class UsuarioService:

    @staticmethod
    def listar(armario_id=None):
        return UsuarioRepository.listar(armario_id)

    @staticmethod
    def buscar_por_id(usuario_id):

        usuario = UsuarioRepository.buscar_por_id(usuario_id)

        if not usuario:
            raise ValueError("Usuário não encontrado.")

        return usuario

    @staticmethod
    def criar(nome, email, telefone, senha, confirmar, perfil, status, armario_id=None):

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

        return UsuarioRepository.criar(
            nome, email, telefone, senha_hash, perfil, status, armario_id
        )

    @staticmethod
    def atualizar(usuario_id, nome, email, telefone, perfil, status, armario_id=None):

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
            usuario_id, nome, email, telefone, perfil, status, armario_id
        )

    @staticmethod
    def alterar_senha(usuario_id, senha, confirmar):

        if not senha:
            raise ValueError("Informe a nova senha.")

        if senha != confirmar:
            raise ValueError("As senhas não conferem.")

        UsuarioRepository.alterar_senha(usuario_id, generate_password_hash(senha))

    @staticmethod
    def excluir(usuario_id):

        if not UsuarioRepository.buscar_por_id(usuario_id):
            raise ValueError("Usuário não encontrado.")

        UsuarioRepository.excluir(usuario_id)
