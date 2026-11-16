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

## Como ligar o stream

1. Entre no painel → **Câmeras**
2. Edite **Serra do Rio do Rastro**
3. Preencha `youtube_video_id` com o ID da live do YouTube
4. Defina `stream_status` = `online`
5. Abra `/eleva-cam`

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
