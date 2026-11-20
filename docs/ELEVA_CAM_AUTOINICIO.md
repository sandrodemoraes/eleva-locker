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

## 4. Checklist pós-blecaute

- [ ] BIOS = Power On após energia  
- [ ] Windows com login automático (ou alguém loga)  
- [ ] `INSTALAR_AUTOINICIO.bat` já rodado  
- [ ] `cloudflared.exe` em `deploy\eleva-cam\`  
- [ ] `config.tunnel.yml` configurado  

Log de tentativas: `logs\elevacam-autoinicio.log`
