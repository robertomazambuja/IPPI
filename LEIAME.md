# LEIAME — PIPELINE DE APOSTILAS DIDÁTICAS (VERSÃO FUNCIONAL)

## Estado atual do projeto

Pipeline com paradigma **funcional** (texto rotulado, sem narrativa, sem simulação de voz humana). Foco atual: fazer o código rodar, ajustar as skills, reduzir custo de tokens via prompt caching e validar a clareza didática do formato funcional. O desafio é fazer uma apostila criada por IA que não busque ser como uma apostila feita por humano mas que seja extremamente funcional justamente por ter sido feita por máquinas.

---

## O que é este projeto

Pipeline de geração de apostilas didáticas de ciências humanas para o Ensino Médio brasileiro, orientadas por habilidades da BNCC ou da Matriz de Referência ENEM. O propósito é que o aluno pratique **operações cognitivas elementares** (definir, classificar, comparar, sequenciar, mapear causalidade, reconhecer perspectiva, aplicar) aplicadas a conteúdos nucleares. O texto não tenta soar humano – é uma **interface funcional clara e rastreável**.

O professor define os parâmetros em um briefing JSON. O Agente 0 (Decompositor) lê esse briefing e gera o `instrucoes.csv`. O pipeline lê o CSV e aciona os agentes em sequência. Cada agente produz um output que serve de input para o seguinte. Os agentes são construídos em Python e usam a API da Anthropic (modelo claude-sonnet/opus). Os agentes operam em modo agêntico: leem os arquivos de instrução por conta própria a partir dos caminhos que o pipeline informa – não há injeção de prompt via código.

---

## Princípio pedagógico central

O texto final não conta uma história – ele executa um **algoritmo de ensino**. Cada habilidade da BNCC ou matriz do ENEM é decomposta em operações elementares. O aluno aprende a habilidade vendo o algoritmo sendo aplicado repetidamente sobre o conteúdo.

As sete operações elementares são:
- **Definir** – apresentar um conceito com seus elementos essenciais
- **Classificar** – atribuir itens a categorias segundo critérios explícitos
- **Comparar** – listar diferenças e semelhanças entre elementos
- **Sequenciar** – ordenar eventos no tempo
- **Mapear causalidade** – identificar relações de causa‑consequência
- **Reconhecer perspectiva** – identificar visão de mundo ou posição de um autor/grupo
- **Aplicar** – usar um conceito para analisar um caso novo

**Não há** "situação-problema narrativa", "tensão", "mobilização", "pergunta retórica" ou qualquer recurso de simulação humana.

---

## Arquitetura de pastas

```
pipeline.py                          — orquestrador principal
.env                                 — chave de API (ANTHROPIC_API_KEY=...) — não versionar

skills/
  decompositor-skill.md              — como o Agente 0 (Decompositor) executa
  agente1-skill.md                   — como o Agente 1 (Arquiteto) executa
  agente2-skill.md                   — como o Agente 2 (Redator Funcional) executa
  agente3-skill.md                   — como o Agente 3 (Validador Técnico) executa
  agente4-skill.md                   — como o Agente 4 (Redator de Estilo) executa
  agente5-skill.md                   — como o Agente 5 (Diagramador) executa

orientacoes/
  decompositor-orientacao.md         — identidade e papel do Agente 0
  agente1-orientacao.md              — identidade e papel do Agente 1
  agente2-orientacao.md              — identidade e papel do Agente 2
  agente3-orientacao.md              — identidade e papel do Agente 3
  agente4-orientacao.md              — identidade e papel do Agente 4
  agente5-orientacao.md              — identidade e papel do Agente 5

contexto/
  principios-pedagogicos-agente1.md  — governa as decisões do Agente 1 (funcional)
  matriz-enem.json                   — base de conhecimento H1–H30 (uso do Decompositor)
  matriz-conteudosenem.json          — conteúdos prioritários e por disciplina H1–H30 (uso do Agente 1)
  disciplinas/
    historia-contexto-funcional.md   — conceitos, autores, regras para História
    sociologia-contexto-funcional.md — conceitos, autores, regras para Sociologia

input/
  [nome-da-apostila]/
    instrucoes.csv                   — gerado pelo Agente 0 ou preenchido pelo professor
    briefing.json                    — input para o Agente 0

output/
  [nome-da-apostila]/
    core/[unidade-slug]/[idx]-[idx]-[nome].md
    texto/[unidade-slug]/[idx]-[idx]-[nome].md
    validacao/[unidade-slug]/[idx]-[idx]-[nome].md
    formatado/[unidade-slug]/[idx]-[idx]-[nome].xml
```

---

## O JSON briefing — input para o Agente 0

O professor ou um chatbot de coleta produz um briefing JSON contendo:

```json
{
  "disciplina": "Sociologia",
  "habilidade_enem": "H9",
  "unidade": "Unidade 1 — Estrutura social e desigualdade",
  "pergunta_unidade": "Como as estruturas sociais constrangem e moldam os indivíduos?",
  "capitulos": [
    "Capítulo 1: Estratificação social",
    "Capítulo 2: Desigualdade, raça e gênero no Brasil"
  ],
  "autores_preferidos": ["Karl Marx", "Max Weber", "Pierre Bourdieu"],
  "elementos_desejáveis": "Usar dados IBGE; exemplos do mercado de trabalho brasileiro"
}
```

O Agente 0 lê esse briefing, consulta a `contexto/matriz-enem.json`, e gera o `instrucoes.csv` que alimenta os Agentes 1–5.

📖 **Documentação:** Ver `decompositor-briefing.md` para especificação completa.

---

## O CSV — output do Agente 0 / input dos Agentes 1–5

**Colunas obrigatórias:**
- `disciplina`, `unidade`, `pergunta_unidade`, `capitulo`
- `habilidade_principal` (código BNCC + texto completo)
- `micro_hab_1`, `operacao_secao_1`, `micro_hab_2`, `operacao_secao_2`, `micro_hab_3`, `operacao_secao_3`, `micro_hab_4`, `operacao_secao_4` (mínimo 4 seções)
- `conteudos_nucleares`, `autores`

**Colunas opcionais:**
- `micro_hab_5`, `operacao_secao_5`, `micro_hab_6`, `operacao_secao_6` (até 6 seções)
- `elementos_desejáveis` (direcionamentos didáticos específicos)

**Validação:**
- Operações devem ser um de: Definir, Classificar, Comparar, Sequenciar, Mapear causalidade, Reconhecer perspectiva, Aplicar
- O CSV é validado automaticamente pelo pipeline antes de acionar qualquer agente

Cada linha é um capítulo. Capítulos da mesma unidade compartilham `unidade`, `pergunta_unidade` e, se for o caso, habilidades. 

📖 **Documentação completa:** Ver arquivo `NOVO_FORMATO_CSV.md`

---

## Como rodar o pipeline

```bash
# Modo completo: Agente 0 gera o CSV, depois roda Agentes 1–5
python pipeline.py --briefing input/apostila-sociologia/briefing.json --apostila apostila-sociologia

# Modo manual: professor já tem o CSV, roda apenas Agentes 1–5
python pipeline.py input/apostila-sociologia/instrucoes.csv

# Roda apenas agentes específicos (ex: 1 e 2)
python pipeline.py input/apostila-sociologia/instrucoes.csv --agentes 1,2

# Força regeneração mesmo que o arquivo de output já exista
python pipeline.py input/apostila-sociologia/instrucoes.csv --force

# Roda apenas o capítulo N (por ordem no CSV, começando em 1)
python pipeline.py input/apostila-sociologia/instrucoes.csv --cap 1

# Roda só o Agente 0 (gera CSV sem continuar)
python pipeline.py --briefing input/apostila-sociologia/briefing.json --apostila apostila-sociologia --agentes 0
```

**Ordem padrão dos agentes (modo manual):** 1 → 2 → 3 → 4 → 5

O Agente 3 valida o texto produzido pelo Agente 2. O Agente 4 reescreve o texto validado em prosa fluida antes de seguir para diagramação.

**Chave de API:** o pipeline lê automaticamente o arquivo `.env` na raiz do projeto:
```
ANTHROPIC_API_KEY=sk-ant-api03-...
```

---

## Os agentes

### Agente 0 — Decompositor (Construtor de Instruções)

**Recebe:** briefing JSON do professor (disciplina, habilidade ENEM, unidade, pergunta, capítulos, autores preferidos, elementos desejáveis).

**Consulta:** `contexto/matriz-enem.json` + `contexto/disciplinas/[disciplina].md`

**Produz:** `instrucoes.csv` – arquivo estruturado que prescreve a progressão pedagógica de cada capítulo (operações cognitivas, micro-habilidades, conteúdos nucleares sugeridos pelo professor, autores sugeridos pelo professor).

**Responsabilidade:** garantir que o CSV gerado seja válido e respeite as regras obrigatórias (progressão, operações, micro-habilidades, conteúdos). É o agente que materializa a decomposição pedagógica autônoma — o professor não prescreve *como* ensinar, apenas *o que* ensinar.

**Estado:** integrado ao pipeline.py via flag `--briefing`.

---

### Agente 1 — Arquiteto Curricular

**Recebe:** linha do CSV + contexto da unidade + lista de todas as unidades + cores de capítulos anteriores (se houver).

**Consulta:** `contexto/principios-pedagogicos-agente1.md` + `contexto/disciplinas/[disciplina]-contexto-funcional.md` + `contexto/matriz-conteudosenem.json` (localiza a habilidade pelo código, filtra conteúdos pela disciplina do capítulo, prioriza itens em `conteudos_prioritarios`)

**Produz:** `core.md` – arquitetura do capítulo baseada em operações elementares. O core contém:
- Cabeçalho: habilidade, operação principal, pergunta do capítulo, contribuição à unidade
- Sequência de 3 a 5 seções, cada uma com `TIPO_OPERACAO` e campos específicos
- Síntese final e encadeamento
- Checklist de verificação interna

**Regra:** o core nunca contém campos como `TENSAO`, `MOBILIZACAO`, `PERGUNTA_RETORICA`.

---

### Agente 2 — Redator Funcional

**Recebe:** `core.md` do Agente 1.

**Consulta:** apenas o documento de contexto disciplinar funcional.

**Produz:** `texto.md` – capítulo em texto funcional rotulado, sem narrativa, sem metáforas, sem perguntas retóricas.

**Formato obrigatório:**
- Começa com **CONTEXTO DE OPERAÇÃO** (habilidade, operação principal, pergunta)
- Cada seção tem cabeçalho idêntico ao core e blocos rotulados (`[DEFINIÇÃO]`, `[COMPARAÇÃO]`, `[EXEMPLO]`, `[VERIFICAÇÃO]`, etc.)
- `[VERIFICAÇÃO]`: perguntas fechadas (múltipla escolha ou V/F) com resposta correta indicada
- Síntese final responde exatamente à pergunta do capítulo

**Proibições:** nenhum recurso narrativo, nenhum "nós", nenhum andaime, nenhuma exclamação, nenhuma metáfora, nenhum advérbio de opinião.

---

### Agente 3 — Validador Técnico

**Recebe:** `core.md` (Agente 1) e `texto.md` (Agente 2).

**Produz:** `validacao.md` – relatório com status Aprovado / Reprovado e lista de erros (com localização) e correções obrigatórias.

**O que verifica:**
- Estrutura geral (CONTEXTO DE OPERAÇÃO, ## SÍNTESE)
- Cada seção: cabeçalho, rótulos corretos, presença de EXEMPLO_ANCOLA
- Autores: nome completo, datas, filiação (boxes biográficos ≤20 palavras)
- Verificações fechadas com respostas
- Proibições (metáforas, exclamações, "nós", andaime, etc.)

**Não faz:** reescrever trechos, avaliar escolhas do Agente 1, sugerir melhorias estilísticas.

---

### Agente 4 — Redator de Estilo

**Recebe:** `texto.md` validado pelo Agente 3 (com rótulos explícitos visíveis: `[PERSPECTIVA 1]`, `[VERIFICAÇÃO]`, etc.).

**Produz:** versão reescrita do `texto.md`, sobrescrevendo o original, com:
- Prosa fluida e legível, sem rótulos visíveis ao leitor
- Estrutura funcional preservada em HTML comments (`<!-- [PERSPECTIVA] -->`, `<!-- [EXEMPLO] -->`, etc.) para uso pelo Agente 5

**Responsabilidade:** tornar invisível a engenharia estrutural sem alterar conteúdo. Não humaniza nem dramatiza — reduz o tom excessivamente maquinal do texto do Agente 2, dando fluidez à leitura, sem abandonar o paradigma funcional.

**O que preserva:** argumento de cada seção, ordem das seções, exemplos, autores, perguntas de verificação, síntese final.

**O que nunca faz:** alterar ordem ou conteúdo das seções, adicionar metáforas, exclamações ou padrões artificiais ("não é X: é Y"), remover os HTML comments.

---

### Agente 5 — Diagramador

**Recebe:** `texto.md` reescrito pelo Agente 4 + `core.md` (para identificar tipos de operação).

**Produz:**
- `[capitulo].xml` – capítulo estruturado para InDesign, com tags como `<secao tipo="Definir">`, `<bloco tipo="VERIFICACAO">`, `<indicacao-imagem>`
- `estilos-indesign.md` – gerado uma vez por apostila; lista os estilos de parágrafo necessários

---

## Histórico de modificações

### 2026-06-06 – Adição de conteudos_nucleares do professor (passo 2/6)

**Mudanças:**
- `skills/decompositor-skill.md`: `conteudos_nucleares` adicionado na tabela de extração do briefing (PASSO 1), na tabela de montagem do CSV (PASSO 4) e no checklist final

### 2026-06-06 – Adição de conteudos_nucleares do professor (passo 1/6)

**Mudanças:**
- `orientacoes/decompositor-orientacao.md`: `conteudos_nucleares` adicionado como campo do briefing e como coluna pass-through no CSV — copiado integralmente para todos os capítulos sem processamento pelo Decompositor

### 2026-06-06 – Atualização do pipeline.py

**Mudanças:**
- `conteudos_nucleares` removido de `COLUNAS_OBRIGATORIAS` na validação do CSV
- User message do Agente 0 atualizado: instrui a usar `sequencia_pedagogica` do JSON e escrever micro-habilidades no nível operação + objeto conceitual
- User message do Agente 1 atualizado: substituído "CONTEÚDOS NUCLEARES A COBRIR" por "MICRO-HABILIDADES PRESCRITAS"; autores descritos como lista a distribuir por afinidade com objeto conceitual

### 2026-06-06 – Atualização do agente1-skill.md

**Mudanças:**
- "O que você recebe" atualizado: Agent 1 agora recebe `micro_hab_1-6` e `operacao_secao_1-6` do CSV; `conteudos_nucleares` removido
- PASSO -1 expandido: inclui agora distribuição de autores (lista completa do CSV → seções por afinidade com objeto conceitual)
- PASSO 1 reescrito: Agent 1 materializa as micro-habilidades prescritas, não inventa a progressão de operações
- Checklist atualizado: referências a `conteudos_nucleares` do CSV removidas; itens de validação da sequência prescrita adicionados

### 2026-06-06 – Atualização do NOVO_FORMATO_CSV.md

**Mudanças:**
- Coluna `conteudos_nucleares` removida do CSV — Agente 1 obtém conteúdos de `contexto/matriz-conteudosenem.json`
- Descrição das micro-habilidades atualizada: formato agora é operação + objeto conceitual, sem autores ou fontes específicas
- Campo `habilidade_principal` atualizado para código ENEM (H1–H30) + enunciado, não mais código BNCC
- Campo `autores` documentado como lista completa do briefing, idêntica em todos os capítulos
- Exemplo atualizado com os dois capítulos do briefing H14

### 2026-06-06 – Criação dos arquivos do Agente 0 (versão revisada)

**Mudanças:**
- Criação de `orientacoes/decompositor-orientacao.md`: define identidade, escopo, regra de abstração das micro-habilidades e proibições do Decompositor
- Criação de `skills/decompositor-skill.md`: guia de execução em 5 passos com exemplos, tabela de validação e armadilhas comuns
- Escopo definido: Decompositor escreve micro-habilidades no nível operação + objeto conceitual — nunca nomeia autores, fontes ou exemplos específicos (território do Agente 1)
- `autores_preferidos` e `elementos_desejáveis` do briefing passam integralmente para todos os capítulos do CSV, sem distribuição pelo Decompositor
- Campo `conteudos_nucleares` removido do CSV — responsabilidade do Agente 1 via `matriz-conteudosenem.json`

### 2026-06-06 – Adição de sequencia_pedagogica ao matriz-enem.json

**Mudanças:**
- Campo `sequencia_pedagogica` adicionado às 30 habilidades (H1–H30) em `contexto/matriz-enem.json`
- Cada entrada contém uma lista de 4 a 5 operações cognitivas ordenadas (`ordem` + `operacao`), sem conteúdo específico
- A sequência segue as regras do paradigma: primeira operação sempre Nível 1 (Definir, Classificar ou Sequenciar); última operação sempre igual à `operacao_predominante` da habilidade; sem repetição de operação em posições consecutivas
- Objetivo: servir de template estrutural para o Agente 0 (Decompositor) ao decompor uma habilidade em micro-habilidades para o CSV



### 2026-06-03 – Integração do Agente 0 ao pipeline.py

**Mudanças:**
- Adicionado `run_agente0()` ao `pipeline.py`: transforma briefing JSON em `instrucoes.csv`
- Nova flag `--briefing [arquivo.json]` na CLI
- Nova flag `--apostila [nome]` define o diretório da apostila quando usando `--briefing`
- Fluxo padrão (modo manual) ajustado: Agentes 1 → 2 → 3 → 5 (Agente 4 removido do padrão)
- LEIAME.md reorganizado: inconsistências removidas, arquitetura documentada de forma coerente
- Excluídas - modificações do Agente 0

### 2026-06-03 – Criação dos arquivos do Agente 0

**Mudanças:**
- Criação de `decompositor-orientacao.md`: define identidade, papel e posição do Agente 0 no pipeline
- Criação de `decompositor-skill.md`: guia executivo completo com 9 passos
- Criação de `decompositor-briefing.md`: especificação do briefing de entrada
- Excluídas - modificações do Agente 0

### 2026-05-30 (tarde) – Implementação do novo formato CSV com andaime de habilidades

**Mudanças:**
- CSV expandido agora prescreve o andaime didático completo (4-6 seções, operações, micro-habilidades)
- Novas colunas: `habilidade_principal`, `micro_hab_1|2|3|4|5|6`, `operacao_secao_1|2|3|4|5|6`, `elementos_desejáveis`
- Removida coluna: `elementos_obrigatorios` → `elementos_desejáveis` (opcional)
- Validação do CSV expandida: operações validadas contra os 7 tipos elementares
- User message do Agente 1 reformulado: recebe andaime explicitamente

### 2026-05-30 (manhã) – Reformulação para pipeline funcional

**Mudanças fundamentais:**
- Abandono da simulação de voz humana. Princípio pedagógico agora é artificialidade funcional
- Substituição dos tipos de seção por sete operações elementares
- Agente 4 (Revisor de Estilo) retirado do fluxo padrão — texto funcional não tem estilo a revisar
- Agente 3 transformado em Validador Técnico (não reescreve, apenas certifica)
- Skills e orientações do Agente 1 e Agente 2 completamente reescritas

---

## Estado dos componentes

**Implementado e integrado:**
- Agente 1 (Arquiteto Curricular) — `agente1-skill.md`, `agente1-orientacao.md`, `contexto/matriz-conteudosenem.json`
- Agente 2 (Redator Funcional) — `agente2-skill.md`, `agente2-orientacao.md`
- Agente 3 (Validador Técnico) — `agente3-skill.md`, `agente3-orientacao.md`
- Agente 4 (Redator de Estilo) — `agente4-skill.md`, `agente4-orientacao.md`
- Agente 5 (Diagramador) — `agente5-skill.md`, `agente5-orientacao.md`
- `pipeline.py` com flags `--briefing`, `--apostila`, `--agentes`, `--force`, `--cap`

**Disciplinas com contexto funcional completo:**
- História — `historia-contexto-funcional.md`
- Sociologia — `sociologia-contexto-funcional.md`

**Matriz ENEM:**
- `contexto/matriz-enem.json` — Base de conhecimento com H1–H30

**Em avaliação:**
- Qualidade das verificações fechadas (se realmente testam a habilidade)
- Precisão do Agente 3 na detecção de violações

**Ainda não existe:**
- Contexto funcional para Filosofia e Geografia
- Correção automática a partir do output do Agente 3 (hoje é manual)
- Interface web para o professor preencher o briefing JSON
- Script/Template para gerar briefing JSON de teste