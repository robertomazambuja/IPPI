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
<!-- Habilidade: EM13CHS401 — Identificar e analisar... -->
<!-- Operação principal: Mapear causalidade -->
<!-- Pergunta do capítulo: Como...? -->
<!-- Por que importa: Este capítulo... -->
<!-- [/CONTEXTO_OPERACAO] -->
```

**✅ Formato correto:**
```
<!-- [CONTEXTO_OPERACAO] -->
**Habilidade:** EM13CHS401 — Identificar e analisar...
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
`CONTEXTO_OPERACAO, TIPO_OPERACAO, APRESENTACAO, DEFINICAO, CLASSIFICACAO, SUBTIPO, PERSPECTIVA, EXEMPLO, CAUSA, CONSEQUENCIA, RELACAO_CAUSAL, INTRODUCAO_COMPARACAO, CONCLUSAO_PARCIAL, COMPARACAO, APLICACAO, RESULTADO, AUTOR, FONTE, FONTE_PRIMARIA, VERIFICACAO, SINTESE, ENCADEAMENTO`

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
