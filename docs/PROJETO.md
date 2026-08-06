# ELEVA LOCKER — Documento Mestre do Sistema

> Sistema inteligente de armários para recebimento e retirada de encomendas.
> Transformação de protótipo operacional em plataforma comercial escalável.

---

## 1. Objetivo

O **ELEVA LOCKER** resolve o problema de **última milha de entregas** em condomínios, empresas, shoppings, hotéis e pontos comerciais. O morador, hóspede ou funcionário recebe a encomenda em um compartimento inteligente e retira quando quiser, com código ou QR Code, sem depender de portaria ou horário fixo.

### Proposta de valor

| Público | Benefício |
|---------|-----------|
| **Condomínio / síndico** | Menos conflito na portaria, rastreabilidade, segurança |
| **Morador / cliente final** | Retirada 24h, notificação instantânea |
| **Transportadora / e-commerce** | Prova de entrega, menos reentrega |
| **Operador ELEVA** | Painel centralizado, múltiplos armários, relatórios |
| **Investidor / franqueado** | Modelo recorrente (SaaS + hardware + serviço) |

### Visão comercial

Operar como **plataforma B2B2C**:

1. **ELEVA** vende/licencia o sistema para **empresas parceiras** (condomínios, administradoras, shoppings).
2. Cada **empresa** gerencia seus **armários**, **operadores** e **encomendas**.
3. O **cliente final** interage via SMS/WhatsApp/app para retirar a encomenda.

---

## 2. Filosofia do Projeto

| Princípio | Significado prático |
|-----------|---------------------|
| **Offline-first** | Armário funciona sem internet; sincroniza quando reconectar |
| **Simplicidade operacional** | Operador deposita em 3 cliques; morador retira com código |
| **Modularidade** | Cada módulo (armário, encomenda, ESP32) é independente |
| **Multi-empresa** | Uma instalação ELEVA atende N clientes (empresas) |
| **Auditável** | Toda abertura de compartimento gera log imutável |
| **Comercial desde o dia 1** | Planos, limites e faturamento fazem parte da arquitetura |

---

## 3. Arquitetura

### 3.1 Visão em camadas

```
┌─────────────────────────────────────────────────────────────┐
│  CAMADA DE APRESENTAÇÃO                                     │
│  Admin Web (Flask/Jinja) │ App Morador │ Totem Armário      │
├─────────────────────────────────────────────────────────────┤
│  CAMADA DE API                                              │
│  REST/JSON │ Webhooks │ WebSocket (status ESP32)            │
├─────────────────────────────────────────────────────────────┤
│  CAMADA DE NEGÓCIO (Services)                               │
│  Encomenda │ Armário │ Notificação │ Faturamento │ Auth     │
├─────────────────────────────────────────────────────────────┤
│  CAMADA DE DADOS (Repositories)                             │
│  SQLite (MVP) → PostgreSQL (produção multi-site)            │
├─────────────────────────────────────────────────────────────┤
│  CAMADA IoT                                                 │
│  ESP32 → Relés → Fechaduras │ Sensores porta aberta         │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Stack atual (MVP)

| Componente | Tecnologia |
|------------|------------|
| Backend | Python 3 + Flask |
| Banco | SQLite (`database/elevalocker.db`) |
| Frontend admin | HTML + CSS + JavaScript (Jinja2) |
| Hardware | ESP32 (Wi-Fi, controle de relés) |
| Backup | Rotação automática (5 cópias) |
| Porta | 15000 |

### 3.3 Stack alvo (produção)

| Componente | Tecnologia sugerida |
|------------|---------------------|
| Banco | PostgreSQL |
| Fila de mensagens | Redis + Celery (notificações assíncronas) |
| Cache | Redis |
| Deploy | Docker + Nginx |
| Monitoramento | Prometheus + Grafana |
| Pagamentos | Stripe / Asaas / Mercado Pago |
| WhatsApp | API oficial ou Evolution API |

---

## 4. Estrutura do Projeto

### 4.1 Estado atual

```
ELEVALOCKER/
├── app.py                    ✅ Entry point
├── database.py               ✅ Schema + seed admin
├── config.py                 ⚠️  Vazio
├── esp32.py                  ⚠️  Vazio
│
├── routes/
│   ├── auth.py               ✅ Login/logout
│   ├── dashboard.py          ✅ Painel (dados estáticos)
│   ├── usuarios.py           ✅ CRUD completo
│   └── empresas.py           ✅ CRUD (parcial JSON)
│
├── services/
│   ├── usuario_service.py    ✅ Com validações
│   ├── empresa_service.py    ✅ CRUD direto (sem repository)
│   └── backup/               ✅ Backup inteligente com hash
│
├── repositories/
│   ├── base_repository.py    ✅ Conexão centralizada
│   ├── usuario_repository.py   ✅ Padrão repository
│   ├── empresa_repository.py   ❌ Vazio
│   └── armario_repository.py   ❌ Vazio
│
├── models/
│   └── usuario.py            ⚠️  Dataclass incompleta
│
├── templates/                ✅ Layout moderno + CRUD
├── static/                   ✅ CSS + JS empresas
└── docs/PROJETO.md           ✅ Este documento
```

### 4.2 Estrutura alvo

```
ELEVALOCKER/
├── routes/
│   ├── armarios.py
│   ├── compartimentos.py
│   ├── encomendas.py
│   ├── esp32.py
│   ├── logs.py
│   ├── relatorios.py
│   ├── planos.py              # Comercial
│   ├── contratos.py           # Comercial
│   └── api/v1/                # API REST para app/totem
│
├── services/
│   ├── encomenda_service.py
│   ├── armario_service.py
│   ├── esp32_service.py
│   ├── notificacao_service.py # SMS, e-mail, WhatsApp
│   ├── faturamento_service.py
│   └── codigo_service.py      # Geração de códigos de retirada
│
├── middleware/
│   ├── auth_required.py
│   ├── perfil_required.py     # Admin, Operador, Cliente
│   └── empresa_scope.py       # Multi-tenant
│
└── schemas/                   # Validação Pydantic (futuro)
```

---

## 5. Banco de Dados

### 5.1 Modelo atual (implementado)

| Tabela | Status | Observação |
|--------|--------|------------|
| `usuarios` | ✅ Ativo | Perfis: Administrador, Operador |
| `empresas` | ✅ Ativo | Clientes B2B |
| `armarios` | ⚠️ Schema only | Sem CRUD |
| `compartimentos` | ⚠️ Schema only | Sem CRUD |
| `esp32` | ⚠️ Schema only | Sem integração |
| `encomendas` | ⚠️ Schema only | Coração do sistema |
| `logs` | ⚠️ Schema only | Auditoria |

### 5.2 Modelo comercial expandido (a implementar)

```sql
-- Vínculo empresa ↔ armário (multi-tenant)
ALTER TABLE armarios ADD COLUMN empresa_id INTEGER REFERENCES empresas(id);

-- Planos comerciais
CREATE TABLE planos (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,              -- Básico, Profissional, Enterprise
    preco_mensal REAL NOT NULL,
    max_armarios INTEGER,
    max_compartimentos INTEGER,
    max_encomendas_mes INTEGER,
    inclui_whatsapp INTEGER DEFAULT 0,
    inclui_relatorios INTEGER DEFAULT 1
);

-- Contrato empresa ↔ plano
CREATE TABLE contratos (
    id INTEGER PRIMARY KEY,
    empresa_id INTEGER REFERENCES empresas(id),
    plano_id INTEGER REFERENCES planos(id),
    data_inicio DATE,
    data_fim DATE,
    status TEXT DEFAULT 'ativo',     -- ativo, suspenso, cancelado
    valor_mensal REAL
);

-- Faturamento
CREATE TABLE faturas (
    id INTEGER PRIMARY KEY,
    contrato_id INTEGER,
    referencia TEXT,                 -- 2026-08
    valor REAL,
    status TEXT,                     -- pendente, pago, vencido
    data_vencimento DATE,
    data_pagamento DATE
);

-- Destinatários (moradores/clientes finais)
CREATE TABLE destinatarios (
    id INTEGER PRIMARY KEY,
    empresa_id INTEGER,
    nome TEXT,
    telefone TEXT,
    email TEXT,
    apartamento TEXT,
    bloco TEXT,
    codigo_acesso TEXT               -- Código permanente opcional
);

-- Encomendas expandidas
ALTER TABLE encomendas ADD COLUMN empresa_id INTEGER;
ALTER TABLE encomendas ADD COLUMN destinatario_id INTEGER;
ALTER TABLE encomendas ADD COLUMN codigo_retirada TEXT UNIQUE;
ALTER TABLE encomendas ADD COLUMN codigo_qr TEXT;
ALTER TABLE encomendas ADD COLUMN operador_id INTEGER;
ALTER TABLE encomendas ADD COLUMN transportadora TEXT;
ALTER TABLE encomendas ADD COLUMN notificado_em DATETIME;
ALTER TABLE encomendas ADD COLUMN expira_em DATETIME;

-- Status padronizados
-- encomendas.status: aguardando_retirada | retirada | expirada | devolvida
-- compartimentos.status: livre | ocupado | manutencao | reservado
-- armarios.status: ativo | inativo | manutencao
-- esp32.status: online | offline | erro
```

### 5.3 Diagrama de relacionamentos

```
empresas ──┬── armarios ──┬── compartimentos ──┬── encomendas
           │              │                     │
           │              └── esp32              └── logs
           │
           ├── contratos ── planos
           ├── faturas
           ├── destinatarios
           └── usuarios (operadores vinculados)
```

---

## 6. Comunicação ESP32

### 6.1 Fluxo operacional

```
Operador deposita encomenda
        │
        ▼
Sistema gera código + abre compartimento
        │
        ▼
POST http://{esp32_ip}/abrir?rele=3&token={secret}
        │
        ▼
ESP32 aciona relé → fechadura abre
        │
        ▼
Sensor confirma porta aberta/fechada
        │
        ▼
ESP32 POST /api/esp32/evento → { compartimento, acao, timestamp }
        │
        ▼
Sistema registra log + atualiza status
```

### 6.2 Protocolo sugerido (esp32.py)

| Endpoint ESP32 | Método | Função |
|----------------|--------|--------|
| `/abrir/{rele}` | GET | Aciona relé por N segundos |
| `/status` | GET | Retorna IP, MAC, relés ativos |
| `/heartbeat` | POST | Ping a cada 30s |

| Endpoint Servidor | Método | Função |
|-------------------|--------|--------|
| `/api/esp32/registrar` | POST | Cadastra ESP32 no armário |
| `/api/esp32/heartbeat` | POST | Atualiza status online |
| `/api/esp32/evento` | POST | Porta abriu/fechou |
| `/api/compartimento/abrir` | POST | Abre via service layer |

### 6.3 Modo offline

1. ESP32 mantém fila local de eventos (SPIFFS).
2. Ao reconectar, sincroniza com servidor.
3. Códigos de retirada válidos são cacheados no ESP32 (últimas 24h).
4. Retirada offline: ESP32 valida código localmente e abre compartimento.

---

## 7. Funcionamento Offline

| Cenário | Comportamento |
|---------|---------------|
| Internet cai | ESP32 continua abrindo com códigos em cache |
| Servidor cai | ESP32 opera autonomamente; fila de sync |
| Energia cai | UPS no armário; ESP32 retoma ao religar |
| Sincronização | Job periódico reconcilia encomendas pendentes |

---

## 8. Segurança

### 8.1 Implementado

- Senhas com hash (`werkzeug.security`)
- Sessão Flask com `secret_key`
- Verificação de sessão nas rotas protegidas

### 8.2 A implementar

| Item | Prioridade |
|------|------------|
| Middleware centralizado `@login_required` | Alta |
| Controle por perfil (`@perfil("Administrador")`) | Alta |
| Escopo por empresa (multi-tenant) | Alta |
| Token API para ESP32 e totem | Alta |
| Rate limiting no login | Média |
| HTTPS obrigatório em produção | Alta |
| Rotação de `secret_key` via env | Média |
| Auditoria imutável de logs | Média |
| Códigos de retirada com expiração (TTL) | Alta |
| LGPD: consentimento e exclusão de dados | Média |

---

## 9. Módulos

### 9.1 Módulos operacionais

#### M1 — Autenticação e usuários ✅
- Login, logout, perfis, CRUD de usuários
- **Próximo:** vincular usuário à empresa; recuperação de senha

#### M2 — Empresas (clientes B2B) ✅ parcial
- CRUD de empresas com CNPJ
- **Próximo:** usar `EmpresaRepository`; dashboard por empresa

#### M3 — Armários 📦
- Cadastro: nome, endereço, empresa, status
- Mapa visual do armário (grid de compartimentos)
- **KPI:** armários ativos, taxa de ocupação

#### M4 — Compartimentos 📬
- Numeração, relé, ESP32 vinculado
- Status: livre / ocupado / manutenção
- Tamanho (P, M, G) para precificação futura

#### M5 — Encomendas 📦 (CRÍTICO)
Fluxo completo:

```
1. DEPÓSITO (Operador)
   → Seleciona compartimento livre
   → Informa destinatário (nome, apto, telefone)
   → Sistema gera código de 6 dígitos + QR
   → Abre compartimento via ESP32
   → Envia notificação (SMS/WhatsApp/e-mail)
   → Status: aguardando_retirada

2. RETIRADA (Morador)
   → Digita código no totem ou app
   → Sistema valida código + compartimento
   → Abre compartimento
   → Status: retirada
   → Registra log

3. EXPIRAÇÃO (Automático)
   → Job diário: encomendas > 72h
   → Notifica operador
   → Status: expirada → devolução
```

#### M6 — ESP32 🤖
- Cadastro, monitoramento online/offline
- Comando de abertura remota
- Log de eventos de hardware

#### M7 — Notificações 📱
- Template: "Sua encomenda chegou! Código: {codigo}. Retire em {local}."
- Canais: SMS (Twilio/Zenvia), WhatsApp, e-mail, push (futuro)

#### M8 — Logs e auditoria 📋
- Toda ação: quem, quando, o quê, qual compartimento
- Exportação CSV/PDF para síndico

#### M9 — Relatórios 📊
- Encomendas por período / armário / empresa
- Taxa de retirada em 24h / 48h / 72h
- Compartimentos mais usados
- Receita por empresa (comercial)

### 9.2 Módulos comerciais

#### C1 — Planos e precificação 💰

| Plano | Preço/mês | Armários | Compartimentos | Encomendas/mês |
|-------|-----------|----------|----------------|----------------|
| **Starter** | R$ 199 | 1 | 20 | 500 |
| **Profissional** | R$ 499 | 5 | 100 | 2.000 |
| **Enterprise** | R$ 1.499 | Ilimitado | Ilimitado | Ilimitado |

Add-ons: WhatsApp (+R$ 99/mês), hardware locação (+R$ 150/armário).

#### C2 — Contratos
- Vínculo empresa ↔ plano com vigência
- Renovação automática
- Suspensão por inadimplência

#### C3 — Faturamento
- Geração automática de faturas mensais
- Integração gateway de pagamento
- Dashboard financeiro (MRR, churn, inadimplência)

#### C4 — Onboarding de clientes
1. Cadastro da empresa
2. Escolha do plano
3. Configuração do primeiro armário
4. Treinamento do operador (vídeo + checklist)
5. Go-live

#### C5 — Portal do cliente (futuro)
- Síndico/administradora acessa seus dados
- Relatórios, faturas, suporte

---

## 10. Roadmap

### Fase 1 — Fundação operacional (atual → 4 semanas)

| # | Entrega | Prioridade |
|---|---------|------------|
| 1.1 | Padronizar services/repositories (empresa → repository) | Alta |
| 1.2 | Middleware `@login_required` + `@perfil_required` | Alta |
| 1.3 | CRUD Armários + Compartimentos | Alta |
| 1.4 | CRUD Encomendas (depósito + retirada manual) | **Crítica** |
| 1.5 | Dashboard com dados reais (contadores SQL) | Alta |
| 1.6 | Logs automáticos em cada ação | Alta |
| 1.7 | `requirements.txt` + variáveis de ambiente | Alta |

### Fase 2 — IoT e automação

| # | Entrega |
|---|---------|
| 2.1 | API REST `/api/v1/` para totem e ESP32 |
| 2.2 | Implementar `esp32.py` (cliente HTTP) |
| 2.3 | Heartbeat e status online/offline |
| 2.4 | Abertura remota de compartimento |
| 2.5 | Modo offline com cache de códigos |

### Fase 3 — Notificações e experiência

| # | Entrega |
|---|---------|
| 3.1 | Serviço de notificação (SMS + e-mail) |
| 3.2 | Integração WhatsApp |
| 3.3 | QR Code para retirada |
| 3.4 | Totem web (tela fullscreen no armário) |
| 3.5 | App morador (PWA ou React Native) |

### Fase 4 — Comercialização

| # | Entrega |
|---|---------|
| 4.1 | Tabelas planos, contratos, faturas |
| 4.2 | Limites por plano (middleware) |
| 4.3 | Geração automática de faturas |
| 4.4 | Gateway de pagamento |
| 4.5 | Portal self-service para empresas |
| 4.6 | Landing page + CRM básico |

### Fase 5 — Escala

| # | Entrega |
|---|---------|
| 5.1 | Migrar SQLite → PostgreSQL |
| 5.2 | Multi-site (franquias) |
| 5.3 | API pública para integrações (Mercado Livre, Shopee) |
| 5.4 | BI avançado e machine learning (previsão de ocupação) |

---

## 11. Histórico de Desenvolvimento

| Versão | Data | Descrição |
|--------|------|-----------|
| v0.1.0 | — | Estrutura inicial, schema DB, layout |
| v0.2.0 | — | Auth, usuários, empresas, backup, layout moderno |
| v0.3.0 | — | Documento mestre + roadmap comercial (este doc) |

---

## 12. Ideias Futuras

- **Integração correios/transportadoras:** API de rastreio automático
- **Reconhecimento facial** no totem (retirada biométrica)
- **Armário refrigerado** para delivery de comida
- **Marketplace de espaço:** condomínio aluga compartimento para vizinhos
- **White-label:** parceiro revende com sua marca
- **Blockchain** para cadeia de custódia de encomendas de alto valor
- **Assistente IA:** chatbot para morador consultar status da encomenda
- **Gamificação:** pontos para retirada rápida (< 24h)

---

## Apêndice A — Fluxo comercial completo

```
PROSPECT → Demo → Proposta → Contrato → Onboarding → Go-live → Suporte → Renovação
   │          │        │          │           │           │         │          │
 Landing   Painel    PDF/      Plano +    Armário +    Operação   Tickets   Fatura
  page     demo      e-mail    assinatura  treinamento   diária    SLA      mensal
```

## Apêndice B — Perfis de usuário

| Perfil | Permissões |
|--------|------------|
| **Super Admin** | Tudo; gerencia empresas e planos |
| **Administrador** | Empresa inteira; usuários, armários, relatórios |
| **Operador** | Depositar/retirar encomendas; ver armários |
| **Cliente/Morador** | Apenas retirar suas encomendas (app/totem) |
| **Financeiro** | Faturas, contratos, relatórios financeiros |

## Apêndice C — KPIs do negócio

| KPI | Meta inicial |
|-----|--------------|
| Encomendas/mês/armário | > 200 |
| Taxa de retirada em 48h | > 85% |
| Uptime ESP32 | > 99% |
| NPS moradores | > 70 |
| MRR (receita recorrente) | Crescimento 10%/mês |
| Churn empresas | < 5%/trimestre |

---

*Documento gerado como blueprint para evolução do ELEVA LOCKER de protótipo para plataforma comercial.*
