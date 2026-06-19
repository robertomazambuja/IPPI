# SKILL — DECOMPOSITOR (Agente 0)

## Leitura obrigatória antes de iniciar

1. `contexto/matriz-bncc.json` — base de conhecimento EM13CHS101–EM13CHS606
2. `orientacoes/decompositor-orientacao.md` — sua identidade, escopo e proibições

Em caso de conflito entre este documento e a orientação, a orientação prevalece.

---

## O que você produz

Um arquivo `instrucoes.json` salvo em:

```
input/[nome-da-apostila]/instrucoes.json
```

Você produz **apenas a parte gerativa**: para cada capítulo, a lista de micro-habilidades com suas operações. O `pipeline.py` faz a serialização determinística para `instrucoes.csv` — ele preenche disciplina, unidade, pergunta, enunciado da habilidade, autores e conteúdos a partir do briefing e da matriz. **Você não escreve CSV e não recopia esses campos.** Isso elimina erros de formatação (vírgulas, aspas, alinhamento de colunas) e garante fidelidade à matriz.

---

## PASSO 1 — LER O BRIEFING

Extraia e normalize as seguintes variáveis:

| Variável | Campo no JSON | Obrigatório |
|---|---|---|
| DISCIPLINA | `disciplina` | Sim |
| HABILIDADE | `habilidade_bncc` | Sim |
| UNIDADE | `unidade` | Sim |
| PERGUNTA | `pergunta_unidade` | Sim |
| CAPÍTULOS | `capitulos` | Sim (mínimo 1) |
| AUTORES_POR_CAPITULO | `autores_por_capitulo` | Não |
| CONTEUDOS_POR_CAPITULO | `conteudos_por_capitulo` | Não |

Se qualquer campo obrigatório estiver ausente ou ambíguo, interrompa e solicite correção.

---

## PASSO 2 — USAR A ENTRADA DA HABILIDADE

A entrada da habilidade de `matriz-bncc.json` já está injetada no user message pelo pipeline — **não é necessário ler o arquivo**. Use o JSON fornecido diretamente. Extraia o que orienta suas micro-habilidades:

```
foco_cognitivo     → que tipo de pensamento ela exercita
operacao_predominante → operação que encerrará cada sequência
sequencia_pedagogica  → lista de operações em ordem (o seu template)
```

O `enunciado` **não** precisa ser copiado por você — o pipeline o injeta no CSV direto da matriz (fonte de verdade). Use-o apenas como contexto para escrever micro-habilidades pertinentes.

Você **não** usa `conteudos_por_area`. Esse campo é para o Agente 1. (A matriz BNCC não traz `autores_referencia`; os autores vêm do briefing.)

### Exemplo — EM13CHS402

```json
"enunciado": "Analisar e comparar indicadores de emprego, trabalho e renda em diferentes espaços, escalas e tempos, associando-os a processos de estratificação e desigualdade socioeconômica.",
"foco_cognitivo": "Comparação de indicadores de emprego, trabalho e renda associados à estratificação.",
"operacao_predominante": "Comparar",
"sequencia_pedagogica": [
  {"ordem": 1, "operacao": "Definir"},
  {"ordem": 2, "operacao": "Classificar"},
  {"ordem": 3, "operacao": "Sequenciar"},
  {"ordem": 4, "operacao": "Comparar"}
]
```

---

## PASSO 3 — PARA CADA CAPÍTULO: ESCREVER MICRO-HABILIDADES

Para cada capítulo do briefing, siga a `sequencia_pedagogica` da habilidade e escreva uma micro-habilidade por operação.

### Formato de cada micro-habilidade

```
[Verbo da operação] [objeto conceitual do capítulo] [contexto quando necessário]
```

O objeto conceitual vem do **tema do capítulo** (não da matriz, não dos autores).

### Regra de abstração — o limite que não pode cruzar

A micro-habilidade descreve **o que o aluno faz cognitivamente** e **sobre qual domínio conceitual**. Ela não prescreve com quais autores, dados ou exemplos isso será feito — essa decisão é do Agente 1.

| ✓ Válido | ✗ Inválido |
|---|---|
| `"Comparar perspectivas teóricas sobre estratificação"` | `"Comparar Marx, Weber e Bourdieu"` |
| `"Mapear relações causais entre estrutura e desigualdade"` | `"Usar dados do IBGE para mapear desigualdade"` |
| `"Reconhecer perspectivas sobre desigualdade racial"` | `"Reconhecer a perspectiva de Lélia Gonzalez"` |
| `"Definir raça como categoria socialmente construída"` | `"Entender o conceito de raça"` |

### Exemplo completo — EM13CHS402, dois capítulos

**Capítulo 1: Estrutura social e estratificação social**
*(sequencia_pedagogica de EM13CHS402: Definir → Classificar → Sequenciar → Comparar)*

```
micro_hab_1: "Definir estratificação como sistema de hierarquias e posições desiguais"
operacao_1:  Definir

micro_hab_2: "Classificar formas de estratificação segundo critérios econômicos, culturais e simbólicos"
operacao_2:  Classificar

micro_hab_3: "Sequenciar os processos que produzem e reproduzem a estratificação ao longo do tempo"
operacao_3:  Sequenciar

micro_hab_4: "Comparar interpretações sobre estratificação e desigualdade social"
operacao_4:  Comparar
```

**Capítulo 2: Desigualdade, raça e gênero no Brasil**
*(mesma sequencia_pedagogica de EM13CHS402)*

```
micro_hab_1: "Definir raça e gênero como categorias socialmente construídas de diferenciação"
operacao_1:  Definir

micro_hab_2: "Classificar formas de desigualdade estrutural segundo raça, gênero e classe"
operacao_2:  Classificar

micro_hab_3: "Sequenciar as etapas históricas de formação das desigualdades de raça e gênero no Brasil"
operacao_3:  Sequenciar

micro_hab_4: "Comparar condições socioeconômicas de diferentes grupos raciais e de gênero"
operacao_4:  Comparar
```

A `sequencia_pedagogica` é a mesma nos dois capítulos. O que muda é o objeto conceitual — determinado pelo tema de cada capítulo.

---

## PASSO 4 — MONTAR O JSON

Produza um objeto JSON com uma entrada por capítulo. Para cada capítulo você fornece **somente** o nome do capítulo (exatamente como no briefing) e a lista de seções (micro-habilidade + operação).

**Não** inclua `disciplina`, `unidade`, `pergunta_unidade`, `habilidade`/enunciado, `autores` nem `conteudos_nucleares` — o pipeline preenche esses campos a partir do briefing e da matriz. Sua responsabilidade é exclusivamente a arquitetura cognitiva (as micro-habilidades e a ordem das operações).

### Formato exato

```json
{
  "capitulos": [
    {
      "capitulo": "Capítulo 1 — <nome exato do briefing>",
      "secoes": [
        {"micro_hab": "Definir estratificação como sistema de hierarquias e posições desiguais", "operacao": "Definir"},
        {"micro_hab": "Classificar formas de estratificação segundo critérios econômicos, culturais e simbólicos", "operacao": "Classificar"},
        {"micro_hab": "Sequenciar os processos que produzem e reproduzem a estratificação ao longo do tempo", "operacao": "Sequenciar"},
        {"micro_hab": "Comparar interpretações sobre estratificação e desigualdade social", "operacao": "Comparar"}
      ]
    }
  ]
}
```

**Regras do JSON:**

- `capitulo` deve ser **idêntico** (caractere a caractere) ao nome no briefing — é a chave de casamento usada pelo pipeline.
- `secoes` tem entre 4 e 6 itens, na ordem da `sequencia_pedagogica`.
- `operacao` deve ser uma das 7 operações válidas, com grafia exata.
- Vírgulas dentro de `micro_hab` são livres — é JSON, não há risco de quebrar colunas.

---

## PASSO 5 — VALIDAR ANTES DE SALVAR

Antes de salvar o `instrucoes.json`, confirme para cada capítulo:

**Operações:**
- [ ] Entre 4 e 6 seções?
- [ ] Primeira operação é Nível 1 (Definir, Classificar ou Sequenciar)?
- [ ] Última operação é a `operacao_predominante` da habilidade?
- [ ] Nenhuma operação repetida em posições consecutivas?
- [ ] Todas as operações estão na lista das 7 válidas (grafia exata)?

**Micro-habilidades:**
- [ ] Cada micro-habilidade começa com o verbo exato da operação?
- [ ] Nenhuma micro-habilidade nomeia autores, fontes de dados ou exemplos específicos?
- [ ] Cada micro-habilidade é específica ao tema do capítulo (não genérica)?

**JSON:**
- [ ] É JSON válido (parseável)?
- [ ] Há um objeto por capítulo do briefing, com `capitulo` idêntico ao briefing?
- [ ] Cada capítulo do briefing está presente?

Se qualquer validação falhar, corrija antes de salvar.

---

## ARMADILHAS COMUNS

**Armadilha 1 — Nomear autores na micro-habilidade**

Errado: `"Comparar Marx, Weber e Bourdieu sobre estratificação"`
Certo: `"Comparar perspectivas teóricas sobre estratificação e desigualdade"`

**Armadilha 2 — Micro-habilidade genérica**

Errado: `"Definir conceitos de sociologia"`
Certo: `"Definir estratificação como sistema de hierarquias e posições desiguais"`

**Armadilha 3 — Última operação errada**

Errado (para EM13CHS402): terminar em `Aplicar`
Certo: terminar em `Comparar` (que é a `operacao_predominante` de EM13CHS402)

**Armadilha 4 — Operação consecutiva repetida**

Errado: `Definir → Definir → Comparar`
Certo: `Definir → Classificar → Comparar`

**Armadilha 5 — Distribuir autores entre capítulos**

Errado: atribuir Marx ao Capítulo 1 e Lélia Gonzalez ao Capítulo 2
Certo: copiar a lista completa para todos os capítulos

---

## CHECKLIST FINAL

- [ ] Usei a entrada da habilidade injetada (`sequencia_pedagogica`) como template de operações?
- [ ] Escrevi micro-habilidades no nível correto (operação + objeto conceitual)?
- [ ] Nenhuma micro-habilidade nomeia autores ou fontes específicas?
- [ ] Há um objeto por capítulo, com `capitulo` idêntico ao briefing?
- [ ] Validei todas as operações e micro-habilidades antes de salvar?
- [ ] JSON válido salvo em `input/[apostila]/instrucoes.json`?

> Lembre: você **não** escreve CSV nem recopia enunciado, autores ou conteúdos. O pipeline serializa o CSV a partir do seu JSON + briefing + matriz.

---

**Data de vigência:** 06/06/2026
