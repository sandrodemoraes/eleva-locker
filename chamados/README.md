# Eleva Chamados

Substitui o Keep no fluxo de campo → escritório.

## Como usar

1. No celular (Chrome), abra o app e toque em **Falar chamado**.
2. Diga o essencial: cliente, telefone, endereço, serviço (câmeras, alarme, elétrica, solar…) e urgência.
3. Revise os campos e toque em **Enviar para o escritório**.
4. No escritório, abra a aba **Escritório**, copie o texto e marque **Nota feita**.

## Desenvolvimento

```bash
cd chamados
npm install
env -u DATABASE_URL npm run dev
```

App em `http://127.0.0.1:3000`.

## Stack

- Next.js + Postgres (PGlite local / Postgres na publicação)
- Ditado por voz via Web Speech API (`pt-BR`)
