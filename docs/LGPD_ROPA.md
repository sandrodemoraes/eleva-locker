# ROPA — Registro de Operações de Tratamento (LGPD)

**Controlador:** ELEVA LOCKER — Matriz ELEVA  
**Versão:** 2026-08-30 (Fase 1)  
**Sistema:** `http://192.168.16.130:15000` · Totem armário id 2

---

## 1. Tratamento: operação de encomendas

| Campo | Detalhe |
|-------|---------|
| **Finalidade** | Depósito, armazenamento e retirada de encomendas |
| **Dados** | Nome, telefone, e-mail morador; código retirada; compartimento; datas |
| **Titulares** | Moradores / destinatários |
| **Base legal** | Execução de contrato / legítimo interesse |
| **Retenção** | Enquanto encomenda ativa + política interna pós-retirada (Fase 4) |
| **Compartilhamento** | WhatsApp (Evolution API) para código de retirada |
| **Medidas** | Acesso autenticado, backup D:, logs |

---

## 2. Tratamento: usuários do painel

| Campo | Detalhe |
|-------|---------|
| **Finalidade** | Autenticação e operação administrativa |
| **Dados** | Nome, e-mail, telefone, senha (hash), perfil |
| **Titulares** | Operadores, administradores |
| **Base legal** | Contrato / legítimo interesse |
| **Retenção** | Vigência do vínculo + logs |
| **Compartilhamento** | Não |

---

## 3. Tratamento: notificações

| Campo | Detalhe |
|-------|---------|
| **Finalidade** | Informar chegada e lembrete de encomenda; ajuda totem |
| **Dados** | Telefone/e-mail destino; conteúdo mensagem; status envio |
| **Titulares** | Moradores; portaria (ajuda) |
| **Base legal** | Execução do serviço |
| **Compartilhamento** | Evolution API (`eleva-locker`) |
| **Retenção** | Tabela `notificacoes` + histórico |

---

## 4. Tratamento: ajuda no totem

| Campo | Detalhe |
|-------|---------|
| **Finalidade** | Suporte morador (código, porta, dúvidas) |
| **Dados** | Armário, horário, IP origem, status WhatsApp |
| **Titulares** | Usuários do totem (não identificados nominalmente) |
| **Base legal** | Legítimo interesse / segurança |
| **Retenção** | `totem_ajuda_pedidos` — pendente até atendido |

---

## 5. Tratamento: logs e auditoria

| Campo | Detalhe |
|-------|---------|
| **Finalidade** | Segurança, troubleshooting, accountability |
| **Dados** | Usuário sistema, ação, data, compartimento |
| **Base legal** | Legítimo interesse |
| **Retenção** | A definir Fase 4 (`LGPD_RETENCAO_LOG_DIAS`) |

---

## 6. Encarregado / canal titular

| Canal | Valor |
|-------|--------|
| E-mail | `.env` → `LGPD_CONTATO_EMAIL` |
| Telefone | `.env` → `LGPD_CONTATO_TELEFONE` |
| Presencial | Portaria Matriz ELEVA |

---

## 7. Histórico de revisões

| Data | Alteração |
|------|-----------|
| 2026-08-30 | ROPA inicial — Fase 1 LGPD (documentação pública) |

---

*Documento interno. Revisar com assessoria jurídica quando expandir comercialmente.*
