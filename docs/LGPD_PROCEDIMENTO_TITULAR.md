# LGPD — Procedimento de atendimento ao titular (Fase 3)

**Versão:** 2026-08-31  
**Canal:** Portaria / administrador ELEVA LOCKER  
**Painel:** `/lgpd/admin/titular` (requer `LGPD_TITULAR_ATIVO=1` e perfil Administrador)

---

## Quando usar

Morador ou operador solicita, via portaria:

- **Acesso** aos dados pessoais (Art. 18, II)
- **Portabilidade** (Art. 18, V) — export CSV/JSON
- **Exclusão / anonimização** (Art. 18, VI)
- **Oposição** a marketing futuro (Art. 18, § 2º)

Correção de cadastro continua em **Usuários → Editar** (CRUD normal).

---

## Passo a passo (operador admin)

1. Confirmar identidade do solicitante (documento, unidade, telefone cadastrado).
2. Abrir **LGPD Titular** no menu lateral (ou Configurações → link Fase 3).
3. Escolher tipo:
   - **Usuário** — morador/operador cadastrado (ID em Usuários)
   - **Encomenda** — dados de uma entrega específica (ID em Encomendas)
4. Informar o **ID** e clicar **Consultar**.
5. Executar a ação:
   - **Exportar JSON** ou **CSV** — entregar arquivo ao titular/portaria
   - **Anonimizar** — remove PII; **não apaga** encomenda (estatísticas/auditoria)
   - **Oposição marketing** — só usuário; bloqueia marketing futuro

Toda ação gera registro em `lgpd_solicitacoes` e em **Logs**.

---

## Anonimização — o que muda

| Campo | Antes | Depois |
|-------|-------|--------|
| Nome / cliente | João Silva | `*** ANONIMIZADO ***` |
| Telefone | (48) 99999-9999 | `*** ANONIMIZADO ***` |
| E-mail | joao@email.com | `anonimizado_{id}@anon.elevalocker.local` (usuário) ou anonimizado (encomenda) |

**Não anonimizar:**
- Administrador do sistema
- Encomenda **aguardando retirada** (retire ou conclua antes)

**Usuário:** encomendas vinculadas pelo mesmo telefone/e-mail também são anonimizadas.

---

## WhatsApp / Evolution

- Anonimizar no ELEVA **não apaga** histórico no celular/WhatsApp do morador.
- Próximas notificações **não enviam** — telefone anonimizado falha na validação.

---

## Rollback

Desligar módulo sem perder dados:

```env
LGPD_TITULAR_ATIVO=0
```

Reiniciar `INICIAR.bat`. Menu some; dados e registros permanecem no banco.

---

## Checklist após atendimento

- [ ] Solicitação registrada em LGPD Titular → Solicitações recentes
- [ ] Log em **Logs** do painel
- [ ] Arquivo exportado entregue (se acesso/portabilidade)
- [ ] Totem e WhatsApp testados (operacao normal)

---

*Documento operacional — revisar com advogado/DPO quando aplicável.*
