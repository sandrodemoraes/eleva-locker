# Eleva Cam — DNS em elevalocker.com.br

Decisão: usar o domínio **já registrado** `elevalocker.com.br` com subdomínio
**`elevacam.elevalocker.com.br`**, sem misturar a marca na home do Locker.

| Host | Função |
|------|--------|
| `elevacam.elevalocker.com.br` | Site Eleva Cam (`/` redireciona para `/eleva-cam`) |
| `elevalocker.com.br` | Portal / painel Eleva Locker (separado) |

---

## 1. DNS (Registro.br ou Cloudflare)

Crie um registro **A** (ou CNAME se usar Cloudflare proxy):

| Tipo | Nome / host | Valor | TTL |
|------|-------------|-------|-----|
| A | `elevacam` | **IP público** do PC ou VPS | 300 / Auto |

Resultado: `elevacam.elevalocker.com.br` → esse IP.

### Onde editar

1. Painel do **Registro.br** (ou onde o DNS do `elevalocker.com.br` aponta hoje — hoje está em parking `dns-parking.com`)
2. Se ainda estiver em parking: aponte os **NS** para Cloudflare **ou** edite os registros A no provedor atual
3. Aguarde propagação (minutos a poucas horas)

### Conferir

```bat
nslookup elevacam.elevalocker.com.br
```

Deve mostrar o IP do seu servidor.

---

## 2. Se o provedor NÃO libera 80/443

Unifique (e similares) às vezes só liberam portas **> 10024**.  
Nesse caso **não use Caddy com Let's Encrypt na 80** — use **Cloudflare Tunnel**:

→ **`docs/ELEVA_CAM_CLOUDFLARE_TUNNEL.md`**

Não precisa port forward. O DNS do `elevacam` passa a ser gerenciado pela Cloudflare.

## 2b. Firewall (só se for Caddy + portas 80/443 liberadas)

```powershell
New-NetFirewallRule -DisplayName "HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
```

Se o PC estiver atrás de roteador: **port forward** 80/443 → IP local do PC.

---

## 3. Caddy neste PC (HTTPS + redirect)

Com o Flask já rodando (`INICIAR_SITE.bat` na porta 15000):

1. Instale o [Caddy](https://caddyserver.com/download) no Windows  
2. Em `deploy/eleva-cam/`:

```bat
copy env.example .env
copy Caddyfile Caddyfile.local
```

3. Ajuste `.env` (`ELEVA_CAM_DOMAIN`, `TLS_EMAIL`)  
4. Suba o Caddy (PowerShell na pasta `deploy\eleva-cam`):

```powershell
$env:ELEVA_CAM_DOMAIN="elevacam.elevalocker.com.br"
$env:TLS_EMAIL="sandro.demoraes@gmail.com"
caddy run --config Caddyfile
```

Acesse: **https://elevacam.elevalocker.com.br** → redireciona para `/eleva-cam`.

Arquivos: `deploy/eleva-cam/Caddyfile` (PC) e `Caddyfile.docker` (VPS/compose).

---

## 4. Checklist rápido

- [ ] Registro A `elevacam` → IP do servidor  
- [ ] `nslookup elevacam.elevalocker.com.br` ok  
- [ ] Flask em `:15000`  
- [ ] Caddy 80/443  
- [ ] https://elevacam.elevalocker.com.br abre Eleva Cam  
- [ ] Login do Locker continua em `elevalocker.com.br` (não na home do Cam)

---

## 5. Depois (opcional)

Quando registrar `elevacam.com.br`, aponte o mesmo IP e adicione o host no Caddy — o app não muda.
