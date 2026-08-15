# PLANO DE IMPLEMENTAÇÃO — ELEVA LOCKER

> Análise profunda e roadmap de desenvolvimento  
> **Data:** 02/08/2026  
> **Autor:** sessão Cloud Agent + Sandro  
> **Objetivo:** registrar o que está pronto, o que falta e a ordem de implementação (prioridade WhatsApp + produção)

---

## 1. Resumo executivo

O ELEVA LOCKER evoluiu de MVP operacional para **plataforma SaaS completa** (Fases 1–5 + ESP32 offline-first). Em **02/08/2026** a **bancada física 8 relés** foi validada com sucesso (depósito + retirada por código na ESP).

**Próxima prioridade:** aprimorar **notificações WhatsApp em produção** e consolidar branches para uma linha estável de deploy.

| Área | Maturidade | Modo atual |
|------|------------|------------|
| Admin web (CRUD) | ⭐⭐⭐⭐ | Produção |
| Fluxo encomenda | ⭐⭐⭐⭐ | Produção |
| ESP32 + relés | ⭐⭐⭐⭐ | **Validado na bancada** |
| Comercial (planos/faturas) | ⭐⭐⭐ | Manual / console |
| Notificações | ⭐⭐ | **Console (print)** |
| Pagamentos | ⭐⭐ | Simulado |

---

## 2. O que foi concluído hoje (02/08/2026)

### 2.1 Bancada ESP32 — VALIDADA ✅

| Item | Resultado |
|------|-----------|
| Servidor Flask | `192.168.16.130:15000` |
| ESP32 IP | `192.168.16.162` |
| Token | `784b417975f530a6cb4623df6c950154` |
| Sync | v10+, 8 compartimentos |
| Heartbeat | HTTP 200 |
| Relés 1–7 | GPIO 16,17,18,19,21,22,23 |
| Relé 8 | **GPIO 27** (GPIO 25 inoperante nesta placa) |
| Depósito + retirada | Funcionando (PC + totem ESP) |

**Mapa GPIO definitivo da bancada:**

```
IN1→16  IN2→17  IN3→18  IN4→19
IN5→21  IN6→22  IN7→23  IN8→27
```

**Comandos úteis:**

```cmd
cd C:\ElevaLocker
set ESP32_MODO_SIMULACAO=0
set APP_URL_BASE=http://192.168.16.130:15000
py app.py
```

```cmd
py tools/setup_bancada.py --ip-esp 192.168.16.162
```

### 2.2 Bug armário editar — CORRIGIDO ✅

- Branch: `cursor/fix-editar-armario-c05c` — PR #8
- Fix: preserva `site_id` ao editar armário
- Script recuperação: `tools/fix_armarios_site.py`

### 2.3 Branches no GitHub

| PR | Branch | Conteúdo | Status |
|----|--------|----------|--------|
| #6 | `cursor/esp32-offline-sync-c05c` | ESP offline + fases 1–5 | Aberto |
| #7 | `cursor/wifi-fix-firmware-c05c` | WiFi boot + token fix | Aberto |
| #8 | `cursor/fix-editar-armario-c05c` | Fix editar armário | Aberto |

**Ação pendente:** merge das 3 branches numa linha estável (`main` ou branch release).

---

## 3. Análise profunda — estado do código

### 3.1 Módulos production-ready

| Módulo | Arquivos principais | Observação |
|--------|---------------------|------------|
| Auth / sessão | `routes/auth.py` | Login admin/operador |
| Dashboard | `routes/dashboard.py`, `services/dashboard_service.py` | Métricas site-scoped |
| Usuários | `routes/usuarios.py`, `services/usuario_service.py` | CRUD completo |
| Empresas | `routes/empresas.py`, `services/empresa_service.py` | CRUD + whatsapp field |
| Armários | `routes/armarios.py`, `services/armario_service.py` | Site-scoped + limites plano |
| Compartimentos | `routes/compartimentos.py` | GPIO, relé, ESP32_id |
| Encomendas | `routes/encomendas.py`, `services/encomenda_service.py` | Depósito→código→relé→notif |
| ESP32 admin | `routes/esp32.py`, `services/esp32_service.py` | CRUD, bancada, teste |
| ESP32 API | `routes/api/esp32_api.py` | sync, heartbeat, eventos |
| Sync offline | `services/esp32_sync_service.py` | Idempotente, fila eventos |
| Firmware | `firmware/elevalocker_sync.ino` | Offline-first 8–32 portas |
| Totem | `routes/totem.py` | Retirada web + QR |
| Planos/Contratos/Faturas | `routes/planos.py`, `contratos.py`, `faturas.py` | SaaS completo |
| Multi-site + API v1 | `routes/sites.py`, `routes/api/v1/public_api.py` | Franquia |
| BI | `routes/relatorios.py` | Ocupação + previsão linear |
| Backup | `services/backup/backup_service.py` | Rotação 5 cópias |

**Testes automatizados:** `tools/test_fase5.py` — 17/17 passando (não cobre ESP físico nem WhatsApp real).

### 3.2 Módulos parciais / modo console

| Módulo | Problema | Variável env |
|--------|----------|--------------|
| **WhatsApp** | Só `print()` no terminal | `NOTIF_MODO=console`, `NOTIF_WHATSAPP_ATIVO=0` |
| **E-mail** | SMTP não configurado por padrão | `SMTP_HOST` vazio |
| **SMS** | Desativado | `NOTIF_SMS_ATIVO=0` |
| **Pagamentos** | Links fake | `PAGAMENTO_MODO=console` |
| **Faturas mensais** | Botão manual, sem cron | — |
| **Portal cliente** | Só admin logado | `usuarios.empresa_id` não usado |
| **Plano inclui_whatsapp** | Flag existe, **não é verificada** | — |

### 3.3 Ausente completamente

| Feature | Impacto | Referência roadmap |
|---------|---------|-------------------|
| Fila async notificações (Celery/Redis) | Médio | VISAO_MUNDIAL B3 |
| WhatsApp Business API (Meta) oficial | Alto | VISAO_MUNDIAL B3 |
| Retry automático notificações | Alto | — |
| Alerta ESP offline → WhatsApp admin | Médio | VISAO_MUNDIAL A6 |
| Cron faturas + webhook pagamento | Alto | Fase comercial |
| Expiração encomenda 72h | Médio | PROJETO.md |
| Tabela `destinatarios` | Baixo | PROJETO.md |
| Sensores porta aberta/fechada | Alto | VISAO_MUNDIAL A1 |
| OTA firmware ESP32 | Médio | VISAO_MUNDIAL A3 |
| CI/CD + testes integração | Médio | — |
| Login empresa (multi-tenant) | Médio | Fase 5 gap |

---

## 4. Análise — sistema de notificações (foco WhatsApp)

### 4.1 Fluxo atual

```
EncomendaService.depositar()
  → Esp32Service.abrir_compartimento()   # abre relé
  → NotificacaoService.notificar_encomenda_chegou()
       → _montar_mensagem()               # template texto
       → _enviar_whatsapp()               # Evolution API ou console
       → NotificacaoRepository.registrar() # histórico
  → EncomendaRepository.marcar_notificado()
```

**Arquivos envolvidos:**

- `services/notificacao_service.py` — lógica central
- `services/encomenda_service.py` — disparo no depósito
- `routes/encomendas.py` — reenviar notificação
- `routes/notificacoes.py` — histórico UI
- `templates/notificacoes.html` — status canais
- `config.py` — variáveis env
- `repositories/notificacao_repository.py` — persistência

### 4.2 Mensagem atual (WhatsApp)

```
Olá {cliente}!

Sua encomenda chegou no *ELEVA LOCKER*.
📍 Local: {armario}
📦 Compartimento: #{compartimento}
🔑 Código de retirada: *{codigo}*

Apresente este código no totem ou informe à portaria.
```

**Limitações:**

1. Sem link clicável para totem (`APP_URL_BASE/totem` ou IP ESP)
2. Markdown `*bold*` misturado no e-mail
3. Sem template Meta aprovado (obrigatório WhatsApp Business oficial)
4. Sem botões interativos ("Ver código", "Abrir mapa")
5. Envio **síncrono** — trava request HTTP do depósito
6. Sem retry se API falhar
7. Plano `inclui_whatsapp` ignorado
8. `.env.example` incompleto (faltam vars WhatsApp/SMTP)

### 4.3 Integração Evolution API (já codificada)

```http
POST {WHATSAPP_API_URL}/message/sendText/{WHATSAPP_INSTANCIA}
Headers: Content-Type: application/json, apikey: {WHATSAPP_API_KEY}
Body: {"number": "5522999998888", "text": "..."}
```

**Para ativar:**

```env
NOTIF_MODO=producao
NOTIF_WHATSAPP_ATIVO=1
WHATSAPP_API_URL=http://servidor:8080
WHATSAPP_API_KEY=sua_chave
WHATSAPP_INSTANCIA=nome_instancia
```

---

## 5. Plano de implementação — fases priorizadas

### FASE 6A — WhatsApp produção (PRIORIDADE AMANHÃ) 🔴

**Objetivo:** cliente recebe WhatsApp real ao depositar encomenda.

| # | Tarefa | Arquivo(s) | Critério de aceite |
|---|--------|------------|-------------------|
| 6A.1 | Escolher provedor | — | Evolution API **ou** Meta Cloud API |
| 6A.2 | Subir Evolution API (Docker) | `docker-compose.yml` (novo serviço) | Instância conectada, QR escaneado |
| 6A.3 | Completar `.env.example` | `.env.example` | Todas vars NOTIF/SMTP/WhatsApp documentadas |
| 6A.4 | Criar `.env` produção Sandro | `.env` (local, gitignore) | Credenciais reais |
| 6A.5 | Melhorar template mensagem | `services/notificacao_service.py` | Link totem + IP ESP + código |
| 6A.6 | Separar template email vs WhatsApp | `services/notificacao_service.py` | Email sem markdown WhatsApp |
| 6A.7 | Validar telefone BR | `services/notificacao_service.py` | DDD + 9 dígitos, erro claro |
| 6A.8 | Exibir resultado no depósito | `routes/encomendas.py`, `templates/encomendas.html` | Flash: "WhatsApp enviado" ou erro |
| 6A.9 | Teste end-to-end | manual | Depositar → WhatsApp chega no celular |
| 6A.10 | Verificar histórico | `/notificacoes` | Status `enviado` com detalhe |

**Estimativa técnica:** 1 sessão de trabalho (provedor + código + teste).

---

### FASE 6B — WhatsApp robusto 🟠

| # | Tarefa | Arquivo(s) | Critério de aceite |
|---|--------|------------|-------------------|
| 6B.1 | Enforce `inclui_whatsapp` do plano | `services/limite_plano_service.py`, `notificacao_service.py` | Starter não envia WA |
| 6B.2 | Retry 3x com backoff | `services/notificacao_service.py` | Falha temporária reenvia |
| 6B.3 | Botão "Testar WhatsApp" admin | `routes/notificacoes.py`, `templates/notificacoes.html` | Envia msg teste |
| 6B.4 | Alerta ESP offline | `services/esp32_service.py`, `notificacao_service.py` | ESP >5min offline → admin |
| 6B.5 | Adapter Meta Cloud API | `services/whatsapp_providers/meta.py` (novo) | Suporte dual provider |
| 6B.6 | Template Meta aprovado | Meta Business Manager | "encomenda_chegou" aprovado |
| 6B.7 | Testes automatizados | `tools/test_notificacoes.py` (novo) | Mock API + plan gate |

---

### FASE 6C — Consolidar branches e release 🟠

| # | Tarefa | Detalhe |
|---|--------|---------|
| 6C.1 | Merge PR #7 wifi-fix | Fix heartbeat `Row.get` + firmware path |
| 6C.2 | Merge PR #8 fix armário | Preserva site_id |
| 6C.3 | Atualizar `setup_bancada.py` | GPIO relé 8 = **27** (não 25) |
| 6C.4 | Atualizar `elevalocker_sync.ino` comment | GPIO map 16–23,27 |
| 6C.5 | Tag release `v0.6.0-bancada` | Bancada validada |
| 6C.6 | Atualizar README + CONTINUAR_AQUI | Estado atual |

---

### FASE 7 — Comercial automático 🟡

| # | Tarefa | Arquivo(s) |
|---|--------|------------|
| 7.1 | Cron faturas mensais | APScheduler ou Task Scheduler Windows |
| 7.2 | Gateway Asaas/Stripe real | `services/faturamento_service.py` |
| 7.3 | Webhook pagamento confirmado | `routes/api/pagamento_webhook.py` (novo) |
| 7.4 | E-mail fatura vencida | `notificacao_service.py` |
| 7.5 | Portal login por empresa | `routes/portal.py`, auth |

---

### FASE 8 — Confiabilidade operacional 🟡

| # | Tarefa | Referência |
|---|--------|------------|
| 8.1 | Sensores porta GPIO input | VISAO_MUNDIAL A1 |
| 8.2 | Confirmação depósito por sensor | A2 |
| 8.3 | Fila async Celery + Redis | Notificações |
| 8.4 | Prometheus + Grafana | A5 |
| 8.5 | OTA firmware ESP | A3 |
| 8.6 | Expiração encomenda 72h | Job diário |

---

### FASE 9 — Produto diferenciado 🟢

Ver `docs/VISAO_MUNDIAL.md` — App morador PWA, QR dinâmico TOTP, integrações e-commerce, ML ocupação, LGPD completo.

---

## 6. Detalhamento técnico — WhatsApp (implementação amanhã)

### 6.1 Opção A — Evolution API (recomendado para começar)

**Prós:** Rápido, número WhatsApp comum, código já pronto  
**Contras:** Não oficial Meta, risco bloqueio número

**Passos:**

1. Docker:
   ```yaml
   # adicionar em docker-compose.yml
   evolution-api:
     image: atendai/evolution-api:latest
     ports: ["8080:8080"]
   ```
2. Criar instância + escanear QR
3. Configurar `.env` do Flask
4. Testar depósito com telefone real

### 6.2 Opção B — WhatsApp Business Cloud API (Meta)

**Prós:** Oficial, escalável, templates aprovados  
**Contras:** Setup Meta Business, custo por mensagem, template pré-aprovado

**Implementação nova:**

```
services/whatsapp_providers/
  __init__.py
  base.py          # interface send_text(), send_template()
  evolution.py     # código atual extraído
  meta.py          # Graph API v18+
```

**Config:**

```env
WHATSAPP_PROVIDER=meta  # evolution | meta
WHATSAPP_META_TOKEN=...
WHATSAPP_META_PHONE_ID=...
WHATSAPP_META_TEMPLATE=encomenda_chegou
```

### 6.3 Mensagem melhorada (proposta)

```
Olá {cliente}! 📦

Sua encomenda chegou no *ELEVA LOCKER*.

📍 {armario}
🚪 Compartimento #{compartimento}
🔑 Código: *{codigo}*

Retire em:
→ Totem: {APP_URL_BASE}/totem
→ Armário: http://192.168.16.162/

Válido até retirada. Dúvidas: portaria.
```

### 6.4 Código a alterar (checklist dev)

- [ ] `services/notificacao_service.py` — `_montar_mensagem_whatsapp()`, `_montar_mensagem_email()`
- [ ] `services/notificacao_service.py` — `_enviar_whatsapp()` retry + parse erro
- [ ] `services/limite_plano_service.py` — `pode_usar_whatsapp(empresa_id)`
- [ ] `config.py` — `WHATSAPP_PROVIDER`, vars Meta
- [ ] `.env.example` — documentação completa
- [ ] `routes/notificacoes.py` — POST `/notificacoes/testar-whatsapp`
- [ ] `templates/notificacoes.html` — botão teste + status provider
- [ ] `templates/encomendas.html` — ícones canal notificado (💬📧)
- [ ] `tools/test_notificacoes.py` — testes unitários

---

## 7. Configuração ambiente Sandro (referência)

```env
# PC servidor
SECRET_KEY=ElevaLocker2026
APP_URL_BASE=http://192.168.16.130:15000
ESP32_MODO_SIMULACAO=0

# Notificações — ATIVAR AMANHÃ
NOTIF_MODO=producao
NOTIF_WHATSAPP_ATIVO=1
NOTIF_EMAIL_ATIVO=1
WHATSAPP_API_URL=http://localhost:8080
WHATSAPP_API_KEY=
WHATSAPP_INSTANCIA=eleva-locker

# SMTP (opcional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=
SMTP_FROM=noreply@elevalocker.com
```

**Firmware ESP32:**

```cpp
WIFI_SSID     = "ELEVA - ENERGIA SOLAR"
WIFI_PASSWORD = "eleva2277"
SERVIDOR_URL  = "http://192.168.16.130:15000"
ESP32_TOKEN   = "784b417975f530a6cb4623df6c950154"
// GPIO relé 8 = 27 (firmware GPIO_PADRAO + banco)
```

**Login admin:** `admin@elevalocker.com` / `123456`

---

## 8. Riscos e dependências

| Risco | Mitigação |
|-------|-----------|
| Evolution API bloqueia número | Migrar para Meta Cloud API |
| GPIO 25 morto em outras placas | Documentar mapa 16–23,27; parametrizar por armário |
| Branches divergentes | Merge 6C esta semana |
| Notificação síncrona lenta | Fase 8 — Celery |
| WhatsApp sem telefone no depósito | Tornar telefone obrigatório se WA ativo |

---

## 9. Mensagem para retomar amanhã

> "Voltei — li o PLANO_IMPLEMENTACAO.md. Vamos implementar Fase 6A WhatsApp produção. Tenho [Evolution API / Meta] disponível."

**Ordem sugerida amanhã:**

1. Ler este doc + `docs/CONTINUAR_AQUI.md`
2. Escolher provedor WhatsApp (Evolution vs Meta)
3. Implementar Fase 6A (itens 6A.1–6A.10)
4. Teste: depositar encomenda → WhatsApp no celular
5. Se sobrar tempo: Fase 6B.1–6B.3 (plano gate + retry + botão teste)

---

## 10. Referências

| Documento | Conteúdo |
|-----------|----------|
| `docs/CONTINUAR_AQUI.md` | Comandos retomada rápida |
| `docs/TESTE_BANCADA.md` | Guia bancada 8 relés |
| `docs/ESP32_SYNC.md` | Protocolo sync ESP |
| `docs/VISAO_MUNDIAL.md` | Roadmap longo prazo |
| `docs/PROJETO.md` | Documento mestre técnico |
| `services/notificacao_service.py` | Código WhatsApp atual |

---

*Documento gerado ao final da sessão 02/08/2026 — bancada 8/8 operacional.*
