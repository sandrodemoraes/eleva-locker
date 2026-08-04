# CONTINUAR AQUI — Retomada do projeto

> **Última atualização:** 03/08/2026 (noite)  
> **Estado:** Bancada OK ✅ — parou na configuração de tamanhos P/M/G/GG (stash pendente)

---

## Onde paramos (03/08/2026 — noite)

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
