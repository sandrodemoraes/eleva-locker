"""Testa URLs do totem no servidor local (rode com servidor ligado)."""
import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:15000"

URLS = [
    ("/totem/versao", 200),
    ("/totem/2", 200),
    ("/totem/quiosque", (200, 302, 308)),
    ("/totem/quiosque/", (200, 302, 308)),
    ("/totem/quiosque/fully.json", 200),
    ("/totem/matriz", (200, 302, 308)),
]


def _ok(status, esperado):
    if isinstance(esperado, tuple):
        return status in esperado
    return status == esperado


def main():
    print()
    print("=" * 60)
    print("  TESTE TOTEM / QUIOSQUE — servidor local")
    print("=" * 60)
    print(f"  Base: {BASE}")
    print()

    falhas = 0
    quiosque_ok = False

    for path, esperado in URLS:
        url = BASE + path
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                status = resp.status
                body = resp.read(500).decode("utf-8", errors="replace")
        except urllib.error.HTTPError as erro:
            status = erro.code
            body = erro.read(200).decode("utf-8", errors="replace")
        except urllib.error.URLError as erro:
            print(f"  ERRO   {path}")
            print(f"         Servidor nao respondeu: {erro.reason}")
            print()
            print("  >>> Rode INICIAR.bat ou py app.py antes deste teste")
            print("=" * 60)
            return 1

        if _ok(status, esperado):
            print(f"  OK     {path}  (HTTP {status})")
            if path == "/totem/versao" and body:
                try:
                    info = json.loads(body)
                    if info.get("quiosque"):
                        quiosque_ok = True
                        print(f"         versao totem: {info.get('versao')} | quiosque: sim")
                    else:
                        print("         AVISO: /totem/versao sem flag quiosque — codigo antigo")
                except json.JSONDecodeError:
                    pass
        else:
            falhas += 1
            print(f"  FALHA  {path}  (HTTP {status}, esperado {esperado})")
            if status == 404:
                print("         >>> Rode ATUALIZAR.bat e reinicie o servidor")

    print()
    if falhas:
        print(f"  {falhas} URL(s) com problema — atualize o codigo e reinicie INICIAR.bat")
    elif quiosque_ok:
        print("  Tudo OK. No celular use:")
        print("  http://192.168.16.130:15000/totem/2")
        print("  ou http://192.168.16.130:15000/totem/quiosque")
    else:
        print("  Totem responde, mas modo quiosque pode estar desatualizado.")
        print("  Rode ATUALIZAR.bat e reinicie o servidor.")
    print("=" * 60)
    print()
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
