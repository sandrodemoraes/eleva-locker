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

> **Atualização (contexto Sandro):** a ideia principal de câmera ao vivo **não é no locker de condomínio**. É colocar câmeras em **pontos turísticos**, começando pelo prédio de 4 andares em construção em **Lauro Müller/SC**, com vista para a **Serra do Rio do Rastro**.  
> Ver análise completa na **Seção 6**. O restante da Seção 2 continua válido para marketing do Eleva Locker (demo/lab), separado da estratégia turística.

### 2.1 A ideia em uma frase

**(A) Turismo:** transmitir paisagens ao vivo (Serra do Rio do Rastro e outros pontos) no YouTube e no site.  
**(B) Produto Eleva Locker:** prova visual controlada em lab/demo (não stream 24/7 em condomínio real).

### 2.2 Veredito

**Câmera turística 24/7 na Serra: ideia forte e viável.**  
**Câmera 24/7 em locker real de condomínio: continuar evitando.**

Para o Eleva Locker em si, o que vale é um **modelo híbrido de prova ao vivo controlada**, não um “Big Brother do armário”.

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
- [ ] Uso do prédio de 4 andares em Lauro Müller (comercial, pousada, misto, sede)?  
- [ ] A vista da serra é limpa do terraço/cobertura ou depende de andar específico?  
- [ ] Marca da webcam: Eleva Locker, marca turística própria, ou white-label da cidade?

---

## 6. Câmeras em pontos turísticos — Serra do Rio do Rastro (Lauro Müller/SC)

### 6.1 O que muda com o novo contexto

Você está construindo um **prédio de 4 andares** com vista bonita para a Serra do Rio do Rastro. A proposta é usar isso (e depois outros pontos turísticos) para transmitir ao vivo no YouTube e no site.

Isso **não é** a ideia frágil de stream do locker. É o modelo clássico e comprovado de **webcam turística / clima ao vivo**, usado por hotéis, prefeituras e destinos no Brasil (ex.: Clima ao Vivo / Destino:On, resorts, parques).

### 6.2 Veredito revisado

| Aspecto | Nota | Comentário |
|---------|------|------------|
| Potencial de audiência | 9/10 | Serra do Rio do Rastro é cartão-postal nacional |
| Diferenciação do seu ângulo | 8/10 | Maioria das cams olha a SC-390 do topo; você está na base (Lauro Müller) olhando a serra |
| Viabilidade técnica (seu perfil) | 9.5/10 | CFTV + rede + energia solar = stack nativa sua |
| LGPD / jurídico | 8/10 | Paisagem pública de propriedade privada é bem mais simples que hall de condomínio |
| Monetização | 7.5/10 | Forte se o prédio tiver uso turístico/comercial; fraca se for só “câmera solta” |
| Sinergia com Eleva Locker | 6.5/10 | Bom como marca-mãe/ecossistema; não misturar demais na 1ª dobra do site do locker |
| Timing da obra | 9/10 | Melhor momento para prever infraestrutura (eletrodutos, PoE, mast, link) |

**Conclusão:** siga com a câmera turística. É uma das melhores aplicações possíveis da sua ideia original de “ao vivo no YouTube + site”.

### 6.3 Concorrência / cenário atual

Já existem referências de câmera da Serra (ex.: portais tipo “Serra do Rio do Rastro ao Vivo”, agregadores WorldCam / Cameras do Mundo). Muitas ficam **offline com frequência**.

Oportunidade:
1. **Confiabilidade 24/7** (uptime) — quem entrega stream estável vira referência  
2. **Ângulo da base (Lauro Müller)** — narrativa diferente do mirante de cima  
3. **Experiência própria** — clima + amanhecer/pôr do sol + neve/neblina + overlay profissional  
4. **Integração local** — parceria com prefeitura/turismo de Lauro Müller (`turismo.lauromuller.sc.gov.br`)

### 6.4 Modelo de negócio recomendado

Não trate a câmera só como “enfeite do Eleva Locker”. Trate como **ativo de mídia do destino**, ancorado no seu prédio.

```
Prédio 4 andares (Lauro Müller)
        │
        ├─ Webcam panorâmica Serra (YouTube 24/7 + site)
        ├─ Página "Serra ao Vivo" (SEO forte)
        ├─ Overlay: temperatura, vento, hora, logo
        │
        ├─ Monetização direta
        │    ├─ Parceria hotel/pousada/restaurante (mention + link)
        │    ├─ Prefeitura / Secretaria de Turismo
        │    ├─ Patrocínio local (vinícola, café colonial, guias)
        │    └─ Se o prédio for hospedagem/comercial: CTA de reserva
        │
        └─ Monetização indireta
             ├─ Autoridade técnica (CFTV/IoT/redes) na região
             ├─ Soft brand Eleva / sua empresa
             └─ Funil para outros produtos (locker, solar, segurança)
```

#### Três arquiteturas de marca (escolha uma)

| Opção | Como funciona | Quando usar |
|-------|---------------|-------------|
| **A. Marca destino** | Site `serradoriodorastro...` / “Lauro Müller Ao Vivo” | Máximo SEO turismo |
| **B. Marca Eleva View / Eleva Cam** | Submarca de mídia/turismo | Se quiser escalar vários pontos turísticos |
| **C. Soft brand Eleva Locker** | Rodapé “tecnologia Eleva” | Só se quiser amarrar ao locker; menos ideal na 1ª dobra |

**Recomendação:** **Opção B** (submarca de câmeras/turismo) + menção técnica Eleva.  
O locker continua com site próprio. A webcam puxa público de viagem; o locker puxa B2B. Misturar na mesma home enfraquece os dois.

### 6.5 Por que o prédio de 4 andares é um ativo estratégico

Enquanto a obra está aberta, você pode (e deve) prever:

| Item na obra | Por quê |
|--------------|---------|
| Eletroduto dedicado câmera → rack | Evita gambiarra depois |
| Ponto PoE no terraço/cobertura + 1 spare | PTZ + fixa |
| Mast/poste curto ou suporte anti-vento | Serra = vento forte |
| Link dedicado ou VLAN câmera | Não misturar com Wi-Fi de obra/hóspedes |
| Nobreak + proteção surto | Quedas típicas do interior |
| Opcional: solar + bateria no topo | Autonomia / showcase da sua expertise |
| Shaft/passagem para fibra | Escalabilidade (2ª/3ª câmera, AP, sensor meteo) |

**Regra de ouro da obra:** se a vista melhor está no 4º andar/cobertura, projete **sala técnica pequena + acesso seguro à cobertura** agora.

### 6.6 Arquitetura técnica sugerida (ponto turístico)

#### Hardware

| Função | Sugestão | Nota |
|--------|----------|------|
| Câmera principal | PTZ IP outdoor (Intelbras/Hik equivalente) com bom zoom óptico | Para enquadrar a serra e “passear” no cenário |
| Câmera secundária | Bullet/dome fixa wide | Plano aberto estável 24/7 |
| Iluminação | Nenhuma agressiva na paisagem; ir/sensibilidade boa | Evitar poluição luminosa |
| Rede | MikroTik + VLAN + QoS priorizando upload do stream | Seu terreno |
| Encoder/relay | Mini PC ou NUC com MediaMTX / OBS | YouTube RTMP |
| Clima | Sensor temp/umidade/vento (ou API OpenWeather no overlay) | Aumenta utilidade da página |
| Energia | Nobreak + DPS; solar opcional | Diferencial “sempre no ar” |

#### Software / distribuição

1. **YouTube Live 24/7** (canal “Serra do Rio do Rastro Ao Vivo — Lauro Müller”)  
2. **Site próprio** com embed + previsão + “como chegar” + parceiros  
3. **Replicação** em agregadores (Cameras do Mundo, etc.) quando estável  
4. **Gravação local** (timelapse nascer do sol / neve) → Shorts/Reels

#### Overlay profissional (obrigatório)

- Nome do local  
- Data/hora  
- Temperatura  
- “Lauro Müller — SC”  
- Logo discreto da submarca  
- QR/URL do site  

Isso transforma stream em **mídia**, não webcam amadora.

### 6.7 Conteúdo que realmente performa aqui

A Serra tem picos naturais de interesse:

| Momento | Por que viraliza |
|---------|------------------|
| Neblina subindo/descendo | Drama visual |
| Possibilidade de neve no inverno | Busca nacional |
| Nascer/pôr do sol | Timelapse + Shorts |
| Fim de semana / feriados | Turista decide se sobe |
| Alerta de visibilidade (“vale a pena ir hoje?”) | Utilidade real |

**Produto de conteúdo paralelo (alto ROI):**  
- Short diário automático “Serra agora”  
- Live especial quando neve/geada  
- Parceria com guias e pousadas nos comentários fixados

### 6.8 Relação com Eleva Locker (como conectar sem misturar)

| Camada | Onde | Mensagem |
|--------|------|----------|
| Turismo | Site/canal da serra | “Veja a Serra ao vivo” |
| Autoridade técnica | Sobre / rodapé | “Operado com infraestrutura Eleva” |
| Cross-sell leve | Página institucional Eleva | “Também operamos mídia IoT e CFTV em campo” |
| Produto locker | Site Eleva Locker | Continua B2B condomínio/empresa |

Não coloque a webcam da serra como hero do site do locker. Use como **prova de capacidade IoT em campo real** e ímã de marca regional.

### 6.9 Riscos específicos deste projeto (e mitigações)

| Risco | Mitigação |
|-------|-----------|
| Ângulo da base menos “postal clássico” que o mirante de cima | Validar enquadramento com fotos/teste antes de fixar suporte; usar PTZ |
| Vento / chuva / umidade na cobertura | Câmera IP66/67, suporte reforçado, passagem de cabo estanque |
| Link de internet fraco no prédio | Link dedicado ou rádio; bitrate adaptativo 2–4 Mbps H.264/H.265 |
| Stream cai e queima reputação | Watchdog + reboot automático + alerta Telegram/WhatsApp |
| Vizinhos / ângulo pega área privada | Enquadramento só na serra/horizonte; sem zoom em casas |
| Concorrente já estabelecido | Competir em uptime, overlay, ângulo Lauro Müller e parceria oficial com turismo |

### 6.10 Roadmap prático (obra + mídia)

#### Agora (durante a construção)
1. ☐ Definir ponto exato da câmera (cobertura/4º andar) com fotos de teste em manhã, tarde e dia nublado  
2. ☐ Prever eletrodutos, PoE, nobreak, mast  
3. ☐ Reservar nome/canal: ex. “Serra Rio do Rastro Ao Vivo” + domínio próprio  
4. ☐ Alinhar com Secretaria de Turismo de Lauro Müller (carta de apoio / parceria)

#### Quando o ponto físico estiver pronto (mesmo antes do prédio 100%)
5. ☐ Instalar 1 câmera fixa ou PTZ piloto  
6. ☐ Subir YouTube Live 24/7  
7. ☐ Página simples com embed + clima + CTA WhatsApp parceiros  
8. ☐ Timelapse e Shorts nas primeiras semanas

#### Escala (pontos turísticos)
9. ☐ 2ª câmera (outro mirante / outro atrativo da região)  
10. ☐ Rede “Eleva Cam / Eleva View” multi-destino  
11. ☐ Pacote comercial para pousadas e prefeituras (“sua cidade ao vivo”)

### 6.11 Avaliação final desta versão da ideia

**Sim — essa é a versão certa da sua ideia de câmeras ao vivo.**

Você junta:
- um destino com demanda real de “como está a serra agora?”  
- um imóvel próprio em construção (controle total do ponto)  
- competência técnica rara na região (CFTV, rede, energia)  
- potencial de mídia contínua com baixo custo operacional depois de instalado  

O Eleva Locker continua como produto B2B. A webcam da serra vira **mídia e vitrine tecnológica** — e, se o prédio tiver uso turístico/comercial, vira também **máquina de atração de público**.

### 6.12 Perguntas que definem o desenho final

1. O prédio será pousada/hotel, comercial, residencial ou sede da empresa?  
2. A vista limpa da serra é do terraço inteiro ou só de um lado/ângulo?  
3. Já tem previsão de link de internet (fibra) na obra? Qual upload real?  
4. Quer parceria oficial com a prefeitura desde o dia 1?  
5. Prefere marca turística própria ou submarca Eleva para escalar outros pontos?
