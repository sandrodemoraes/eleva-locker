# Deploy na nuvem — Portal público + Painel (ELEVA)

**Para:** Sandro / ELEVA
**Objetivo:** Colocar no ar, com domínio + HTTPS, o **site público** (energia solar / orçamentos)
e o **painel de gestão** — sem depender do PC de casa ficar ligado.

> **Regra de ouro (não quebrar):** a **operação do armário** (ESP32 / totem / abrir porta)
> continua **local / offline-first**. Só vão para a nuvem o **portal público**, a **gestão** e,
> quando você quiser, a **notificação** (WhatsApp). Ver [ARQUITETURA_REDE_FASES.md](ARQUITETURA_REDE_FASES.md).

---

## O que sobe na nuvem

| Container | O quê | Exposto na internet? |
|-----------|-------|----------------------|
| `caddy` | Proxy reverso + HTTPS automático (Let's Encrypt) | Sim (portas 80/443) |
| `web` | App Flask (site + painel) via **gunicorn** | Não — só via Caddy |
| `db` | PostgreSQL com volume persistente | **Não** (rede interna) |

Arquivos: `deploy/docker-compose.prod.yml`, `deploy/Caddyfile`, `deploy/.env.prod.example`.

---

## Pré-requisitos (ações suas, fora do código)

1. **Um VPS Linux** (Ubuntu 22.04+), com **Docker** e **Docker Compose** instalados.
   Basta 1 vCPU / 1–2 GB RAM para começar.
2. **Domínio `elevalocker.com.br`** com acesso ao painel de DNS.
   Crie um registro **A** apontando `elevalocker.com.br` (e opcionalmente `www`) para o **IP do VPS**.
   O HTTPS só emite o certificado depois que o DNS estiver propagado.
3. Portas **80** e **443** liberadas no firewall do VPS.

---

## Passo a passo

```bash
# 1) No VPS, clone o repositório
git clone <url-do-repo> elevalocker && cd elevalocker

# 2) Configure o ambiente de produção
cp deploy/.env.prod.example deploy/.env
nano deploy/.env      # edite SITE_DOMAIN, TLS_EMAIL, SECRET_KEY e senhas

# 3) Suba tudo (build + start em background)
cd deploy
docker compose -f docker-compose.prod.yml --env-file .env up -d --build

# 4) Acompanhe os logs (o Caddy vai emitir o certificado HTTPS)
docker compose -f docker-compose.prod.yml logs -f caddy
```

Pronto: acesse `https://elevalocker.com.br/energia-solar` (site público) e
`https://elevalocker.com.br/login` (painel).

O banco e o admin são criados automaticamente no primeiro start
(usuário admin padrão — **troque a senha no primeiro login**).

### Comandos úteis

```bash
cd deploy
docker compose -f docker-compose.prod.yml ps         # status
docker compose -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.prod.yml down        # parar (mantém dados no volume)
docker compose -f docker-compose.prod.yml up -d --build   # atualizar após git pull
```

### Backup do banco

```bash
cd deploy
docker compose -f docker-compose.prod.yml exec db \
  pg_dump -U eleva elevalocker > backup_$(date +%F).sql
```

---

## Guia específico — Hostinger VPS (provedor escolhido)

Passo a passo do zero, do jeito Hostinger. Plano sugerido: **KVM 1** (1 vCPU / 4 GB) só para o
portal, ou **KVM 2** (2 vCPU / 8 GB) se já quiser rodar o **WhatsApp (Evolution)** junto na nuvem.

### 1) Contratar o VPS

1. Em [hostinger.com.br](https://www.hostinger.com/br/servidor-vps), escolha **KVM 1** ou **KVM 2**.
2. No checkout, em **localização do servidor**, selecione **Brasil — São Paulo**.
   Se "São Paulo" não aparecer (vagas limitadas), tente outro dia/plano — vale insistir pela latência.
3. Em **sistema operacional / template**, escolha **Ubuntu 24.04 com Docker** (ou "Docker").
   Se só houver Ubuntu puro, o guia instala o Docker no passo 4.
4. Pagamento aceita **PIX / boleto**. Anote o **IP do servidor** e a **senha root** (aba VPS do hPanel).

### 2) Registrar e apontar o domínio

1. Registre `elevalocker.com.br` no [registro.br](https://registro.br) (~R$ 40/ano), se ainda não tiver.
2. No DNS do domínio, crie os registros apontando para o **IP do VPS**:

   | Tipo | Nome | Valor |
   |------|------|-------|
   | A | `@` (ou `elevalocker.com.br`) | IP do VPS |
   | A | `www` | IP do VPS |

3. Espere propagar (minutos a algumas horas). Só suba o HTTPS **depois** que o DNS estiver apontando —
   o certificado só é emitido com o domínio já resolvendo para o servidor.

### 3) Liberar o firewall

No hPanel da Hostinger, em **VPS → Firewall**, garanta liberadas as portas **22** (SSH),
**80** e **443** (HTTP/HTTPS). Sem 80/443 o certificado não é emitido.

### 4) Acessar e subir a aplicação

Conecte via SSH (`ssh root@IP_DO_VPS`, senha do hPanel) ou pelo **Browser Terminal** do painel, e rode:

```bash
# (só se o Docker NÃO veio no template)
command -v docker || curl -fsSL https://get.docker.com | sh

# Clonar o projeto
git clone <url-do-repo> elevalocker && cd elevalocker

# Configurar produção
cp deploy/.env.prod.example deploy/.env
nano deploy/.env      # SITE_DOMAIN, TLS_EMAIL, SECRET_KEY, senhas do Postgres

# Subir (build + start)
cd deploy
docker compose -f docker-compose.prod.yml --env-file .env up -d --build

# Acompanhar o HTTPS sendo emitido
docker compose -f docker-compose.prod.yml logs -f caddy
```

### 5) Validar

- Site público: `https://elevalocker.com.br/energia-solar`
- Painel: `https://elevalocker.com.br/login` → **troque a senha do admin no 1º acesso**.

### Atenção Hostinger (2 avisos honestos)

- **Renovação sobe:** o preço promocional (24 meses) quase dobra na renovação — some 24 meses de
  promoção + 12 de renovação e divida por 36 para saber o custo real por mês.
- **Vaga em SP é limitada:** confirme "São Paulo" disponível no checkout antes de fechar.

---

## Alternativa — Self-host num PC próprio (com IP fixo)

Em vez de VPS, dá para hospedar o portal num **PC dedicado** na sua estrutura, aproveitando que você
tem **IP fixo**. Sem custo de servidor, sem esperar vaga. Roda o **mesmo** `docker-compose.prod.yml`.

> ⚠️ Use um **PC separado**, **não** o servidor que controla os armários — essa máquina abre fechaduras
> físicas e não deve ficar exposta na internet. Mantenha a operação (ESP32/totem) isolada e offline-first.

> ⚠️ Lembre-se: a disponibilidade depende da **energia e internet locais**. Se cair, o site cai. Use um
> **nobreak (UPS)** e conexão cabeada.

### Máquina recomendada (não precisa ser potente)

| Item | Mínimo | Recomendado (com WhatsApp) |
|------|--------|-----------------------------|
| CPU | 2 núcleos | 4 núcleos (i3/Ryzen 3 ou melhor) |
| RAM | 4 GB (só o site) | **8 GB** (site + banco + Evolution + Redis) |
| Disco | SSD 60 GB | SSD 120 GB |
| Rede | Ethernet cabeada | Ethernet cabeada |
| SO | Ubuntu Server 24.04 | Ubuntu Server 24.04 |
| Energia | — | **Nobreak (UPS)** |

> Windows com Docker Desktop também funciona, mas para um servidor ligado 24/7 o **Ubuntu** é mais leve e estável.

### Passo a passo

1. **Instale o Ubuntu Server 24.04** no PC e o Docker:
   ```bash
   command -v docker || curl -fsSL https://get.docker.com | sh
   ```
2. **Rede:**
   - Reserve um **IP interno fixo** para o PC no roteador (ex.: `192.168.0.20`).
   - No roteador, **encaminhe (port forward) as portas 80 e 443** para esse IP interno.
   - Aponte o domínio: registro **A** de `elevalocker.com.br` → seu **IP fixo público**.
   - No firewall do Ubuntu, libere as portas:
     ```bash
     sudo ufw allow 22/tcp && sudo ufw allow 80/tcp && sudo ufw allow 443/tcp && sudo ufw enable
     ```
3. **Suba a aplicação** (igual ao VPS):
   ```bash
   git clone <url-do-repo> elevalocker && cd elevalocker
   cp deploy/.env.prod.example deploy/.env
   nano deploy/.env
   cd deploy
   docker compose -f docker-compose.prod.yml --env-file .env up -d --build
   # (com WhatsApp: adicione -f docker-compose.whatsapp.yml)
   ```
4. **Pronto:** o Caddy emite o HTTPS e o site fica em `https://elevalocker.com.br`.

### Se o provedor bloquear a porta 80 (ou você não quiser abrir portas)

Alguns provedores bloqueiam a 80/443 mesmo com IP fixo. Nesse caso, use um **túnel** (ex.: Cloudflare
Tunnel) — o PC faz conexão de saída e publica o site com HTTPS **sem abrir portas**. Me avise que eu
adiciono o serviço do túnel ao pacote de deploy.

---

## Segurança (checklist rápido)

- [x] Banco **não exposto** (sem `ports:` no serviço `db`)
- [x] **HTTPS** automático via Caddy
- [x] Painel atrás de **login**
- [ ] Trocar `SECRET_KEY` e senha do Postgres no `.env` (**obrigatório**)
- [ ] Trocar a senha do admin no primeiro acesso
- [ ] (melhorar depois) rate-limit no formulário público de orçamento
- [ ] (melhorar depois) 2FA no painel admin

---

## WhatsApp na nuvem (Evolution API) — opcional

Sobe o Evolution API junto do portal para enviar as notificações **direto da nuvem**
(fim do problema de "o PC reiniciou e o WhatsApp parou"). Fica em containers separados,
com banco e cache próprios, e **não é exposto na internet**.

### 1) Preencher o `.env`

No `deploy/.env`, ligue o WhatsApp e configure o Evolution:

```env
NOTIF_MODO=producao
NOTIF_WHATSAPP_ATIVO=1
WHATSAPP_PROVIDER=evolution
WHATSAPP_API_URL=http://evolution:8080
WHATSAPP_API_KEY=<uma-chave-forte>        # vira o AUTHENTICATION_API_KEY do Evolution
WHATSAPP_INSTANCIA=eleva-locker

EVOLUTION_SERVER_URL=http://localhost:8080
EVOLUTION_DB_USER=evolution
EVOLUTION_DB_PASSWORD=<senha-forte>
EVOLUTION_DB_NAME=evolution_db
```

### 2) Subir portal + WhatsApp juntos

```bash
cd deploy
docker compose -f docker-compose.prod.yml -f docker-compose.whatsapp.yml --env-file .env up -d --build
```

### 3) Conectar seu número (escanear o QR)

O Evolution só escuta em `127.0.0.1:8080` (seguro). Do **seu PC**, abra um túnel SSH:

```bash
ssh -L 8080:localhost:8080 root@IP_DO_VPS
```

Com o túnel aberto, acesse `http://localhost:8080/manager` no navegador:
1. Faça login com a **`WHATSAPP_API_KEY`**.
2. Crie uma instância com o nome **exatamente igual** a `WHATSAPP_INSTANCIA` (ex.: `eleva-locker`).
3. **Escaneie o QR** com o WhatsApp do número que vai enviar as mensagens.

Pronto: o painel do ELEVA (`/notificacoes`) mostra o status "conectado" e passa a enviar de verdade.

> Se preferir não usar túnel SSH, dá para expor o manager num subdomínio (ex.: `evo.elevalocker.com.br`)
> via Caddy — mas o túnel é mais seguro e não requer editar o `Caddyfile`.

---

## Melhorar depois (fases seguintes)

1. **Marca própria:** logo, cores e fotos dos seus trabalhos elétricos no site público.
2. **Área do cliente + acesso ao locker** pelo site.
3. **Câmeras Intelbras** ao vivo (fase futura).

> Enquanto isso, os **armários** continuam operando **localmente** (Modelo A) e podem
> sincronizar com a nuvem quando online — sem risco de uma queda de internet trancar a porta.
