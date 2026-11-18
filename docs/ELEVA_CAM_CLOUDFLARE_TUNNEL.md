# Eleva Cam — Cloudflare Tunnel (sem abrir porta 80/443)

Para provedor que **só libera portas > 10024**. O túnel publica o site sem port forward.

Fluxo:

```
Internet → Cloudflare → cloudflared (PC 10.0.0.44) → Flask :15000 → /eleva-cam
```

URL final: **https://elevacam.elevalocker.com.br**

---

## 1. Colocar o domínio na Cloudflare (uma vez)

1. Crie/entre em https://dash.cloudflare.com  
2. **Add a site** → `elevalocker.com.br` → plano **Free**  
3. Cloudflare mostra 2 **nameservers** (ex.: `xxx.ns.cloudflare.com`)  
4. Na **Hostinger** → Domínios → `elevalocker.com.br` → **Alterar nameservers**  
   - Troque `apollo/athena.dns-parking.com` pelos da Cloudflare  
5. Aguarde ficar **Active** na Cloudflare (minutos a algumas horas)

---

## 2. Instalar cloudflared no PC do site

1. Baixe Windows: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/  
   (ou: https://github.com/cloudflare/cloudflared/releases → `cloudflared-windows-amd64.exe`)  
2. Renomeie para `cloudflared.exe`  
3. Copie para: `C:\Users\terminal\eleva-locker\deploy\eleva-cam\`

---

## 3. Login e criar o túnel

PowerShell:

```powershell
cd $HOME\eleva-locker\deploy\eleva-cam

.\cloudflared.exe tunnel login
```

Abre o browser → autorize o domínio `elevalocker.com.br`.

```powershell
.\cloudflared.exe tunnel create eleva-cam
.\cloudflared.exe tunnel route dns eleva-cam elevacam.elevalocker.com.br
```

Anote o **Tunnel ID** (pasta normalmente em `%USERPROFILE%\.cloudflared\`).

---

## 4. Arquivo de config

Copie o exemplo:

```powershell
copy config.tunnel.example.yml config.tunnel.yml
notepad config.tunnel.yml
```

Troque `SEU_TUNNEL_ID` pelo ID real (e o caminho do `.json` de credenciais, se diferente).

---

## 5. Subir

Deixe o Flask rodando:

```powershell
cd $HOME\eleva-locker
.\tools\eleva-cam\INICIAR_SITE.bat
```

Outro PowerShell:

```powershell
cd $HOME\eleva-locker\deploy\eleva-cam
.\INICIAR_TUNNEL.bat
```

Ou:

```powershell
.\cloudflared.exe tunnel --config config.tunnel.yml run eleva-cam
```

Teste: **https://elevacam.elevalocker.com.br**

### Atalho de um clique (site + túnel)

Na pasta do projeto:

- `INICIAR_ELEVA_CAM.bat` (raiz)  
- ou `tools\eleva-cam\INICIAR_TUDO.bat`

Abre o Flask, o `cloudflared` e o navegador. Pode criar um atalho na área de trabalho apontando para esse `.bat`.

---

## 6. Checklist

- [ ] Nameservers Cloudflare ativos  
- [ ] Flask em `http://127.0.0.1:15000/eleva-cam`  
- [ ] `cloudflared tunnel run` sem erro  
- [ ] HTTPS abre Eleva Cam no celular (dados móveis)

**Não precisa** liberar 80/443 no roteador Unifique.

OBS/YouTube continuam locais (câmera `10.0.0.20` → OBS no PC).
