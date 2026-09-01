# Domínio público — passo a passo (Matriz ELEVA)

**Para:** Sandro / Matriz  
**Ambiente:** `C:\ElevaLocker` · PC `192.168.16.130:15000` · Mikrotik HUB RB · WireGuard ESP  
**Objetivo:** Morador abrir links no WhatsApp e portal pelo celular (fora da rede Wi‑Fi).

---

## O que vocês já têm

| Item | Status |
|------|--------|
| IP público fixo | ✅ |
| Túnel WireGuard (placas ESP) | ✅ |
| Servidor Eleva Locker | ✅ `http://192.168.16.130:15000` |
| WhatsApp Evolution | ✅ `:8080` |

## O que falta

1. Registrar **domínio** (ex.: `locker.eleva.com.br`)
2. **DNS** apontando pro IP público
3. **HTTPS** na porta 443 (Caddy ou Nginx)
4. **NAT** no Mikrotik (443 → PC)
5. Atualizar **`.env`** (`APP_URL_BASE=https://...`)

---

## Parte 1 — Registrar domínio e DNS

### 1.1 Escolher o nome

Sugestões:

- `locker.eleva.com.br`
- `elevalocker.com.br`
- `armario.seudominio.com.br`

Anote o nome escolhido: `______________________________`

### 1.2 Registrar

1. Acesse [Registro.br](https://registro.br) (ou provedor que preferir).
2. Pesquise disponibilidade e registre (~R$ 40–60/ano).
3. Guarde login e senha do painel DNS.

### 1.3 Criar registro DNS

No painel do domínio, adicione:

| Campo | Valor |
|-------|--------|
| Tipo | **A** |
| Nome | `locker` (ou `@` se for domínio raiz) |
| Destino | **Seu IP público** (anote abaixo) |
| TTL | 300 (5 min) |

**IP público da sede:** `______________________________`

Aguarde 5–30 min. Teste no PC:

```powershell
nslookup locker.seudominio.com.br
```

Deve retornar o IP público.

---

## Parte 2 — Mikrotik (HUB RB ELEVA)

> Objetivo: internet na porta **443** chega no PC `192.168.16.130`.

### 2.1 NAT (dst-nat)

No Winbox ou terminal Mikrotik (ajuste interface WAN se necessário):

```
/ip firewall nat add chain=dstnat protocol=tcp dst-port=443 \
  action=dst-nat to-addresses=192.168.16.130 to-ports=443 \
  comment="Eleva Locker HTTPS"
```

### 2.2 Firewall (permitir encaminhamento)

```
/ip firewall filter add chain=forward protocol=tcp dst-address=192.168.16.130 dst-port=443 \
  action=accept comment="Eleva Locker HTTPS"
```

### 2.3 Hairpin NAT (opcional, recomendado)

Permite abrir o domínio **de dentro** da rede (celular no Wi‑Fi do condomínio):

- No Mikrotik: habilitar **hairpin NAT** / **NAT loopback** para o mesmo dst-nat da 443.
- Sem isso, o link funciona fora da rede mas pode falhar no Wi‑Fi local.

### 2.4 Não expor na internet

- **Não** abrir porta `15000` direto — use só **443** com Caddy na frente.
- WireGuard das ESP **mantém como está** (VPN separada).

---

## Parte 3 — HTTPS no PC (Caddy no Windows)

Flask continua em `15000`. Caddy escuta **443** e repassa.

### 3.1 Baixar Caddy

1. [https://caddyserver.com/download](https://caddyserver.com/download) → Windows amd64.
2. Extraia `caddy.exe` para `C:\ElevaLocker\tools\caddy\`

### 3.2 Criar Caddyfile

Arquivo: `C:\ElevaLocker\tools\caddy\Caddyfile`

Substitua pelo seu domínio real:

```
locker.seudominio.com.br {
    reverse_proxy localhost:15000
}
```

Caddy gera certificado Let's Encrypt **automaticamente** (porta 443 precisa estar acessível de fora).

### 3.3 Testar Caddy (manual)

```powershell
cd C:\ElevaLocker\tools\caddy
.\caddy.exe run --config Caddyfile
```

Em outro navegador (celular **4G**, não Wi‑Fi):

`https://locker.seudominio.com.br/dashboard`

Se abrir login Eleva Locker → HTTPS OK.

### 3.4 Caddy sempre ligado (opcional)

- Criar atalho ou tarefa agendada “Ao iniciar Windows”:
  - Programa: `C:\ElevaLocker\tools\caddy\caddy.exe`
  - Argumentos: `run --config C:\ElevaLocker\tools\caddy\Caddyfile`
  - Iniciar em: `C:\ElevaLocker\tools\caddy`

Ordem ao ligar o PC:

1. Docker (Evolution) — se usar
2. `INICIAR.bat` (Flask :15000)
3. Caddy (:443)

---

## Parte 4 — Implementar no Eleva Locker

### 4.1 Atualizar código (recomendado)

No PowerShell:

```powershell
cd C:\ElevaLocker
git pull origin main
git pull origin cursor/whatsapp-endereco-armario-c05c
git pull origin cursor/fix-cadastro-armario-c05c
```

*(Ou só `main` se os PRs já estiverem mergeados.)*

### 4.2 Editar `.env`

Arquivo: `C:\ElevaLocker\.env`

```env
APP_URL_BASE=https://locker.seudominio.com.br
ELEVA_PAINEL_URL=https://locker.seudominio.com.br/dashboard
NOTIF_INCLUIR_LINK_TOTEM=1
```

Salvar.

### 4.3 Reiniciar serviços

```powershell
cd C:\ElevaLocker
# Parar INICIAR.bat (Ctrl+C → S)
.\INICIAR.bat
# Caddy rodando na pasta tools\caddy
```

### 4.4 Conferir leitura do `.env`

```powershell
cd C:\ElevaLocker
py tools\diagnostico_env.py
```

Deve mostrar:

```
APP_URL_BASE = 'https://locker.seudominio.com.br'
```

### 4.5 Endereço do armário (WhatsApp)

Painel → **Armários → Matriz → Editar armário**:

- Endereço: `rua castelo branco 240`
- Cidade: `Lauro Müller`
- UF: `SC`

Usado na mensagem WhatsApp (nome + endereço).

---

## Parte 5 — Checklist de testes

Marque conforme for testando:

| # | Teste | Onde | OK |
|---|--------|------|-----|
| 1 | `nslookup` resolve pro IP público | PC | ☐ |
| 2 | `https://dominio/dashboard` (4G) | Celular | ☐ |
| 3 | `https://dominio/totem/2` (4G) | Celular | ☐ |
| 4 | `py tools\diagnostico_env.py` | PC | ☐ |
| 5 | `py tools\testar_whatsapp_endereco.py` | PC | ☐ |
| 6 | Depósito teste → WhatsApp com link **https** | Celular | ☐ |
| 7 | Link do WhatsApp abre totem | Celular 4G | ☐ |
| 8 | ESP Matriz online (heartbeat) | Painel ESP32 | ☐ |
| 9 | Totem Fully ainda abre (Wi‑Fi local) | Tablet | ☐ |

### Teste WhatsApp esperado (com domínio)

```
Olá *Nome*! 📦
...
📍 *ELEVA Locker Matriz*
   rua castelo branco 240 · Lauro Müller/SC
...
👉 Retire no totem:
https://locker.seudominio.com.br/totem/2
```

*(Com IP local, o sistema mostra endereço sem link — PR #44.)*

---

## Parte 6 — Placas ESP + WireGuard

- ESP na rede `192.168.16.x`: em geral **continuam OK** (heartbeat local).
- Sync recebe `servidor_url` do `APP_URL_BASE`: após mudar pro domínio, confira no painel se placas seguem **online**.
- Se alguma placa cair após a mudança:
  1. Verifique hairpin NAT (Parte 2.3)
  2. Temporariamente teste se a placa alcança `https://dominio` pela VPN
  3. WireGuard **não precisa mudar** só por causa do domínio

---

## Parte 7 — Se algo der errado (rollback)

Volte o `.env` temporariamente:

```env
APP_URL_BASE=http://192.168.16.130:15000
NOTIF_INCLUIR_LINK_TOTEM=0
```

Reinicie `INICIAR.bat`. Totem e ESP voltam ao modo local.

Domínio e Caddy podem ficar instalados — só não usar até corrigir.

---

## Resumo em ordem (amanhã)

1. ☐ Registrar domínio  
2. ☐ DNS tipo A → IP público  
3. ☐ NAT Mikrotik 443 → 192.168.16.130  
4. ☐ Instalar Caddy + Caddyfile  
5. ☐ Testar HTTPS pelo celular (4G)  
6. ☐ Atualizar `.env` (`APP_URL_BASE`, `NOTIF_INCLUIR_LINK_TOTEM=1`)  
7. ☐ Reiniciar `INICIAR.bat` + Caddy  
8. ☐ `diagnostico_env.py` + depósito teste WhatsApp  
9. ☐ Confirmar ESP online  

---

## Anexos — comandos rápidos

```powershell
cd C:\ElevaLocker
py tools\diagnostico_env.py
py tools\testar_whatsapp_endereco.py
py tools\url_totem_quiosque.py
```

Totem quiosque (Fully): URL continua podendo ser local na rede:

`http://192.168.16.130:15000/totem/2?kiosk=1`

O tablet do totem **não precisa** usar domínio público se o Wi‑Fi local for estável.

---

*Documento criado em 01/09/2026 — revisar após primeiro deploy com domínio real.*
