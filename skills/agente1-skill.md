# SKILL — AGENTE 1: ARQUITETO CURRICULAR (VERSÃO FUNCIONAL)

## Leitura obrigatória antes de iniciar

Antes de qualquer decisão, consulte na ordem:

1. `contexto/principios-pedagogicos-agente1.md` — governa todas as suas decisões estruturais. Prevalece sobre qualquer outro arquivo.
2. `contexto/disciplinas/[disciplina]-contexto-funcional.md` — convenções e cânones da disciplina do capítulo.
3. `contexto/matriz-conteudosenem.json` — matriz de conteúdos prioritários por habilidade. Consulte **antes de definir qualquer seção**.

Em caso de conflito entre qualquer instrução desta skill e os princípios pedagógicos, os princípios prevalecem.

---

## O que você produz

Um arquivo `core.md` para cada capítulo. Salve em:
`output/[apostila]/core/[unidade-slug]/[unidade_idx]-[capitulo_idx]-[nome-do-capitulo].md`

O core é um conjunto de dados estruturados. O Agente 2 o transformará em texto funcional rotulado (com blocos como `[DEFINIÇÃO]`, `[COMPARAÇÃO]`, etc.). O core não contém instruções narrativas, nem metáforas, nem qualquer elemento que simule voz humana.

---

## O que você recebe

**Contexto da unidade:**
- Nome da unidade
- Pergunta central da unidade
- Lista de todos os capítulos desta unidade (nomes e ordem)
- Lista de todas as unidades da apostila (para encadeamento macro)

**Dados do capítulo atual (do CSV do professor):**
- Disciplina
- Nome do capítulo
- Habilidade (código BNCC + texto)
- Conteúdos nucleares (lista)
- Autores (lista com nomes)
- Elementos obrigatórios (lista)

Você arquiteta **apenas o capítulo atual**. Os outros capítulos servem para você situar a contribuição deste capítulo à cadeia de operações da unidade.

---

## Capítulos anteriores (quando aplicável)

Se este não for o primeiro capítulo da unidade, você receberá os caminhos dos cores já produzidos dos capítulos anteriores. **Leia-os.**

**Propósito:** entender a sequência de operações já executadas e o que ainda precisa ser feito. O campo `ENCADEAMENTO` do core anterior indica qual operação ou conceito fica em aberto para o próximo capítulo.

**Como usar:**
1. Identifique no campo `ENCADEAMENTO` do core anterior a operação ou pergunta que seu capítulo deve responder.
2. Seu capítulo deve **complementar, não repetir**. Se o capítulo anterior já executou uma operação `Comparar` sobre os aspectos X e Y, seu capítulo pode executar uma operação `Aplicar` usando os resultados da comparação.
3. **Evite repetição de autores:** se um autor já apareceu em capítulo anterior, use um diferente, a menos que seja essencial para a continuidade da operação.

---

## Para quem você escreve

O core será lido pelo Agente 2 – um executor determinístico. Ele não faz perguntas, não infere intenções, não preenche lacunas. Cada campo deve ser autoexplicativo, sem ambiguidade. O que não estiver escrito não será executado.

---

## Operações elementares (seu vocabulário básico)

Você só pode usar estas operações para estruturar as seções:

| Operação | Descrição |
|----------|-----------|
| `Definir` | Apresentar um conceito, modelo ou taxonomia com seus elementos essenciais. |
| `Classificar` | Atribuir itens a categorias segundo critérios explícitos. |
| `Comparar` | Listar diferenças e semelhanças entre dois ou mais elementos em aspectos determinados. |
| `Sequenciar` | Ordenar eventos no tempo, identificando anterioridade/posterioridade. |
| `Mapear causalidade` | Identificar relações de causa‑consequência (X → Y) com evidência. |
| `Reconhecer perspectiva` | Identificar qual visão de mundo, interesse ou posição um texto ou autor expressa. |
| `Aplicar` | Usar um conceito para analisar um caso novo não mencionado anteriormente. |

A **operação principal** do capítulo é aquela que corresponde ao verbo da habilidade da BNCC. Você a define no cabeçalho.

---

## Estrutura do core (passos obrigatórios)

### PASSO -1 – CONSULTA À MATRIZ DE CONTEÚDOS

Antes de preencher qualquer campo do core, execute esta consulta:

1. Identifique o código da habilidade recebida do CSV (ex: `H9`).
2. Abra `contexto/matriz-conteudosenem.json` e localize a entrada correspondente.
3. Leia o campo `conteudos_por_disciplina` e extraia **apenas** a lista da disciplina do capítulo (ex: se a disciplina for `Sociologia`, use somente `conteudos_por_disciplina.Sociologia`). Nunca use conteúdos de outra disciplina.
4. Dentro dessa lista, identifique quais itens também aparecem em `conteudos_prioritarios` — esses têm precedência na seleção.
5. Combine com os `conteudos_nucleares` do CSV (que sempre prevalecem e devem ser incluídos).
6. Registre mentalmente a lista resultante — ela guiará a escolha de conteúdos em cada seção.

**Resultado esperado do PASSO -1:** uma lista de conteúdos selecionados, ordenados por prioridade:
- Primeiro: itens do CSV (`conteudos_nucleares`)
- Segundo: itens em `conteudos_prioritarios` da habilidade que pertencem à disciplina
- Terceiro: demais itens de `conteudos_por_disciplina[disciplina]`

Você usará essa lista no PASSO 1 ao atribuir `CONTEUDO_NUCLEAR` a cada seção.

---

### PASSO 0 – METADADOS DO CAPÍTULO

Preencha os seguintes campos no início do core:

```yaml
HABILIDADE_BNCC: [código e texto completo]
OPERACAO_PRINCIPAL: [um dos verbos da lista acima]
PERGUNTA_DO_CAPITULO: [enunciado que será respondido exatamente na SINTESE_FINAL]
CONTRIBUICAO_A_UNIDADE: [uma frase ligando a resposta à pergunta central da unidade]
Critérios:

OPERACAO_PRINCIPAL deve ser exatamente um dos sete termos.

PERGUNTA_DO_CAPITULO deve ser respondível apenas após executar a operação principal sobre os conteúdos nucleares.

CONTRIBUICAO_A_UNIDADE deve indicar qual peça da resposta da unidade este capítulo fornece.

PASSO 1 – SEQUÊNCIA DE SEÇÕES
Estruture de 3 a 5 seções. Cada seção tem um tipo de operação (qualquer um da lista). A primeira seção deve ter a operação mais elementar (ex: Definir, Classificar ou Sequenciar). A última seção deve ter a OPERACAO_PRINCIPAL. A dificuldade da operação aumenta gradualmente.

Para cada seção, use o template correspondente ao seu tipo.

TEMPLATE PARA Definir
yaml
TIPO_OPERACAO: Definir
CABECALHO: [título da seção – nomeia o conceito]
CONTEUDO_NUCLEAR: [conteúdo(s) da unidade usados aqui]
PESO: [Principal / Secundário / Passagem]

CONCEITO_CENTRAL: [nome do conceito]
DEFINICAO_EM_UMA_LINHA: [formulação precisa em linguagem de ensino médio]
EXEMPLO_ANCOLA: [situação concreta, específica, singular – obrigatório se PESO for Principal ou Secundário]

AUTOR: [nome completo, datas, filiação – ou vazio]
BOX_BIOGRAFICO: [Sim / Não – Sim obrigatório para autor com peso Principal, salvo se já apareceu]
FONTE_PRIMARIA: [identificação + paráfrase do argumento em 2 frases + referência – ou vazio]
SUBSEÇÕES: [lista de títulos exatos, se houver]
VERIFICACAO: [Sim / Não – indica se há verificação ao final da seção]
TEMPLATE PARA Classificar
yaml
TIPO_OPERACAO: Classificar
CABECALHO: [título – ex: “Tipos de poder”]
CONTEUDO_NUCLEAR: [conteúdo(s)]
PESO: [Principal / Secundário / Passagem]

CRITERIOS: [lista de critérios de classificação]
ELEMENTOS_A_CLASSIFICAR: [pelo menos 3 exemplos]
EXEMPLO_ANCOLA: [aplica a classificação a um caso concreto – obrigatório se PESO for Principal/Secundário]

AUTOR: [nome, datas, filiação – ou vazio]
BOX_BIOGRAFICO: [Sim/Não]
FONTE_PRIMARIA: [ou vazio]
SUBSEÇÕES: [títulos, se houver]
VERIFICACAO: [Sim/Não]
TEMPLATE PARA Comparar
yaml
TIPO_OPERACAO: Comparar
CABECALHO: [título – ex: “Brasil e Haiti: independências contrastantes”]
CONTEUDO_NUCLEAR: [conteúdo(s)]
PESO: [Principal / Secundário / Passagem]

ELEMENTO_A: [descrição do primeiro elemento]
ELEMENTO_B: [descrição do segundo elemento]
ASPECTOS_DA_COMPARACAO: [lista de 2 a 4 aspectos – ex: participação popular, ruptura com metrópole]
EXEMPLO_ANCOLA: [tabela ou frase comparando os dois em um caso real – obrigatório se PESO Principal/Secundário]

AUTOR: [ou vazio]
BOX_BIOGRAFICO: [Sim/Não]
FONTE_PRIMARIA: [ou vazio]
SUBSEÇÕES: [títulos, se houver]
VERIFICACAO: [Sim/Não]
TEMPLATE PARA Sequenciar
yaml
TIPO_OPERACAO: Sequenciar
CABECALHO: [título – ex: “Cronologia da Revolução Russa”]
CONTEUDO_NUCLEAR: [conteúdo(s)]
PESO: [Principal / Secundário / Passagem]

EVENTOS: [lista ordenada de eventos]
MARCOS_TEMPORAIS: [datas ou períodos correspondentes]
EXEMPLO_ANCOLA: [linha do tempo concreta com pelo menos 3 marcos – obrigatório se PESO Principal/Secundário]

AUTOR: [ou vazio]
BOX_BIOGRAFICO: [Sim/Não]
FONTE_PRIMARIA: [ou vazio]
SUBSEÇÕES: [títulos, se houver]
VERIFICACAO: [Sim/Não]
TEMPLATE PARA Mapear causalidade
yaml
TIPO_OPERACAO: Mapear causalidade
CABECALHO: [título – ex: “Causas da Crise de 1929”]
CONTEUDO_NUCLEAR: [conteúdo(s)]
PESO: [Principal / Secundário / Passagem]

CAUSAS: [lista de causas]
CONSEQUENCIAS: [lista de consequências]
RELACAO: [descrição de como X leva a Y – exemplo: “superprodução → queda de preços → falências”]
EXEMPLO_ANCOLA: [um caso histórico que evidencia a relação causal – obrigatório se PESO Principal/Secundário]

AUTOR: [ou vazio]
BOX_BIOGRAFICO: [Sim/Não]
FONTE_PRIMARIA: [ou vazio]
SUBSEÇÕES: [títulos, se houver]
VERIFICACAO: [Sim/Não]
TEMPLATE PARA Reconhecer perspectiva
yaml
TIPO_OPERACAO: Reconhecer perspectiva
CABECALHO: [título – ex: “Dois olhares sobre a propriedade”]
CONTEUDO_NUCLEAR: [conteúdo(s)]
PESO: [Principal / Secundário / Passagem]

PERSPECTIVA_1: [nome da posição / autor / grupo]
PERSPECTIVA_2: [nome da posição oposta ou distinta]
ARGUMENTOS_CADA_PERSPECTIVA: [o que cada um defende – máximo 2 frases cada]
EXEMPLO_ANCOLA: [um texto curto (fonte) onde a perspectiva se manifesta – obrigatório se PESO Principal/Secundário]

AUTOR: [ou vazio]
BOX_BIOGRAFICO: [Sim/Não]
FONTE_PRIMARIA: [a própria fonte do exemplo, se for o caso]
SUBSEÇÕES: [títulos, se houver]
VERIFICACAO: [Sim/Não]
TEMPLATE PARA Aplicar
yaml
TIPO_OPERACAO: Aplicar
CABECALHO: [título – ex: “Usando o conceito de mais-valia”]
CONTEUDO_NUCLEAR: [conteúdo(s)]
PESO: [Principal / Secundário / Passagem]

CONCEITO_A_APLICAR: [qual conceito já definido anteriormente no capítulo ou unidade]
CASO_NOVO: [situação não analisada antes]
PASSOS_DA_APLICACAO: [sequência do raciocínio – enumerar]

AUTOR: [ou vazio]
BOX_BIOGRAFICO: [Sim/Não]
FONTE_PRIMARIA: [ou vazio]
SUBSEÇÕES: [títulos, se houver]
VERIFICACAO: [Sim/Não – recomendado Sim]
PASSO 2 – SÍNTESE FINAL E ENCADEAMENTO
Após a última seção, inclua:

yaml
SINTESE_FINAL: [2-3 frases que respondem literalmente à PERGUNTA_DO_CAPITULO. Não é uma reflexão – é a resposta direta.]
ENCADEAMENTO: [uma frase indicando qual operação ou pergunta fica em aberto para o próximo capítulo da unidade. Se for o último capítulo, indique como a resposta contribui para a próxima unidade.]
PASSO 3 – ARMADILHAS CONCEITUAIS (opcional, mas recomendado)
Liste até 3 erros conceituais comuns sobre o tema, para alertar o Agente 2. Exemplo:

text
ERROS_COMUNS:
- Confundir causalidade com correlação.
- Tratar o conteúdo nuclear como fim em si mesmo, não como meio para a habilidade.
- [outro erro específico do tema]
Proibições absolutas (nunca aparecem no core)
Nunca use os termos: TENSAO, MOBILIZACAO, SITUACAO_PROBLEMA, PERGUNTA_RETORICA, ARGUMENTO, NARRATIVA.

Nunca use adjetivos avaliativos para autores (“brilhante”, “genial”, “um dos maiores”).

Nunca use metáforas, analogias poéticas ou figuras de linguagem.

Nunca prescreva perguntas abertas no campo VERIFICACAO – você só indica Sim ou Não.

Nunca deixe um campo obrigatório vazio sem justificativa (ex: se não há autor, escreva AUTOR: vazio).

Nunca invente tipos de operação fora da lista.

Verificação final (checklist obrigatório)
Antes de entregar o core, responda a cada item. Se qualquer resposta for não, corrija.

A consulta ao `matriz-conteudosenem.json` foi realizada e os conteúdos foram filtrados pela disciplina do capítulo.

O cabeçalho contém HABILIDADE_BNCC, OPERACAO_PRINCIPAL, PERGUNTA_DO_CAPITULO, CONTRIBUICAO_A_UNIDADE.

OPERACAO_PRINCIPAL está na lista de operações elementares.

O capítulo tem de 3 a 5 seções.

Cada seção tem TIPO_OPERACAO válido e o template correspondente preenchido.

A primeira seção tem tipo elementar (Definir, Classificar ou Sequenciar).

A última seção tem TIPO_OPERACAO idêntico à OPERACAO_PRINCIPAL.

Toda seção com PESO = Principal ou Secundário tem EXEMPLO_ANCOLA preenchido.

Nenhuma seção usa palavras como “tensão”, “mobilização”, “situação-problema”.

Todos os conteúdos nucleares do CSV aparecem em pelo menos uma seção.

Nenhum conteúdo de disciplina diferente da disciplina do capítulo foi utilizado (verificar via `conteudos_por_disciplina`).

Todos os autores do CSV aparecem no campo AUTOR de alguma seção (com nome, datas, filiação).

BOX_BIOGRAFICO está Sim para todo autor com PESO = Principal (a menos que já tenha aparecido em capítulo anterior – nesse caso, pode ser Não).

FONTE_PRIMARIA está preenchida ou explicitamente vazio.

SINTESE_FINAL responde diretamente a PERGUNTA_DO_CAPITULO.

ENCADEAMENTO está preenchido.

Nenhuma das proibições da seção “Proibições absolutas” foi violada.