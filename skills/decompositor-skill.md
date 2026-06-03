# SKILL — DECOMPOSITOR (Agente 0): CONSTRUTOR DE INSTRUÇÕES CURRICULARES

## Leitura obrigatória antes de iniciar

Antes de qualquer decisão, consulte (nesta ordem):

1. **`contexto/matriz-enem.json`** — base de conhecimento. Para cada habilidade (H1–H30), contém competência, foco cognitivo, operação predominante, conteúdos por área e autores de referência.
2. **`contexto/disciplinas/[disciplina].md`** — define conceitos, autores e convenções específicas da disciplina (ex: `sociologia.md`, `historia.md`).
3. **`orientacoes/decompositor-orientacao.md`** — sua identidade, papel e proibições.

Em caso de conflito, a matriz ENEM prevalece. Em caso de conflito entre a skill e a orientação, a orientação prevalece.

---

## O que você produz

Um arquivo `instrucoes.csv` para cada apostila. Salve em:
```
input/[nome-apostila]/instrucoes.csv
```

O CSV é validado pelo `pipeline.py` antes de acionar os agentes 1-5. Se alguma validação falhar, o pipeline para — responsabilidade sua.

---

## O que você recebe

Um briefing contendo:
- **Disciplina** — "Sociologia", "História", "Filosofia" ou "Geografia"
- **Habilidade ENEM** — código (H1–H30) ou descrição aproximada
- **Unidade** — nome ou tema da unidade (ex: "Estrutura social e desigualdade")
- **Pergunta da unidade** — questão central que governa toda a unidade
- **Capítulos** — lista de 1 a N capítulos com temas
- **Autores preferidos** (opcional)
- **Elementos desejáveis** (opcional)

O briefing pode estar em texto, markdown, JSON ou até uma conversa de chatbot. Você interpreta e estrutura.

---

## PASSO 0: INTERPRETAR O BRIEFING

**Objetivo:** normalizar o briefing em variáveis estruturadas.

### Extração

Leia o briefing e identifique:

1. **DISCIPLINA** — qual das quatro? Se o briefing não especificar, tente inferir do conteúdo. Se ainda assim for ambíguo, peça clarificação.
2. **HABILIDADE_ENEM** — código (H1–H30) ou descrição. Se for descrição aproximada, você precisará mapear para código na Matriz. Exemplo:
   - Briefing: "Analisar indicadores de emprego e renda"
   - Matriz: H13 — "Analisar indicadores de emprego, trabalho e renda em diferentes espaços..."
   - Você mapeia: H13

3. **UNIDADE** — nome exato. Exemplo: "Unidade 1 — Estrutura social e desigualdade"

4. **PERGUNTA_UNIDADE** — questão central. Exemplo: "Como as estruturas sociais constrangem e moldam os indivíduos — e como os indivíduos as transformam?"

5. **CAPÍTULOS** — lista com nome de cada capítulo. Exemplo:
   ```
   - Capítulo 1: Estratificação social
   - Capítulo 2: Desigualdade, raça e gênero no Brasil
   ```

6. **AUTORES_PREFERIDOS** (opcional) — lista de nomes que o professor quer incluir. Exemplo:
   ```
   - Karl Marx
   - Max Weber
   - Pierre Bourdieu
   ```

7. **ELEMENTOS_DESEJÁVEIS** (opcional) — direcionamentos pedagógicos. Exemplo:
   ```
   Usar dados IBGE/PNAD; exemplos do mercado de trabalho brasileiro
   ```

### Validação mínima

- Disciplina é uma das quatro? Sim: continua. Não: peça clarificação.
- Habilidade ENEM está na matriz (H1–H30)? Sim: continua. Não: procure por descrição aproximada ou peça clarificação.
- Unidade e pergunta estão claras? Sim: continua. Não: peça clarificação.
- Há pelo menos um capítulo? Sim: continua. Não: peça clarificação.

Se qualquer validação falhar, pare e peça ao professor que reformule o briefing.

---

## PASSO 1: CONSULTAR A MATRIZ ENEM

**Objetivo:** obter os parâmetros pedagógicos da habilidade.

### Ação

Abra `contexto/matriz-enem.json` e procure pela habilidade. Você precisa extrair:

```json
{
  "codigo": "H13",
  "competencia": "C3",
  "enunciado": "[texto completo da habilidade]",
  "foco_cognitivo": "[que tipo de pensamento esta habilidade exercita]",
  "operacao_predominante": "Mapear causalidade",
  "conteudos_por_area": {
    "Sociologia": ["...", "...", "..."],
    "Historia": ["...", "...", "..."],
    "Filosofia": ["...", "...", "..."],
    "Geografia": ["...", "...", "..."]
  },
  "autores_referencia": ["Marx", "Weber", "Bourdieu", "...]
}
```

### Extração crítica

Você **obrigatoriamente** precisa de:
1. **OPERACAO_PREDOMINANTE** — será a operação da última seção
2. **CONTEUDOS_POR_AREA[DISCIPLINA]** — filtre só a sua disciplina
3. **AUTORES_REFERENCIA** — use como complemento se o professor não especificou autores

### Se a habilidade não estiver exatamente na matriz

Procure por descrição aproximada. Exemplo:
- Briefing: "Analisar indicadores de emprego e renda em diferentes contextos"
- Matriz não tem "indicadores"
- Procura por "emprego" → encontra H13
- Mapeia para H13 com confiança

Se realmente não encontrar, peça clarificação ao professor.

---

## PASSO 2: CONSULTAR CONTEXTO DE DISCIPLINA

**Objetivo:** entender os conceitos, autores e convenções específicas da disciplina.

### Ação

Abra `contexto/disciplinas/[disciplina].md`. Este arquivo contém:
- Conceitos-chave e suas definições
- Autores importantes e suas contribuições
- Convenções e modos de falar da disciplina
- Exemplos típicos

Leia com atenção. Você o usará para:
1. Validar se os conteúdos nucleares da matriz fazem sentido para a disciplina
2. Complementar autores da matriz com nomes locais (se apropriado)
3. Contextualizar os exemplos

### Exemplo

Se disciplina = "Sociologia":
- Leia `sociologia.md`
- Identifique: quais conceitos são centrais? Quais autores clássicos?
- Use isso para calibrar suas decisões

---

## PASSO 3: PARA CADA CAPÍTULO — CONSTRUIR PROGRESSÃO DE OPERAÇÕES

**Objetivo:** decidir qual operação cognitiva cada seção executará, em ordem crescente de dificuldade.

### Hierarquia de dificuldade

```
Nível 1 (fácil):    Definir, Classificar, Sequenciar
Nível 2 (médio):    Comparar, Mapear causalidade
Nível 3 (difícil):  Reconhecer perspectiva, Aplicar
```

### Regra de progressão

1. **Seção 1:** sempre Nível 1 (Definir, Classificar ou Sequenciar)
2. **Seção 2:** pode ser Nível 1 ou 2
3. **Seção 3:** pode ser Nível 1, 2 ou 3
4. **Seção 4+:** pode ser qualquer, desde que...
   - **Nunca repita operação consecutiva** (ex: Comparar → Comparar é proibido)
   - **Última seção = OPERACAO_PREDOMINANTE da habilidade** (obtida na Matriz)

### Exemplo de progressão válida para H13 (operação predominante = Mapear causalidade)

```
Seção 1: Definir [conteúdo central]
Seção 2: Classificar [aspecto do conteúdo]
Seção 3: Comparar [perspectivas ou casos]
Seção 4: Mapear causalidade [relação causa-consequência]
```

✓ Válido: Nível 1 → Nível 1 → Nível 2 → Nível 2, sem repetição, termina em operação predominante.

Outro exemplo (6 seções):
```
Seção 1: Classificar
Seção 2: Sequenciar
Seção 3: Comparar
Seção 4: Reconhecer perspectiva
Seção 5: Aplicar
Seção 6: Mapear causalidade [se for a operação predominante]
```

### Exemplo de progressão **inválida**

```
Seção 1: Comparar [ERRADO — Nível 2, deveria ser Nível 1]
Seção 2: Comparar [ERRADO — repetição]
Seção 3: Definir [ERRADO — regressão]
```

---

## PASSO 4: PARA CADA SEÇÃO — ESCREVER MICRO-HABILIDADES

**Objetivo:** descrever o que o aluno será capaz de fazer após cada seção.

### Formato obrigatório

Micro-habilidade = Verbo + Conteúdo + Contexto

**Padrão:**
```
[Verbo da operação] [conteúdo específico] [aspecto ou contexto]
```

**Exemplos:**

| Operação | Micro-habilidade |
|----------|------------------|
| Definir | "Definir estratificação como sistema de posições desiguais criadas pela sociedade" |
| Classificar | "Classificar tipos de estratificação segundo critérios de propriedade e renda" |
| Comparar | "Comparar as visões de Marx, Weber e Bourdieu sobre desigualdade" |
| Sequenciar | "Sequenciar as transformações da estrutura de classes no Brasil desde a abolição até hoje" |
| Mapear causalidade | "Mapear como raça e gênero geram mecanismos de exclusão estrutural e interseccionalidade" |
| Reconhecer perspectiva | "Reconhecer a perspectiva do pensamento marxista sobre conflito de classes e revolução" |
| Aplicar | "Aplicar conceitos de capital cultural para analisar desigualdade educacional no Brasil" |

### Validação

Cada micro-habilidade deve passar em TODOS estes testes:

1. Começa com o verbo exato da operação? (Não: "Entender", "Compreender" — sempre verbo específico)
2. Descreve o que o **aluno faz**, não o que aprendem de forma passiva? (Sim: "classificar", não: "aprender sobre tipos")
3. É específica ao conteúdo? (Sim: "Marx e Weber", não: "diferentes autores")
4. Tem 10-20 palavras? (Se muito curta, adicione contexto; se muito longa, simplifique)
5. Não usa dois verbos? (Não: "Definir e classificar")

---

## PASSO 5: PARA CADA SEÇÃO — SELECIONAR CONTEÚDOS NUCLEARES

**Objetivo:** identificar quais conteúdos da matriz (filtrados pela disciplina) serão trabalhados em cada seção.

### Processo

1. Você tem uma lista de conteúdos da matriz para a disciplina + habilidade. Exemplo para H13 + Sociologia:
   ```
   Indicadores de emprego, Estrutura ocupacional, Trabalho precário, Desigualdade de renda,
   Mercado de trabalho segmentado, Gênero e trabalho, Raça e trabalho, ...
   ```

2. Para cada seção, decida **quais conteúdos se aplicam melhor** àquela operação. Exemplo:
   - Seção 1 (Definir): "Estrutura ocupacional; mercado de trabalho segmentado"
   - Seção 2 (Classificar): "Indicadores de emprego; desigualdade de renda"
   - Seção 3 (Comparar): "Gênero e trabalho; raça e trabalho"
   - Seção 4 (Mapear causalidade): "Trabalho precário; mercado segmentado; desigualdade de renda"

3. **Consolidar no final:** liste TODOS os conteúdos nucleares usados, separados por ponto-e-vírgula.

### Validação

- Total de conteúdos nucleares: 8-15 por capítulo
- Todos vêm da matriz para a disciplina + habilidade?
- Nenhum está repetido na lista final?

---

## PASSO 6: PARA CADA SEÇÃO — SELECIONAR AUTORES

**Objetivo:** atribuir autores às seções, respeitando progressão pedagógica e preferências do professor.

### Prioridade

1. **Autores especificados pelo professor** — use sempre que possível
2. **Autores da matriz** — use para complementar
3. **Autores do contexto da disciplina** — use apenas se necessário para contexto local

### Regra de distribuição

- Cada autor aparece **exatamente uma vez** (em uma única seção)
- Distribua de forma que as seções principais (peso Principal) tenham autores
- Autores com PESO Principal devem ter "Box Biográfico = Sim" (no core do Agente 1)
- Autores com PESO Secundário/Passagem podem não ter box

### Exemplo de distribuição (4 autores para 4 seções)

```
Capítulo: Estratificação social
Autores professor: Marx, Weber, Bourdieu
Autores matriz: Dahrendorf, Lenski, Pakulski, Waters

Seção 1 (Definir — Principal):
  Contenido: definição de estratificação
  Autor: Marx [PESO Principal]

Seção 2 (Classificar — Principal):
  Conteúdo: tipos de estratificação
  Autor: Weber [PESO Principal]

Seção 3 (Comparar — Secundário):
  Conteúdo: diferentes visões
  Autor: Bourdieu [PESO Secundário]

Seção 4 (Aplicar — Principal):
  Conteúdo: aplicação ao Brasil
  Autor: VAZIO [nenhum autor obrigatório em Aplicar, a menos que haja ilustração de um pensador]
```

### Validação

- Todos os autores do professor estão no CSV?
- Nenhum autor está repetido?
- Autores PESO Principal têm nomes completos + datas?

---

## PASSO 7: PARA CADA CAPÍTULO — MONTAR A LINHA DO CSV

**Objetivo:** construir uma linha CSV bem-formada e válida.

### Template de linha CSV

```csv
disciplina,unidade,pergunta_unidade,capitulo,habilidade_principal,micro_hab_1,operacao_secao_1,micro_hab_2,operacao_secao_2,micro_hab_3,operacao_secao_3,micro_hab_4,operacao_secao_4,micro_hab_5,operacao_secao_5,micro_hab_6,operacao_secao_6,conteudos_nucleares,autores,elementos_desejáveis
```

### Preenchimento campo a campo

| Campo | Fonte | Exemplo | Regras |
|-------|-------|---------|--------|
| `disciplina` | briefing | Sociologia | Uma das quatro: Sociologia, História, Filosofia, Geografia |
| `unidade` | briefing | "Unidade 1 — Estrutura social" | Idêntico para capítulos da mesma unidade |
| `pergunta_unidade` | briefing | "Como as estruturas moldam os indivíduos?" | Idêntico para capítulos da mesma unidade |
| `capitulo` | briefing | "Capítulo 1: Estratificação social" | Começa com "Capítulo N:" |
| `habilidade_principal` | matriz ENEM | "EM13CHS402 - Analisar e comparar..." | Código + enunciado completo da matriz |
| `micro_hab_1` | Passo 4 | "Definir estratificação como..." | Obrigatório |
| `operacao_secao_1` | Passo 3 | Definir | Obrigatório, um da lista de 7 |
| `micro_hab_2` | Passo 4 | "Classificar tipos de..." | Obrigatório |
| `operacao_secao_2` | Passo 3 | Classificar | Obrigatório |
| `micro_hab_3` | Passo 4 | "Comparar visões de..." | Obrigatório |
| `operacao_secao_3` | Passo 3 | Comparar | Obrigatório |
| `micro_hab_4` | Passo 4 | "Aplicar conceitos..." | Obrigatório (seção 4 é mínimo) |
| `operacao_secao_4` | Passo 3 | Aplicar | Obrigatório |
| `micro_hab_5` | Passo 4 | "..." ou vazio | Opcional (se houver 5+ seções) |
| `operacao_secao_5` | Passo 3 | "..." ou vazio | Opcional |
| `micro_hab_6` | Passo 4 | "..." ou vazio | Opcional (máximo 6 seções) |
| `operacao_secao_6` | Passo 3 | "..." ou vazio | Opcional |
| `conteudos_nucleares` | Passo 5 | "Estratificação; classe social; ..." | Separados por "; " (ponto-e-vírgula + espaço), sem quebra de linha |
| `autores` | Passo 6 | "Karl Marx; Max Weber; Pierre Bourdieu" | Separados por "; ", nomes completos |
| `elementos_desejáveis` | briefing | "Usar dados IBGE; exemplos Brasil" | Opcional, separados por "; " |

### Exemplo completo de linha CSV

```csv
Sociologia,Unidade 1 — Estrutura social,Como as estruturas sociais constrangem os indivíduos?,Capítulo 1: Estratificação social,EM13CHS402 - Analisar e comparar indicadores de emprego trabalho e renda,Definir estratificação como sistema de posições desiguais criadas pela sociedade,Definir,Classificar tipos de estratificação segundo critérios de propriedade e renda,Classificar,Comparar as visões de Marx Weber e Bourdieu sobre desigualdade,Comparar,Aplicar conceitos de capital para analisar desigualdade no Brasil,Aplicar,,,,,Estratificação social; classe social; posições desiguais; meios de produção; capital econômico; capital cultural; desigualdade socioeconômica; mobilidade social,Karl Marx; Max Weber; Pierre Bourdieu,Usar dados IBGE; exemplos mercado trabalho brasileiro
```

**Nota:** Este é **uma linha**. Se houver quebra, é erro de formatação.

---

## PASSO 8: VALIDAÇÃO OBRIGATÓRIA

Antes de salvar o CSV, responda a CADA item:

### Validação estrutural

- [ ] O arquivo é um `.csv` válido (separado por vírgula)?
- [ ] Cada linha tem exatamente o número correto de colunas (19-22)?
- [ ] Nenhuma célula obrigatória está vazia?
- [ ] Nenhuma célula contém quebra de linha (`\n`)?

### Validação de operações

- [ ] Toda `operacao_secao_N` é uma das 7 válidas?
- [ ] Nenhuma operação está repetida consecutivamente (operacao_1 ≠ operacao_2)?
- [ ] A primeira operação é Nível 1 (Definir, Classificar ou Sequenciar)?
- [ ] A última operação é a OPERACAO_PREDOMINANTE da habilidade (da matriz)?
- [ ] Existe progressão crescente de dificuldade?

### Validação de micro-habilidades

- [ ] Toda `micro_hab_N` começa com um verbo específico (não "compreender", "entender")?
- [ ] Toda `micro_hab_N` descreve o que o aluno **faz**?
- [ ] Toda `micro_hab_N` é específica ao conteúdo (não genérica)?
- [ ] Nenhuma `micro_hab_N` usa dois verbos?

### Validação de conteúdos

- [ ] `conteudos_nucleares` tem 8-15 itens (separados por "; ")?
- [ ] Todos os conteúdos vêm da matriz para a habilidade + disciplina?
- [ ] Nenhum conteúdo está repetido na lista?

### Validação de autores

- [ ] `autores` contém nomes completos (não apelidos)?
- [ ] Nenhum autor está repetido na lista?
- [ ] Todos os autores do briefing do professor estão presentes (se possível)?

### Validação de habilidade

- [ ] `habilidade_principal` está na matriz (H1–H30)?
- [ ] `habilidade_principal` contém código + enunciado completo?
- [ ] A `operacao_secao_4+` corresponde ao `operacao_predominante` da habilidade?

### Validação de unidade

- [ ] `unidade` é idêntica para todos os capítulos da mesma unidade?
- [ ] `pergunta_unidade` é idêntica para todos os capítulos da mesma unidade?

Se qualquer validação falhar, **não salve o CSV**. Corrija o erro e re-valide.

---

## PASSO 9: SALVAR O CSV

**Objetivo:** guardar o CSV no local esperado pelo pipeline.

### Comando

Salve em:
```
input/[apostila-nome]/instrucoes.csv
```

Exemplo:
```
input/apostila-sociologia-desigualdade/instrucoes.csv
```

### Formato

- Encoding: UTF-8
- Separador: vírgula (`,`)
- Sem quebras de linha nas células
- Com cabeçalho (primeira linha)

### Validação final (pipeline.py)

O arquivo será validado por `pipeline.py` ao ser consumido. Se falhar, você receberá um erro do tipo:

```
ValueError: Coluna obrigatória 'operacao_secao_2' vazia na linha 2
ValidationError: Operação 'Analisar' não está na lista de 7 válidas
```

Se isso ocorrer, volte a este documento, encontre o erro e corrija o CSV.

---

## ARMADILHAS COMUNS

### Armadilha 1: Micro-habilidades com verbos genéricos

**Erro:**
```
"Compreender o conceito de classe social"
"Aprender sobre Marx e Weber"
```

**Por quê:** Não descreve ação específica do aluno.

**Correção:**
```
"Definir classe social como relação com meios de produção"
"Reconhecer a perspectiva de Marx e Weber sobre classe"
```

---

### Armadilha 2: Repetição de operações consecutivas

**Erro:**
```
operacao_secao_1: Definir
operacao_secao_2: Definir
operacao_secao_3: Comparar
```

**Por quê:** Viola progressão pedagógica.

**Correção:**
```
operacao_secao_1: Definir
operacao_secao_2: Classificar
operacao_secao_3: Comparar
```

---

### Armadilha 3: Operação final não é a operacao_predominante

**Erro:**
Habilidade H13 tem `operacao_predominante: "Mapear causalidade"`, mas você preenche:
```
operacao_secao_4: Aplicar
```

**Por quê:** Viola a regra de que a última operação deve responder ao verbo principal da habilidade.

**Correção:**
```
operacao_secao_1: Definir
operacao_secao_2: Classificar
operacao_secao_3: Comparar
operacao_secao_4: Mapear causalidade
```

---

### Armadilha 4: Conteúdos nucleares não vêm da matriz

**Erro:**
Você inventa conteúdos não listados na matriz.

**Por quê:** O pipeline espera conteúdos alinhados à BNCC/ENEM.

**Correção:**
Sempre filtre pela disciplina + habilidade na matriz. Se o professor quer um conteúdo não listado, adicione-o ao campo `elementos_desejáveis`.

---

### Armadilha 5: Autores sem atribuição de seção

**Erro:**
Professor lista 5 autores, você inclui só 3 no CSV.

**Por quê:** Você achou que faltavam seções, mas há 4 seções obrigatórias.

**Correção:**
Distribua 1 autor por seção (mínimo 4). Se há mais de 6 autores, escolha os mais relevantes.

---

### Armadilha 6: Primeira seção não é Nível 1

**Erro:**
```
operacao_secao_1: Comparar
```

**Por quê:** O aluno ainda não tem base para comparar.

**Correção:**
```
operacao_secao_1: Definir
```

---

### Armadilha 7: Conteúdos nucleares com quebra de linha

**Erro:**
```
conteudos_nucleares: Estratificação social,
classe social,
desigualdade
```

**Por quê:** CSV quebra quando há quebra de linha nas células.

**Correção:**
```
conteudos_nucleares: Estratificação social; classe social; desigualdade
```

---

### Armadilha 8: Habilidade incompleta ou fora da matriz

**Erro:**
```
habilidade_principal: H99 - Analisar algo
```
(H99 não existe)

**Correção:**
Mapeie para uma habilidade existente (H1–H30). Se impossível, peça clarificação ao professor.

---

## CHECKLIST FINAL ANTES DE SALVAR

- [ ] Li `contexto/matriz-enem.json` para a habilidade?
- [ ] Li `contexto/disciplinas/[disciplina].md`?
- [ ] Interpretei corretamente o briefing?
- [ ] Defini progressão válida de operações (sem repetição, Nível 1 → Nível 3)?
- [ ] Escrevi micro-habilidades com verbo específico + contexto?
- [ ] Selecionei conteúdos nucleares da matriz (filtrados por disciplina)?
- [ ] Distribuí autores (1 por seção, priorizando professor)?
- [ ] Montei linha CSV sem erros de formatação?
- [ ] Validei TODA a seção "VALIDAÇÃO OBRIGATÓRIA"?
- [ ] CSV será salvo em `input/[apostila]/instrucoes.csv`?

Se qualquer checkbox for **Não**, volte e corrija antes de salvar.

---

**Data de vigência:** 03/06/2026 (imediata).

**Próximo passo após salvar:** O pipeline.py consumirá o CSV e acionará o Agente 1.
