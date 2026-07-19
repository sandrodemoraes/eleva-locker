from dataclasses import dataclass


@dataclass
class Usuario:
    id: int = None
    nome: str = ""
    email: str = ""
    senha: str = ""
    perfil: str = "Usuario"
    ativo: bool = True