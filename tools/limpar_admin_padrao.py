#!/usr/bin/env python3
"""
Remove admin padrão (admin@elevalocker.com / 123456) e garante admin principal.

Opcional: alterar senha do admin principal.

Uso:
  python tools/limpar_admin_padrao.py
  python tools/limpar_admin_padrao.py --alterar-senha
  python tools/limpar_admin_padrao.py --senha "MinhaSenhaForte123" --confirmar "MinhaSenhaForte123"
  python tools/limpar_admin_padrao.py --remover-outros-admins --alterar-senha
"""
import argparse
import getpass
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

from env_bancada import aplicar_bancada_processo
from werkzeug.security import generate_password_hash

aplicar_bancada_processo()

EMAIL_PADRAO_REMOVER = "admin@elevalocker.com"
ADMIN_PRINCIPAL_PADRAO = "sandro.demoraes@gmail.com"
SENHA_MIN = 8


def _resolver_nova_senha(args):
    if args.senha:
        if not args.confirmar:
            print("ERRO: use --confirmar com a mesma senha de --senha.")
            return None
        if args.senha != args.confirmar:
            print("ERRO: senha e confirmação não conferem.")
            return None
        nova = args.senha
    elif args.alterar_senha:
        print(f"\n  Nova senha para {args.admin.strip().lower()} (mínimo {SENHA_MIN} caracteres)")
        nova = getpass.getpass("  Digite a nova senha: ")
        conf = getpass.getpass("  Confirme a nova senha: ")
        if nova != conf:
            print("ERRO: senhas não conferem.")
            return None
    else:
        return None

    if len(nova) < SENHA_MIN:
        print(f"ERRO: senha deve ter pelo menos {SENHA_MIN} caracteres.")
        return None

    return nova


def main():
    parser = argparse.ArgumentParser(description="Remove admin padrão do ELEVA LOCKER")
    parser.add_argument(
        "--admin",
        default=ADMIN_PRINCIPAL_PADRAO,
        help="E-mail que permanece como Administrador",
    )
    parser.add_argument(
        "--remover-outros-admins",
        action="store_true",
        help="Remove outros Administradores além do principal",
    )
    parser.add_argument(
        "--alterar-senha",
        action="store_true",
        help="Pede nova senha no terminal (não aparece na tela)",
    )
    parser.add_argument("--senha", help="Nova senha (use com --confirmar)")
    parser.add_argument("--confirmar", help="Confirmação da nova senha")
    args = parser.parse_args()

    if args.senha and not args.alterar_senha:
        args.alterar_senha = True

    admin_email = args.admin.strip().lower()
    if not admin_email:
        print("ERRO: informe --admin com e-mail válido.")
        return 1

    nova_senha = _resolver_nova_senha(args)
    if args.alterar_senha and nova_senha is None:
        return 1

    from repositories.base_repository import BaseRepository

    with BaseRepository.get_connection() as conn:
        principal = conn.execute(
            "SELECT id, nome, email, perfil, status FROM usuarios WHERE lower(email) = ?",
            (admin_email,),
        ).fetchone()

        if not principal:
            print(f"ERRO: usuário '{admin_email}' não encontrado no banco.")
            print("Cadastre-o em Usuários antes de rodar este script.")
            return 1

        padrao = conn.execute(
            "SELECT id, nome, email FROM usuarios WHERE lower(email) = ?",
            (EMAIL_PADRAO_REMOVER.lower(),),
        ).fetchone()

        if padrao:
            conn.execute("DELETE FROM usuarios WHERE id = ?", (padrao["id"],))
            print(f"  Removido: {padrao['email']} ({padrao['nome']})")
        else:
            print(f"  OK: {EMAIL_PADRAO_REMOVER} já não existe.")

        conn.execute(
            """
            UPDATE usuarios
            SET perfil = 'Administrador', status = 1
            WHERE id = ?
            """,
            (principal["id"],),
        )

        if nova_senha:
            conn.execute(
                "UPDATE usuarios SET senha = ? WHERE id = ?",
                (generate_password_hash(nova_senha), principal["id"]),
            )
            print(f"  Admin principal: {admin_email} (senha ATUALIZADA)")
        else:
            print(f"  Admin principal: {admin_email} (senha NÃO alterada)")

        if args.remover_outros_admins:
            outros = conn.execute(
                """
                SELECT id, nome, email FROM usuarios
                WHERE perfil = 'Administrador'
                  AND lower(email) != ?
                  AND id != ?
                """,
                (admin_email, principal["id"]),
            ).fetchall()
            for u in outros:
                conn.execute("DELETE FROM usuarios WHERE id = ?", (u["id"],))
                print(f"  Removido admin extra: {u['email']} ({u['nome']})")

        conn.commit()

        print("\n  Usuários restantes:")
        rows = conn.execute(
            """
            SELECT id, nome, email, perfil, status
            FROM usuarios ORDER BY id
            """
        ).fetchall()
        for r in rows:
            st = "ativo" if r["status"] == 1 else "inativo"
            print(f"    [{r['id']}] {r['email']} — {r['perfil']} ({st})")

    print(
        """
  Pronto.

  Faça logout e login com:
    """
        + admin_email
        + """
"""
    )
    if nova_senha:
        print("  Use a NOVA senha que você acabou de definir.\n")
    else:
        print(
            """
  O admin padrão admin@elevalocker.com / 123456 não volta se já existir
  outro usuário no banco (após atualizar o código).
"""
        )
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
