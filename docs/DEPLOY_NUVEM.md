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

## Segurança (checklist rápido)

- [x] Banco **não exposto** (sem `ports:` no serviço `db`)
- [x] **HTTPS** automático via Caddy
- [x] Painel atrás de **login**
- [ ] Trocar `SECRET_KEY` e senha do Postgres no `.env` (**obrigatório**)
- [ ] Trocar a senha do admin no primeiro acesso
- [ ] (melhorar depois) rate-limit no formulário público de orçamento
- [ ] (melhorar depois) 2FA no painel admin

---

## Melhorar depois (fases seguintes)

1. **WhatsApp na nuvem:** subir o Evolution API junto (fim do problema de reboot do PC).
   Basta ligar `NOTIF_WHATSAPP_ATIVO=1` e apontar `WHATSAPP_API_URL/KEY/INSTANCIA` no `.env`.
2. **Marca própria:** logo, cores e fotos dos seus trabalhos elétricos no site público.
3. **Área do cliente + acesso ao locker** pelo site.
4. **Câmeras Intelbras** ao vivo (fase futura).

> Enquanto isso, os **armários** continuam operando **localmente** (Modelo A) e podem
> sincronizar com a nuvem quando online — sem risco de uma queda de internet trancar a porta.
