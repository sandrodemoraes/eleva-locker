# Tablet totem — sempre abrir na página do armário

> Tablet 10" (ou 7") fixo no locker — abre direto no totem, sem distrações.

## URL do totem (Matriz)

```
http://192.168.16.130:15000/totem/3
```

Rede externa (4G/outra WiFi): `http://177.74.79.32:15000/totem/3`

---

## Opção 1 — Android: app **Fully Kiosk Browser** (recomendado)

Melhor para tablet **sempre** no totem (liga e abre sozinho).

1. Play Store → instale **Fully Kiosk Browser** (versão gratuita serve)
2. Abra o app → **Web Content Settings**
   - **Start URL:** `http://192.168.16.130:15000/totem/3`
   - Marque **Load Start URL on startup**
3. **Kiosk Mode** → ative **Lock task mode** / modo quiosque
4. **Device Management**
   - **Keep screen on** — tela sempre ligada
   - **Screen brightness** — 70–100%
5. **Restart on idle** — opcional: recarrega página a cada 30 min
6. Defina Fully Kiosk como app padrão ao ligar (alguns tablets Samsung: Configurações → Apps padrão)

**Sair do modo kiosk:** senha admin do Fully Kiosk (você define na 1ª configuração).

---

## Opção 2 — Android: atalho na tela inicial (simples)

Sem app extra — bom para **testar** no tablet de trabalho.

1. Chrome → abra `http://192.168.16.130:15000/totem/3`
2. Menu **⋮** → **Adicionar à tela inicial** ou **Instalar app**
3. Nome: **ELEVA Totem**
4. Toque no ícone na home — abre **tela cheia** direto no totem

Limitação: não abre sozinho ao ligar o tablet — precisa tocar no ícone.

---

## Opção 3 — Android: fixar tela (Screen Pinning)

1. Configurações → **Segurança** → **Fixação de tela** → ativar
2. Abra o totem no Chrome
3. Botão **Recentes** → ícone do pin/agulha → fixa só o Chrome no totem

Para soltar: segurar Voltar + Recentes.

---

## Opção 4 — iPad / iPhone

1. Safari → `http://192.168.16.130:15000/totem/3`
2. **Compartilhar** → **Adicionar à Tela de Início**
3. Modo quiosque forte: **Acesso Guiado** (Configurações → Acessibilidade)

---

## Opção 5 — Tablet Windows

1. Crie atalho Chrome com:
   ```
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --kiosk --app=http://192.168.16.130:15000/totem/3
   ```
2. Coloque na pasta **Inicializar** do Windows
3. Ou: Configurações → Contas → **Acesso atribuído** (modo quiosque Windows)

Atalho pronto no repo: `tools\atalho_totem_kiosk.bat` (edite o IP se mudar).

---

## Checklist antes de fixar no armário

- [ ] PC servidor com `tools\iniciar_tudo.bat` ou início automático
- [ ] Tablet na **mesma WiFi** do servidor
- [ ] URL `/totem/3` abre e mostra **ELEVA Locker Matriz**
- [ ] Teste retirada com código WhatsApp
- [ ] Tablet na **tomada** (tela sempre ligada)
- [ ] Brilho ~80%, timeout de tela = **nunca**

---

## Tablet de trabalho vs fixo no locker

| Uso | Configuração |
|-----|----------------|
| **Testar hoje** | Opção 2 — atalho na home |
| **Fixo no armário** | Opção 1 — Fully Kiosk |
| **Uso misto** | Atalho na home; abre quando precisar |

---

## Trocar de armário

Troque `3` na URL pelo ID do armário:
`/totem/1`, `/totem/2`, etc.

No painel: **Armários** → veja o número na URL ao clicar no armário.
