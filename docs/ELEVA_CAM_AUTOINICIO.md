# elevacam — ligar sozinho após queda de energia

Dois ajustes: **BIOS** (PC liga) + **Windows** (site e túnel sobem).

---

## 1. BIOS — ligar o PC quando a energia voltar

1. Reinicie o PC e entre na BIOS (`Del`, `F2` ou `F10` na tela inicial)
2. Procure uma destas opções (nomes variam):
   - **Restore on AC/Power Loss**
   - **AC Power Recovery**
   - **After Power Loss**
   - **Power On After Power Fail**
3. Defina como **Power On** / **Always On** (não `Last State` se quiser sempre ligar)
4. Salve e saia (`F10` → Yes)

Sem isso, o Windows não inicia sozinho depois de um blecaute.

---

## 2. Windows — entrar sozinho (recomendado)

Para o script rodar sem alguém digitar senha:

1. `Win + R` → `netplwiz` → Enter  
2. Desmarque **“Os usuários devem digitar um nome de usuário e uma senha…”**  
3. Informe a senha do usuário `terminal` → OK  

(Em Windows 11 às vezes: `Win + R` → `control userpasswords2`)

---

## 3. Instalar o início do elevacam

No PC do site (já com o projeto atualizado):

```bat
cd C:\Users\terminal\eleva-locker
git pull

cd tools\eleva-cam
INSTALAR_AUTOINICIO.bat
```

Isso cria o atalho em:

`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\elevacam-autoinicio.lnk`

Que chama `INICIAR_AUTOMATICO.bat` (espera a rede e sobe Flask + Cloudflare Tunnel).

### Testar sem reiniciar

```bat
cd C:\Users\terminal\eleva-locker\tools\eleva-cam
INICIAR_AUTOMATICO.bat
```

Devem abrir as janelas do Site e do Túnel.

### Remover o autoinício

Apague o atalho:

`Win + R` → `shell:startup` → apague `elevacam-autoinicio`

---

## 4. OBS — transmitir sozinho após o login

O `INSTALAR_AUTOINICIO.bat` sobe **só o site + túnel**. A live do YouTube depende do OBS.

1. Abra o OBS → **Arquivo** → **Configurações** → **Geral**  
2. Em **Inicialização do sistema**, marque:
   - **Abrir automaticamente ao iniciar o sistema** (ou coloque o atalho do OBS em `shell:startup`)
   - **Iniciar transmissão automaticamente quando a transmissão estiver ativa** / **Start streaming when OBS starts** (se disponível na sua versão)
3. Em **Transmissão**, deixe **YouTube - RTMPS** + conta/chave já salvos  
4. Confirme que a cena com a câmera Intelbras está ativa

Sem o OBS autoiniciar + stream, o Eleva Cam sobe mas o embed fica “indisponível” até alguém clicar **Iniciar transmissão**.

---

## 5. YouTube — ID estável no `/cameras`

Cada live **nova** no YouTube gera um Video ID diferente. Depois do reboot:

1. Se a live continuar a **mesma** (mesmo Video ID), nada a fazer no painel  
2. Se criar live nova, atualize em `/cameras` → Serra → `youtube_video_id`  
3. Evite trocar `0` (zero) por `o` (letra) — copie da URL `watch?v=` ou do Studio

Dica: reutilize a mesma transmissão agendada/recorrente no Studio quando possível, para o ID não mudar.

---

## 6. Checklist pós-blecaute

- [ ] BIOS = Power On após energia  
- [ ] Windows com login automático (ou alguém loga)  
- [ ] `INSTALAR_AUTOINICIO.bat` já rodado  
- [ ] OBS abre e inicia a transmissão sozinho  
- [ ] `youtube_video_id` no `/cameras` ainda é o da live atual  
- [ ] `cloudflared.exe` em `deploy\eleva-cam\`  
- [ ] `config.tunnel.yml` configurado  

Log de tentativas: `logs\elevacam-autoinicio.log`
