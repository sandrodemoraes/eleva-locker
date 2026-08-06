#!/usr/bin/env python3
"""Descobre se porta 15000 serve totem NOVO ou ANTIGO."""

import json
import subprocess
import urllib.error
import urllib.request


def quem_na_porta():
    try:
        r = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True, text=True, check=False,
        )
        for linha in r.stdout.splitlines():
            if ":15000" in linha and "LISTENING" in linha.upper():
                return linha.strip()
    except Exception:
        pass
    return "(nenhum)"


def get(url):
    req = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.read().decode("utf-8", errors="replace"), resp.headers


print("=" * 55)
print("  QUAL SERVIDOR NA PORTA 15000?")
print("=" * 55)
print(f"Processo: {quem_na_porta()}")
print()

try:
    body, headers = get("http://127.0.0.1:15000/totem/versao")
    print("/totem/versao:")
    print(f"  Header X-Eleva-Totem: {headers.get('X-Eleva-Totem', '(nao tem)')}")
    try:
        dados = json.loads(body)
        print(f"  JSON: {json.dumps(dados, ensure_ascii=False)}")
        if dados.get("ok"):
            print("  => Servidor NOVO (API OK)")
        else:
            print("  => API respondeu mas ok=false — reinicie app.py")
    except json.JSONDecodeError:
        print("  => Resposta nao e JSON — servidor ANTIGO ou erro")
except urllib.error.HTTPError as e:
    print(f"/totem/versao: HTTP {e.code} — servidor ANTIGO (sem rota versao)")
    if e.code == 404:
        print()
        print("  *** 404 = totem ANTIGO na porta 15000 ***")
        print("  RODE AGORA:  tools\\recuperar_totem.bat")
        print("  (ou: tools\\somente_servidor.bat se ja fez git pull)")
except urllib.error.URLError as e:
    print(f"/totem/versao: OFFLINE — {e.reason}")
    print("Rode: tools\\somente_servidor.bat")
    raise SystemExit(1)

print()
try:
    html, headers = get("http://127.0.0.1:15000/totem/3")
    print("/totem/3 HTML:")
    print(f"  Header X-Eleva-Totem: {headers.get('X-Eleva-Totem', '(nao tem)')}")
    if "Retirar encomenda" in html and "Totem v2" in html:
        print("  => Pagina NOVA (Retirar + Depositar)")
    elif "Digite o código de retirada" in html:
        print("  => Pagina ANTIGA — Docker ou app.py velho")
        print("  RODE: tools\\somente_servidor.bat")
    else:
        print("  => Conteudo desconhecido")
except Exception as e:
    print(f"/totem/3: erro — {e}")

print()
print("=" * 55)
