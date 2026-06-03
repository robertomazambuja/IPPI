# Briefing para o Claude Cowork — Agente Decompositor

## O que é este documento

Este documento descreve um projeto de pipeline de geração de apostilas didáticas e solicita a criação de dois arquivos específicos: `orientacoes/decompositor-orientacao.md` e `skills/decompositor-skill.md`. Leia o projeto inteiro antes de escrever qualquer coisa.

---

## O projeto

Um pipeline automatizado que gera apostilas didáticas de Ciências Humanas para o Ensino Médio brasileiro, orientadas pela Matriz de Referência do ENEM. O pipeline é composto por agentes que se comunicam via arquivos — cada agente lê arquivos de entrada, processa e salva arquivos de saída que alimentam o próximo agente.

### Como o pipeline funciona hoje

```
instrucoes.csv
      ↓
Agente 1 (Arquiteto) → core.md
      ↓
Agente 2 (Redator Funcional) → texto.md
      ↓
Agente 4 (Redator de Estilo) → texto.md qualificado
      ↓
Agente 5 (Formatador) → .xml para InDesign
```

O ponto de entrada do pipeline é sempre um `instrucoes.csv`. O `pipeline.py` lê esse arquivo, valida sua estrutura e aciona os agentes em sequência.

### O problema a resolver

O `instrucoes.csv` precisa ter uma estrutura pedagógica precisa: cada capítulo deve ter micro-habilidades definidas, operações cognitivas em progressão crescente de dificuldade, conteúdos nucleares e autores adequados à habilidade ENEM trabalhada. Até agora esse CSV era produzido artesanalmente. O objetivo é automatizar essa produção.

---

## A nova arquitetura

```
Professor → Agente 0 (Chatbot) → briefing
                                      ↓
                              Decompositor → instrucoes.csv
                                                   ↓
                                           pipeline.py (existente)
```

O **Decompositor** é o agente que esta tarefa deve criar. Ele recebe um briefing do professor (via Agente 0) e produz o `instrucoes.csv` que alimenta o pipeline existente.

---

## O CSV que o Decompositor deve produzir

O `pipeline.py` valida rigorosamente o CSV de entrada. As colunas obrigatórias são:

```
disciplina, unidade, pergunta_unidade, capitulo, habilidade_principal,
micro_hab_1, operacao_secao_1,
micro_hab_2, operacao_secao_2,
micro_hab_3, operacao_secao_3,
micro_hab_4, operacao_secao_4,
conteudos_nucleares, autores
```

Colunas opcionais:
```
micro_hab_5, operacao_secao_5,
micro_hab_6, operacao_secao_6,
elementos_desejáveis
```

**Regras críticas do CSV (validadas pelo pipeline.py):**
- Cada linha = 1 capítulo
- Operações válidas: `Definir`, `Classificar`, `Comparar`, `Sequenciar`, `Mapear causalidade`, `Reconhecer perspectiva`, `Aplicar`
- Mínimo 4 seções por capítulo, máximo 6
- Nenhuma célula obrigatória pode estar vazia

**Exemplo de CSV válido** (ver `input/` no projeto para referência completa):
```
disciplina,unidade,pergunta_unidade,capitulo,habilidade_principal,micro_hab_1,operacao_secao_1,micro_hab_2,operacao_secao_2,micro_hab_3,operacao_secao_3,micro_hab_4,operacao_secao_4,conteudos_nucleares,autores,elementos_desejáveis
Sociologia,Unidade 1 — Estrutura social,Como as estruturas sociais moldam os indivíduos?,Capítulo 1: Estratificação social,H9 — Comparar o significado histórico-geográfico das organizações políticas e socioeconômicas,Definir estratificação como sistema de posições desiguais,Definir,Classificar tipos de estratificação segundo critérios de propriedade e renda,Classificar,Comparar três visões sobre como funciona a estratificação,Comparar,Aplicar conceitos para analisar desigualdade no Brasil,Aplicar,Estratificação social; classe social; desigualdade socioeconômica; mobilidade social,Karl Marx; Max Weber; Pierre Bourdieu,Usar dados IBGE; exemplos do mercado de trabalho brasileiro
```

---

## O briefing que o Decompositor recebe

O Decompositor recebe um briefing produzido pelo Agente 0 (chatbot que conversa com o professor). O briefing contém o mínimo necessário:

- **Disciplina** — ex: "Sociologia", "História", "Filosofia", "Geografia"
- **Habilidade ENEM** — código da habilidade (ex: "H12") ou descrição aproximada
- **Unidade** — nome/tema da unidade
- **Pergunta da unidade** — a questão central que governa toda a unidade
- **Capítulos** — lista de capítulos com seus temas (pode ser 1 a N capítulos)
- **Autores preferidos** — opcional, lista de autores que o professor quer incluir
- **Elementos desejáveis** — opcional, contexto específico (ex: "usar exemplos do Rio Grande do Sul", "focar no período republicano")

O briefing pode chegar como texto estruturado, JSON simples ou arquivo `.md`. O Decompositor deve ser capaz de interpretar qualquer formato razoável.

---

## A fonte de conhecimento principal: matriz-enem.json

O arquivo `contexto/matriz-enem.json` é a base de conhecimento que o Decompositor usa para enriquecer o CSV. Para cada habilidade ENEM (H1–H30), ele contém:

```json
{
  "H12": {
    "codigo": "H12",
    "competencia": "C3",
    "enunciado": "Analisar o papel da justiça como instituição na organização das sociedades.",
    "foco_cognitivo": "Justiça como instituição, norma, mediação de conflitos e organização da sociedade.",
    "operacao_predominante": "Mapear causalidade",
    "conteudos_por_area": {
      "Historia": ["..."],
      "Geografia": ["..."],
      "Sociologia": ["..."],
      "Filosofia": ["..."]
    },
    "autores_referencia": ["Aristóteles", "John Locke", "Rousseau", "Montesquieu", "John Rawls", "Michel Foucault"]
  }
}
```

O Decompositor deve:
1. Identificar a habilidade ENEM a partir do briefing
2. Ler a entrada correspondente no `matriz-enem.json`
3. Filtrar conteúdos pela disciplina do professor (usar só a área relevante)
4. Complementar com autores da matriz quando o professor não especificou

---

## A lógica pedagógica que o Decompositor deve aplicar

Esta é a parte mais crítica. O Decompositor não apenas transfere dados — ele constrói um andaime pedagógico. As regras são:

### As 7 operações cognitivas (únicas válidas)

| Operação | O que o aluno faz |
|----------|------------------|
| Definir | Entender um conceito com seus elementos essenciais |
| Classificar | Atribuir itens a categorias segundo critérios explícitos |
| Comparar | Listar diferenças e semelhanças entre elementos |
| Sequenciar | Ordenar eventos no tempo |
| Mapear causalidade | Identificar relações causa-consequência (X → Y) |
| Reconhecer perspectiva | Identificar qual visão de mundo um texto/autor expressa |
| Aplicar | Usar um conceito para analisar um caso novo |

### Progressão obrigatória (do fácil ao difícil)

```
Nível 1 (mais fácil):   Definir, Classificar, Sequenciar
Nível 2:                Comparar, Mapear causalidade
Nível 3 (mais difícil): Reconhecer perspectiva, Aplicar
```

**Regras de progressão:**
- A primeira seção SEMPRE deve ser Nível 1 (Definir, Classificar ou Sequenciar)
- A última seção SEMPRE deve ser a operação que responde à habilidade ENEM (usar `operacao_predominante` da matriz como referência)
- As seções intermediárias constroem progressivamente para a operação final
- Nunca repetir a mesma operação em seções consecutivas

### Regras para micro-habilidades

Cada micro-habilidade:
- Começa com UM ÚNICO verbo de ação
- Descreve o que o aluno será capaz de fazer após aquela seção
- É específica ao conteúdo (não genérica)

**Exemplos válidos:**
- "Definir estratificação como sistema de posições desiguais criadas pela sociedade"
- "Classificar tipos de estratificação segundo critérios de propriedade e renda"
- "Comparar as visões de Marx, Weber e Bourdieu sobre desigualdade"
- "Aplicar o conceito de capital cultural para analisar desigualdade educacional no Brasil"

**Exemplos inválidos:**
- "Compreender estratificação" (verbo genérico)
- "Definir e classificar estratificação" (dois verbos)
- "Estudar Marx" (não é ação do aluno)

### Seleção de conteúdos nucleares

- Filtrar pela disciplina do professor (ex: se disciplina = "Sociologia", usar principalmente `conteudos_por_area.Sociologia`)
- Incluir conteúdos de outras áreas apenas quando diretamente relevantes
- Listar como string separada por ponto-e-vírgula

### Seleção de autores

- Priorizar autores que o professor especificou no briefing
- Complementar com `autores_referencia` da matriz quando o professor não especificou
- Cada autor deve ter função pedagógica real (não incluir por decoração)
- Listar como string separada por ponto-e-vírgula

---

## Arquitetura de arquivos do projeto

```
projeto/
├── pipeline.py                          # Pipeline principal (não modificar)
├── orientacoes/
│   ├── agente1-orientacao.md
│   ├── agente2-orientacao.md
│   ├── decompositor-orientacao.md       # CRIAR ESTE
│   └── ...
├── skills/
│   ├── agente1-skill.md
│   ├── agente2-skill.md
│   ├── decompositor-skill.md            # CRIAR ESTE
│   └── ...
├── contexto/
│   ├── matriz-enem.json                 # Base de conhecimento (já existe)
│   ├── principios-pedagogicos-agente1.md
│   └── disciplinas/
│       ├── sociologia.md
│       ├── historia.md
│       └── ...
└── input/
    └── {apostila-slug}/
        └── instrucoes.csv               # OUTPUT do Decompositor
```

---

## O que precisa ser criado

### Arquivo 1: `orientacoes/decompositor-orientacao.md`

Deve conter:
- Identidade e papel do Decompositor no pipeline
- Posição na cadeia (recebe do Agente 0, entrega para o pipeline.py)
- O que recebe (briefing) e o que produz (instrucoes.csv)
- Hierarquia de fontes (matriz-enem.json prevalece sobre inferência própria)
- Proibições específicas (ex: nunca inventar operações fora das 7 válidas, nunca deixar célula obrigatória vazia)
- Referência à skill para execução passo a passo

O tom e estrutura devem ser **consistentes com os outros arquivos de orientação do projeto** — leia `orientacoes/agente1-orientacao.md` como referência de formato e voz antes de escrever.

### Arquivo 2: `skills/decompositor-skill.md`

Deve conter:
- Leitura obrigatória antes de iniciar (matriz-enem.json, arquivo de disciplina)
- Passo a passo de execução:
  1. Interpretar o briefing do Agente 0
  2. Identificar a habilidade ENEM
  3. Ler a entrada correspondente na matriz-enem.json
  4. Para cada capítulo do briefing: construir progressão de operações, escrever micro-habilidades, selecionar conteúdos e autores
  5. Montar e salvar o CSV
- Checklist de validação antes de salvar (replicar as validações do parse_csv do pipeline.py)
- Armadilhas comuns e como evitá-las
- Template explícito de como montar cada linha do CSV

O tom e estrutura devem ser **consistentes com `skills/agente1-skill.md`** — leia esse arquivo como referência antes de escrever.

---

## Restrições importantes

- **Não modificar o pipeline.py** — o CSV gerado deve ser compatível com o pipeline existente
- **Não modificar arquivos de outros agentes** — apenas criar os dois arquivos do Decompositor
- **Seguir o padrão de ferramentas** — o Decompositor usa `read_file` e `write_file` como todos os outros agentes do projeto
- **Ser determinístico** — dada a mesma habilidade e disciplina, o Decompositor deve sempre produzir uma progressão pedagógica coerente, mesmo que o professor não especifique autores ou elementos desejáveis

---

## Contexto pedagógico adicional

O projeto parte de uma premissa central: **a decomposição pedagógica de uma habilidade não é responsabilidade do professor**. O professor sabe o que quer ensinar (tema, habilidade, disciplina). A máquina decide como ensinar (progressão de operações, andaime pedagógico). Isso é o diferencial do projeto — material didático com estrutura de aprendizado de máquinas, não dependente do conhecimento técnico-pedagógico do professor.

O Decompositor é o agente que materializa essa premissa. Ele deve operar de forma totalmente autônoma na parte pedagógica, consultando a matriz ENEM e aplicando as regras de progressão sem precisar perguntar nada ao professor.

---

*Este documento foi gerado em 03/06/2026 para orientar a criação do Agente Decompositor no pipeline de geração de apostilas didáticas.*
