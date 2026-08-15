# Firmware ESP32 — ELEVA LOCKER

## Arquivo correto no Arduino IDE

Abra **sempre**:

```
firmware/elevalocker_sync/elevalocker_sync.ino
```

O Arduino exige pasta com o mesmo nome do `.ino`.

> Não abra `firmware/elevalocker_sync.ino` solto na raiz — use a pasta acima.

## Após `git pull`

Os dois arquivos são sincronizados pelo script `tools/atualizar_matriz.py`.
Se abrir o `.ino` e **Ctrl+F `SENSOR_GPIO`** não achar nada, rode:

```cmd
python tools\atualizar_matriz.py --so-firmware
```

## Configurar antes do Upload

```cpp
const char* SERVIDOR_URL  = "http://192.168.16.130:15000";
const char* ESP32_TOKEN   = "...";  // painel → Armários → Matriz → ESP
const bool RELE_ATIVO_LOW = true;   // placa BESTER 8ch
```

Token: painel **Armários → ELEVA Locker Matriz → ESP Matriz 8ch** ou `python tools/diagnostico_bancada.py --token SEU_TOKEN`.

## Backup .ino no disco D:

Recomendado: **uma pasta por placa** com token próprio:

```
firmware/elevalocker_matriz/elevalocker_matriz.ino
firmware/elevalocker_bancada2/elevalocker_bancada2.ino
```

Backup automático para `D:\ElevaLockerBackup\firmware\`:

```cmd
tools\backup_firmware_esp.bat
```

Ou junto com o backup completo:

```cmd
tools\backup_obrigatorio.bat
tools\backup_disco_d.bat
```

Cada ESP ganha subpasta com `.ino`, `ficha.txt` (IP, token, RELE_ATIVO_LOW) e cópia datada.
