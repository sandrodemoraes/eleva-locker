# Cópia da pasta Windows antiga no disco novo

Você tem a pasta do **Windows antigo copiada** para o HD/SSD novo (não é o Windows que está rodando agora).

## O que isso permite (e o que não)

| Dá para | Não dá (em geral) |
|---------|-------------------|
| Recuperar arquivos de usuário, configs, ElevaLocker, Arduino, etc. | Fazer o PC **bootar** só apontando o BCD para essa pasta copiada |
| Ler registros offline (`SOFTWARE`, `SYSTEM`) com cuidado | Substituir `C:\Windows` do Windows novo pela pasta antiga e esperar funcionar |
| Restaurar programas *se* também copiou `Program Files` + dados do AppData | “Remendar” boot com `bcdboot` nessa cópia e ter um SO estável |

**Por quê o boot falha com cópia de pasta?**  
O Windows precisa de partição EFI + BCD + drivers do disco atual + registro coerente com o hardware. Uma pasta `Windows` copiada (Explorer/robocopy) quase nunca é bootável.

**Caminho certo:** usar a cópia como **arquivo morto** e puxar o que importa para o Windows novo que já inicia.

---

## 1. Achar onde está a cópia

No Windows **novo** (PowerShell ou CMD):

```powershell
# Procura pastas Windows "de backup" (fora do sistema ativo)
Get-PSDrive -PSProvider FileSystem | ForEach-Object {
  $root = $_.Root
  @(
    "$root\Windows",
    "$root\Windows.old",
    "$root\Windows_antigo",
    "$root\Backup\Windows",
    "$root\Users\*\Desktop\Windows",
    "$env:USERPROFILE\Windows",
    "$env:USERPROFILE\Desktop\Windows",
    "$env:USERPROFILE\Documents\Windows"
  ) | ForEach-Object {
    if (Test-Path "$_\System32\ntoskrnl.exe") {
      "ACHADO: $_"
    }
  }
}
```

Ou rode: `tools\windows_boot\05_localizar_windows_copiado.bat`

Anote o caminho, ex.: `D:\Backup\Windows` ou `C:\Windows.old`.

> **Não confunda** com `C:\Windows` do sistema atual (é o novo). A cópia costuma chamar `Windows.old`, `Windows_backup`, ou estar em outro disco/pasta.

---

## 2. Extrair o que importa (recomendado)

Script pronto: `tools\windows_boot\06_extrair_dados_windows_antigo.bat`

```bat
tools\windows_boot\06_extrair_dados_windows_antigo.bat "D:\Backup\Windows" "D:\Recuperado_Windows_Antigo"
```

Ele procura e copia (se existir) para a pasta de destino:

| Origem típica (relativa à cópia) | Conteúdo |
|----------------------------------|----------|
| `..\Users\` | Documentos, Desktop, Downloads, AppData |
| `..\ElevaLocker` / `..\eleva-locker` | Projeto ElevaLocker |
| `..\Program Files\Arduino*` | IDE / sketches se estiverem lá |
| `..\Users\*\Documents\Arduino` | Sketches ESP32 |
| `..\Users\*\.cursor` | Config Cursor (se houver) |
| `System32\config\` | Hives (só backup; não substitua os do Windows novo) |

Também lista caminhos úteis no log `RECUPERACAO_LOG.txt`.

### Manual (Explorer)

Se a cópia for tipo `D:\Backup\Windows`, os usuários costumam estar em:

- `D:\Backup\Users\sandr\...` (irmão da pasta Windows), ou
- `D:\Backup\Windows\...\` (menos comum)

Procure:

```
...\Users\<seu usuário>\Desktop
...\Users\<seu usuário>\Documents
...\Users\<seu usuário>\Downloads
...\Users\<seu usuário>\AppData\Roaming
...\eleva-locker
...\ElevaLocker
```

---

## 3. ElevaLocker a partir da cópia

1. Se achar a pasta do projeto no backup → compare com o clone novo do Git  
2. Prefira o código da branch `cursor/recuperar-servidor-antigo-615b` (GitHub)  
3. Da cópia antiga, salve sobretudo:
   - `database\elevalocker.db` (dados reais)
   - `.env` / configs / backups em `backups\`
   - firmware / sketches locais
4. Guia do app: `docs/RECUPERAR_SERVIDOR.md`

---

## 4. Se a intenção era “voltar a bootar o Windows antigo”

| Situação real | O que fazer |
|---------------|-------------|
| Só a pasta `Windows` foi copiada | **Não tente boot.** Extraia dados (seções 1–3) |
| Existe `Windows.old` de upgrade/reinstall | Configurações → Sistema → Recuperação → **Voltar** (se ainda disponível) **ou** extrair de `C:\Windows.old\Users` |
| HD velho ainda tem instalação completa (EFI + Windows) | `docs/RECUPERAR_BOOT_WINDOWS.md` no WinRE, apontando para **esse** disco |
| Clone/imagem completa do disco (Macrium, dd, etc.) | Restaurar a **imagem inteira** para um disco, não só a pasta |

Substituir `C:\Windows` do sistema novo pela pasta antiga **quebra** o Windows que está funcionando. Não faça isso.

---

## 5. Checklist

- [ ] Localizei a cópia (não é o `C:\Windows` atual)
- [ ] Localizei `Users` (irmão ou dentro do backup)
- [ ] Copiei Desktop/Documents/Downloads/ElevaLocker/DB para `D:\Recuperado_...`
- [ ] NÃO substituí `C:\Windows` do sistema novo
- [ ] Subi ElevaLocker pela branch de recuperação + DB antigo se necessário

---

## Me mande (para afinar o próximo passo)

No PowerShell do Windows novo:

```powershell
# Troque pelo caminho onde você acha que está a cópia
$p = "D:\CAMINHO\Windows"
Test-Path "$p\System32\ntoskrnl.exe"
Get-ChildItem (Split-Path $p -Parent) -Name | Select-Object -First 40
```

Cole o caminho exato da pasta e se existe `Users` do lado. Aí indico o comando de cópia exato para o seu layout.
