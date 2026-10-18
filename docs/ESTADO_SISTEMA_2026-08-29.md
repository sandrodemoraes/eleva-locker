# ELEVA LOCKER — Registro do estado do sistema

**Data do snapshot:** 29/08/2026  
**Ambiente:** Bancada Matriz ELEVA (Sandro)  
**Branch Git:** `cursor/retirada-pacote-retido-c05c`  
**Pull Request:** [#40](https://github.com/sandrodemoraes/eleva-locker/pull/40)  
**Versão do totem:** `2.4.8` (`TOTEM_VERSAO` em `routes/totem.py`)

> Documento de referência para comparar evoluções futuras.  
> Use junto com `git log`, `py tools/diagnostico_codigo.py` e este arquivo datado.

---

## 1. Resumo executivo

O ELEVA LOCKER na bancada Matriz está **operacional em produção local**:

- Painel admin em `http://192.168.16.130:15000`
- Totem Matriz (armário id **2**, 16 portas) acessível em `/totem/2`
- Celular configurado como totem em **modo quiosque** (Fully Kiosk Browser + licença Plus)
- WhatsApp via **Evolution API** (`eleva-locker`) para encomendas e **ajuda no totem**
- Backup automático e manual no **disco D:**
- ESP32 em modo real (`ESP32_MODO_SIMULACAO=0`)

**Próximo foco planejado:** LGPD (consentimento, retenção, política de privacidade, auditoria).

---

## 2. Infraestrutura na bancada

| Item | Valor |
|------|--------|
| PC / pasta | `C:\ElevaLocker` |
| IP local | `192.168.16.130` |
| Porta Flask | `15000` |
| URL base | `http://192.168.16.130:15000` |
| Banco | SQLite — `database\elevalocker.db` |
| Disco backup | `D:\ElevaLockerBackup\` |
| SO | Windows 10/11 |
| Python | 3.14 (via `py` ou `python`) |
| Docker Desktop | Sim — Evolution API + Postgres + Redis |

### Containers Docker (WhatsApp)

| Container | Imagem | Porta |
|-----------|--------|-------|
| `elevalocker-evolution-api-1` | `evoapicloud/evolution-api:v2.3.0` | 8080 |
| `elevalocker-evolution-postgres-1` | `postgres:15-alpine` | 5432 |
| `elevalocker-evolution-redis-1` | `redis:7-alpine` | 6379 |

**Subir após reiniciar o PC:**

```cmd
docker start elevalocker-evolution-postgres-1
docker start elevalocker-evolution-redis-1
docker start elevalocker-evolution-api-1
```

---

## 3. Armários cadastrados (snapshot)

| ID | Nome | Portas | Uso |
|----|------|--------|-----|
| **2** | ELEVA Locker Matriz | 16 | **Totem fixo** (`TOTEM_ARMARIO_ID=2`) |
| **3** | ELEVA Locker Bancada 2 | 24 | Segundo armário / testes |

Site selecionado no painel: **Matriz ELEVA**.

---

## 4. Módulos do sistema (menu admin)

| Módulo | Rota principal | Status |
|--------|----------------|--------|
| Dashboard | `/dashboard` | ✅ Operacional |
| Usuários | `/usuarios` | ✅ CRUD |
| Empresas | `/empresas` | ✅ CRUD |
| Armários | `/armarios` | ✅ Listagem + detalhe (ESP, compartimentos, usuários) |
| Compartimentos | `/compartimentos` | ✅ CRUD |
| Encomendas | `/encomendas` | ✅ Depósito, retirada, retida, QR, reenvio |
| ESP32 | `/esp32` | ✅ Placas + sync/heartbeat |
| Totem | `/totem/escolher` | ✅ Escolha admin; totem fixo id 2 |
| Financeiro | `/financeiro` | ✅ Módulo comercial |
| Planos | `/planos` | ✅ |
| Contratos | `/contratos` | ✅ |
| Faturas | `/faturas` | ✅ |
| Portal Cliente | `/portal` | ✅ |
| Sites / API | `/sites` | ✅ Multi-site |
| Relatórios BI | `/relatorios` | ✅ |
| Notificações | `/notificacoes` | ✅ Histórico + ajuda totem |
| Logs | `/logs` | ✅ Auditoria de ações |
| Configurações | `/configuracoes` | ✅ Backup manual |

---

## 5. Totem (v2.4.8)

### URLs

| URL | Função |
|-----|--------|
| `/totem/2` | Totem Matriz (principal) |
| `/totem/matriz` | Atalho → redireciona para id 2 |
| `/totem/quiosque` | Modo quiosque → `/totem/2?kiosk=1` |
| `/totem/quiosque/fully.json` | Config importável Fully Kiosk |
| `/totem/escolher` | Admin escolhe armário (login) |
| `/totem/versao` | JSON de diagnóstico |

### Funcionalidades do totem

- Retirada com código 6 dígitos (WhatsApp)
- Depósito (sem PIN quando `TOTEM_DEPOSITO_SEM_PIN=1`)
- Mapa de portas / polling de status
- **Preciso de ajuda** → WhatsApp portaria + registro no painel
- Rate limit anti-abuso
- PWA / manifest por armário
- Modo quiosque (`?kiosk=1`): wake lock, bloqueio voltar, tela ligada

### Celular como totem (29/08/2026)

- App: **Fully Kiosk Browser** (licença Plus)
- Start URL: `http://192.168.16.130:15000/totem/2`
- Kiosk Mode: ligado, Launch on Boot, Keep Screen On, Disable Home Button
- **Single App Mode:** desligado (usa página web, não app Android)

---

## 6. Notificações

### Canais (.env produção)

| Canal | Status |
|-------|--------|
| WhatsApp (Evolution) | ✅ `NOTIF_WHATSAPP_ATIVO=1`, instância `eleva-locker` |
| E-mail | ⚠️ Ativo no .env; SMTP não configurado |
| SMS | ❌ Desligado |

### Ajuda no totem

| Variável | Valor (teste 29/08) |
|----------|------------------------|
| `TOTEM_AJUDA_TELEFONE` | `48991570639` |
| `TOTEM_AJUDA_ALERTA` | `1` |

**Fluxo:**

1. Morador toca **Preciso de ajuda** no totem
2. Sistema envia WhatsApp para a portaria
3. Registra pedido em `totem_ajuda_pedidos`
4. **Sininho** no painel mostra badge vermelho (pendentes)
5. Admin em `/notificacoes#ajuda-totem` → **Atendido**

---

## 7. ESP32

- Token configurado no `.env` (`ESP32_TOKEN`)
- Modo simulação: **desligado** (hardware real)
- API: `/api/esp32/sync`, `/heartbeat`, `/eventos`, `/validar-codigo`
- Sync de versão por placa (`sync_versao`)
- Detecção offline por heartbeat

---

## 8. Backup

### Automático (servidor)

- Pasta rotativa: `backups\` (até 5 cópias) ou `BACKUP_DIR`
- Dispara ao iniciar `app.py` (se `SKIP_BACKUP=0`)

### Manual disco D:

```cmd
BACKUP_DISCO_D.bat
```

| Destino | Conteúdo |
|---------|----------|
| `D:\ElevaLockerBackup\rotativo\backup_01\` | Banco, `.env`, uploads |
| `D:\ElevaLockerBackup\projeto\` | Espelho do código |
| `D:\ElevaLockerBackup\zip\` | ZIP seguro (opcional) |

### Scripts relacionados

- `tools\backup_zip_seguro.bat`
- `tools\abrir_pasta_backup_zip.bat`

---

## 9. Scripts úteis (raiz e `tools\`)

| Script | Função |
|--------|--------|
| `INICIAR.bat` | Sobe servidor + abre navegador |
| `ATUALIZAR.bat` | Atualiza código da branch |
| `DIAGNOSTICO.bat` | Verifica se código local está atualizado |
| `BACKUP_DISCO_D.bat` | Backup completo no D: |
| `CONFIGURAR_CELULAR_TOTEM.bat` | URL totem no celular |
| `CONFIGURAR_QUIOSQUE.bat` | Modo quiosque Fully Kiosk |
| `CONFIGURAR_AJUDA_TOTEM.bat` | Telefone WhatsApp portaria |
| `TESTAR_TOTEM.bat` | Testa rotas totem/quiosque |
| `tools\diagnostico_env.py` | Confere se `.env` é lido |
| `tools\atualizar_bancada.bat` | Reset hard preservando banco |
| `tools\instalar_inicio_windows.bat` | Inicia com Windows |
| `tools\corrigir_totem_armario.bat` | Garante Matriz no banco |

---

## 10. Configuração `.env` (referência — sem segredos)

Variáveis principais em produção na bancada:

```env
ELEVA_BANCADA=1
APP_URL_BASE=http://192.168.16.130:15000
TOTEM_ARMARIO_ID=2
TOTEM_AJUDA_TELEFONE=48991570639
TOTEM_AJUDA_ALERTA=1
TOTEM_DEPOSITO_SEM_PIN=1
NOTIF_MODO=producao
NOTIF_WHATSAPP_ATIVO=1
WHATSAPP_PROVIDER=evolution
WHATSAPP_API_URL=http://192.168.16.130:8080
WHATSAPP_INSTANCIA=eleva-locker
ESP32_MODO_SIMULACAO=0
FLASK_DEBUG=0
SKIP_BACKUP=0
```

> **Correção 29/08:** `config.py` passou a **carregar `.env` automaticamente** (antes o `py app.py` ignorava o arquivo).

---

## 11. Evoluções desta sessão (29/08/2026)

Registro do que foi implementado/corrigido neste dia:

| # | Evolução |
|---|----------|
| 1 | Totem celular — URLs `/totem/2`, `/totem/matriz`, `/totem/quiosque` |
| 2 | Modo quiosque — Fully Kiosk + JSON importável |
| 3 | Scripts `CONFIGURAR_*` e `TESTAR_TOTEM.bat` |
| 4 | Ajuda no totem — `TOTEM_AJUDA_TELEFONE` + WhatsApp |
| 5 | Carregamento automático do `.env` em `config.py` |
| 6 | Badge vermelho no sininho (pedidos ajuda pendentes) |
| 7 | Seção `/notificacoes#ajuda-totem` + botão **Atendido** |
| 8 | Fix erro 500 ao marcar atendido (`total_changes` no SQLite) |
| 9 | Fix redirect **Atendido** → sempre `/notificacoes#ajuda-totem` |
| 10 | Navbar — sino → notificações, engrenagem → configurações |
| 11 | Tela `/armarios/<id>` restaurada (ESP, compartimentos, usuários) |
| 12 | Ctrl+C com confirmação S/N |
| 13 | Início automático Windows + atalho área de trabalho |
| 14 | Backup disco D: documentado e testado |

---

## 12. Problemas conhecidos resolvidos (para não repetir)

| Problema | Causa | Solução |
|----------|--------|---------|
| `.env` ignorado | `config.py` não lia arquivo | `git pull` + `_carregar_env_arquivo()` |
| WhatsApp ajuda falha | Evolution parada | `docker start` nos 3 containers |
| 404 `/totem/quiosque` | Código desatualizado | `ATUALIZAR.bat` + reiniciar |
| Erro 500 Atendido | `conn.total_changes` inexistente | Fix em `totem_ajuda_repository.py` |
| Fully "Oops" kiosk | Single App Mode sem app | Desligar Single App Mode |
| `echo VAR=1>>` vazio | CMD interpreta `1>>` | Espaço antes de `>>` |

---

## 13. Pendências / próximos passos

| Prioridade | Item |
|------------|------|
| Alta | **LGPD** — política, consentimento, exclusão, mascaramento |
| Média | SMTP para e-mail de produção |
| Média | PostgreSQL (vars no .env existem; ainda usa SQLite) |
| Baixa | Polling automático do sininho (atualiza ao recarregar página) |
| Baixa | Documentar compose Evolution em repo (`docker-compose.evolution.yml`) |

---

## 14. Como comparar no futuro

1. **Data + branch:** anote commit (`git rev-parse --short HEAD`)
2. **Totem:** acesse `/totem/versao` — compare `versao` e flags
3. **Diagnóstico código:** `DIAGNOSTICO.bat` ou `py tools\diagnostico_codigo.py`
4. **Diagnóstico .env:** `py tools\diagnostico_env.py`
5. **Teste totem:** `TESTAR_TOTEM.bat`
6. **Novo snapshot:** copie este arquivo como `docs/ESTADO_SISTEMA_YYYY-MM-DD.md`
7. **Backup:** rode `BACKUP_DISCO_D.bat` antes de mudanças grandes

### Comandos rápidos

```cmd
cd C:\ElevaLocker
git log -1 --oneline
py tools\diagnostico_env.py
py tools\diagnostico_codigo.py
docker ps
findstr TOTEM .env
```

---

## 15. Contatos e responsável

| Papel | Nome |
|-------|------|
| Desenvolvimento / bancada | Sandro |
| Repositório | `github.com/sandrodemoraes/eleva-locker` |

---

*Documento gerado em 29/08/2026 — snapshot fiel ao estado após sessão de totem, quiosque, notificações e backup.*
