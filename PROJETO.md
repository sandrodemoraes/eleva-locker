# ELEVA LOCKER

Sistema inteligente de armários para recebimento e retirada de encomendas.

## Documentação completa

Consulte **[docs/PROJETO.md](docs/PROJETO.md)** para:

- Visão comercial e modelo B2B2C
- Arquitetura técnica e IoT (ESP32)
- Modelo de dados expandido (planos, contratos, faturas)
- Módulos operacionais e comerciais
- Roadmap por fases
- KPIs e fluxos de negócio

## Status atual (v0.2)

| Módulo | Status |
|--------|--------|
| Autenticação | ✅ |
| Usuários | ✅ |
| Empresas | ✅ |
| Armários | ⚠️ Schema only |
| Compartimentos | ⚠️ Schema only |
| Encomendas | ⚠️ Schema only |
| ESP32 | ⚠️ Schema only |
| Backup automático | ✅ |

## Próximo passo recomendado

**Fase 1:** CRUD de Armários + Compartimentos + Encomendas (fluxo depósito/retirada manual).

## Estrutura

```
ELEVALOCKER/
├── app.py
├── database.py
├── docs/PROJETO.md      ← Documento mestre
├── routes/
├── services/
├── repositories/
├── templates/
└── static/
```

## Porta padrão

15000
