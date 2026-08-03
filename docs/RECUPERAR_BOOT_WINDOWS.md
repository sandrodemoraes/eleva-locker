# Recuperar boot do Windows (SERVIDOR-ELEVA)

> **Importante:** daqui (Cloud Agent) **não dá para ver nem montar** o HD físico do seu PC.  
> Estes passos rodam **no próprio computador**, em modo de recuperação (WinRE) ou com um pendrive de instalação do Windows 11.

Contexto conhecido:
- Máquina: **SERVIDOR-ELEVA** (Windows 11 Pro, i7-12700K, 32 GB)
- O Windows antigo **parou de iniciar** → você colocou **outro HD** e reinstalou
- O **HD velho** foi mantido com dados (backup / possível Windows antigo)

---

## Antes de mexer: decida o objetivo

| Objetivo | O que fazer |
|----------|-------------|
| **A)** Só ler dados do HD velho | Conectar como disco secundário no Windows novo → copiar pastas → **não** tente bootar nele |
| **B)** Fazer o Windows do HD velho voltar a dar boot | Siga a seção **Reparar boot (BCD/UEFI)** abaixo |
| **C)** Windows novo não inicia | Mesmos passos, apontando para a partição `Windows` do HD **novo** |

Se o Windows **novo** já está ok e você só precisa do ElevaLocker no boot do Windows: use `tools\criar_atalho_desktop.bat` (isso **não** é boot do SO).

---

## 1. Entrar no ambiente de recuperação

### Opção A — Windows ainda abre às vezes
1. **Configurações → Sistema → Recuperação → Inicialização avançada → Reiniciar agora**
2. **Solucionar problemas → Prompt de Comando**

### Opção B — não inicia (recomendado)
1. Crie um pendrive de instalação do Windows 11 (Media Creation Tool em outro PC)
2. No BIOS/UEFI do SERVIDOR-ELEVA: boot pelo pendrive (USB)
3. Na tela de instalar: **Reparar o computador → Solucionar problemas → Prompt de Comando**

### BIOS (cheque rápido)
- Modo: **UEFI** (não Legacy/CSM, se o Windows 11 foi instalado em UEFI)
- Secure Boot: pode deixar ligado; se `bcdboot` falhar, teste desligado temporariamente
- Ordem de boot: disco certo (SSD/NVMe do sistema) em 1º

---

## 2. Mapear os discos (estrutura)

No **Prompt de Comando** do WinRE:

```bat
diskpart
list disk
list vol
```

Anote:
- Qual disco é o **novo** (Windows atual)
- Qual é o **velho** (dados / Windows antigo)
- Qual volume tem a pasta `Windows` (geralmente `C:` no WinRE pode ser outra letra!)
- Qual volume é **EFI** (FAT32, ~100–500 MB, sem letra às vezes)

Para ver o conteúdo sem adivinhar a letra:

```bat
exit
dir C:\Windows\System32\ntoskrnl.exe
dir D:\Windows\System32\ntoskrnl.exe
dir E:\Windows\System32\ntoskrnl.exe
```

A letra onde o arquivo existir é a partição do Windows a reparar. Chame-a de `W:` nos exemplos abaixo (troque pela letra real).

Scripts prontos neste repo (copie para um pendrive se quiser):

| Arquivo | Função |
|---------|--------|
| `tools/windows_boot/01_listar_discos.bat` | Lista discos/volumes |
| `tools/windows_boot/02_reparar_boot_uefi.bat` | Repara BCD/EFI (pede letra do Windows) |
| `tools/windows_boot/03_reparar_boot_legado.bat` | Alternativa MBR/legado |
| `tools/windows_boot/04_checar_saude_disco.bat` | `chkdsk` na partição Windows |

---

## 3. Reparar boot UEFI (caso mais comum no Win 11)

No Prompt do WinRE (troque `W:` pela letra encontrada):

```bat
diskpart
list vol
```

Identifique o volume **EFI** (FAT32 pequeno). Exemplo se for volume 2:

```bat
select vol 2
assign letter=S
exit
```

Depois:

```bat
bcdboot W:\Windows /s S: /f UEFI
bootrec /fixboot
bootrec /scanos
bootrec /rebuildbcd
```

Se `rebuildbcd` perguntar se deseja adicionar à lista de inicialização → **S**.

Reinicie e retire o pendrive:

```bat
wpeutil reboot
```

### Alternativa clássica (às vezes ajuda)

```bat
bootrec /fixmbr
bootrec /fixboot
bootrec /scanos
bootrec /rebuildbcd
```

Em UEFI puro, o passo decisivo costuma ser o **`bcdboot`**, não só o `bootrec`.

---

## 4. Se o Windows do HD velho deve bootar de novo

1. No BIOS, coloque o **HD velho** como primeiro disco de boot **só para o teste**
2. Rode a seção 3 apontando `W:` para o `Windows` **desse** HD
3. Se bootar: ótimo — copie o que faltar para o HD novo
4. Depois **volte** o HD novo como disco de boot do dia a dia
5. HD velho → idealmente só backup (NTFS/exFAT), sem depender dele para iniciar o PC

**Não** deixe dois Windows “brigando” pela mesma entrada EFI sem saber qual disco é o principal — isso gera boot loop / “escolhe o disco errado”.

---

## 5. Se o disco está com erro de arquivo / blue screen

Com a letra `W:` da partição Windows:

```bat
chkdsk W: /f /r
sfc /scannow /offbootdir=W:\ /offwindir=W:\Windows
```

`chkdsk /r` pode demorar **horas** em HD grande.

Se o disco estiver falhando (cliques, SMART ruim): **priorize copiar dados** no Windows novo (como disco secundário) em vez de insistir no boot.

---

## 6. Recuperar dados sem consertar o boot (mais seguro)

Com o Windows **novo** funcionando:

1. Desligue → conecte o HD velho (SATA/USB dock)
2. Abra o Explorer → copie:
   - `Users\<seu usuário>\Documents`, `Desktop`, `Downloads`
   - Pastas do ElevaLocker, `.env`, backups, Arduino sketches
   - `C:\ElevaLocker` ou `%USERPROFILE%\eleva-locker` se existirem no velho
3. Só depois formate o HD velho se for usá-lo só como backup

---

## 7. Depois que o Windows bootar de novo

1. Recuperar o ElevaLocker: `docs/RECUPERAR_SERVIDOR.md`
2. Branch: `cursor/recuperar-servidor-antigo-615b`
3. Atalho + início com Windows: `tools\criar_atalho_desktop.bat`
4. Servidor: http://localhost:15000

---

## Checklist rápido

- [ ] Entrou no WinRE / pendrive de reparo
- [ ] `list disk` / `list vol` — sabe qual é HD novo vs velho
- [ ] Achou `...\Windows\System32\ntoskrnl.exe` (letra `W:`)
- [ ] Montou EFI em `S:` (se UEFI)
- [ ] Rodou `bcdboot W:\Windows /s S: /f UEFI`
- [ ] Reiniciou sem pendrive
- [ ] Se só queria dados: copiou pastas no Windows novo

---

## O que me mande se ainda falhar

Para eu afinar o próximo passo (ainda remoto, por texto):

1. Foto/tela do erro de boot (código tipo `0xc0000001`, `INACCESSIBLE_BOOT_DEVICE`, etc.)
2. Saída de `list disk` e `list vol`
3. Em qual letra existe `Windows\System32`
4. Se o disco com problema é o **novo** ou o **velho**
