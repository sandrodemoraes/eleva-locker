# Eleva Cam — setup no PC do site

Guia para o PC que hospeda o site e (quando a câmera estiver pronta) o encoder do stream.

**Branch:** `cursor/eleva-cam-mvp-c1b7`  
**Conta Cursor / GitHub:** a mesma do Sandro

---

## 0. Papel deste PC

| Função | O quê |
|--------|--------|
| Site | Flask em `http://IP:15000/eleva-cam` |
| Encoder | MediaMTX ou OBS → YouTube Live |
| Depois | Domínio + HTTPS (VPS ou túnel) |

---

## 1. Abrir o projeto neste PC

No Cursor / terminal:

```bat
git clone https://github.com/sandrodemoraes/eleva-locker.git
cd eleva-locker
git fetch origin
git checkout cursor/eleva-cam-mvp-c1b7
```

Python 3.10+ e:

```bat
pip install flask werkzeug
```

---

## 2. Subir o site (já funciona sem câmera)

**Windows** (na pasta do repo):

```bat
tools\eleva-cam\INICIAR_SITE.bat
```

**Linux / macOS:**

```bash
bash tools/eleva-cam/iniciar_site.sh
```

Abra:

- Site: http://127.0.0.1:15000/eleva-cam  
- Painel: http://127.0.0.1:15000/cameras  
- Login: `admin@elevalocker.com` / `123456` (troque depois)

Enquanto não houver YouTube ID, a Serra aparece como “Em breve ao vivo”.

---

## 3. Canal YouTube (faça uma vez)

1. Crie o canal **Eleva Cam** (handle sugerido `@ElevaCam`)
2. YouTube Studio → **Transmitir** / **Go live** → **Stream**
3. Copie a **chave de transmissão** (stream key)
4. Guarde em `tools/eleva-cam/.env.stream` (não versionar):

```bat
copy tools\eleva-cam\env.stream.example tools\eleva-cam\.env.stream
notepad tools\eleva-cam\.env.stream
```

Preencha:

```
YOUTUBE_STREAM_KEY=sua-chave-aqui
CAMERA_RTSP_URL=rtsp://usuario:senha@IP_DA_CAMERA:554/cam/realmonitor?channel=1&subtype=0
```

---

## 4. Encoder no PC — duas opções

### Opção A — OBS (mais simples para o 1º teste)

1. Instale [OBS Studio](https://obsproject.com/)
2. Fonte → **Media Source** ou **VLC** com o RTSP da câmera  
   (ou captura se for USB)
3. Configurações → Transmitir → Serviço **YouTube** → cole a chave
4. Iniciar transmissão
5. No YouTube Studio, copie o **ID do vídeo** da live
6. Painel `/cameras` → editar Serra → `youtube_video_id` + `stream_status = online`

### Opção B — MediaMTX (24/7, recomendado Eleva Cam)

1. Baixe o [MediaMTX](https://github.com/bluenviron/mediamtx/releases) (Windows amd64)
2. Extraia para `tools/eleva-cam/mediamtx/` (ou outro path fixo)
3. Copie o exemplo de config:

```bat
copy tools\eleva-cam\mediamtx.yml.example tools\eleva-cam\mediamtx.yml
```

4. Edite `mediamtx.yml`: ajuste o path `serra` com o RTSP da câmera
5. Tenha o `ffmpeg` no PATH ([gyan.dev builds](https://www.gyan.dev/ffmpeg/builds/) no Windows)
6. Preencha `.env.stream` e rode:

```bat
tools\eleva-cam\INICIAR_STREAM.bat
```

Isso sobe o MediaMTX e, com a chave YouTube, o `ffmpeg` empurra RTMP para a live.

7. Cole o ID da live no painel, como na opção A.

---

## 5. Checklist “está no ar?”

- [ ] Site abre em `/eleva-cam`
- [ ] Câmera no painel com status **online**
- [ ] Embed mostra a live (não o placeholder)
- [ ] Ângulo só na serra/horizonte (sem sacadas do 3º/4º)
- [ ] PC não hiberna / nobreak se for 24/7

---

## 6. Próximo depois do teste local

1. Registrar `elevacam.com.br`
2. Publicar em VPS (pacote `deploy/` do portal) **ou** Cloudflare Tunnel neste PC
3. Overlay (hora, temperatura, logo) no encoder

Detalhes de marca e obra: `docs/CHECKLIST-MARCA-SITE-CAMERAS.md`  
Visão do produto: `docs/ELEVA_CAM.md`
