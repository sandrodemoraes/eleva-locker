# Recuperar servidor antigo — ELEVA LOCKER

Guia para voltar ao servidor completo (Fases 1–5 + bancada ESP32) no PC novo.

> **Branch:** `cursor/recuperar-servidor-antigo-615b`  
> **03/08/2026:** não recuperar mais boot do HD velho — usar **backup Defender** + dados em `D:\backup pc fabio` + esta branch.

---

## O que usar agora

| Fonte | Para quê |
|-------|----------|
| Esta branch (GitHub) | Código completo do ElevaLocker |
| Backup Windows Defender | Arquivos que o Defender salvou |
| `D:\backup pc fabio\` | Users / projetos / possível `elevalocker.db` |
| `D:\Recuperado_Windows_Antigo\` | Se a extração `06`/`07` tiver terminado |

---

## 1. Código no PC

```cmd
cd %USERPROFILE%\eleva-locker
git fetch origin
git checkout cursor/recuperar-servidor-antigo-615b
git pull origin cursor/recuperar-servidor-antigo-615b
pip install -r requirements.txt
```

---

## 2. Atalho + início com Windows

```cmd
tools\criar_atalho_desktop.bat
```

---

## 3. Subir o servidor

```cmd
iniciar_elevalocker.bat
```

Ou:

```cmd
set ESP32_MODO_SIMULACAO=0
set APP_URL_BASE=http://192.168.16.130:15000
py app.py
```

→ http://localhost:15000  
Login: `admin@elevalocker.com` / `123456`

---

## 4. Restaurar banco (se tiver no backup)

Com o app **parado**:

```cmd
copy /Y "D:\Recuperado_Windows_Antigo\databases\elevalocker.db" "%USERPROFILE%\eleva-locker\database\elevalocker.db"
```

Se o DB estiver no Defender ou em `D:\backup pc fabio\...`, ajuste a origem. Faça cópia de segurança do `database\elevalocker.db` atual antes.

---

## 5. Bancada ESP32 (se precisar)

```cmd
py tools\setup_bancada.py --ip-esp 192.168.16.162
```

---

## Referências

- `docs/CONTINUAR_AQUI.md` — estado atual  
- `docs/RECUPERAR_COPIA_WINDOWS.md` — extrair de `D:\backup pc fabio\Windows`  
- `docs/TESTE_BANCADA.md` · `docs/ESP32_SYNC.md` · `docs/PLANO_IMPLEMENTACAO.md`  

Docs de boot/HD velho (`RECUPERAR_BOOT_WINDOWS`, `RECUPERAR_PENDRIVE_WIN11`) ficam só como histórico — **não seguir**.
