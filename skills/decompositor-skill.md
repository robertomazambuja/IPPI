# SKILL — DECOMPOSITOR (Agente 0)

## Leitura obrigatória antes de iniciar

1. `contexto/matriz-bncc.json` — base de conhecimento EM13CHS101–EM13CHS606
2. `orientacoes/decompositor-orientacao.md` — sua identidade, escopo e proibições

Em caso de conflito entre este documento e a orientação, a orientação prevalece.

---

## O que você produz

Um arquivo `instrucoes.csv` salvo em:

```
input/[nome-da-apostila]/instrucoes.csv
```

Uma linha por capítulo. O CSV é validado pelo `pipeline.py` antes de acionar o Agente 1.

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

A entrada da habilidade de `matriz-bncc.json` já está injetada no user message pelo pipeline — **não é necessário ler o arquivo**. Use o JSON fornecido diretamente. Extraia:

```
enunciado          → texto completo da habilidade
foco_cognitivo     → que tipo de pensamento ela exercita
operacao_predominante → operação que encerrará cada sequência
sequencia_pedagogica  → lista de operações em ordem (o seu template)
```

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

## PASSO 4 — MONTAR CADA LINHA DO CSV

Para cada capítulo, monte a linha completa:

| Coluna | Valor |
|---|---|
| `disciplina` | do briefing |
| `unidade` | do briefing |
| `pergunta_unidade` | do briefing |
| `capitulo` | do briefing |
| `habilidade` | código + enunciado completo (ex: `EM13CHS402 — Analisar e comparar indicadores de emprego, trabalho e renda...`) |
| `micro_hab_1` | micro-habilidade da operação 1 |
| `operacao_secao_1` | operação 1 (ex: `Definir`) |
| `micro_hab_2` | micro-habilidade da operação 2 |
| `operacao_secao_2` | operação 2 |
| ... | até micro_hab_6 / operacao_secao_6 |
| `autores` | `autores_por_capitulo[nome_do_capitulo]`, separada por `; ` (se presente) |
| `conteudos_nucleares` | `conteudos_por_capitulo[nome_do_capitulo]`, separada por `; ` (se presente) |

**Atenção:** `autores` e `conteudos_nucleares` variam por capítulo — cada linha do CSV recebe os dados específicos do seu capítulo, exatamente como o professor definiu. O Agente 1 decide como usar cada item dentro das seções.

**CRÍTICO — alinhamento de colunas:** O CSV sempre tem as 6 colunas opcionais (`micro_hab_5`, `operacao_secao_5`, `micro_hab_6`, `operacao_secao_6`), mesmo quando a sequência tem só 4 seções. Quando não usadas, deixe-as vazias com vírgulas explícitas. Exemplo correto para 4 seções:

```
...,micro_hab_4_valor,Comparar,,,,Karl Marx; Max Weber,capital cultural
                                ↑↑↑↑
                     4 vírgulas para os 4 slots vazios
```

Se escrever apenas 3 vírgulas, `autores` cai em `operacao_secao_6` e o pipeline falha.

---

## PASSO 5 — VALIDAR ANTES DE SALVAR

Para cada linha do CSV, confirme:

**Operações:**
- [ ] Entre 4 e 6 micro-habilidades?
- [ ] Primeira operação é Nível 1 (Definir, Classificar ou Sequenciar)?
- [ ] Última operação é a `operacao_predominante` da habilidade?
- [ ] Nenhuma operação repetida em posições consecutivas?
- [ ] Todas as operações estão na lista das 7 válidas?

**Micro-habilidades:**
- [ ] Cada micro-habilidade começa com o verbo exato da operação?
- [ ] Nenhuma micro-habilidade nomeia autores, fontes de dados ou exemplos específicos?
- [ ] Cada micro-habilidade é específica ao tema do capítulo (não genérica)?

**CSV:**
- [ ] Nenhuma célula obrigatória está vazia?
- [ ] Nenhuma célula contém quebra de linha?
- [ ] `autores` e `conteudos_nucleares` de cada capítulo vieram do dict correto do briefing?

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

- [ ] Li `contexto/matriz-bncc.json` para a habilidade do briefing?
- [ ] Usei a `sequencia_pedagogica` como template de operações?
- [ ] Escrevi micro-habilidades no nível correto (operação + objeto conceitual)?
- [ ] Nenhuma micro-habilidade nomeia autores ou fontes específicas?
- [ ] `autores` e `conteudos_nucleares` de cada capítulo foram mapeados corretamente do briefing?
- [ ] Validei todas as operações e micro-habilidades antes de salvar?
- [ ] CSV salvo em `input/[apostila]/instrucoes.csv`?

---

**Data de vigência:** 06/06/2026
