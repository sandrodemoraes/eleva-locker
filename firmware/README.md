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
