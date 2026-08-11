# Teste ESP32 offline (sem servidor)

> Retirada funciona na ESP mesmo com o PC/servidor desligado — usando cache de códigos sincronizado antes.

## Pré-requisitos

1. Pelo menos **1 depósito** feito com servidor online (código gravado na ESP)
2. Firmware `firmware/elevalocker_sync/elevalocker_sync.ino` gravado
3. ESP com WiFi configurado (mesma rede do armário)

## Passo a passo

### 1. Sincronizar códigos (servidor LIGADO)

```cmd
cd C:\ElevaLocker
python app.py
```

1. Deposite uma encomenda de teste (telefone fictício OK)
2. Confirme ESP **online** em Armários → ESP Matriz
3. A ESP puxa códigos via `GET /api/esp32/sync` automaticamente

### 2. Testar retirada online (opcional)

- Totem: http://192.168.16.130:15000/totem/3
- Ou ESP local: http://192.168.16.162/ → campo código

### 3. Desligar só o servidor

```cmd
Ctrl+C   (na janela do python app.py)
```

**Não desligue** o roteador nem a ESP. O WiFi da ESP pode continuar ligado.

### 4. Retirar offline na ESP

1. Abra no celular/PC: **http://192.168.16.162/**
2. Digite o **código de 6 dígitos** (o morador recebeu no WhatsApp — operador não vê no painel)
3. A porta deve **abrir localmente** (relé aciona)
4. A ESP grava o evento na fila interna

### 5. Religar servidor e sincronizar

```cmd
tools\iniciar_tudo.bat
```

A ESP envia a fila via `POST /api/esp32/eventos` quando detecta o servidor de novo.  
No painel, a encomenda deve aparecer como **retirada**.

## O que funciona offline

| Ação | Offline? |
|------|----------|
| Retirar com código já sincronizado | ✅ |
| Abrir porta (relé) | ✅ |
| Depositar nova encomenda | ❌ (precisa servidor) |
| Enviar WhatsApp | ❌ |
| Totem web (`/totem`) | ❌ (precisa Flask) |

## Totem no tablet (precisa servidor)

Configure o tablet em modo kiosk apontando para:

```
http://192.168.16.130:15000/totem/3
```

(substitua `3` pelo ID do armário Matriz)

## Diagnóstico

```cmd
python tools/diagnostico_bancada.py --token SEU_TOKEN
curl http://192.168.16.162/status?token=SEU_TOKEN
```

## Segurança do código

- **Operador/depositante** não vê código nem QR no painel — só o morador recebe no WhatsApp
- **Administrador** ainda pode ver código/QR para suporte

## Problemas comuns

| Sintoma | Solução |
|---------|---------|
| Código inválido offline | Deposite de novo com servidor online; espere sync (~30s) |
| ESP não abre | Confira IP, token no firmware, relé GPIO |
| Retirada offline não aparece no painel | Servidor estava off — ligue e espere sync eventos |
| Totem sem conexão | Normal offline — use ESP local ou ligue servidor |
