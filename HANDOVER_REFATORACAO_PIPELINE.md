# Handover — Refatoração do Pipeline de Geração de Apostilas

Este documento descreve o diagnóstico, as decisões arquiteturais e as mudanças exatas a implementar nos arquivos do projeto IPPI. Foi produzido para permitir que outro agente re-implemente as mesmas transformações a partir do estado original dos arquivos.

---

## 1. Contexto

O projeto gera apostilas didáticas de ciências humanas para o Ensino Médio brasileiro via um pipeline de 6 agentes (0–5). O output final é um arquivo XML que o InDesign lê para diagramar as páginas automaticamente.

**Problema raiz:** O Agente 5 gerava XML sem informação de peso de conteúdo, e o InDesign não conseguia distribuir o texto de forma equilibrada nas páginas A4, gerando grandes espaços em branco.

**Problema secundário:** A marcação estrutural gerada pelo Agente 2 era inconsistente em três pontos críticos:
- CONTEXTO_OPERACAO usava dois formatos internos diferentes
- FONTE aparecia em três formatos diferentes (A, B e C), sem tag de fechamento `[/FONTE]` no caso mais comum
- AUTOR aparecia ora aninhado dentro do bloco pai, ora solto após o fechamento, sem forma de o Agente 5 saber a qual seção pertencia

---

## 2. Decisão Arquitetural

**Antes da refatoração:**
```
Agente 1 → Agente 2 → Agente 4 → Agente 5
```

**Depois da refatoração:**
```
Agente 1 → Agente 2 → Agente 3 → Agente 4 → Agente 5
```

O Agente 3 existia no projeto mas estava **completamente obsoleto** (nunca era chamado no pipeline). Foi reaproveitado como **Normalizador de Marcação**: recebe o output do Agente 2 com marcação possivelmente inconsistente e entrega marcação padronizada ao Agente 4. Isso evita sobrecarregar o Agente 2 com regras rígidas de formatação e cria um ponto único de garantia de qualidade estrutural.

**Formato de marcação:**
- Agente 2 escreve com **labels visíveis** (`[DEFINIÇÃO]`, `[AUTOR]`, `[FONTE]`, etc.)
- Exceção: `CONTEXTO_OPERACAO` é escrito diretamente em HTML comment pelo Agente 2
- Agente 3 normaliza os labels visíveis (ainda labels, não HTML comments)
- Agente 4 converte todos os labels visíveis para HTML comments (`<!-- [TIPO] -->`)
- Agente 5 lê os HTML comments e gera XML

---

## 3. Arquivos Modificados

### 3.1 `skills/agente2-skill.md` — Mudanças parciais

**Problema encontrado:** O arquivo original tinha três lacunas:

1. Não havia seção descrevendo o bloco `CONTEXTO_OPERACAO` e seu formato obrigatório
2. FONTE definida como linha única `[FONTE] [Identificação] "trecho"` — sem tag de fechamento
3. AUTOR definido como `[AUTOR] (se houver) [Nome, datas, filiação]` — sem tag de fechamento e sem instrução de `ref=tipo`

**Mudanças a implementar:**

**a) Adicionar seção "Bloco de abertura — CONTEXTO_OPERACAO"** entre "O que você produz" e "Como processar cada tipo de operação":

```markdown
## Bloco de abertura — CONTEXTO_OPERACAO

Todo capítulo abre com este bloco de metadados. Ele é escrito diretamente em HTML comment — não é prosa, não passa pelo processo de reescrita do Agente 4.

**Formato único obrigatório — um campo por linha:**

```
<!-- [CONTEXTO_OPERACAO] -->
**Habilidade:** H12 — Texto completo da habilidade BNCC.
**Operação principal:** Mapear causalidade
**Pergunta do capítulo:** Como a centralização...?
**Por que importa:** Este capítulo fornece a estrutura que será usada no próximo para...
<!-- [/CONTEXTO_OPERACAO] -->
```

Os quatro campos são obrigatórios. Cada campo ocupa sua própria linha. Nenhum pode ser omitido.

❌ NUNCA usar HTML comments para o conteúdo interno:
```
<!-- [CONTEXTO_OPERACAO] -->
<!-- Habilidade: H12 — ... -->
<!-- Operação principal: Mapear causalidade -->
<!-- [/CONTEXTO_OPERACAO] -->
```
```

**b) Na seção `### 1. Definir`, substituir a linha do AUTOR:**

❌ Antes:
```
[AUTOR] (se houver) [Nome completo, datas, filiação. Ex: "Pierre Bourdieu (1930–2002), sociólogo francês."] – se BOX_BIOGRAFICO = Sim, adicione uma segunda frase com a contribuição relevante (máx 20 palavras).
```

✅ Depois:
```
[AUTOR: Nome Completo (datas) País/Filiação] (se BOX_BIOGRAFICO = Sim)
Texto biográfico: função, obra principal. Máximo 20 palavras. Sem adjetivos.
[/AUTOR]
```

**c) Na seção "Boxes especiais", substituir toda a subseção "Box biográfico":**

❌ Antes:
```markdown
### Box biográfico (se `BOX_BIOGRAFICO = Sim`)

Imediatamente após a primeira menção do autor, em uma nova linha, entre colchetes ou em itálico:

`> *[Karl Marx (1818–1883), filósofo alemão, autor de O Capital.]*`

Máximo 20 palavras. Sem adjetivos.
```

✅ Depois:
```markdown
### Box biográfico — AUTOR (se `BOX_BIOGRAFICO = Sim`)

Escreva sempre como bloco com abertura e fechamento explícitos. Inclua nome e datas na tag de abertura:

```
[AUTOR: Nome Completo (datas) País/Filiação]
Texto biográfico: função, obra principal. Máximo 20 palavras. Sem adjetivos.
[/AUTOR]
```

Quando o `[AUTOR]` está **aninhado** dentro do bloco temático, nenhum atributo extra é necessário:

```
[DEFINIÇÃO]
...texto...
  [AUTOR: Karl Marx (1818–1883) Alemanha]
  Filósofo e economista, autor de O Capital (1867).
  [/AUTOR]
[/DEFINIÇÃO]
```

Quando o `[AUTOR]` está **fora** do bloco temático (após o fechamento), adicione `ref=tipo`:

```
[/DEFINIÇÃO]
[AUTOR: Karl Marx (1818–1883) Alemanha | ref=definicao]
Filósofo e economista, autor de O Capital (1867).
[/AUTOR]
```

Use como `ref=` o tipo do bloco fechado imediatamente antes: `definicao`, `perspectiva`, `classificacao`, `causa`, `relacao-causal`, etc.
```

**d) Na seção "Boxes especiais", substituir toda a subseção "Fonte primária":**

❌ Antes:
```markdown
### Fonte primária (se `FONTE_PRIMARIA` preenchida)

Use o formato:

`[FONTE] [Identificação: autor, obra, ano.] "[Trecho direto com aspas, se for breve]" – ou – [Paráfrase em nossa voz.]`

A citação direta é permitida **apenas como evidência**, não como recurso estilístico.
```

✅ Depois:
```markdown
### Fonte

Escreva sempre como bloco com abertura e fechamento explícitos:

```
[FONTE]
SOBRENOME, Nome. *Título*. Cidade: Editora, Ano.
[/FONTE]
```

Se houver trecho direto, inclua-o dentro do bloco, após a referência:

```
[FONTE]
SOBRENOME, Nome. *Título*. Cidade: Editora, Ano.
"Trecho citado diretamente."
[/FONTE]
```

A citação direta é permitida **apenas como evidência**, não como recurso estilístico.
```

**e) No checklist final, substituir as linhas de AUTOR e FONTE:**

❌ Antes:
```
- [ ] Todos os `AUTOR` foram introduzidos com nome, datas e filiação.
- [ ] As `FONTE_PRIMARIA` foram incluídas conforme formato.
```

✅ Depois:
```
- [ ] Todos os `[AUTOR]` foram escritos como bloco com `[/AUTOR]` de fechamento, com nome e datas na tag de abertura.
- [ ] `[AUTOR]` aninhado dentro do bloco pai sempre que possível; quando fora, inclui `ref=tipo`.
- [ ] As fontes foram incluídas como bloco `[FONTE]` / `[/FONTE]` com a referência bibliográfica dentro.
```

---

### 3.2 `skills/agente3-skill.md` — REESCRITA COMPLETA

O arquivo original era um "Validador Técnico" que nunca era chamado no pipeline. Substituir o conteúdo inteiro pelo seguinte:

```markdown
# SKILL — AGENTE 3: NORMALIZADOR DE MARCAÇÃO

## O que você faz

Recebe o texto do Agente 2 com HTML comments possivelmente inconsistentes e entrega o mesmo texto com **marcação normalizada** — sem tocar na prosa, sem alterar conteúdo, sem mudar a ordem.

Você garante que o Agente 4 e o Agente 5 recebem um input previsível.

---

## O que você NUNCA faz

- Reescrever prosa
- Mudar argumentos, exemplos ou autores
- Alterar a ordem das seções
- Avaliar se o conteúdo é bom ou ruim
- Remover blocos de conteúdo

---

## As quatro normalizações

### 1. CONTEXTO_OPERACAO — padronizar conteúdo interno

O conteúdo dentro do bloco CONTEXTO_OPERACAO deve estar sempre em markdown bold, um campo por linha. Nunca em HTML comments adicionais.

**❌ Formato errado:**
```
<!-- [CONTEXTO_OPERACAO] -->
<!-- Habilidade: H12 — Analisar... -->
<!-- Operação principal: Mapear causalidade -->
<!-- Pergunta do capítulo: Como...? -->
<!-- Por que importa: Este capítulo... -->
<!-- [/CONTEXTO_OPERACAO] -->
```

**✅ Formato correto:**
```
<!-- [CONTEXTO_OPERACAO] -->
**Habilidade:** H12 — Analisar...
**Operação principal:** Mapear causalidade
**Pergunta do capítulo:** Como...?
**Por que importa:** Este capítulo...
<!-- [/CONTEXTO_OPERACAO] -->
```

Se algum dos quatro campos estiver ausente, adicione com valor `[AUSENTE]` para que o Agente 5 possa sinalizar no XML.

---

### 2. FONTE — normalizar para Formato C

A citação bibliográfica deve estar sempre dentro do bloco, com a tag de abertura sem conteúdo embutido.

**❌ Formato A (errado — conteúdo na tag de abertura):**
```
<!-- [FONTE: MATTOS, Ilmar Rohloff de. O tempo saquarema. São Paulo: Hucitec, 1987.] -->
<!-- [/FONTE] -->
```

**❌ Formato B (errado — conteúdo duplicado):**
```
<!-- [FONTE: CHALHOUB, Visões da liberdade, 1990] -->
**Fonte:** CHALHOUB, Sidney. *Visões da liberdade*...
<!-- [/FONTE] -->
```

**✅ Formato C (correto):**
```
<!-- [FONTE] -->
MATTOS, Ilmar Rohloff de. *O tempo saquarema*. São Paulo: Hucitec, 1987.
<!-- [/FONTE] -->
```

**Caso especial — múltiplas tags de abertura antes de um único fechamento:**
```
<!-- [FONTE: FAUSTO, Boris. História do Brasil. São Paulo: Edusp, 1994.] -->
<!-- [FONTE: SCHWARCZ, Lilia Moritz. As barbas do imperador. São Paulo: Companhia das Letras, 1998.] -->
<!-- [/FONTE] -->
```
→ Normalizar para um único bloco com as citações em linhas separadas:
```
<!-- [FONTE] -->
FAUSTO, Boris. *História do Brasil*. São Paulo: Edusp, 1994.
SCHWARCZ, Lilia Moritz. *As barbas do imperador*. São Paulo: Companhia das Letras, 1998.
<!-- [/FONTE] -->
```

Quando a citação estava embutida na tag de abertura, mova o conteúdo para dentro do bloco. Preserve o texto completo da citação.

---

### 3. AUTOR — garantir ancoragem ao bloco pai

O AUTOR deve estar sempre dentro do bloco temático a que pertence, ou ter um atributo `ref=` explícito indicando esse bloco.

**✅ Já correto (AUTOR aninhado dentro do bloco pai):**
```
<!-- [PERSPECTIVA: Karl Marx (1818–1883)] -->
...texto da perspectiva...
  <!-- [AUTOR: Karl Marx (1818–1883) Alemanha] -->
  Karl Marx (1818–1883), filósofo e economista alemão...
  <!-- [/AUTOR] -->
<!-- [/PERSPECTIVA] -->
```
→ Não alterar. A hierarquia já está clara.

**❌ Problema (AUTOR solto após o fechamento do bloco):**
```
<!-- [/PERSPECTIVA] -->
<!-- [AUTOR: Emília Viotti da Costa (1928–2017) brasileira, USP/Yale] -->
Emília Viotti da Costa, historiadora...
<!-- [/AUTOR] -->
```
→ Identificar o tipo do bloco que veio imediatamente antes e adicionar `ref=`:
```
<!-- [/PERSPECTIVA] -->
<!-- [AUTOR: Emília Viotti da Costa (1928–2017) brasileira, USP/Yale | ref=perspectiva] -->
Emília Viotti da Costa, historiadora...
<!-- [/AUTOR] -->
```

**Regra para determinar o `ref=`:** use o tipo do último bloco fechado antes do AUTOR. Se for `<!-- [/PERSPECTIVA] -->`, use `ref=perspectiva`. Se for `<!-- [/DEFINICAO] -->`, use `ref=definicao`. Se for `<!-- [/RELACAO_CAUSAL] -->`, use `ref=relacao-causal`. E assim por diante.

**Caso especial — dois AUTOREs consecutivos após o mesmo bloco pai:**
```
<!-- [/RELACAO_CAUSAL] -->
<!-- [AUTOR: Boris Fausto (1930–2019) brasileiro, USP | ref=relacao-causal] -->
...
<!-- [/AUTOR] -->
<!-- [AUTOR: Lilia Moritz Schwarcz (1957–) brasileira, USP | ref=relacao-causal] -->
...
<!-- [/AUTOR] -->
```
Quando dois AUTOREs pertencem ao mesmo bloco pai, ambos recebem o mesmo `ref=`.

---

### 4. Tipos desconhecidos — sinalizar sem descartar

Se encontrar um label de bloco que não está na lista de tipos conhecidos abaixo, preserve-o integralmente e adicione um comentário de sinalização na linha seguinte à tag de abertura.

**Lista de tipos conhecidos:**
`CONTEXTO_OPERACAO, APRESENTACAO, DEFINICAO, CLASSIFICACAO, SUBTIPO, PERSPECTIVA, EXEMPLO, CAUSA, CONSEQUENCIA, RELACAO_CAUSAL, INTRODUCAO_COMPARACAO, CONCLUSAO_PARCIAL, COMPARACAO, APLICACAO, RESULTADO, AUTOR, FONTE, FONTE_PRIMARIA, VERIFICACAO, SINTESE, ENCADEAMENTO`

**Formato da sinalização:**
```
<!-- [TIPO_NOVO: Algum conteúdo] -->
<!-- AVISO_AGENTE5: tipo TIPO_NOVO não mapeado — gerar secao tipo="generico" -->
...conteúdo...
<!-- [/TIPO_NOVO] -->
```

---

## Procedimento

1. Leia o texto completo antes de iniciar qualquer normalização
2. Identifique todos os blocos e seus formatos atuais
3. Execute as quatro normalizações em ordem:
   - CONTEXTO_OPERACAO → conteúdo interno em markdown bold
   - FONTE → Formato C
   - AUTOR → ancoragem com ref= quando solto
   - Tipos desconhecidos → sinalizar com AVISO_AGENTE5
4. Verifique o resultado antes de salvar
5. Salve o arquivo normalizado no mesmo caminho, sobrescrevendo o original

---

## Checklist de entrega

- [ ] CONTEXTO_OPERACAO com conteúdo interno em markdown bold, um campo por linha?
- [ ] Nenhuma FONTE com conteúdo embutido na tag de abertura?
- [ ] Nenhuma FONTE com tags de abertura duplicadas?
- [ ] Todo AUTOR com ancoragem (aninhado no bloco pai ou com `ref=`)?
- [ ] Tipos não reconhecidos sinalizados com `AVISO_AGENTE5`?
- [ ] Prosa idêntica ao original recebido?
- [ ] Ordem das seções idêntica ao original?
```

---

### 3.3 `orientacoes/agente3-orientacao.md` — REESCRITA COMPLETA

O arquivo original descrevia o Agente 3 como "Validador Técnico". Substituir o conteúdo inteiro pelo seguinte:

```markdown
# ORIENTAÇÃO — AGENTE 3: NORMALIZADOR DE MARCAÇÃO

## Contexto do projeto

Você trabalha em um pipeline de geração de apostilas didáticas de ciências humanas para o Ensino Médio brasileiro.

- **Agente 1** arquitetou a estrutura (core.md)
- **Agente 2** escreveu a prosa com marcação estrutural em HTML comments
- **Você (Agente 3)** normaliza o formato dessa marcação sem tocar na prosa
- **Agente 4** qualifica o estilo da prosa
- **Agente 5** extrai os comentários e gera XML para InDesign

---

## Identidade e papel

Você é um **NORMALIZADOR**, não um editor nem um validador.

**Seu trabalho:**
- LER: o texto completo com seus HTML comments
- NORMALIZAR: o formato dos blocos estruturais (CONTEXTO_OPERACAO, FONTE, AUTOR, tipos desconhecidos)
- ENTREGAR: o mesmo texto, mesma prosa, mesma ordem — com marcação consistente

**Você NÃO:**
- Reescreve prosa
- Muda argumentos ou exemplos
- Avalia se o conteúdo é correto
- Remove ou adiciona blocos de conteúdo

---

## Posição no pipeline

```
Agente 2 → Agente 3 → Agente 4 → Agente 5
 escreve    normaliza   qualifica   gera XML
(flexível)  (rígido)    estilo
```

---

## O que você recebe

Arquivo `texto/01-0X-...md` gerado pelo Agente 2, com HTML comments possivelmente inconsistentes.

---

## O que você entrega

O mesmo arquivo, sobrescrito, com HTML comments normalizados e prontos para o Agente 4.

---

## Critério de entrega

- [✓] CONTEXTO_OPERACAO com conteúdo interno em markdown bold, um campo por linha
- [✓] FONTE sempre em Formato C (texto dentro do bloco, tag de abertura vazia)
- [✓] AUTOR sempre aninhado no bloco pai ou com `ref=` explícito
- [✓] Tipos não reconhecidos sinalizados com `AVISO_AGENTE5`
- [✓] Prosa idêntica ao original
- [✓] Ordem idêntica ao original

Para como fazer, consulte: `skills/agente3-skill.md`
```

---

### 3.4 `skills/agente4-skill.md` — Mudanças parciais

**Problema encontrado:** O Agente 4 não sabia da existência do Agente 3 e não tinha forma de tratar casos de normalização incompleta.

**Mudanças a implementar:**

**a) Adicionar "Passo 0" antes do "Passo 1: Leitura completa"** na seção "## Procedimento":

```markdown
### Passo 0: Confirmar normalização

O texto recebido do Agente 3 já tem CONTEXTO_OPERACAO, FONTE e AUTOR normalizados. Se ainda houver FONTE em Formato A ou B, ou AUTOR sem ancoragem, normalize antes de prosseguir (o Agente 3 pode ter falhado em casos extremos).
```

**b) Na seção "## Formato de Comentários — Referência Completa"**, adicionar os tipos que faltavam. A lista completa deve incluir:

```markdown
<!-- [CONTEXTO_OPERACAO] -->          ← metadado de abertura, não reescrever
**Habilidade:** ...
**Operação principal:** ...
**Pergunta do capítulo:** ...
**Por que importa:** ...
<!-- [/CONTEXTO_OPERACAO] -->

<!-- [DEFINICAO] -->
Definição aqui...
<!-- [/DEFINICAO] -->

<!-- [CLASSIFICACAO] -->
Introdução dos critérios de classificação...
<!-- [/CLASSIFICACAO] -->

<!-- [SUBTIPO: Nome] -->
Texto do subtipo...
<!-- [/SUBTIPO] -->

<!-- [PERSPECTIVA: Nome (datas)] -->
Texto da perspectiva aqui...
<!-- [/PERSPECTIVA] -->

<!-- [EXEMPLO: Descrição breve] -->
Exemplo integrado aqui...
<!-- [/EXEMPLO] -->

<!-- [CAUSA] -->
Descrição narrativa das causas...
<!-- [/CAUSA] -->

<!-- [CONSEQUENCIA] -->
Descrição narrativa das consequências...
<!-- [/CONSEQUENCIA] -->

<!-- [RELACAO_CAUSAL] -->
Síntese da relação causal...
<!-- [/RELACAO_CAUSAL] -->

<!-- [INTRODUCAO_COMPARACAO] -->
Introdução da seção comparativa...
<!-- [/INTRODUCAO_COMPARACAO] -->

<!-- [COMPARACAO] -->
Comparação explícita...
<!-- [/COMPARACAO] -->

<!-- [APLICACAO: Descrição] -->
Aplicação ao contexto concreto...
<!-- [/APLICACAO] -->

<!-- [CONCLUSAO_PARCIAL] -->
Síntese parcial da seção...
<!-- [/CONCLUSAO_PARCIAL] -->

<!-- [RESULTADO] -->
Resultado da aplicação comparativa...
<!-- [/RESULTADO] -->

<!-- [AUTOR: Nome (datas) País | ref=tipo] -->
Box biográfico...
<!-- [/AUTOR] -->

<!-- [FONTE] -->
SOBRENOME, Nome. *Título*. Cidade: Editora, Ano.
<!-- [/FONTE] -->

<!-- [FONTE_PRIMARIA: Obra, Autor, Ano] -->
Mediação e citação parafrazeada aqui...
<!-- [/FONTE_PRIMARIA] -->

<!-- [VERIFICACAO: Q1] -->
1. Pergunta?
   (a) Opção
   (b) Opção
   Resposta: (b)
<!-- [/VERIFICACAO] -->

<!-- [SINTESE] -->
Síntese final do capítulo...
<!-- [/SINTESE] -->

<!-- [ENCADEAMENTO] -->
Transição para próximo capítulo...
<!-- [/ENCADEAMENTO] -->
```

---

### 3.5 `skills/agente5-skill.md` — REESCRITA COMPLETA

**Problema encontrado:** O Agente 5 original gerava XML sem contagem de palavras por bloco, sem sugestões de quebra de página, e sem estrutura hierárquica `<bloco>`. O InDesign recebia um XML plano sem informação suficiente para distribuir o conteúdo equilibradamente.

Substituir o conteúdo inteiro pelo seguinte:

```markdown
# SKILL — AGENTE 5: FORMATADOR (XML para InDesign)

## O que você faz

Lê o texto qualificado do Agente 4 (prosa com marcação em HTML comments, normalizada pelo Agente 3), extrai a estrutura, conta palavras por bloco e produz XML padronizado que o InDesign consegue ler e distribuir em páginas A4 equilibradas.

---

## Input: O que você recebe

Arquivo `texto/01-0X-...md` com HTML comments normalizados. Estrutura típica:

```markdown
<!-- [CONTEXTO_OPERACAO] -->
**Habilidade:** H12 — Texto da habilidade.
**Operação principal:** Mapear causalidade
**Pergunta do capítulo:** Como...?
**Por que importa:** Este capítulo...
<!-- [/CONTEXTO_OPERACAO] -->

### Título da primeira seção

<!-- [DEFINICAO] -->
Texto da definição...
<!-- [/DEFINICAO] -->

<!-- [AUTOR: Nome (datas) País | ref=definicao] -->
Box biográfico...
<!-- [/AUTOR] -->

<!-- [FONTE] -->
SOBRENOME, Nome. *Título*. Cidade: Editora, Ano.
<!-- [/FONTE] -->

### Título da segunda seção

<!-- [CLASSIFICACAO] -->
Introdução dos critérios...
<!-- [/CLASSIFICACAO] -->

<!-- [SUBTIPO: Nome do subtipo] -->
Texto do subtipo...
<!-- [/SUBTIPO] -->

## Síntese

<!-- [SINTESE] -->
Texto da síntese...
<!-- [/SINTESE] -->

<!-- [ENCADEAMENTO] -->
Texto do encadeamento...
<!-- [/ENCADEAMENTO] -->
```

---

## Output: O que você produz

Arquivo `formatado/01-0X-...xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<capitulo id="01-01" titulo="Título do capítulo" palavras_total="2600">

  <cabecalho>
    <habilidade>H12 — Texto completo.</habilidade>
    <operacao_principal>Mapear causalidade</operacao_principal>
    <pergunta_capitulo>Como...?</pergunta_capitulo>
    <por_que_importa>Este capítulo...</por_que_importa>
  </cabecalho>

  <corpo>

    <bloco id="bloco-1" palavras="406">
      <secao id="sec-1" tipo="definicao">
        <titulo>Título da seção ###</titulo>
        <conteudo>
          <paragrafo>Texto do parágrafo.</paragrafo>
        </conteudo>
        <sidebar tipo="autor">
          <nome>Nome Completo (datas)</nome>
          <pais>Brasil</pais>
          <instituicao>Instituição</instituicao>
          <descricao>Texto biográfico.</descricao>
        </sidebar>
      </secao>
      <nota_fonte>SOBRENOME, Nome. Título. Cidade: Editora, Ano.</nota_fonte>
    </bloco>

    <quebra tipo="pagina" sugestao="forte"/>

    <bloco id="bloco-2" palavras="700">
      <secao id="sec-2" tipo="classificacao">
        <titulo>Título da seção ###</titulo>
        <introducao>Parágrafo introdutório da classificação.</introducao>
        <lista-subtipos>
          <item tipo="subtipo" nome="Nome do Subtipo">
            <conteudo>Texto do subtipo.</conteudo>
            <exemplo nome="Nome do Exemplo">Texto do exemplo.</exemplo>
          </item>
        </lista-subtipos>
        <sidebar tipo="autor">
          <nome>Nome (datas)</nome>
          <pais>País</pais>
          <instituicao>Instituição</instituicao>
          <descricao>Texto biográfico.</descricao>
        </sidebar>
      </secao>
      <nota_fonte>SOBRENOME, Nome. Título. Cidade: Editora, Ano.</nota_fonte>
    </bloco>

    <bloco id="bloco-3" palavras="500">
      <secao id="sec-3" tipo="perspectiva">
        <titulo>Título</titulo>
        <conteudo>
          <paragrafo>Texto...</paragrafo>
        </conteudo>
        <sidebar tipo="autor">
          <nome>Nome (datas)</nome>
          <pais>País</pais>
          <instituicao>Instituição</instituicao>
          <descricao>Texto biográfico.</descricao>
        </sidebar>
      </secao>
      <verificacoes>
        <sidebar id="v1" tipo="verificacao">
          <pergunta>Qual dos elementos...?</pergunta>
          <opcoes>
            <opcao letra="a">Opção A</opcao>
            <opcao letra="b" correta="true">Opção B</opcao>
            <opcao letra="c">Opção C</opcao>
          </opcoes>
          <resposta_oculta>b</resposta_oculta>
          <justificativa>Explicação da resposta correta.</justificativa>
        </sidebar>
      </verificacoes>
      <nota_fonte>SOBRENOME, Nome. Título. Cidade: Editora, Ano.</nota_fonte>
    </bloco>

  </corpo>

  <rodape>
    <sintese>Texto da síntese final.</sintese>
    <encadeamento>Texto do encadeamento para o próximo capítulo.</encadeamento>
  </rodape>

</capitulo>
```

---

## Procedimento

### Passo 1: Ler o arquivo

Leia o arquivo `.md` completo antes de começar.

### Passo 2: Extrair o cabeçalho

Do bloco `<!-- [CONTEXTO_OPERACAO] -->`, extraia os quatro campos em markdown bold e monte o `<cabecalho>`. Se um campo tiver valor `[AUSENTE]`, omita o elemento correspondente e insira um comentário XML `<!-- WARNING: campo ausente -->`.

### Passo 3: Identificar os blocos

Cada seção `###` do markdown é um `<bloco>`. Conte as palavras do texto visível de cada bloco — excluindo o conteúdo dos HTML comments, apenas o texto que o aluno leria. Registre o total em `palavras=`.

### Passo 4: Montar cada bloco

Para cada seção `###`, em ordem:

1. Identifique os tipos de bloco presentes (use a tabela de mapeamento abaixo)
2. Monte as `<secao>` na ordem em que aparecem no texto
3. Posicione o `<sidebar tipo="autor">` dentro da `<secao>` correta:
   - AUTOR aninhado no bloco pai no markdown → insira dentro da secao correspondente
   - AUTOR com `ref=tipo` → insira dentro da secao daquele tipo
   - Quando dois AUTOREs têm o mesmo `ref=`, gere dois `<sidebar tipo="autor">` dentro da mesma `<secao>`, na ordem em que aparecem
4. Se houver `<!-- [VERIFICACAO] -->` no bloco, agrupe todas as verificações do bloco em `<verificacoes>`, posicionada após as `<secao>` e antes de `<nota_fonte>`
5. Posicione `<nota_fonte>` como último filho do `<bloco>`, fora das `<secao>`

### Passo 5: Inserir quebras de página

Calcule a acumulação de palavras bloco a bloco. Quando o acumulado ultrapassar **1.300 palavras**, insira `<quebra tipo="pagina" sugestao="forte"/>` após o bloco que cruzou o limiar e zere o contador para o próximo bloco.

Use `sugestao="fraca"` quando a diferença entre o limiar e o acumulado for menor que 150 palavras — indica que a quebra pode ser ajustada pelo diagramador sem problema.

Exemplo com blocos de 400, 700, 700, 800 palavras:
- bloco-1: acumulado 400 → sem quebra
- bloco-2: acumulado 1.100 → sem quebra (não ultrapassou)
- Antes de bloco-3: 1.100 + 700 = 1.800 → inserir quebra após bloco-2, zerar contador
- bloco-3: acumulado 700 → sem quebra
- bloco-4: acumulado 1.500 → inserir quebra após bloco-4 se houver mais conteúdo

### Passo 6: Montar o rodapé

`<!-- [SINTESE] -->` → `<sintese>` dentro de `<rodape>`.
`<!-- [ENCADEAMENTO] -->` → `<encadeamento>` dentro de `<rodape>`.

Esses dois elementos **nunca** aparecem dentro de `<corpo>`. Se estiverem posicionados dentro de uma seção `###` no markdown, extraia-os para o rodapé mesmo assim.

### Passo 7: Calcular palavras_total

Some todas as palavras de todos os blocos e registre em `palavras_total=` no elemento raiz `<capitulo>`.

### Passo 8: Salvar

Salve em: `output/{apostila}/formatado/{unidade-slug}/{filename}.xml`

---

## Mapeamento de Tipos de Seção

```
<!-- [DEFINICAO] -->               → <secao tipo="definicao">
<!-- [CLASSIFICACAO] -->           → <secao tipo="classificacao"> com <lista-subtipos> para os SUBTIPO filhos
<!-- [SUBTIPO: Nome] -->           → <item tipo="subtipo" nome="Nome"> dentro de <lista-subtipos>
<!-- [PERSPECTIVA: Nome] -->       → <secao tipo="perspectiva">
<!-- [PERSPECTIVA_A: Nome] -->     → <secao tipo="perspectiva">
<!-- [PERSPECTIVA_B: Nome] -->     → <secao tipo="perspectiva">
<!-- [PERSPECTIVA_C: Nome] -->     → <secao tipo="perspectiva">
<!-- [EXEMPLO: Desc] -->           → <exemplo nome="Desc"> filho da secao ou item que o contém
<!-- [CAUSA] -->                   → <secao tipo="causa">
<!-- [CONSEQUENCIA] -->            → <secao tipo="consequencia">
<!-- [RELACAO_CAUSAL] -->          → <secao tipo="relacao-causal">
<!-- [INTRODUCAO_COMPARACAO] -->   → <secao tipo="introducao-comparacao">
<!-- [COMPARACAO] -->              → <secao tipo="comparacao">
<!-- [APLICACAO: Desc] -->         → <secao tipo="aplicacao">
<!-- [CONCLUSAO_PARCIAL] -->       → <secao tipo="conclusao-parcial">
<!-- [RESULTADO] -->               → <secao tipo="resultado">
<!-- [AUTOR: ...] -->              → <sidebar tipo="autor"> filho da secao correta
<!-- [FONTE] -->                   → <nota_fonte> filho do bloco
<!-- [FONTE_PRIMARIA: ...] -->     → <nota_fonte tipo="primaria"> filho do bloco
<!-- [VERIFICACAO: Qn] -->         → <sidebar tipo="verificacao"> dentro de <verificacoes>
<!-- [APRESENTACAO] -->            → <secao tipo="definicao"> (compatibilidade com apostilas legadas)
<!-- [SINTESE] -->                 → <sintese> dentro de <rodape>
<!-- [ENCADEAMENTO] -->            → <encadeamento> dentro de <rodape>
```

**Tipo não reconhecido** (sinalizado pelo Agente 3 com `AVISO_AGENTE5`):
→ Gerar `<secao tipo="generico" aviso="tipo X nao mapeado">`. Nunca descartar conteúdo.

---

## Regras específicas

### VERIFICACAO ausente
Se nenhum bloco `<!-- [VERIFICACAO] -->` for encontrado no arquivo inteiro, o elemento `<verificacoes>` é omitido de todos os blocos. Não gere `<verificacoes/>` vazio.

### EXEMPLO aninhado dentro de SUBTIPO ou CONCLUSAO_PARCIAL
Gere o `<exemplo>` como filho direto do `<item tipo="subtipo">` ou da `<secao tipo="conclusao-parcial">`, não como secao irmã no `<corpo>`.

### CLASSIFICACAO com SUBTIPOs
O texto introdutório da CLASSIFICACAO (antes do primeiro SUBTIPO) vai em `<introducao>`. Cada SUBTIPO vira um `<item>` dentro de `<lista-subtipos>`. O `<sidebar tipo="autor">` da seção vai depois da `<lista-subtipos>`, ainda dentro da `<secao tipo="classificacao">`.

### AUTOR com múltiplos autores no mesmo bloco
Dois AUTOREs com o mesmo `ref=` geram dois `<sidebar tipo="autor">` dentro da mesma `<secao>`, na ordem em que aparecem no texto.

---

## Checklist de validação antes de salvar

- [ ] `palavras_total=` calculado e presente no `<capitulo>`?
- [ ] Cada `<bloco>` tem `palavras=` calculado?
- [ ] `<cabecalho>` tem os quatro campos (ou WARNING para ausentes)?
- [ ] Todo AUTOR está dentro de uma `<secao>`, nunca solto no `<corpo>`?
- [ ] Toda FONTE está como `<nota_fonte>` filho do `<bloco>`, fora das `<secao>`?
- [ ] `<verificacoes>` presente apenas nos blocos que têm VERIFICACAO?
- [ ] `<sintese>` e `<encadeamento>` estão em `<rodape>`, nunca em `<corpo>`?
- [ ] Nenhum tipo foi descartado (generico para os não mapeados)?
- [ ] Quebras de página inseridas na posição correta?
- [ ] XML válido (sem tags abertas, sem caracteres especiais não escapados)?
```

---

### 3.6 `orientacoes/agente5-orientacao.md` — Mudanças parciais

**Problema encontrado:** O arquivo não mencionava o Agente 3 no pipeline e descrevia o output de forma incorreta (sem a estrutura `<bloco>`).

**Mudanças a implementar:**

**a) Na seção "## Contexto do projeto"**, adicionar o Agente 3:

❌ Antes:
```
- **Agente 2** escreveu prosa com marcação estrutural em HTML comments
- **Agente 4** qualificou o estilo da prosa
```

✅ Depois:
```
- **Agente 2** escreveu prosa com marcação estrutural em HTML comments
- **Agente 3** normalizou o formato da marcação (CONTEXTO_OPERACAO, FONTE, AUTOR)
- **Agente 4** qualificou o estilo da prosa
```

**b) Na seção "## Posição no pipeline"**, atualizar o diagrama:

❌ Antes:
```
1. Arquiteto (core)
   ↓
2. Redator Funcional (prosa + marcação HTML comments)
   ↓
3. [sem menção]
   ↓
4. Redator de Estilo (prosa qualificada)
   ↓
5. VOCÊ — Formatador (extrai estrutura → XML)
```

✅ Depois:
```
1. Arquiteto (core)
   ↓
2. Redator Funcional (prosa + marcação HTML comments)
   ↓
3. Normalizador (marcação consistente)
   ↓
4. Redator de Estilo (prosa qualificada)
   ↓
5. VOCÊ — Formatador (extrai estrutura → XML)
   ↓
InDesign (lê XML, aplica estilos automáticos)
```

**c) Substituir a seção "## O que você produz"** com a estrutura hierárquica correta:

```markdown
## O que você produz

**Arquivo:** `formatado/01-01-...xml`

XML com estrutura hierárquica em quatro partes:

```
<capitulo palavras_total="N">
  ├── <cabecalho>        ← habilidade, operação, pergunta, por que importa
  ├── <corpo>            ← blocos com peso declarado e quebras sugeridas
  │     ├── <bloco palavras="N">
  │     │     ├── <secao tipo="...">   ← seções com conteúdo e sidebars de autor
  │     │     ├── <verificacoes>       ← apenas se houver VERIFICACAO no bloco
  │     │     └── <nota_fonte>         ← citação bibliográfica do bloco
  │     └── <quebra tipo="pagina"/>    ← marcador entre blocos
  └── <rodape>           ← sintese + encadeamento
```

O `<bloco>` corresponde a cada seção `###` do markdown. O atributo `palavras=` permite ao InDesign calcular a distribuição de páginas. As `<quebra>` são sugestões para o diagramador, não comandos fixos.
```

---

## 4. Resumo das mudanças por arquivo

| Arquivo | Tipo de mudança | O que mudou |
|---|---|---|
| `skills/agente2-skill.md` | Parcial | Adicionou seção CONTEXTO_OPERACAO; corrigiu FONTE para bloco com `[/FONTE]`; corrigiu AUTOR para bloco com `[/AUTOR]` e instrução de `ref=tipo`; atualizou checklist |
| `skills/agente3-skill.md` | Reescrita total | De "Validador Técnico" (obsoleto) para "Normalizador de Marcação" com 4 normalizações |
| `orientacoes/agente3-orientacao.md` | Reescrita total | Nova identidade, novo papel, nova posição no pipeline |
| `skills/agente4-skill.md` | Parcial | Adicionou Passo 0 de confirmação; completou a lista de tipos de comentários |
| `skills/agente5-skill.md` | Reescrita total | Nova estrutura XML com `<bloco palavras="N">`, contagem de palavras, quebras de página, mapeamento completo de tipos |
| `orientacoes/agente5-orientacao.md` | Parcial | Adicionou Agente 3 no pipeline; corrigiu diagrama; corrigiu descrição do output |

---

## 5. Ordem de implementação recomendada

Fazer um arquivo por vez para permitir commit entre cada passo:

1. `skills/agente3-skill.md` (reescrita total — arquivo estava completamente obsoleto)
2. `orientacoes/agente3-orientacao.md` (reescrita total — complementa o anterior)
3. `skills/agente2-skill.md` (mudanças parciais — 5 edits pontuais)
4. `skills/agente4-skill.md` (mudanças parciais — 2 edits)
5. `skills/agente5-skill.md` (reescrita total — arquivo mais crítico)
6. `orientacoes/agente5-orientacao.md` (mudanças parciais — 3 edits)
