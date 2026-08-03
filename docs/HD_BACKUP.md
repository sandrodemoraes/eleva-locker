# HD velho como disco de backup (Windows novo)

**Decisão:** não recuperar o Windows do HD velho.  
Ligar o HD no PC → boot pelo **Windows novo** → **formatar** o velho → usar só como **backup**.

---

## Antes de formatar (obrigatório)

Confirme que isto já está seguro **fora** do HD velho:

| Item | Onde deve estar |
|------|-----------------|
| Backup Windows Defender | Já recuperado / acessível no disco novo |
| `D:\backup pc fabio\` | No disco **novo** (não só no velho) |
| ElevaLocker (Git) | `%USERPROFILE%\eleva-locker` nesta branch |
| `elevalocker.db` / projetos importantes | Copiados para o disco novo ou Defender |

Se algo importante **só** existir no HD velho, **copie antes** de formatar.

```bat
dir E:\
dir E:\Users
dir E:\ElevaLocker
dir E:\eleva-locker
```

(`E:` = letra que o Windows der ao HD velho — confira no Explorer.)

---

## Passo a passo

### 1. Ligar o HD
1. PC desligado → conecte o HD velho (SATA ou dock USB)  
2. Ligue e entre no **Windows novo** (não mude o boot no BIOS para o velho)

### 2. Identificar o disco
- Explorer → veja a letra nova  
- Ou: `Win + X` → **Gerenciamento de Disco**  
- Anote: disco nº, tamanho, letra  

**Não formate** o disco do Windows novo (C:).

### 3. Formatar o HD velho
No Gerenciamento de Disco, no volume do HD **velho**:
1. Clique direito → **Formatar**  
2. Sistema de arquivos: **NTFS**  
3. Rótulo: `BACKUP_ELEVA`  
4. Desmarque “Formatação rápida” só se quiser checagem mais profunda (demora mais)

### 4. Estrutura sugerida

```
E:\BACKUP_ELEVA\
  \eleva-locker\          ← cópia do projeto / DB
  \Documentos\
  \Desktop\
  \Downloads\
  \Arduino\
  \Defender\              ← dumps do backup Defender se quiser
  \PC\                    ← backup geral do perfil
```

### 5. Primeira cópia (manual / robocopy)

No CMD (ajuste a letra `E:`):

```bat
mkdir "E:\BACKUP_ELEVA\eleva-locker"
mkdir "E:\BACKUP_ELEVA\PC"

robocopy "%USERPROFILE%\eleva-locker" "E:\BACKUP_ELEVA\eleva-locker" /E /COPY:DAT /R:2 /W:2 /XD .git __pycache__ .venv venv
robocopy "%USERPROFILE%\Documents" "E:\BACKUP_ELEVA\PC\Documents" /E /COPY:DAT /R:1 /W:1
robocopy "%USERPROFILE%\Desktop" "E:\BACKUP_ELEVA\PC\Desktop" /E /COPY:DAT /R:1 /W:1
robocopy "%USERPROFILE%\Downloads" "E:\BACKUP_ELEVA\PC\Downloads" /E /COPY:DAT /R:1 /W:1
```

Script pronto (depois do `git pull`):

```bat
tools\windows_boot\09_backup_para_hd.bat E:
```

### 6. Backup automático (simples)

Opção A — **Histórico de Arquivos** (Windows):  
Configurações → Sistema → Armazenamento → Configurações avançadas → Histórico de Arquivos → escolher `BACKUP_ELEVA`.

Opção B — agendar o `09_backup_para_hd.bat` no Agendador de Tarefas (diário).

---

## ElevaLocker no dia a dia

- Disco **C:** (novo) = sistema + app rodando  
- Disco **backup** = cópia; não rode o servidor a partir do HD de backup  
- Depois de mudanças importantes no app: rode de novo o `09_backup_para_hd.bat`

---

## Me manda quando o HD aparecer

1. Letra do HD velho (Explorer)  
2. Print do Gerenciamento de Disco (só para confirmar qual formatar)  

Aí te confirmo o formatar + o comando de backup com a letra certa.
