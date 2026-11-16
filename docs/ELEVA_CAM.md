# Eleva Cam — MVP

Câmeras ao vivo em pontos turísticos. Marca separada do Eleva Locker.

**1º ponto:** Serra do Rio do Rastro (Lauro Müller/SC), vista da base.

## URLs

| Rota | Função |
|------|--------|
| `/eleva-cam` | Site público (home + hero) |
| `/eleva-cam/<slug>` | Página de uma câmera |
| `/cameras/ao-vivo` | Alias da home pública |
| `/cameras` | Painel admin (login) |

## Setup no PC do site

Guia passo a passo (clone, Flask, OBS/MediaMTX, YouTube):

→ **`docs/ELEVA_CAM_SETUP_PC.md`**

Scripts: `tools/eleva-cam/` (`INICIAR_SITE.bat`, `INICIAR_STREAM.bat`).

## Como ligar o stream

1. Suba o site: `tools\eleva-cam\INICIAR_SITE.bat`
2. Transmita com OBS ou `INICIAR_STREAM.bat` (MediaMTX + ffmpeg)
3. Painel → **Câmeras** → edite Serra
4. Preencha `youtube_video_id` com o ID da live
5. Defina `stream_status` = `online`
6. Abra `/eleva-cam`

Enquanto o ID estiver vazio, o site mostra placeholder “Em breve ao vivo”.

## Modelo de dados

Tabela `cameras`:

- `nome`, `slug`, `local`, `cidade`, `estado`, `descricao`
- `youtube_video_id`, `youtube_channel_url`
- `stream_status` (`online` \| `offline` \| `manutencao`)
- `latitude`, `longitude`, `ordem`, `status`

Seed automático na criação do banco: `serra-do-rio-do-rastro`.

## Arquitetura alvo (próximas fases)

```
Câmera IP (PoE) → MediaMTX / OBS → YouTube Live (RTMP)
                                      ↓
                              Embed no site Eleva Cam
```

Detalhes de marca, privacidade, obra e monetização:
`docs/CHECKLIST-MARCA-SITE-CAMERAS.md` (seção 6).

## Fronteiras de marca

| Marca | Uso |
|-------|-----|
| **Eleva Cam** | Webcam turística / mídia |
| **Eleva Locker** | Smart lockers B2B |
| **Hospedagem** | Kitnets do 3º piso — marca separada (nome a definir) |

A câmera pública filma **só a serra/horizonte**, nunca o interior do prédio.
