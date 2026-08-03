# Recuperar com pendrive bootável Windows 11

Roteiro para o **SERVIDOR-ELEVA** — recuperação **no próprio PC**, comigo te guiando pelo celular.

## O que você precisa

1. Pendrive ≥ 8 GB  
2. Outro PC (ou este, se o Windows novo ainda inicia) para gravar a mídia  
3. Pasta deste repo: `tools\windows_boot\` (copiar para o pendrive)

---

## Parte A — Criar o pendrive (no Windows que funciona)

1. Baixe a **[Ferramenta de Criação de Mídia](https://www.microsoft.com/pt-br/software-download/windows11)** (Media Creation Tool)
2. Aceitar → **Criar mídia de instalação** → pendrive
3. Depois de gravar, copie a pasta de scripts para o pendrive:

```bat
cd %USERPROFILE%\eleva-locker
git pull origin cursor/recuperar-servidor-antigo-615b
xcopy /E /I /Y tools\windows_boot F:\windows_boot
```

Troque `F:` pela letra do pendrive.

Ou rode:

```bat
tools\windows_boot\08_copiar_scripts_para_pendrive.bat F:
```

No pendrive deve ficar algo como:

```
F:\windows_boot\01_listar_discos.bat
F:\windows_boot\00_montar_efi.bat
F:\windows_boot\02_reparar_boot_uefi.bat
...
```

---

## Parte B — Bootar pelo pendrive

1. Desligue o PC  
2. Enfie o pendrive  
3. Ligue e entre no menu de boot (comum no seu PC: **F12**, **F10**, **Esc** ou **F2** → Boot)  
4. Escolha o pendrive (**UEFI:** …)  
5. Tela azul do Windows → **Avançar** → **Reparar o computador**  
   (não clique em “Instalar agora” para formatar)  
6. **Solucionar problemas** → **Prompt de Comando**

---

## Parte C — No Prompt de Comando (me manda print de cada passo)

### 1) Ver letras dos discos / pendrive

```bat
diskpart
list vol
exit
```

Anote:
- letra do **pendrive** (FAT32/exFAT, ~8–32 GB)
- letra onde está o **Windows** (tem pasta `\Windows`)
- volume **EFI** (FAT32, ~100–500 MB)

Teste:

```bat
dir C:\Windows\System32\ntoskrnl.exe
dir D:\Windows\System32\ntoskrnl.exe
dir E:\Windows\System32\ntoskrnl.exe
```

### 2) Rodar os scripts do pendrive

Se o pendrive for `F:`:

```bat
F:
cd \windows_boot
01_listar_discos.bat
```

### 3) Montar EFI e reparar boot

Ache o **nº do volume EFI** no `list vol` (FAT32 pequeno). Exemplo volume `2`, Windows em `D:`:

```bat
00_montar_efi.bat 2
02_reparar_boot_uefi.bat D
```

### 4) Reiniciar

```bat
wpeutil reboot
```

Tire o pendrive quando reiniciar.

---

## Parte D — Se o objetivo for só dados do HD velho

1. No WinRE, use `list vol` e `dir X:\Users` no HD velho  
2. Ou boot pelo Windows **novo** com o HD velho como secundário (mais fácil)  
3. A cópia `D:\backup pc fabio\Windows` já é backup de pasta — não substitui reparo de boot

---

## Me manda nesta ordem

1. Print do **list vol**  
2. Em qual letra existe `Windows\System32\ntoskrnl.exe`  
3. Qual volume é EFI (FAT32 pequeno)  

Com isso eu te devolvo os 2 comandos finais já com as letras certas.
