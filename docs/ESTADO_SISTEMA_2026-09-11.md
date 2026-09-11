# ELEVA LOCKER — Registro do estado do sistema

**Data do snapshot:** 11/09/2026
**Ambiente:** Bancada / Matriz ELEVA (Sandro)
**Branch Git de referência:** `cursor/site-piloto-c05c`
**PRs recentes:** [#46](https://github.com/sandrodemoraes/eleva-locker/pull/46) (AGENTS.md), [#47](https://github.com/sandrodemoraes/eleva-locker/pull/47) (helper WhatsApp)
**Versão do totem:** `2.4.8` (`TOTEM_VERSAO` em `routes/totem.py`)

> Snapshot de referência para comparar evoluções futuras.
> Use junto com `git log`, `py tools/diagnostico_codigo.py`, `py tools/diagnostico_env.py`.
> Snapshot anterior: [`ESTADO_SISTEMA_2026-08-29.md`](ESTADO_SISTEMA_2026-08-29.md).

---

## 1. Resumo executivo

ELEVA LOCKER **operacional em produção local** na bancada Matriz:

- Painel admin em `http://192.168.16.130:15000`
- Totem Matriz (armário id **2**, 16 portas) em `/totem/2`; celular em modo quiosque (Fully Kiosk)
- WhatsApp via **Evolution API** (`eleva-locker`) — encomendas e ajuda no totem
- Backup automático e manual (disco D:)
- ESP32 em modo real (`ESP32_MODO_SIMULACAO=0`)

**Novidades desde 29/08:** pacote de **site piloto (Modelo A)** para testar site remoto,
e **ferramentas de operação do WhatsApp** (script de religamento + doc de diagnóstico).

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
| Python | 3 (via `py` ou `python`) |
| Docker Desktop | Sim — Evolution API + Postgres + Redis |

### Containers Docker (WhatsApp)

| Container | Imagem | Porta |
|-----------|--------|-------|
| `elevalocker-evolution-api-1` | `evoapicloud/evolution-api:v2.3.0` | 8080 |
| `elevalocker-evolution-postgres-1` | `postgres:15-alpine` | 5432 |
| `elevalocker-evolution-redis-1` | `redis:7-alpine` | 6379 |

Volumes (dados persistem entre reinícios): `elevalocker_evolution_pg`,
`elevalocker_evolution_redis`, `elevalocker_evolution_data`, `elevalocker_pgdata`.

**Reinício automático aplicado em 11/09** (para sobreviver a reboot):

```cmd
docker update --restart unless-stopped elevalocker-evolution-postgres-1 elevalocker-evolution-redis-1 elevalocker-evolution-api-1
```

**Religar manualmente após reiniciar o PC** (ordem importa):

```cmd
docker start elevalocker-evolution-postgres-1 elevalocker-evolution-redis-1
docker start elevalocker-evolution-api-1
```

Atalho: `tools\iniciar_evolution.bat`. Diagnóstico completo: `docs/WHATSAPP_EVOLUTION.md`.

---

## 3. Armários (conforme último snapshot — confirmar no painel)

| ID | Nome | Portas | Uso |
|----|------|--------|-----|
| **2** | ELEVA Locker Matriz | 16 | **Totem fixo** (`TOTEM_ARMARIO_ID=2`) |
| **3** | ELEVA Locker Bancada 2 | 24 | Segundo armário / testes |

> Os dados de armário ficam no banco da máquina. Confirme a lista atual em `/armarios`.

---

## 4. Módulos do sistema (menu admin)

| Módulo | Rota principal | Status |
|--------|----------------|--------|
| Dashboard | `/dashboard` | ✅ |
| Usuários | `/usuarios` | ✅ CRUD |
| Empresas | `/empresas` | ✅ CRUD |
| Armários | `/armarios` | ✅ Listagem + detalhe (ESP, compartimentos, usuários) |
| Compartimentos | `/compartimentos` | ✅ CRUD |
| Encomendas | `/encomendas` | ✅ Depósito, retirada, retida, QR, reenvio |
| ESP32 | `/esp32` | ✅ Placas + sync/heartbeat |
| Totem | `/totem/escolher` | ✅ Escolha admin; totem fixo id 2 |
| Financeiro | `/financeiro` | ✅ |
| Planos / Contratos / Faturas | `/planos` `/contratos` `/faturas` | ✅ |
| Portal Cliente | `/portal` | ✅ |
| Sites / API | `/sites` | ✅ Multi-site + API v1 |
| Relatórios BI | `/relatorios` | ✅ |
| Notificações | `/notificacoes` | ✅ Histórico + ajuda totem |
| Logs | `/logs` | ✅ Auditoria |

---

## 5. Site piloto (Modelo A) — novo

Pacote para testar um **site remoto com servidor local** (offline-first). Ver
[`INSTALACAO_SITE.md`](INSTALACAO_SITE.md).

- Bootstrap: `py tools\bootstrap_site_piloto.py --nome "..." --codigo piloto-050 --ip-servidor 192.168.50.10 --gerar-api-key`
- Cria Site + Armário + `Sites\<codigo>\` (env.txt, rede.txt, api_key.txt) com `SECRET_KEY` e `ESP32_TOKEN` próprios
- Superfície exposta ao morador: **totem/quiosque + WhatsApp** (painel fica restrito ao operador)
- Domínio público (`www.elevalocker.com.br`) só na **Fase 3**; piloto roda em IP local

---

## 6. Notificações

| Canal | Status |
|-------|--------|
| WhatsApp (Evolution) | ✅ `NOTIF_WHATSAPP_ATIVO=1`, instância `eleva-locker` |
| E-mail | ⚠️ Ativo no .env; SMTP não configurado |
| SMS | ❌ Desligado |

Envio em `services/notificacao_service.py`. Status ao vivo:
`NotificacaoService.status_whatsapp()` (usado na tela `/notificacoes`).
Se cair, o totem mostra o erro no fim do depósito e a encomenda pode ser **reenviada** pelo painel.

---

## 7. `.env` (referência — sem segredos)

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

> No próprio PC, `WHATSAPP_API_URL=http://localhost:8080` também funciona.

---

## 8. Backup

- **Automático:** dispara ao iniciar `app.py` (se `SKIP_BACKUP=0`); até 5 cópias em `backups\`
  (banco, uploads, config, logs, `.env`, `PROJETO.md`). Código em `services/backup/backup_service.py`.
- **Manual disco D::** `BACKUP_DISCO_D.bat` → `D:\ElevaLockerBackup\` (banco, `.env`, espelho do código, ZIP).
- **Restaurar dados de antes:** `BackupService.restaurar(numero)`.

Camadas de histórico disponíveis:

| Quero ver... | Onde |
|--------------|------|
| Como o sistema estava | Este arquivo + `ESTADO_SISTEMA_2026-08-29.md` |
| Como o **código** estava | Git (`git log`, `git diff`, `git checkout <commit>`) |
| Voltar **dados** (banco/.env) | Backups (`backups\` ou D:) |
| Notificações / ações | Tabelas `notificacoes` e `logs` no banco |

---

## 9. Evoluções desde o snapshot anterior (29/08 → 11/09)

| # | Evolução | Commit/PR |
|---|----------|-----------|
| 1 | Pacote **site piloto Modelo A** (bootstrap, .env.site, docs) | `7f14f63` |
| 2 | Docs de arquitetura de rede em fases + domínio público | `028476d`, `f8e0979` |
| 3 | Fix WhatsApp: nome + endereço do armário em vez de IP local | `4d39188` |
| 4 | Helper **`tools/iniciar_evolution.bat`** + `docs/WHATSAPP_EVOLUTION.md` | PR #47 |
| 5 | `AGENTS.md` com instruções de ambiente (Cursor Cloud) | PR #46 |

---

## 10. Problemas conhecidos resolvidos (para não repetir)

| Problema | Causa | Solução |
|----------|--------|---------|
| **WhatsApp não envia — `WinError 10061`** | Containers Evolution **parados** após reboot | `docker start` (postgres→redis→api) + `--restart unless-stopped`. Ver `tools/iniciar_evolution.bat` |
| `.env` ignorado | `config.py` não lia arquivo | `_carregar_env_arquivo()` (já corrigido) |
| 404 `/totem/quiosque` | Código desatualizado | `ATUALIZAR.bat` + reiniciar |
| Erro 500 "Atendido" | `conn.total_changes` inexistente | Fix em `totem_ajuda_repository.py` |
| Fully "Oops" kiosk | Single App Mode sem app | Desligar Single App Mode |

---

## 11. Pendências / próximos passos

| Prioridade | Item |
|------------|------|
| Alta | Iniciar Evolution junto com o Windows (Docker autostart + login automático) |
| Média | SMTP para e-mail de produção |
| Média | Documentar compose da Evolution no repo (`docker-compose.evolution.yml`) |
| Média | PostgreSQL para o app (vars no `.env` existem; ainda usa SQLite) |
| Baixa | Executar o piloto Modelo A em campo (1º condomínio) |

---

## 12. Como comparar / diagnosticar no futuro

```cmd
cd C:\ElevaLocker
git log -1 --oneline
py tools\diagnostico_env.py
py tools\diagnostico_codigo.py
docker ps
findstr TOTEM .env
```

- Totem: acessar `/totem/versao` — comparar `versao` e flags.
- WhatsApp: `docker ps` (3 containers `Up`) + abrir `http://localhost:8080`.
- Novo snapshot: copie este arquivo como `docs/ESTADO_SISTEMA_YYYY-MM-DD.md`.
- Antes de mudanças grandes: `BACKUP_DISCO_D.bat`.

---

*Documento gerado em 11/09/2026 — snapshot após pacote de site piloto e ferramentas de operação do WhatsApp.*
