# MANUAL DE DECOMPOSIÇÃO DE HABILIDADES BNCC EM ANDAIMES PEDAGÓGICOS

**Objetivo:** Ensinar como decompor uma habilidade BNCC em micro-habilidades para criar um CSV de entrada para um pipeline de geração de apostilas didáticas funcionais.

**Público:** Outro chatbot, professor, designer instrucional ou desenvolvedor que precisa replicar o processo.

**Versão:** 1.0 | Data: 2026-05-30

---

## PARTE 1: CONTEXTO E FUNDAÇÃO

### O que você precisa saber ANTES de começar

#### 1.1 O Pipeline Funcional

O projeto funciona assim:
```
Professor preenche CSV 
    ↓ 
Agente 1 lê CSV + andaime 
    ↓ 
Agente 1 cria "core" (estrutura de dados)
    ↓ 
Agente 2 lê core 
    ↓ 
Agente 2 cria texto funcional
    ↓ 
Agentes 3+ processam validação, estilo, diagramação
```

**Você está aqui:** Ajudando o professor a **preencher o CSV de forma inteligente**.

#### 1.2 O Novo Formato de CSV (desde 30 de maio de 2026)

Colunas obrigatórias:
- `disciplina` — ex: "Sociologia"
- `unidade` — ex: "Unidade 1 — Estrutura social e desigualdade"
- `pergunta_unidade` — pergunta central que governa toda a unidade
- `capitulo` — nome do capítulo
- `habilidade_principal` — código BNCC completo (ex: EM13CHS402)
- `micro_hab_1` a `micro_hab_4` (mínimo) até `micro_hab_6` (máximo) — uma por seção
- `operacao_secao_1` a `operacao_secao_6` — operação elementar de cada seção
- `conteudos_nucleares` — lista de tópicos a cobrir
- `autores` — lista de autores que podem ser usados
- `elementos_desejáveis` (opcional) — direcionamentos específicos

**Importante:** Cada linha do CSV = 1 capítulo. Cada capítulo = 4-6 seções. Cada seção = 1 micro-habilidade + 1 operação.

#### 1.3 As 7 Operações Elementares (seu vocabulário básico)

Você **só pode usar estas**:

| Operação | O que o aluno faz | Exemplo |
|----------|------------------|---------|
| **Definir** | Entender um conceito, modelo ou categoria com seus elementos essenciais | "Definir o que é classe social" |
| **Classificar** | Atribuir itens a categorias segundo critérios explícitos | "Classificar tipos de estratificação" |
| **Comparar** | Listar diferenças e semelhanças entre elementos em aspectos determinados | "Comparar visões de Marx, Weber e Bourdieu" |
| **Sequenciar** | Ordenar eventos no tempo, identificando anterioridade/posterioridade | "Sequenciar a Revolução Francesa em fases" |
| **Mapear causalidade** | Identificar relações de causa-consequência (X → Y) com evidência | "Mapear como a automação causa desemprego" |
| **Reconhecer perspectiva** | Identificar qual visão de mundo, interesse ou posição um texto/autor expressa | "Reconhecer a visão marxista vs. funcionalista" |
| **Aplicar** | Usar um conceito já aprendido para analisar um caso novo | "Aplicar o conceito de capital cultural a um exemplo atual" |

---

## PARTE 2: O PROCESSO — PASSO A PASSO

### PASSO 0: Entender a Habilidade BNCC

**O que fazer:**
1. Leia a habilidade BNCC completa (código + texto)
2. Extraia o **verbo principal** — é lá que está a operação
3. Pergunte-se: "O que o aluno deve ser capaz de fazer ao final?"

**Exemplo 1 (Sociologia):**
```
EM13CHS402 - Analisar e comparar indicadores de emprego, 
trabalho e renda em diferentes espaços, escalas e tempos, 
associando-os a processos de estratificação e desigualdade 
socioeconômica.

Verbo principal: ANALISAR E COMPARAR
O aluno deve ser capaz de: COMPARAR indicadores e explicar 
por que variam (causa-efeito).
Operação principal: APLICAR (análise de caso real) ou COMPARAR
```

**Exemplo 2 (Inclusão Social):**
```
EM13CHS5XX - Identificar estratégias que promovam formas 
de inclusão social.

Verbo principal: IDENTIFICAR
O aluno deve ser capaz de: RECONHECER qual estratégia é apropriada 
para um contexto (requer definir, classificar, depois aplicar).
Operação principal: APLICAR (escolher estratégia para caso)
```

---

### PASSO 1: Definir a Pergunta do Capítulo

**O que fazer:**
1. Reescreva a habilidade como uma **pergunta** que o capítulo responde
2. A pergunta deve ser respondível apenas APÓS toda a progressão de seções

**Exemplo 1:**
- Habilidade: "Analisar e comparar indicadores de emprego..."
- **Pergunta:** "Por que pessoas que nascem em posições sociais diferentes têm acesso desigual a emprego, renda e oportunidades?"

**Exemplo 2:**
- Habilidade: "Identificar estratégias que promovam inclusão social"
- **Pergunta:** "Quais estratégias promovem inclusão social e como escolher a mais apropriada para um contexto específico?"

**Critério de qualidade:** A pergunta deve ser impossível responder com um único conceito — exige síntese de múltiplos ângulos.

---

### PASSO 2: Mapear a Operação Principal

**O que fazer:**
1. Volte à habilidade e identifique qual das 7 operações é a **final** (aquela que encerra o aprendizado)
2. Essa será a operação da **Seção 4 ou 5** (as últimas)

**Exemplo 1:**
```
Habilidade: "Analisar e comparar indicadores..."
Verbos: analisar, comparar, associar-se
Mapeamento: 
  - "analisar" = APLICAR (usar conceito a dados)
  - "comparar" = COMPARAR (lado a lado)
  - "associar-se a processos" = MAPEAR CAUSALIDADE
Operação principal: APLICAR (porque é o mais desafiador — analisar dados reais)
```

**Exemplo 2:**
```
Habilidade: "Identificar estratégias que promovam inclusão"
Verbo: identificar
Mapeamento:
  - "identificar" poderia ser RECONHECER (qual estratégia)
  - ou APLICAR (escolher para um caso)
Operação principal: APLICAR (porque "identificar" implica escolher 
entre opções conforme contexto)
```

---

### PASSO 3: Construir a Progressão (4-6 seções)

**O que fazer:**
1. Comece com a operação **mais elementar** (Definir, Classificar ou Sequenciar)
2. Termine com a operação **principal** (aquela que responde à habilidade)
3. As operações intermediárias devem **construir para a final**

**Regra de progressão (do fácil ao difícil):**

```
NÍVEL 1 (mais fácil):    Definir, Classificar, Sequenciar
NÍVEL 2:                 Comparar, Mapear causalidade
NÍVEL 3 (mais difícil):  Reconhecer perspectiva, Aplicar
```

**Exemplo 1 — Estratificação social:**
```
Seção 1: Definir estratificação (DEFINIR)
  → O aluno entende o conceito-raiz

Seção 2: Classificar tipos (CLASSIFICAR)  
  → Aplica o conceito a diferentes sistemas

Seção 3: Comparar três visões (COMPARAR)
  → Vê múltiplos ângulos do mesmo fenômeno

Seção 4: Aplicar ao Brasil (APLICAR)
  → Responde à pergunta usando tudo que aprendeu
```

**Exemplo 2 — Inclusão social:**
```
Seção 1: Definir inclusão social (DEFINIR)
  → O aluno entende o objetivo

Seção 2: Classificar estratégias por tipo (CLASSIFICAR)
  → Identifica diferentes caminhos

Seção 3: Mapear como funcionam (MAPEAR CAUSALIDADE)
  → Entende os mecanismos

Seção 4: Reconhecer perspectivas de atores (RECONHECER PERSPECTIVA)
  → Vê que diferentes agentes têm diferentes estratégias

Seção 5: Aplicar a um caso (APLICAR)
  → Responde à pergunta escolhendo estratégia
```

---

### PASSO 4: Decompor em Micro-Habilidades

**O que fazer:**
1. Para cada seção, escreva uma **micro-habilidade** específica
2. A micro-habilidade começa com **UM VERBO** (não dois)
3. A micro-habilidade descreve **o que o aluno será capaz de fazer** após essa seção, não isoladamente

**Critério:**
- ✅ "Definir estratificação como sistema de posições desiguais"
- ✅ "Classificar tipos de estratificação segundo critérios de propriedade"
- ✅ "Comparar visões de Marx, Weber e Bourdieu"
- ✅ "Mapear como a escolaridade causa diferenças de renda"
- ✅ "Reconhecer que atores diferentes implementam estratégias diferentes"
- ✅ "Aplicar conceitos para escolher estratégia apropriada a um caso"

- ❌ "Compreender estratificação" (verbo muito genérico)
- ❌ "Estudar Marx" (muito vago)
- ❌ "Saber sobre inclusão" (não é ação)
- ❌ "Desnaturalizar; compreender raça" (dois verbos — escolha um)

---

### PASSO 5: Identificar Conteúdos Nucleares

**O que fazer:**
1. Liste todos os **conceitos-chave** que precisam aparecer no capítulo
2. Não são operações — são o "quê" (não o "como")

**Exemplo 1:**
```
Estratificação social; classe social; posições desiguais; 
meios de produção; capital econômico; capital cultural; 
desigualdade socioeconômica; mobilidade social
```

**Exemplo 2:**
```
Inclusão social; estratégia; direitos; acesso; igualdade 
de oportunidades; exclusão; vulnerabilidade; políticas públicas; 
protagonismo; economia solidária; renda básica; cotas
```

**Critério:**
- Todos devem aparecer em **pelo menos uma seção**
- Devem ser conceitos, não exemplos
- Não devem ser operações (não são verbos)

---

### PASSO 6: Escolher Autores

**O que fazer:**
1. Liste autores que **têm função pedagógica real** para esse tema
2. Cada autor deve responder a uma **perspectiva diferente** ou iluminar um aspecto diferente

**Exemplo 1 — Estratificação:**
```
Karl Marx — estrutura de produção e classe
Max Weber — múltiplas dimensões (classe, status, poder)
Pierre Bourdieu — capital cultural e reprodução social
```

**Exemplo 2 — Inclusão social:**
```
Celso Furtado — estratégias econômicas de inclusão
Thomas Piketty — mecanismos de desigualdade (capital, renda)
Boaventura de Sousa Santos — perspectiva do Sul global
Jurema Werneck — inclusão racial e perspectiva de sujeitos oprimidos
```

**Critério:**
- ❌ "Augusto Comte" (histórico, sem função prática)
- ❌ "Louis Althusser" (muito complexo para EM1)
- ✅ "Paulo Freire" (tem proposta pedagógica clara)
- ✅ "bell hooks" (interseccionalidade, perspectiva feminista negra)

---

### PASSO 7: Adicionar "Fios Condutores" (novo — baseado no feedback)

**O que fazer:**
1. Para cada transição entre seções, **escreva uma frase de conexão**
2. Essa frase será usada pelo Agente 2 para conectar blocos
3. Não é narrativa — é **articulação lógica explícita**

**Exemplo 1 — Transição Seção 1 → 2:**
```
"Agora que sabemos o que é estratificação, como os sociólogos 
a classificaram historicamente?"
```

**Exemplo 1 — Transição Seção 2 → 3:**
```
"Identificamos três tipos históricos. Mas qual é o mecanismo 
que mantém essas desigualdades? Marx, Weber e Bourdieu deram 
respostas diferentes."
```

**Exemplo 2 — Transição Seção 3 → 4:**
```
"Esses mecanismos não funcionam sozinhos — precisam de atores 
que os coloquem em prática. Governo, mercado e sociedade civil 
têm estratégias diferentes."
```

**Critério:**
- ✅ Usa conectivos: "Portanto", "No entanto", "Por outro lado", "Para ilustrar"
- ✅ Retoma a pergunta do capítulo
- ✅ Prepara o aluno para a próxima seção
- ❌ Não é narrativo ("Era uma vez...")
- ❌ Não usa metáforas ("Como um jardim que precisa ser cultivado...")

---

### PASSO 8: Completar "Elementos Desejáveis"

**O que fazer:**
1. Liste direcionamentos específicos para o professor/Agente 2
2. Especifique quais autores vão em quais seções
3. Indique quais dados/exemplos usar

**Exemplo 1:**
```
"Usar dados IBGE/PNAD; exemplos do mercado de trabalho brasileiro. 
Distribuição de autores: Marx (seção 2 — classe/propriedade), 
Weber (seção 3 — status/poder), Bourdieu (seção 3 — capital cultural). 
Enfatizar a diferença entre os três modelos."
```

**Exemplo 2:**
```
"Priorizar perspectivas de sujeitos historicamente oprimidos. 
Exemplos de desigualdade racial no mercado de trabalho, educação 
e segurança pública. Distribuição de autores: Furtado (seção 2 — 
estratégias econômicas), Piketty (seção 3 — mecanismos), 
Santos (seção 4 — perspectiva do Sul), Werneck (seção 5 — inclusão racial). 
Ênfase em feminismo negro e interseccionalidade."
```

---

## PARTE 3: VALIDAÇÃO — CHECKLIST

Antes de submeter o CSV, verifique:

### Estrutura
- ☑ O capítulo tem 4-6 seções? (mínimo 4)
- ☑ Cada seção tem exatamente 1 micro-habilidade + 1 operação?
- ☑ As operações estão em ordem crescente de dificuldade?
- ☑ A última operação é a operação principal da habilidade?

### Micro-Habilidades
- ☑ Cada uma começa com UM VERBO?
- ☑ Cada uma descreve uma **ação do aluno**, não um conteúdo?
- ☑ Todas as micro-habilidades juntas respondem à pergunta do capítulo?
- ☑ Não há repetição de verbos em seções consecutivas?

### Operações
- ☑ Todas as operações estão na lista de 7 válidas?
- ☑ Seção 1 é uma das mais elementares (Definir, Classificar, Sequenciar)?
- ☑ Última seção é a operação principal?
- ☑ Há progressão clara (fácil → intermediário → difícil)?

### Conteúdos e Autores
- ☑ Todos os conteúdos nucleares aparecem em alguma seção?
- ☑ Autores têm função pedagógica (não são decorativos)?
- ☑ Há clareza sobre em qual seção cada autor entra?
- ☑ Não há repetição desnecessária de autores?

### Pergunta e Fios Condutores
- ☑ A pergunta do capítulo é respondível apenas após toda a progressão?
- ☑ Há fios condutores entre as seções?
- ☑ Os fios condutores usam articulação lógica (não narrativa)?
- ☑ A pergunta é retomada em momentos-chave?

### Elementos Desejáveis
- ☑ Especificam distribuição de autores por seção?
- ☑ Indicam quais dados/exemplos usar?
- ☑ Oferecem direcionamentos para evitar catálogos?
- ☑ Mencionam contexto (Brasil, contemporâneo, etc.)?

---

## PARTE 4: ARMADILHAS COMUNS (O QUE EVITAR)

### ❌ Armadilha 1: Confundir micro-habilidade com conteúdo
```
ERRADO: "Conteúdo nuclear: Karl Marx, classe social, propriedade"
CERTO: "Micro-habilidade: Definir classe social segundo Marx 
        como relação com os meios de produção"
```

### ❌ Armadilha 2: Dois verbos na mesma micro-habilidade
```
ERRADO: "Desnaturalizar: compreender raça como construção social"
CERTO: "Definir raça como construção social, não categoria biológica"
```

### ❌ Armadilha 3: Operação principal na Seção 2
```
ERRADO: 
  Seção 1: Definir inclusão (DEFINIR)
  Seção 2: Aplicar a casos brasileiros (APLICAR) ← muito cedo!
  
CERTO:
  Seção 1: Definir inclusão (DEFINIR)
  Seção 2: Classificar estratégias (CLASSIFICAR)
  Seção 3: Mapear mecanismos (MAPEAR CAUSALIDADE)
  Seção 4: Aplicar a casos (APLICAR)
```

### ❌ Armadilha 4: Criar um catálogo
```
ERRADO:
  Seção 3: "Comparar Marx, Weber e Bourdieu"
           Com 3 mini-seções: Marx fala X, Weber fala Y, Bourdieu fala Z
           
CERTO:
  Seção 3: "Comparar Marx, Weber e Bourdieu"
           Com articulação entre eles: Marx vê classe como propriedade.
           Weber acrescenta status e poder. Bourdieu adiciona capital cultural.
           Cada um ilumina algo diferente.
```

### ❌ Armadilha 5: Muitas verificações fragmentadas
```
ERRADO: Q1 após definição, Q2 após exemplo, Q3 após classificação...

CERTO: Uma verificação ao final de cada seção completa, 
       testando a compreensão da progressão inteira
```

### ❌ Armadilha 6: Esquecer de conectar à pergunta do capítulo
```
ERRADO: A pergunta aparece no cabeçalho e desaparece

CERTO: A pergunta é retomada em pontos-chave:
       "Isso responde à primeira parte da pergunta..."
       "Agora entendemos o segundo mecanismo..."
```

### ❌ Armadilha 7: Autores sem função
```
ERRADO: "Autores: Marx, Weber, Bourdieu, Foucault, Lacan"
        (por quê Foucault e Lacan em EM1 sobre estratificação?)

CERTO: "Autores: Marx, Weber, Bourdieu"
       (cada um traz uma dimensão diferente e apropriada)
```

---

## PARTE 5: EXEMPLOS COMPLETOS

### Exemplo A — Já implementado: Estratificação Social

**Habilidade:** EM13CHS402 - Analisar e comparar indicadores...

**Pergunta:** Por que pessoas que nascem em posições sociais diferentes têm acesso desigual a emprego, renda e oportunidades?

**Operação principal:** Aplicar

**Andaime:**
```
Seção 1: Definir estratificação (DEFINIR)
         "A base: entender o conceito"
         
         Fio condutor:
         "Vemos desigualdade de renda no Brasil. 
          Mas o que produz essa distribuição? 
          Como a sociedade se organiza em camadas?"

Seção 2: Classificar tipos (CLASSIFICAR)
         "Aplicar o conceito a sistemas históricos"
         
         Fio condutor:
         "Existem diferentes formas de organizar desigualdade. 
          Vejamos três tipos históricos que mostram essa variedade."

Seção 3: Comparar visões (COMPARAR)
         "Entender múltiplos ângulos"
         
         Fio condutor:
         "O que causa estratificação? Não há uma resposta única. 
          Marx, Weber e Bourdieu ofereceram explicações diferentes."

Seção 4: Aplicar ao Brasil (APLICAR)
         "Responder à pergunta"
         
         Fio condutor:
         "Essas três visões explicam a realidade brasileira? 
          Sim, e cada uma ilumina um mecanismo diferente."
```

---

### Exemplo B — Novo: Inclusão Social

**Habilidade:** EM13CHS5XX - Identificar estratégias que promovam inclusão social

**Pergunta:** Quais estratégias promovem inclusão social e como escolher a mais apropriada?

**Operação principal:** Aplicar

**Andaime:**
```
Seção 1: Definir inclusão social (DEFINIR)
         Micro-hab: "Definir inclusão como garantia de acesso 
                     igual a direitos, recursos e oportunidades"
         
         Fio condutor:
         "Começamos entendendo o objetivo. 
          Mas como alcançá-lo? Não há uma única resposta."

Seção 2: Classificar estratégias (CLASSIFICAR)
         Micro-hab: "Classificar estratégias segundo seu tipo: 
                     legislativas, educacionais, econômicas, comunitárias"
         
         Fio condutor:
         "Existem diferentes caminhos. Vejamos quais tipos 
          de estratégias os diferentes atores usam."

Seção 3: Mapear mecanismos (MAPEAR CAUSALIDADE)
         Micro-hab: "Mapear como cada tipo de estratégia 
                     produz efeitos em educação, trabalho 
                     e direitos políticos"
         
         Fio condutor:
         "Mas como essas estratégias funcionam? O mecanismo 
          varia conforme o tipo e o contexto."

Seção 4: Reconhecer perspectivas (RECONHECER PERSPECTIVA)
         Micro-hab: "Reconhecer que Estado, mercado e 
                     sociedade civil implementam com prioridades distintas"
         
         Fio condutor:
         "Quem implementa inclusão? A resposta importa porque 
          cada ator tem perspectivas e recursos diferentes."

Seção 5: Aplicar a casos (APLICAR)
         Micro-hab: "Aplicar conceitos para escolher estratégia 
                     apropriada a um caso específico brasileiro"
         
         Síntese da pergunta:
         "Agora você consegue identificar qual estratégia 
          é mais eficaz para responder a cada tipo de exclusão."
```

---

## PARTE 6: PRÓXIMOS PASSOS APÓS COMPLETAR O CSV

Uma vez que o CSV está validado e completo:

1. **Passe para o Agente 1:** O Agente 1 receberá seu CSV e transformará cada linha em um "core.md" (estrutura de dados estruturada)

2. **O Agente 1 saberá:** 
   - Qual operação executar em cada seção (vindo de você)
   - Em qual ordem (progressão que você criou)
   - Qual micro-habilidade responder (você especificou)

3. **O Agente 2 receberá o core.md** e o transformará em texto funcional com blocos rotulados

4. **Você receberá o texto final** — agora é hora de validar fluxo, conectivos e se a progressão pedagógica funcionou

---

## CONCLUSÃO

Para decompor qualquer habilidade BNCC em um andaime pedagógico, você precisa:

1. ✅ Entender a habilidade (extrair o verbo principal)
2. ✅ Transformá-la em uma pergunta respondível
3. ✅ Identificar a operação principal (final)
4. ✅ Construir uma progressão de 4-6 operações
5. ✅ Descrever cada seção como micro-habilidade (um verbo)
6. ✅ Mapear conteúdos, autores, exemplos
7. ✅ Adicionar fios condutores para conectar seções
8. ✅ Validar contra o checklist
9. ✅ Evitar as armadilhas comuns
10. ✅ Submeter o CSV

**O CSV não é apenas um arquivo** — é o **blueprint pedagógico** que governa todo o pipeline. Quanto melhor seu CSV, melhor o texto gerado pelos agentes.

---

**Versão para citar:**
> Manual de Decomposição de Habilidades BNCC em Andaimes Pedagógicos. Criado em 30 de maio de 2026 para o pipeline de geração de apostilas didáticas funcionais. v1.0
