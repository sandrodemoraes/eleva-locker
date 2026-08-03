# CONTINUAR AQUI — Retomada do projeto

> **Última atualização:** 03/08/2026  
> **Estado:** Servidor antigo recuperado nesta branch · Bancada 8 relés VALIDADA ✅ — próximo: WhatsApp produção  
> **Recuperação pós-formatação:** [`docs/RECUPERAR_SERVIDOR.md`](RECUPERAR_SERVIDOR.md)

---

## Onde paramos

| Item | Status |
|------|--------|
| Fases 1–5 (operacional → escala) | ✅ |
| ESP32 sync offline 8 portas | ✅ |
| Bancada física 8 relés BESTER | ✅ **VALIDADA** |
| Depósito + retirada por código (ESP totem) | ✅ |
| Fix editar armário (site_id) | ✅ PR #8 |
| **WhatsApp produção** | ⏳ **PRÓXIMO (Fase 6A)** |

### Mapa GPIO bancada (definitivo)

```
IN1→GPIO16   IN5→GPIO21
IN2→GPIO17   IN6→GPIO22
IN3→GPIO18   IN7→GPIO23
IN4→GPIO19   IN8→GPIO27  ← NÃO usar GPIO25 nesta placa
```

### Ambiente Sandro

| Item | Valor |
|------|-------|
| PC servidor | `192.168.16.130:15000` |
| ESP32 IP | `192.168.16.162` |
| Token ESP | `784b417975f530a6cb4623df6c950154` |
| WiFi | `ELEVA - ENERGIA SOLAR` |
| Login admin | `admin@elevalocker.com` / `123456` |
| Armário teste | Bancada Teste (id=4) |
| ESP cadastro | ESP Bancada 8ch (id=4) |

---

## Comandos para subir o servidor

```cmd
cd %USERPROFILE%\eleva-locker
git fetch origin
git checkout cursor/recuperar-servidor-antigo-615b
git pull origin cursor/recuperar-servidor-antigo-615b
set ESP32_MODO_SIMULACAO=0
set APP_URL_BASE=http://192.168.16.130:15000
py app.py
```

Ou use o atalho **ElevaLocker** (`tools\criar_atalho_desktop.bat`).

ESP liga sozinha → sync automático.

---

## Plano completo de implementação

**Leia:** [`docs/PLANO_IMPLEMENTACAO.md`](PLANO_IMPLEMENTACAO.md)

Contém:
- Análise profunda de todos os módulos
- O que está pronto vs console vs ausente
- **Fase 6A:** WhatsApp produção (prioridade amanhã)
- Fases 6B–9: robustez, comercial, hardware
- Checklist técnico arquivo por arquivo
- Config `.env` proposta

---

## Prioridade amanhã — Fase 6A WhatsApp

1. Escolher provedor: **Evolution API** (rápido) ou **Meta Business** (oficial)
2. Configurar `.env` com `NOTIF_MODO=producao` + credenciais
3. Melhorar mensagem (link totem + código)
4. Testar: depositar encomenda → WhatsApp no celular
5. Verificar histórico em `/notificacoes`

Detalhes: `docs/PLANO_IMPLEMENTACAO.md` seção 5 (Fase 6A) e seção 6.

---

## URLs úteis

| URL | Função |
|-----|--------|
| http://localhost:15000/encomendas | Depositar/retirar |
| http://localhost:15000/esp32/bancada | Testar relés |
| http://localhost:15000/notificacoes | Histórico WhatsApp/email |
| http://192.168.16.162/ | Totem retirada ESP |

---

## PRs / branches

| PR | Branch | Conteúdo |
|----|--------|----------|
| recuperação | `cursor/recuperar-servidor-antigo-615b` | **Servidor completo + atalho Windows** |
| [#8](https://github.com/sandrodemoraes/eleva-locker/pull/8) | `cursor/fix-editar-armario-c05c` | Fix editar armário + bancada |
| [#9](https://github.com/sandrodemoraes/eleva-locker/pull/9) | `cursor/atalho-desktop-elevalocker-ffcf` | Atalho / autoinício Windows |
| [#6](https://github.com/sandrodemoraes/eleva-locker/pull/6) | `cursor/esp32-offline-sync-c05c` | ESP offline + fases |

**Branch recomendada no PC:** `cursor/recuperar-servidor-antigo-615b`

---

## Mensagem para retomar no Cursor

> "Voltei — li o RECUPERAR_SERVIDOR.md e CONTINUAR_AQUI. Servidor OK. Vamos implementar WhatsApp Fase 6A."

---

## Documentação

- `docs/PLANO_IMPLEMENTACAO.md` — **plano completo (NOVO)**
- `docs/TESTE_BANCADA.md` — guia bancada
- `docs/ESP32_SYNC.md` — protocolo ESP
- `docs/VISAO_MUNDIAL.md` — roadmap longo prazo
