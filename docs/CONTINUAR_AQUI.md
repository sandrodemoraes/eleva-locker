# CONTINUAR AQUI — Retomada do projeto

> **Última atualização:** 05/08/2026  
> **Estado:** Matriz OK ✅ — WhatsApp em configuração ⏳ — menu mobile anotado para resolver

---

## Onde paramos (05/08/2026)

| Item | Status |
|------|--------|
| Operador global + síndico por armário | ✅ PR #12 |
| Docker + Evolution API WhatsApp | ✅ containers rodando |
| Instância `eleva-locker` no manager | ✅ criada |
| Acesso externo IP público | ✅ `http://177.74.79.32:15000` |
| WhatsApp no depósito | ⏳ testar à noite (`py app.py` + não usar container web) |
| Menu mobile (celular) | 🔧 parcial — ver pendência abaixo |

### Ambiente atual

| Item | Valor |
|------|-------|
| PC servidor (rede local) | `192.168.16.130:15000` |
| PC servidor (rede externa) | `http://177.74.79.32:15000` |
| Evolution API / manager | `http://192.168.16.130:8080/manager` |
| Branch | `cursor/whatsapp-producao-c05c` |
| Login admin | `admin@elevalocker.com` / `123456` |

---

## Totem tablet (amanhã)

Tablet 7" em modo kiosk → URL fixa do armário:

```
http://192.168.16.130:15000/totem/3
```

Fluxo: **Retirar encomenda** → digitar código WhatsApp → tela com **compartimento grande**.

Código/QR **não aparece** para operador no depósito — só morador recebe WhatsApp.

Teste ESP offline: `docs/TESTE_ESP_OFFLINE.md`  
**Tablet amanhã:** `docs/AMANHA_TABLET.md`

---

**Reportado pelo Sandro (05/08/2026):**

| Dispositivo | Comportamento atual | Problema |
|-------------|---------------------|----------|
| **PC (tela grande)** | Menu **vertical** (sidebar esquerda) abre e funciona | Menu **horizontal** (topo) não abre / não existe navegação horizontal |
| **Celular (tela pequena)** | Só aparece barra **horizontal** do topo | Menu **vertical** fica escondido → não dá para ir em Armários, Encomendas, etc. |

**Por que acontece:** no CSS, em telas &lt; 768px a sidebar vertical é movida para fora da tela (`left: -260px`) sem botão visível (até correção recente).

**O que já foi feito (commit `2de4fff`):**
- Botão ☰ (hambúrguer) no celular para abrir menu vertical
- Overlay escuro ao abrir menu

**Ainda falta resolver:**
1. [ ] Testar ☰ no celular após `git pull` + reiniciar `py app.py`
2. [ ] Definir se no **PC** quer menu horizontal (abas no topo) **ou** melhorar navbar (sino/engrenagem/site selector)
3. [ ] Links diretos no dashboard (cards clicáveis → Armários, Encomendas)
4. [ ] Botões sino ⚙️ do topo hoje não fazem nada — implementar ou remover

**Workaround celular (funciona hoje):**
- http://177.74.79.32:15000/armarios
- http://177.74.79.32:15000/encomendas
- http://177.74.79.32:15000/notificacoes

---

## À noite — WhatsApp (retomar)

**Após reiniciar o PC (1 clique):**
```cmd
cd C:\ElevaLocker
git pull
tools\iniciar_tudo.bat
```
Sobe Docker WhatsApp + `python app.py`. Mantenha a janela aberta.

Para parar só o Docker WhatsApp: `tools\parar_tudo.bat` (servidor: Ctrl+C).

**Início automático ao ligar o PC (1 vez):**
```cmd
tools\instalar_inicio_automatico.bat
```
Docker Desktop: Settings → **Start Docker Desktop when you sign in**.  
Remover: `tools\desinstalar_inicio_automatico.bat`

**Manual (se preferir):**
```cmd
docker stop elevalocker-web-1
cd C:\ElevaLocker
git pull
docker compose --profile whatsapp up -d evolution-api evolution-postgres evolution-redis
python app.py
```

1. Manager → instância `eleva-locker` **connected/open**
2. Notificações → Testar WhatsApp
3. Depositar encomenda com telefone
4. Se falhar: `python tools/testar_whatsapp_direto.py 48996587858`

**Corrigir `.env` (1 clique):**
```cmd
cd C:\ElevaLocker
git pull
tools\criar_env_producao.bat
```
Ou: `python tools/criar_env_producao.py` → deve mostrar `OK — WhatsApp pronto para producao`.

---

## Onde paramos (03/08/2026 — noite) — histórico bancada

Você estava configurando tamanhos dos compartimentos:

| # | Tamanho |
|---|---------|
| 1–4 | P |
| 5–6 | M |
| 7 | G |
| 8 | GG |

**O que aconteceu hoje:**
- Código pronto no GitHub (PR #11, branch `cursor/bancada-tamanhos-compartimentos-c05c`)
- Você fez `git stash` do banco + firmware para trocar de branch ✅
- Branch trocada com sucesso ✅
- `fix_tamanhos_bancada.py` falhou porque o banco ativo ficou **vazio** (ESP não encontrado)
- **Seus dados antigos estão no stash** — não perdeu nada

### Stash guardado no seu PC

```cmd
git stash list
```

Deve aparecer algo como: `stash@{0}: On main: config-bancada`

Contém:
- `database/elevalocker.db` — banco com ESP, armário, encomendas
- `firmware/elevalocker_sync/elevalocker_sync.ino` — token + WiFi que você configurou

---

## AMANHÃ — 3 comandos e pronto (5 min)

Abra CMD como admin:

```cmd
cd C:\ElevaLocker
git checkout cursor/bancada-tamanhos-compartimentos-c05c
git pull
git restore --source=stash@{0} -- database/elevalocker.db
py tools/fix_tamanhos_bancada.py
set ESP32_MODO_SIMULACAO=0
set APP_URL_BASE=http://192.168.16.130:15000
py app.py
```

Confira: http://192.168.16.130:15000/compartimentos → **Bancada Teste** → coluna Tamanho.

**Firmware (token/WiFi):**

```cmd
git restore --source=stash@{0} -- firmware/elevalocker_sync/elevalocker_sync.ino
```

Abra o `.ino`, confira `ESP32_TOKEN` e `SERVIDOR_URL`, faça **Upload** no Arduino.

Se `fix_tamanhos` ainda falhar:

```cmd
py tools/setup_bancada.py --ip-esp 192.168.16.162
```

(copia o token novo para o firmware)

---

## O que JÁ evoluiu (não é zero)

| Item | Status |
|------|--------|
| Bancada 8 relés funcionando | ✅ |
| Depósito + retirada por código | ✅ |
| Firmware anti-crash (sendContent) | ✅ |
| Painel ESP 8 portas | ✅ |
| Tamanhos P/M/G/GG no código | ✅ PR #11 |
| Script `fix_tamanhos_bancada.py` | ✅ PR #11 |
| Tamanho visível na tela ESP | ✅ PR #11 (precisa regravar firmware) |
| Aplicar tamanhos no seu PC | ⏳ amanhã (restore stash) |

---

## Ambiente Sandro

| Item | Valor |
|------|-------|
| PC servidor | `192.168.16.130:15000` |
| ESP32 IP | `192.168.16.162` |
| WiFi | `ELEVA - ENERGIA SOLAR` / `eleva2277` |
| Login admin | `admin@elevalocker.com` / `123456` |
| Armário teste | Bancada Teste |
| ESP cadastro | ESP Bancada 8ch |
| Branch no PC | `cursor/bancada-tamanhos-compartimentos-c05c` |

### Mapa GPIO bancada (definitivo)

```
IN1→GPIO16   IN5→GPIO21
IN2→GPIO17   IN6→GPIO22
IN3→GPIO18   IN7→GPIO23
IN4→GPIO19   IN8→GPIO27  ← NÃO usar GPIO25 nesta placa
```

---

## PRs abertos

| PR | Branch | Conteúdo |
|----|--------|----------|
| [#6](https://github.com/sandrodemoraes/eleva-locker/pull/6) | `cursor/esp32-offline-sync-c05c` | ESP offline + fases |
| [#7](https://github.com/sandrodemoraes/eleva-locker/pull/7) | WiFi boot fixes |
| [#8](https://github.com/sandrodemoraes/eleva-locker/pull/8) | Fix editar armário |
| [#11](https://github.com/sandrodemoraes/eleva-locker/pull/11) | **Tamanhos bancada P/M/G/GG** |

---

## Depois dos tamanhos — próximo passo

1. Confirmar 8/8 relés + tamanhos no painel e na ESP
2. Teste fluxo: depositar em `/encomendas` → retirar código na ESP
3. Fase 6A WhatsApp — ver `docs/PLANO_IMPLEMENTACAO.md`

---

## Mensagem para retomar no Cursor

> "Voltei — li CONTINUAR_AQUI.md. Restaurei o stash e rodei fix_tamanhos. Vamos continuar."

---

## Documentação

- `docs/PLANO_IMPLEMENTACAO.md` — plano completo
- `docs/TESTE_BANCADA.md` — guia bancada
- `docs/ESP32_SYNC.md` — protocolo ESP
