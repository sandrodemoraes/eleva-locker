# Recuperar servidor antigo — ELEVA LOCKER

Guia para voltar ao servidor completo (Fases 1–5 + bancada ESP32) depois da formatação do PC.

> **Branch desta recuperação:** `cursor/recuperar-servidor-antigo-615b`  
> Base: `cursor/fix-editar-armario-c05c` (bancada validada) + scripts Windows (atalho / autoinício)

---

## O que estava “perdido”

Após formatar, o clone em `main` traz só a versão inicial (login, usuários, empresas).  
O servidor antigo completo (armários, compartimentos, ESP32, bancada, comercial, etc.) está nesta branch.

---

## 1. Baixar o código no PC

```cmd
cd %USERPROFILE%
git clone https://github.com/sandrodemoraes/eleva-locker.git
cd eleva-locker
git fetch origin
git checkout cursor/recuperar-servidor-antigo-615b
pip install -r requirements.txt
```

Se o projeto já existir:

```cmd
cd %USERPROFILE%\eleva-locker
git fetch origin
git checkout cursor/recuperar-servidor-antigo-615b
git pull origin cursor/recuperar-servidor-antigo-615b
pip install -r requirements.txt
```

---

## 2. Atalho na área de trabalho + início com Windows

```cmd
tools\criar_atalho_desktop.bat
```

Isso cria:
- Atalho **ElevaLocker** na área de trabalho
- Entrada na pasta **Startup** (inicia com o Windows, minimizado)

Para remover o autoinício: `tools\remover_inicio_windows.bat`

---

## 3. Subir o servidor

**Opção A — atalho**  
Duplo clique em **ElevaLocker** → abre `http://localhost:15000`

**Opção B — terminal**

```cmd
cd %USERPROFILE%\eleva-locker
set ESP32_MODO_SIMULACAO=0
set APP_URL_BASE=http://192.168.16.130:15000
py app.py
```

Porta: **15000**

---

## 4. Recriar a bancada ESP32 (se precisar)

WiFi: `ELEVA - ENERGIA SOLAR`  
ESP: `192.168.16.162` · PC: `192.168.16.130`

```cmd
py tools\setup_bancada.py --ip-esp 192.168.16.162
```

Copie o TOKEN gerado para o firmware `firmware\elevalocker_sync.ino`, grave na ESP e abra:

- http://localhost:15000/esp32/bancada
- http://192.168.16.162/

Se armários “sumirem” após editar:

```cmd
py tools\fix_armarios_site.py
```

---

## 5. Login e URLs

| Item | Valor |
|------|--------|
| Admin | `admin@elevalocker.com` / `123456` |
| App | http://localhost:15000 |
| Encomendas | http://localhost:15000/encomendas |
| Bancada | http://localhost:15000/esp32/bancada |
| Totem ESP | http://192.168.16.162/ |

---

## 6. Atualizar depois

```cmd
tools\atualizar.bat
```

Ou:

```cmd
git pull origin cursor/recuperar-servidor-antigo-615b
```

---

## Referências

- `docs/CONTINUAR_AQUI.md` — estado da bancada e próximo passo (WhatsApp)
- `docs/TESTE_BANCADA.md` — guia da bancada
- `docs/ESP32_SYNC.md` — protocolo ESP
- `docs/PLANO_IMPLEMENTACAO.md` — plano completo
