# FORMATO CSV — INSTRUCOES DE APOSTILA

## Visão Geral

O CSV é o documento de passagem entre o Agente 0 (Decompositor) e o Agente 1 (Arquiteto Curricular). Ele prescreve a **estrutura cognitiva** de cada capítulo — sequência de operações e micro-habilidades — sem determinar o conteúdo específico. O Agente 1 recebe essa estrutura e a materializa com autores, exemplos e conteúdos obtidos de suas próprias fontes.

**Uma linha = um capítulo.**

---

## Estrutura do CSV

### Colunas obrigatórias

| Coluna | Descrição | Exemplo |
|--------|-----------|---------|
| `disciplina` | Nome da disciplina | `Sociologia` |
| `unidade` | Nome da unidade | `Unidade 1 — Estrutura social e desigualdade` |
| `pergunta_unidade` | Questão central que governa toda a unidade | `Como as estruturas sociais constrangem os indivíduos?` |
| `capitulo` | Nome do capítulo | `Capítulo 1: Estrutura social e estratificação` |
| `habilidade_principal` | Código + enunciado completo da matriz ENEM | `H14 — Comparar diferentes pontos de vista sobre instituições sociais, políticas e econômicas` |
| `micro_hab_1` | Micro-habilidade da seção 1 | `Definir estratificação como sistema de hierarquias e posições desiguais` |
| `operacao_secao_1` | Operação elementar da seção 1 | `Definir` |
| `micro_hab_2` | Micro-habilidade da seção 2 | `Classificar formas de estratificação segundo critérios econômicos, culturais e simbólicos` |
| `operacao_secao_2` | Operação elementar da seção 2 | `Classificar` |
| `micro_hab_3` | Micro-habilidade da seção 3 | `Reconhecer perspectivas teóricas distintas sobre a origem da estratificação` |
| `operacao_secao_3` | Operação elementar da seção 3 | `Reconhecer perspectiva` |
| `micro_hab_4` | Micro-habilidade da seção 4 | `Comparar interpretações sobre estratificação e desigualdade social` |
| `operacao_secao_4` | Operação elementar da seção 4 | `Comparar` |
| `autores` | Lista completa de autores do briefing | `Karl Marx; Max Weber; Pierre Bourdieu; Lélia Gonzalez` |

### Colunas opcionais (presentes quando o professor as informou no briefing)

| Coluna | Descrição |
|--------|-----------|
| `micro_hab_5` | Micro-habilidade da seção 5 (se houver 5 seções) |
| `operacao_secao_5` | Operação elementar da seção 5 |
| `micro_hab_6` | Micro-habilidade da seção 6 (se houver 6 seções) |
| `operacao_secao_6` | Operação elementar da seção 6 |
| `conteudos_nucleares` | Conteúdos mandatórios definidos pelo professor — o Agente 1 é obrigado a cobri-los. Separados por `; `. Idêntico em todos os capítulos da unidade. |
| `elementos_desejáveis` | Direcionamentos pedagógicos específicos do professor |

---

## O que são as micro-habilidades

Cada micro-habilidade descreve **o que o aluno faz cognitivamente** e **sobre qual domínio conceitual** — sem prescrever autores, dados ou exemplos concretos.

Formato: `[verbo da operação] [objeto conceitual do capítulo]`

| ✓ Correto | ✗ Incorreto |
|-----------|-------------|
| `"Comparar perspectivas teóricas sobre estratificação"` | `"Comparar Marx, Weber e Bourdieu"` |
| `"Mapear relações causais entre estrutura e desigualdade"` | `"Usar dados do IBGE para mapear desigualdade"` |
| `"Definir raça como categoria socialmente construída"` | `"Entender o conceito de raça"` |

O Agente 1 lê a micro-habilidade e decide quais autores, conteúdos e exemplos usar para executá-la — buscando em `contexto/matriz-conteudosenem.json` e nos `autores` do CSV.

---

## Enumeração de operações

As colunas `operacao_secao_X` devem conter **exatamente um** destes termos:

`Definir` · `Classificar` · `Comparar` · `Sequenciar` · `Mapear causalidade` · `Reconhecer perspectiva` · `Aplicar`

---

## Regras de progressão

- Mínimo 4 seções, máximo 6
- Primeira operação sempre Nível 1: `Definir`, `Classificar` ou `Sequenciar`
- Última operação sempre igual à `operacao_predominante` da habilidade ENEM
- Nenhuma operação repetida em posições consecutivas

---

## Exemplo completo — H14, dois capítulos

```csv
disciplina,unidade,pergunta_unidade,capitulo,habilidade_principal,micro_hab_1,operacao_secao_1,micro_hab_2,operacao_secao_2,micro_hab_3,operacao_secao_3,micro_hab_4,operacao_secao_4,micro_hab_5,operacao_secao_5,micro_hab_6,operacao_secao_6,autores,elementos_desejáveis
Sociologia,Unidade 1 — Estrutura social e desigualdade,Como as estruturas sociais constrangem os indivíduos?,Capítulo 1: Estrutura social e estratificação social,H14 — Comparar diferentes pontos de vista sobre situação ou fatos de natureza histórico-geográfica acerca das instituições sociais,Definir estratificação como sistema de hierarquias e posições desiguais,Definir,Classificar formas de estratificação segundo critérios econômicos culturais e simbólicos,Classificar,Reconhecer perspectivas teóricas distintas sobre a origem e reprodução da estratificação,Reconhecer perspectiva,Comparar interpretações sobre estratificação e desigualdade social,Comparar,,,,"Karl Marx; Max Weber; Pierre Bourdieu; Lélia Gonzalez; Carlos Hasenbalg; Octavio Ianni; Flávia Rios; bell hooks",usar dados do IBGE
Sociologia,Unidade 1 — Estrutura social e desigualdade,Como as estruturas sociais constrangem os indivíduos?,Capítulo 2: Desigualdade raça e gênero no Brasil,H14 — Comparar diferentes pontos de vista sobre situação ou fatos de natureza histórico-geográfica acerca das instituições sociais,Definir raça e gênero como categorias socialmente construídas de diferenciação,Definir,Classificar formas de desigualdade estrutural segundo raça gênero e classe,Classificar,Reconhecer perspectivas sobre desigualdade racial e de gênero no Brasil,Reconhecer perspectiva,Comparar condições socioeconômicas de diferentes grupos raciais e de gênero,Comparar,,,,"Karl Marx; Max Weber; Pierre Bourdieu; Lélia Gonzalez; Carlos Hasenbalg; Octavio Ianni; Flávia Rios; bell hooks",usar dados do IBGE
```

---

## Como o Agente 1 usa o CSV

O Agente 1 recebe as micro-habilidades como **estrutura cognitiva prescrita** e tem autonomia sobre o conteúdo:

**O que está prescrito (não altera):**
- Sequência de operações
- Objeto conceitual de cada seção

**O que o Agente 1 decide:**
- Quais autores da lista vão em quais seções
- Quais conteúdos de `matriz-conteudosenem.json` cobrir em cada seção (complementares)
- Como distribuir os `conteudos_nucleares` do professor entre as seções (obrigatório cobri-los todos)
- Exemplo-âncora de cada seção
- Peso de cada seção (Principal / Secundário / Passagem)
- Quais autores merecem box biográfico
- Perguntas de verificação

---

## Validação no pipeline

O `pipeline.py` valida:

1. Todas as colunas obrigatórias presentes
2. `operacao_secao_X` contém um dos 7 valores permitidos
3. `micro_hab_1` a `micro_hab_4` preenchidas (mínimo 4 seções)
4. `micro_hab_5` e `micro_hab_6` opcionais (máximo 6 seções)
5. Nenhuma célula obrigatória vazia
6. Nenhuma célula com quebra de linha interna

---

## Notas

- **`autores`** é a lista completa do briefing, idêntica em todos os capítulos da mesma unidade. O Agente 1 distribui por seção.
- **`elementos_desejáveis`** é opcional. Se ausente no briefing, deixar em branco.
- **`conteudos_nucleares`** é opcional. Quando presente, contém os conteúdos mandatórios que o professor definiu no briefing — o Agente 1 é obrigado a cobri-los em pelo menos uma seção. O Agente 1 complementa com conteúdos adicionais de `contexto/matriz-conteudosenem.json`.
