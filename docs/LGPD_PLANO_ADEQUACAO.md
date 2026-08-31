# ELEVA LOCKER — Plano de adequação LGPD (sem interrupção)

**Data:** 30/08/2026  
**Objetivo:** Adequar o sistema à LGPD (Lei 13.709/2018) **sem parar** totem, encomendas, WhatsApp, ESP32 ou painel admin.  
**Referência de baseline:** [ESTADO_SISTEMA_2026-08-29.md](ESTADO_SISTEMA_2026-08-29.md)

---

## Princípio central: evolução aditiva

| Regra | O que significa na prática |
|-------|----------------------------|
| **Nada de “big bang”** | Cada fase entra por feature flag ou tela nova; o fluxo atual continua igual até você ativar |
| **Backup antes de cada fase** | `BACKUP_DISCO_D.bat` + anotar commit Git |
| **Totem e WhatsApp intocados na Fase 1–2** | Só documentação e telas informativas; zero mudança em `/totem/2` |
| **Banco: só ADD COLUMN** | Novas colunas nullable; nunca apagar coluna/tabela em produção sem migração planejada |
| **Testar na bancada, depois Matriz** | Mesmo padrão que usamos no totem celular |
| **Rollback simples** | Desligar flag no `.env` ou reverter commit |

---

## Mapa de dados pessoais hoje (inventário)

O que o sistema **já trata** como dado pessoal:

| Onde | Dados | Finalidade | Base legal (sugestão LGPD) |
|------|-------|------------|----------------------------|
| `usuarios` | nome, e-mail, telefone, senha | Login operadores | Execução de contrato / legítimo interesse |
| `empresas` | CNPJ, responsável, e-mail, telefone, endereço | Cliente B2B | Contrato |
| `encomendas` | cliente, telefone, e-mail, código | Entrega e retirada | Execução do serviço |
| `notificacoes` | destinatário (tel/e-mail), mensagem | WhatsApp/e-mail/SMS | Consentimento ou legítimo interesse* |
| `totem_ajuda_pedidos` | armário, IP origem, horário | Ajuda portaria | Legítimo interesse / segurança |
| `logs` | usuário, ação, data | Auditoria | Legítimo interesse / obrigação |
| Totem depósito | nome morador, telefone | Cadastro encomenda | Execução do serviço |
| WhatsApp (Evolution) | números, conteúdo | Notificar morador | Informar entrega |

\* Para **marketing** futuro seria consentimento; para **“sua encomenda chegou”** costuma ser execução do serviço — validar com advogado/DPO.

**O que NÃO mexer sem plano:** `ESP32_TOKEN`, fluxo de retirada por código, Evolution API, `TOTEM_ARMARIO_ID=2`.

---

## Visão das fases (cronograma técnico, não calendário)

```
Fase 0 ──► Preparação (1 dia, zero código crítico)
Fase 1 ──► Documentação e transparência (sem impacto operacional)
Fase 2 ──► Consentimento e registro (aditivo, flags desligadas)
Fase 3 ──► Direitos do titular (exportar / anonimizar / excluir)
Fase 4 ──► Retenção automática e mascaramento
Fase 5 ──► Auditoria LGPD e hardening (opcional avançado)
```

Cada fase **só começa** quando a anterior estiver estável e com backup feito.

---

## Fase 0 — Preparação (hoje / amanhã)

**Impacto no sistema:** nenhum.

### Passo a passo

1. **Backup completo**
   ```cmd
   cd C:\ElevaLocker
   BACKUP_DISCO_D.bat
   ```

2. **Registrar baseline**
   - Anotar commit: `git log -1 --oneline`
   - Ler `docs/ESTADO_SISTEMA_2026-08-29.md`

3. **Definir responsáveis**
   | Papel | Quem (preencher) |
   |-------|------------------|
   | Controlador | ELEVA / condomínio |
   | Operador técnico | Sandro |
   | Contato titular | e-mail/WhatsApp portaria |

4. **Checklist “não quebrar”** (rodar antes e depois de cada fase)
   ```cmd
   INICIAR.bat                    REM servidor sobe
   TESTAR_TOTEM.bat               REM rotas totem OK
   py tools\diagnostico_env.py    REM .env OK
   docker ps                      REM Evolution Up
   ```
   - Totem `/totem/2` → retirar + ajuda + depósito
   - Painel → encomenda teste + sininho ajuda
   - ESP32 → heartbeat verde (se placa ligada)

5. **Criar branch LGPD** (quando for codar)
   ```cmd
   git checkout -b cursor/lgpd-adequacao-c05c
   ```

---

## Fase 1 — Documentação e transparência

**Impacto:** páginas estáticas novas; **totem e painel iguais**.

### O que implementar

| Item | Onde | Risco |
|------|------|-------|
| Política de Privacidade | `/privacidade` (pública) | Zero |
| Termos de Uso do totem | `/termos` ou rodapé totem | Baixo — só link |
| Página “Seus dados” (resumo) | `/lgpd` (pública, sem login) | Zero |
| Registro de operação de tratamento (ROPA) | `docs/LGPD_ROPA.md` (interno) | Zero |

### Passo a passo

1. Redigir **Política de Privacidade** (modelo abaixo — revisar com advogado):
   - Quem é o controlador (ELEVA / Matriz)
   - Quais dados coletamos (tabela inventário acima)
   - Por quanto tempo guardamos
   - Com quem compartilhamos (Evolution/WhatsApp, hospedagem)
   - Direitos: acesso, correção, exclusão, portabilidade
   - Canal de contato: e-mail + telefone portaria

2. Publicar rotas **sem alterar** rotas existentes:
   - `GET /privacidade`
   - `GET /termos`
   - `GET /lgpd`

3. **Totem:** adicionar link pequeno no rodapé:
   - “Privacidade” → `/privacidade`
   - **Não** exigir aceite ainda (Fase 2)

4. **Painel admin:** link em Configurações → “Documentos LGPD”

5. **Teste regressão:** checklist Fase 0

### `.env` (Fase 1 — opcional)

```env
LGPD_AVISO_ATIVO=0
LGPD_POLITICA_VERSAO=2026-08-30
LGPD_CONTATO_EMAIL=privacidade@elevalocker.com.br
LGPD_CONTATO_TELEFONE=48991570639
```

---

## Fase 2 — Consentimento e registro (aditivo)

**Impacto:** novas colunas e telas; **com flags desligadas = comportamento idêntico ao hoje**.

### Banco (migração segura)

Novas colunas **nullable** — não quebram inserts atuais:

```sql
-- usuarios / moradores vinculados
lgpd_consentimento_em DATETIME
lgpd_consentimento_versao TEXT
lgpd_consentimento_ip TEXT

-- encomendas (morador no depósito totem)
lgpd_base_legal TEXT DEFAULT 'execucao_servico'
```

Nova tabela (não mexe nas existentes):

```sql
lgpd_consentimentos (
  id, titular_tipo, titular_id, telefone, email,
  finalidade, versao_politica, ip, user_agent, criado_em
)
```

### Funcionalidades

| Feature | Flag `.env` | Comportamento |
|---------|-------------|---------------|
| Checkbox no cadastro usuário | `LGPD_CONSENTIMENTO_USUARIO=0` | Off = cadastro como hoje |
| Aviso no totem depósito | `LGPD_AVISO_TOTEM=0` | Off = depósito como hoje |
| Log de consentimento | sempre grava se houver aceite | — |

### Passo a passo implementação

1. Migração em `database.py` (`adicionar_coluna` + `CREATE TABLE IF NOT EXISTS`)
2. Serviço `lgpd_consentimento_service.py` — só grava; não bloqueia
3. Tela admin usuários: checkbox + texto (oculto se flag=0)
4. Totem depósito: linha “Ao depositar, você concorda…” **só se** `LGPD_AVISO_TOTEM=1`
5. Deploy com **todas flags = 0**
6. Testar totem + encomendas + WhatsApp
7. **Ativar gradualmente:** primeiro admin, depois totem

### O que NÃO fazer na Fase 2

- Não bloquear retirada por código
- Não exigir login morador no totem
- Não desligar WhatsApp

---

## Fase 3 — Direitos do titular (ART. 18 LGPD)

**Impacto:** novas ações no painel admin; dados existentes intactos até solicitação.

### Funcionalidades (menu Usuários / Encomendas / novo “LGPD”)

| Direito | Ação no sistema | Efeito |
|---------|-----------------|--------|
| Acesso | Exportar JSON/PDF dos dados do titular | Leitura only |
| Correção | Já existe em CRUD usuários | — |
| Exclusão | “Anonimizar titular” | Substitui nome/tel/e-mail por `*** ANONIMIZADO ***`; mantém encomenda para estatística |
| Portabilidade | Export CSV | Download |
| Oposição | Flag `marketing_opt_out` | Só marketing futuro |

### Passo a passo

1. `LGPD_TITULAR_ATIVO=0` no `.env`
2. Rota admin `POST /lgpd/anonimizar/<tipo>/<id>` — só admin
3. **Anonimizar ≠ apagar encomenda** (evita quebrar relatórios e portas)
4. Registrar em `logs` + nova tabela `lgpd_solicitacoes`
5. Procedimento manual documentado em `docs/LGPD_PROCEDIMENTO_TITULAR.md`:
   - Morador pede via portaria → operador executa no painel
6. Testar: anonimizar usuário teste; totem e WhatsApp continuam normais

### WhatsApp / Evolution

- Exclusão no ELEVA **não apaga** histórico no WhatsApp do celular — documentar na política
- Número anonimizado no banco → próximas notificações não enviam (validação telefone)

---

## Fase 4 — Retenção e minimização

**Impacto:** job noturno; **não apaga** dados ativos de encomendas em curso.

### Regras sugeridas (configuráveis `.env`)

```env
LGPD_RETENCAO_ENCOMENDA_DIAS=365      # após retirada
LGPD_RETENCAO_LOG_DIAS=180
LGPD_RETENCAO_AJUDA_TOTEM_DIAS=90
LGPD_RETENCAO_NOTIFICACAO_DIAS=365
LGPD_JOB_ATIVO=0                       # 0 = não roda; 1 = roda 1x/dia
```

### Passo a passo

1. Script `tools/lgpd_retencao.py` — **dry-run** por padrão (`--simular`)
2. Só anonimiza registros **já retirados / atendidos / antigos**
3. Agendar via Task Scheduler Windows (3h da manhã) — **depois** de validar simulação
4. Log do job em `logs/lgpd_retencao.log`
5. Nunca rodar em produção sem backup D:

### Mascaramento na UI (sem apagar banco)

- Listagens: telefone `(48) 991**-**39` para perfil Operador
- Admin vê completo
- Flag: `LGPD_MASCARAR_TELEFONE=0` → quando 1, ativa mascaramento

---

## Fase 5 — Auditoria e segurança (complementar LGPD)

**Impacto:** baixo se incremental.

| Item | Prioridade | Interrompe? |
|------|------------|-------------|
| HTTPS (reverse proxy) | Alta prod | Não — paralelo |
| Senha forte / expiração | Média | Não |
| Log imutável (append-only) | Média | Não |
| DPO / encarregado contato fixo | Organizacional | Não |
| DPIA simplificada | Documento | Não |
| Acordo operador (Evolution) | Contrato | Não |

---

## Ordem recomendada de execução (resumo)

| # | Ação | Para quando | Para o sistema |
|---|------|-------------|----------------|
| 1 | Backup D: + checklist | Agora | — |
| 2 | ROPA + Política Privacidade (doc) | Dia 1 | Zero impacto |
| 3 | Páginas `/privacidade`, `/termos` | Dia 1–2 | Só links novos |
| 4 | Migração colunas LGPD (flags off) | Dia 2–3 | Zero impacto |
| 5 | Consentimento admin (flag off) | Dia 3–4 | Zero até ligar flag |
| 6 | Aviso totem (flag off) | Dia 4–5 | Zero até ligar flag |
| 7 | Exportar / anonimizar titular | Semana 2 | Só admin |
| 8 | Retenção simulada | Semana 2–3 | Zero até agendar |
| 9 | Mascaramento tel | Semana 3 | Visual only |
| 10 | Ativar flags uma a uma | Conforme validação | Controlado |

---

## Checklist de regressão (usar sempre)

Após **qualquer** deploy LGPD:

- [ ] `INICIAR.bat` sobe sem erro
- [ ] `http://192.168.16.130:15000/totem/2` abre
- [ ] Retirada com código 6 dígitos funciona
- [ ] Depósito totem funciona
- [ ] **Preciso de ajuda** → WhatsApp + sininho
- [ ] **Atendido** no painel funciona
- [ ] Encomenda nova + notificação WhatsApp
- [ ] ESP32 heartbeat (se hardware on)
- [ ] `docker ps` — Evolution Up
- [ ] `BACKUP_DISCO_D.bat` OK

---

## Modelo mínimo — Política de Privacidade (rascunho)

> **Controlador:** [Razão social ELEVA] — Matriz ELEVA, Florianópolis/SC  
> **Contato:** [e-mail] | [telefone portaria]  
>  
> **Dados tratados:** nome, telefone, e-mail de moradores e operadores; dados de encomenda; logs de acesso ao armário; IP no pedido de ajuda do totem.  
>  
> **Finalidades:** entrega e retirada de encomendas; notificação por WhatsApp; segurança do condomínio; suporte técnico.  
>  
> **Compartilhamento:** API WhatsApp (Evolution) para envio de mensagens; não vendemos dados.  
>  
> **Retenção:** encomendas retiradas — até [X] meses; logs — [X] meses (ver `.env` Fase 4).  
>  
> **Seus direitos:** acesso, correção, exclusão/anonimização — solicite à portaria ou [contato].  
>  
> **Atualização:** versão [data] — mudanças relevantes serão avisadas no totem/painel.

*(Revisar com advogado antes de publicar.)*

---

## Variáveis `.env` LGPD (consolidado futuro)

```env
# --- LGPD (Fase 1+) — tudo 0 até ativar deliberately ---
LGPD_AVISO_ATIVO=0
LGPD_POLITICA_VERSAO=2026-08-30
LGPD_CONTATO_EMAIL=
LGPD_CONTATO_TELEFONE=

LGPD_CONSENTIMENTO_USUARIO=0
LGPD_AVISO_TOTEM=0
LGPD_TITULAR_ATIVO=0
LGPD_MASCARAR_TELEFONE=0
LGPD_JOB_ATIVO=0

LGPD_RETENCAO_ENCOMENDA_DIAS=365
LGPD_RETENCAO_LOG_DIAS=180
LGPD_RETENCAO_AJUDA_TOTEM_DIAS=90
LGPD_RETENCAO_NOTIFICACAO_DIAS=365
```

---

## Próximo passo concreto (amanhã com Sandro)

1. Ler este plano e ajustar prazos internos  
2. Preencher controlador + contato titular  
3. Rodar **Fase 0** (backup + checklist)  
4. Decidir: começamos **Fase 1** (só páginas `/privacidade` + doc ROPA)?  

Quando confirmar, implementamos **Fase 1** na branch `cursor/lgpd-adequacao-c05c` sem tocar em totem/WhatsApp/ESP32.

---

## Documentos relacionados

| Arquivo | Conteúdo |
|---------|----------|
| [ESTADO_SISTEMA_2026-08-29.md](ESTADO_SISTEMA_2026-08-29.md) | Snapshot antes da LGPD |
| [PROJETO.md](PROJETO.md) | Visão comercial e roadmap |
| `docs/LGPD_ROPA.md` | *(criar na Fase 1)* Registro de tratamento |
| `docs/LGPD_PROCEDIMENTO_TITULAR.md` | *(criar na Fase 3)* Atendimento pedidos morador |

---

*Plano elaborado para evolução incremental — compatível com operação 24h do totem Matriz (id 2) e WhatsApp Evolution.*
