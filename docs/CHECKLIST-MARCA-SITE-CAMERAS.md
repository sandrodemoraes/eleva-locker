# Eleva Locker — Checklist de Marca, Site e Câmeras ao Vivo

Documento de consultoria estratégica e técnica.
Atualizado: 2026-08-06

---

## 1. Checklist de proteção da marca

### 1.1 Domínios (fazer primeiro — esta semana)

| Prioridade | Domínio | Ação | Status |
|------------|---------|------|--------|
| P0 | `elevalocker.com.br` | Registrar no Registro.br | ☐ |
| P0 | `elevalocker.com` | Registrar (Namecheap / Cloudflare / Registro.br parceiro) | ☐ |
| P1 | `elevalocker.it` | Registrar (NIC.it / registrar IT) — expansão UE | ☐ |
| P2 | `eleva-locker.com` | Defensivo | ☐ |
| P2 | `elevalocker.net` | Defensivo | ☐ |

**E-mails profissionais após domínio:**
- `contato@elevalocker.com.br`
- `comercial@elevalocker.com.br`
- `suporte@elevalocker.com.br`

**DNS recomendado:** Cloudflare (DNS + CDN + proteção básica).

---

### 1.2 Redes sociais (mesmo dia dos domínios)

| Canal | Handle sugerido | Status |
|-------|-----------------|--------|
| Instagram | `@elevalocker` | ☐ |
| YouTube | `@ElevaLocker` | ☐ |
| LinkedIn | Empresa Eleva Locker | ☐ |
| Facebook | Eleva Locker | ☐ |
| TikTok | `@elevalocker` (opcional) | ☐ |
| WhatsApp Business | número comercial + catálogo | ☐ |

---

### 1.3 Marca no INPI (Brasil)

**Tipo:** marca mista (nome + logo) **e**, se possível, nominativa “ELEVA LOCKER”.

**Classes Nice sugeridas:**

| Classe | Cobertura | Por quê |
|--------|-----------|---------|
| **9** | Sistemas eletrônicos, IoT, software embarcado, câmeras, controle de acesso | Core técnico do produto |
| **20** | Armários, móveis metálicos, compartimentos | Hardware físico |
| **39** | Armazenamento, logística de encomendas, entrega | Serviço operacional |
| **42** | Software como serviço (SaaS), plataforma web, API | Sistema Flask / cloud |

**Passo a passo INPI:**

1. ☐ Criar conta gov.br + acesso e-INPI  
2. ☐ Pesquisa de anterioridade no pePI (marcas “ELEVA”, “LOCKER”, “ELEVALOCKER”, “ELEVA LOCKER”)  
3. ☐ Definir apresentação: nominativa e/ou mista  
4. ☐ Redigir especificação de produtos/serviços por classe  
5. ☐ Emitir GRU e protocolar pedido  
6. ☐ Acompanhar RPI (Revista da Propriedade Industrial) por oposições  
7. ☐ Após concessão: uso efetivo + renovação (10 anos)

**Observação:** a pesquisa oficial no pePI deve ser refeita no dia do protocolo (a busca web anterior não substitui o pePI).

---

### 1.4 Europa (EUIPO / Itália)

| Etapa | Ação | Status |
|-------|------|--------|
| 1 | Busca no [TMview](https://www.tmdn.org/tmview/) por ELEVA LOCKER / ELEVALOCKER / ELEVA | ☐ |
| 2 | Atenção especial à marca **ELEVA (Arken Group – IT)** — armários fitness | ☐ |
| 3 | Decidir: marca da UE (EUIPO) vs. só Itália (UIBM) | ☐ |
| 4 | Protocolar nas mesmas classes (9, 20, 39, 42) se o posicionamento for produto+serviço+software | ☐ |
| 5 | Avaliar Madrid Protocol depois, se expandir além da UE | ☐ |

**Recomendação de timing:**  
- Domínios + redes: **agora**  
- INPI: **nas próximas 2–4 semanas** (assim que logo estiver estável)  
- EUIPO: quando houver piloto comercial ou proposta firme na Itália (evita custo prematuro, mas não espere lançar lá sem marca)

---

### 1.5 Empresa / contratos

| Item | Status |
|------|--------|
| Nome fantasia “Eleva Locker” no CNPJ / alteração contratual | ☐ |
| Cláusula de propriedade intelectual em contratos com equipe | ☐ |
| Termo de uso da marca em propostas comerciais | ☐ |
| Política de marca (como escrever: Eleva Locker, não ElevaLocker em textos oficiais — definir padrão) | ☐ |

**Padrão sugerido de escrita:**
- Marca: **Eleva Locker**
- Domínio/handle: `elevalocker`
- Código/repo: `eleva-locker` / `ElevaLocker`

---

## 2. Análise profunda: site + câmeras ao vivo (YouTube + site)

### 2.1 A ideia em uma frase

Usar câmeras ao vivo no Eleva Locker (e/ou no processo de fabricação/instalação) para transmitir no YouTube e embutir no site institucional, gerando transparência, prova social e conteúdo de marketing.

### 2.2 Veredito

**A direção é boa. A execução 24/7 com câmera aberta no locker real de condomínio é arriscada e, na maioria dos casos, errada.**

O que vale a pena é um **modelo híbrido de prova ao vivo controlada**, não um “Big Brother do armário”.

| Modelo | Recomendação | Motivo |
|--------|--------------|--------|
| Câmera 24/7 em locker de condomínio real | **Não** | LGPD, segurança física, baixo engajamento, risco jurídico |
| Câmera 24/7 em unidade demo (showroom/lab) | **Sim, com regras** | Controle total de imagem e narrativa |
| Lives agendadas (instalação, testes, demos) | **Sim — prioridade** | Alto valor comercial, conteúdo editável |
| Cliques curtos automáticos (evento → clipe) | **Sim — melhor custo/benefício** | Escala sem streaming contínuo caro |
| Dashboard público de métricas (sem vídeo de pessoas) | **Sim** | Transparência sem risco de privacidade |

---

### 2.3 Por que a ideia é forte (o que acerta)

1. **Mercado B2B confia em prova visual**  
   Síndico, administradora e construtora compram menos por “promessa de app” e mais por ver o equipamento funcionando: entrega → notificação → retirada.

2. **Diferenciação real no Brasil**  
   Concorrentes (Meu Locker, BoxLocker, Clique Retire, CondoLocker) vendem página institucional + cases. Poucos mostram operação com transparência técnica. Você, com background em CFTV/Intelbras + IoT, consegue isso de forma autêntica.

3. **Funil de conteúdo YouTube**  
   Canal bem posicionado (“smart locker condomínio”, “armário inteligente encomendas”, “ESP32 locker”) gera leads orgânicos por meses.

4. **Alinhamento com expansão Europa**  
   Conteúdo técnico em PT + legendas IT/EN acelera credibilidade sem equipe de marketing grande.

5. **Sinergia com seu DNA**  
   Você já domina CFTV, rede, MikroTik, energia. Câmera + streaming + NVR/VPS é competência interna — custo menor que terceirizar.

---

### 2.4 Por que a versão “câmera ao vivo o tempo todo” é frágil

#### A) Jurídico / LGPD (bloqueador)

Imagens de:
- entregadores
- moradores
- rostos
- etiquetas de encomenda (nome, endereço, código)
- número de apartamento

são **dados pessoais** (e às vezes sensíveis no contexto de segurança).

Riscos:
- Base legal frágil para transmissão pública contínua  
- Necessidade de aviso, política de privacidade, DPIA na prática  
- Condomínio precisa autorizar em assembleia/administradora  
- Multa LGPD + ação civil se vazamento/uso indevido  
- Na UE/Itália: **GDPR** ainda mais rígido (se stream for acessível na Europa, a análise de transferência/aplicabilidade aparece cedo)

#### B) Segurança física (bloqueador operacional)

Stream público ensina o atacante:
- horários de pico de entrega
- padrão de abertura das portas
- se há ou não gente na área
- layout do hall / pontos cegos
- falhas de iluminação

**Smart locker + câmera pública = mapa de oportunidade.**  
Isso destrói o argumento comercial de “segurança”.

#### C) Marketing / engajamento (bloqueador de ROI)

Locker fica parado 90%+ do tempo. Stream 24/7 vira:
- tela vazia
- retenção baixa no YouTube
- algoritmo não impulsiona “nada acontecendo”
- custo de banda/encoder sem retorno

YouTube recompensa **vidas com pico de ação** e **VODs editados**, não webcam ociosa.

#### D) Operacional

- Quedas de internet no condomínio  
- IP público / CGNAT / firewall  
- Manutenção de encoder (MediaMTX, OBS, YouTube Live key)  
- Moderação de chat  
- Consumo elétrico e ponto de falha a mais no produto

---

### 2.5 Modelo recomendado (arquitetura de conteúdo)

```
┌─────────────────────────────────────────────────────────┐
│  UNIDADE DEMO / LAB (sua empresa)                       │
│  - Locker real + ESP32 + app                            │
│  - 1–2 câmeras Intelbras (ângulo controlado)            │
│  - Sem rostos de terceiros / sem etiquetas reais        │
└───────────────────────┬─────────────────────────────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
   Live agendada    Clipe evento   Bastidores
   (YouTube)        (webhook)      (instalação)
          │             │             │
          └─────────────┼─────────────┘
                        ▼
              Site Eleva Locker
         (embed + cases + CTA WhatsApp)
```

#### Camada 1 — Prova ao vivo controlada (recomendado começar aqui)

- **1 live semanal ou quinzenal** (30–45 min):  
  “Demo Eleva Locker: depósito → WhatsApp/código → retirada”  
- Ângulo de câmera só no equipamento (evitar faces)  
- Pacotes fake / caixas neutras  
- Link permanente no site: “Próxima live” + replay

#### Camada 2 — Clipe automático por evento (melhor engenharia)

No firmware/backend, ao eventos `DEPOSITO` / `RETIRADA`:
1. Câmera local grava 10–20 s (buffer pré/pós)
2. Sistema anonimiza (blur face se necessário — OpenCV/frigate)
3. Publica short no YouTube/Instagram **ou** só no painel do cliente do condomínio

Isso é moderno, eficiente e vende melhor que webcam 24/7.

#### Camada 3 — Transparência sem vídeo sensível

No site, página pública:
- uptime do lab
- tempo médio abertura
- nº de ciclos de teste na semana
- foto do hardware (não stream de pessoas)

Ex.: “1.284 ciclos de abertura testados este mês”

#### Camada 4 — Câmera interna do produto (para o condomínio, não para o YouTube)

Câmera **dentro/sobre o locker** para auditoria do síndico:
- acesso autenticado no painel Eleva Locker
- retenção 7–30 dias
- **nunca** público

Isso é feature de produto (você já tem expertise Intelbras). Separe mentalmente:

| Uso | Público? | Onde |
|-----|----------|------|
| Marketing / YouTube | Sim | Lab/demo controlado |
| Auditoria condomínio | Não | Painel privado do cliente |
| Stream 24/7 hall real | Não | Evitar |

---

### 2.6 Stack técnica sugerida (custo-benefício)

**Para lives e demo lab:**

| Componente | Opção recomendada | Alternativa |
|------------|-------------------|-------------|
| Câmera | Intelbras VIP / iM4 / equivalente PoE | USB + PC se lab simples |
| Encoder / relay | [MediaMTX](https://github.com/bluenviron/mediamtx) em Mini PC/NUC | OBS Studio manual |
| Destino live | YouTube Live (RTMP) | Cloudflare Stream (pago, mais controle) |
| Embed no site | YouTube iframe / API | HLS próprio só se necessário |
| Gravação local | Frigate NVR ou Intelbras NVR | Blue Iris (Windows) |
| Evento → clipe | webhook Flask + ffmpeg | Node-RED na borda |

**Arquitetura mínima viável (fase 1):**
1. 1 câmera fixa no lab  
2. Mini PC com OBS ou MediaMTX  
3. YouTube Live key  
4. Página do site com embed + CTA WhatsApp  
5. Agenda de lives no Instagram/LinkedIn  

**Custo estimado fase 1:** baixo (você já tem câmeras/know-how). O gargalo é processo e jurídico, não hardware.

---

### 2.7 Site institucional — o que deve ter (e o que não)

O site **não** deve nascer como dashboard. Primeira dobra = marca + promessa + prova.

#### Estrutura recomendada (1 job por seção)

1. **Hero** — marca Eleva Locker + 1 frase + CTA (WhatsApp / demo) + visual do produto (full-bleed)  
2. **Como funciona** — 3 passos (deposita → notifica → retira)  
3. **Prova ao vivo / demos** — próximas lives + replays (embed YouTube)  
4. **Para quem é** — condomínios, empresas, hotéis (sem cards decorativos vazios)  
5. **Tecnologia** — offline-first, ESP32, segurança, CFTV integrado (seu diferencial)  
6. **Cases / piloto** — fotos reais de instalação  
7. **Contato comercial**

#### Separação importante

| Sistema | Função |
|---------|--------|
| **Site marketing** (`elevalocker.com.br`) | Venda, marca, conteúdo, SEO |
| **App/painel** (Flask porta 15000) | Operação do locker, usuários, empresas |

Não misturar painel administrativo com site público na mesma UX. Podem compartilhar backend depois; front deve ser separado.

#### SEO / crescimento

Conteúdos que convertem no BR:
- “Smart locker para condomínio”
- “Armário inteligente de encomendas”
- “Locker com câmera e auditoria”
- “Alternativa a portaria sobrecarregada”

YouTube vira motor; o site captura o lead.

---

### 2.8 Matriz de decisão

| Critério | Stream 24/7 condomínio | Lab + lives + clipes |
|----------|------------------------|----------------------|
| LGPD/GDPR | Ruim | Bom |
| Segurança do cliente | Ruim | Bom |
| Engajamento YouTube | Ruim | Bom |
| Custo contínuo | Médio/Alto | Baixo/Médio |
| Credibilidade técnica | Média | Alta |
| Diferencial comercial | Frágil | Forte |
| Complexidade | Alta | Média |
| Alinhado à expansão IT/UE | Problemático | Adequado |

**Escolha recomendada:** Lab + lives + clipes por evento + câmera privada como feature do produto.

---

### 2.9 Roadmap sugerido

#### Fase A — Proteção (semana 1)
- Domínios + redes  
- Nome padrão da marca  
- Canal YouTube criado (mesmo sem vídeo)

#### Fase B — Site MVP (semanas 1–3)
- 1 página institucional forte  
- CTA WhatsApp  
- Seção “Demos / Ao vivo” (mesmo que ainda com “Em breve” + 1 vídeo gravado)  
- Política de privacidade básica

#### Fase C — Prova visual (semanas 2–6)
- Montar locker demo filmável  
- 1 vídeo demo profissional (não precisa agência; roteiro técnico seu)  
- 1ª live no YouTube  
- Embed no site

#### Fase D — Produto (paralelo)
- Câmera de auditoria **privada** no painel do condomínio  
- Retenção, permissões, LGPD by design  
- Evento → clipe interno (síndico)

#### Fase E — Escala
- Shorts semanais  
- Cases reais (com autorização de imagem do condomínio)  
- INPI protocolado  
- Avaliar EUIPO

---

## 3. Avaliação final da sua ideia

### O que manter
- Site próprio com marca forte  
- YouTube como canal de prova e educação  
- Uso de câmeras — você tem vantagem competitiva real nisso  
- Transparência técnica como posicionamento (“vemos o que vendemos”)

### O que ajustar
- De **câmera pública 24/7 no condomínio** para **prova ao vivo controlada no lab + lives agendadas**  
- Separar **marketing** de **auditoria de segurança**  
- Tratar LGPD/GDPR como requisito de projeto, não detalhe jurídico depois

### O que adicionar (melhor que a proposta original)
1. Clipe automático por evento (ffmpeg + webhook)  
2. Dashboard público de métricas do lab (sem faces)  
3. Câmera privada no produto como argumento de venda para síndicos  
4. Conteúdo bilíngue PT/IT cedo (mesmo que só legendas)

### Nota geral da ideia

| Dimensão | Nota | Comentário |
|----------|------|------------|
| Potencial de marketing | 9/10 | Excelente se bem executado |
| Viabilidade técnica (você) | 9/10 | Stack dentro do seu domínio |
| Viabilidade jurídica da versão 24/7 pública | 3/10 | Evitar |
| Viabilidade do modelo híbrido recomendado | 8.5/10 | Caminho certo |
| Custo-benefício | 8/10 | Alto retorno com baixo CAPEX |
| Alinhamento BR + Itália | 8/10 | Desde que privacidade esteja correta |

**Conclusão:** a ideia de site + presença com câmeras/YouTube é estratégica e deve ser feita. A variante “ao vivo o tempo todo no ambiente real” deve ser descartada. A variante “demo controlada + lives + clipes + auditoria privada” é moderna, vendável e defensável tecnicamente.

---

## 4. Próximos passos concretos (quando autorizar execução)

1. Registrar domínios P0  
2. Definir logo mínimo (mesmo que tipográfico)  
3. Protocolar INPI (classes 9, 20, 39, 42)  
4. Criar site MVP marketing (separado do painel Flask)  
5. Montar canto de filmagem do locker demo  
6. Publicar 1º vídeo + agenda da 1ª live  
7. Desenhar feature “câmera de auditoria” no produto (não no YouTube)

---

## 5. Decisões pendentes (para alinharmos)

- [ ] Orçamento mensal de marketing (domínio + hosting + anúncios)  
- [ ] O site MVP será estático (HTML/CSS) ou Next.js / Flask templates públicos?  
- [ ] Já existe unidade física demo filmável?  
- [ ] Público-alvo inicial: só condomínios ou também empresas/hotéis?  
- [ ] Idioma do site na v1: só PT ou PT+IT?
