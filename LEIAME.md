# LEIAME — PIPELINE DE APOSTILAS DIDÁTICAS

## Estado atual do projeto

Pipeline funcional de geração de apostilas didáticas de ciências humanas para o Ensino Médio brasileiro, orientadas por habilidades do ENEM. O texto produzido não simula voz humana — é uma interface funcional clara e rastreável, escrita por máquinas para ser lida por humanos.

O foco atual é validar a qualidade didática do output e testar o pipeline completo com capítulos reais.

---

## O que é este projeto

O professor define os parâmetros de cada capítulo em um CSV. O pipeline lê esse CSV e aciona os agentes em sequência. Cada agente produz um output que serve de input para o seguinte. Os agentes são construídos em Python e usam a API da Anthropic (modelo claude-sonnet/opus). Os agentes operam em modo agêntico: leem os arquivos de instrução por conta própria a partir dos caminhos que o pipeline informa.

---

## Princípio pedagógico central

O texto final não conta uma história — ele executa um **algoritmo de ensino**. Cada habilidade do ENEM é decomposta em operações elementares. O aluno aprende a habilidade vendo o algoritmo sendo aplicado repetidamente sobre o conteúdo.

As sete operações elementares são:

- **Definir** — apresentar um conceito com seus elementos essenciais
- **Classificar** — atribuir itens a categorias segundo critérios explícitos
- **Comparar** — listar diferenças e semelhanças entre elementos
- **Sequenciar** — ordenar eventos no tempo
- **Mapear causalidade** — identificar relações de causa-consequência
- **Reconhecer perspectiva** — identificar visão de mundo ou posição de um autor/grupo
- **Aplicar** — usar um conceito para analisar um caso novo

**Não há** situação-problema narrativa, tensão, mobilização, pergunta retórica ou qualquer recurso de simulação humana.

---

## Arquitetura de pastas

```
pipeline.py                  — orquestrador principal
.env                         — chave de API (não versionar)

skills/
  agente1-skill.md
  agente2-skill.md
  agente3-skill.md
  agente4-skill.md
  agente5-skill.md
  decompositor-skill.md

orientacoes/
  agente1-orientacao.md
  agente2-orientacao.md

contexto/
  principios-pedagogicos-agente1.md
  disciplinas/
    historia.md
    sociologia.md
    filosofia.md
    geografia.md

input/
  [nome-da-apostila]/
    instrucoes.csv

output/
  [nome-da-apostila]/
    core/[unidade-slug]/[idx]-[capitulo].md
    texto/[unidade-slug]/[idx]-[capitulo].md
    validacao/[unidade-slug]/[idx]-[capitulo].md
    xml/[unidade-slug]/[idx]-[capitulo].xml
    estilos-indesign.md
```

---

## O CSV — input do professor

**Colunas obrigatórias:**
`disciplina`, `unidade`, `pergunta_unidade`, `capitulo`, `habilidade`,
`micro_hab_1`, `operacao_secao_1`, `micro_hab_2`, `operacao_secao_2`,
`micro_hab_3`, `operacao_secao_3`, `micro_hab_4`, `operacao_secao_4`,
`autores`

**Colunas opcionais:**
`micro_hab_5`, `operacao_secao_5`, `micro_hab_6`, `operacao_secao_6`, `conteudos_nucleares`

Total: 19 colunas (header fixo). Os slots opcionais devem estar presentes no header mesmo quando vazios.

Cada linha é um capítulo. Capítulos da mesma unidade compartilham `unidade` e `pergunta_unidade`.

**Operações válidas** para `operacao_secao_*`: `Definir`, `Classificar`, `Comparar`, `Sequenciar`, `Mapear causalidade`, `Reconhecer perspectiva`, `Aplicar`.

---

## Como rodar o pipeline

```bash
# Roda todos os agentes em todos os capítulos
python pipeline.py input/teste-sociologia/instrucoes.csv

# Roda apenas agentes específicos
python pipeline.py input/teste-sociologia/instrucoes.csv --agentes 1,2,3,4

# Força regeneração mesmo que o output já exista
python pipeline.py input/teste-sociologia/instrucoes.csv --force

# Roda apenas o capítulo N (por ordem no CSV, começando em 1)
python pipeline.py input/teste-sociologia/instrucoes.csv --cap 1
```

Chave de API: o pipeline lê automaticamente o arquivo `.env` na raiz do projeto.

---

## Os agentes

### Agente 1 — Arquiteto Curricular

Recebe: linha do CSV + contexto da unidade + lista de todas as unidades + cores de capítulos anteriores.

Consulta: `contexto/principios-pedagogicos-agente1.md` + `contexto/disciplinas/[disciplina].md`

Produz: `core.md` — estrutura do capítulo com operações elementares, campos específicos por tipo de operação, síntese final e encadeamento. O core é um conjunto de dados estruturados, nunca narrativa.

O campo `VERIFICACAO: Sim/Não` existe no core mas é ignorado pelos agentes subsequentes — a verificação foi removida do pipeline de texto.

---

### Agente 2 — Redator Funcional

Recebe: `core.md` do Agente 1.

Consulta: `contexto/disciplinas/[disciplina].md`

Produz: `texto.md` — prosa didática integrada com marcação estrutural em **HTML comments invisíveis**. Não usa rótulos visíveis. Não gera blocos de verificação.

Formato obrigatório:
- Abre com `<!-- [CONTEXTO_OPERACAO] -->` (quatro campos)
- Cada seção tem cabeçalho idêntico ao core e marcação em HTML comments
- Definição e exemplo integrados em parágrafo único com transição denotativa
- Síntese final responde exatamente à pergunta do capítulo

Responsabilidade do Agente 2: **didática e conteúdo**. Formatação exata da marcação é responsabilidade do Agente 3.

---

### Agente 3 — Normalizador de Marcação

Recebe: `texto.md` do Agente 2.

Produz: `texto.md` normalizado — aplica quatro normalizações de marcação e salva de volta no mesmo caminho. **Não altera prosa, não avalia conteúdo, não reordena seções.**

As quatro normalizações:
1. **CONTEXTO_OPERACAO** — garante os quatro campos em markdown bold, um por linha
2. **FONTE** — garante citação bibliográfica dentro do bloco, tag de abertura sem conteúdo embutido
3. **AUTOR** — garante ancoragem ao bloco pai (aninhado ou com `ref=tipo`)
4. **Tipos desconhecidos** — sinaliza com `AVISO_AGENTE5` sem descartar o conteúdo

O Agente 3 é o contrato de interface entre a zona criativa (Agentes 2 e 4) e a zona estrutural (Agente 5). Ele existe porque modelos de linguagem não são consistentes em formatação — e isso é esperado.

---

### Agente 4 — Polidor de Prosa

Recebe: `texto.md` normalizado pelo Agente 3.

Produz: `texto.md` com prosa aprimorada — melhora transições entre blocos, naturalidade das frases e encadeamento entre parágrafos. **Não toca nos HTML comments. Não cria conteúdo novo.**

Responsabilidade do Agente 4: **fluência da prosa**. Estrutura e conteúdo chegam intocados ao Agente 5.

---

### Agente 5 — Diagramador

Recebe: `texto.md` (processado pelo Agente 4) + `core.md`.

Produz:
- `[capitulo].xml` — capítulo estruturado para InDesign, com tags como `<secao tipo="Definir">`, `<bloco tipo="AUTOR">`, `<indicacao-imagem>`
- `estilos-indesign.md` — gerado uma vez por apostila; lista os estilos de parágrafo necessários

---

## Fluxo resumido

```
Agente 2  →  conteúdo + HTML comments + prosa aproximada
Agente 3  →  normaliza marcação, não toca na prosa
Agente 4  →  aprimora prosa, não toca na marcação
Agente 5  →  lê marcação limpa, gera XML determinístico
```

---

## Bugs conhecidos e mitigações

**Bug: desalinhamento de colunas no CSV gerado pelo Agente 0**
O Decompositor (Agente 0) escreve consistentemente 3 campos vazios de trailing após a última seção preenchida. O número correto varia:
- 4 seções preenchidas → precisa de 4 campos vazios
- 5 seções preenchidas → precisa de 2 campos vazios

**Mitigação implementada (07/06/2026):** função `fix_csv_alignment()` em `pipeline.py` executa automaticamente após o Agente 0 salvar o CSV. Detecta linhas com contagem de campos errada e corrige antes da validação. O pipeline loga `⚠ CSV corrigido automaticamente` quando a correção é aplicada.

---

## Histórico de modificações

**2026-06-08 — Reformulação do Agente 2 e redefinição do Agente 4**

Problema identificado: a skill do Agente 2 pedia formatação exata de AUTOR, FONTE e CONTEXTO_OPERACAO — responsabilidade que pertence ao Agente 3. Além disso, gerava blocos `[VERIFICAÇÃO]` visíveis e usava rótulos explícitos, conflitando com a arquitetura de HTML comments.

Mudanças realizadas:
- `agente2-skill.md` reescrito: HTML comments diretos, exemplos antes/depois para todas as 7 operações, banco de transições denotativas, sem VERIFICACAO, sem exigências de formatação exata
- `agente4-skill.md` reescrito: papel redefinido de "conversor de rótulos" para "polidor de prosa"
- `agente4-skill-v2.md` excluído — um único arquivo por agente
- Campo `VERIFICACAO: Sim/Não` do core mantido mas ignorado pelo Agente 2

**2026-06-08 — Princípio pedagógico da LISTA_COMPLEMENTAR definido**
Decisão: trabalhar uma habilidade é aplicá-la a diferentes conteúdos. O Agente 1 deve usar itens da LISTA_COMPLEMENTAR como CONTEUDO_NUCLEAR de seções, ao lado dos conteúdos obrigatórios, sempre que a operação principal puder ser demonstrada sobre eles com a mesma precisão.

**2026-06-08 — Correção de campo: HABILIDADE_BNCC → HABILIDADE_ENEM**
Corrigido em `skills/agente1-skill.md` e `contexto/principios-pedagogicos-agente1.md`.

**2026-05-30 — Reformulação para pipeline funcional**
Abandono da simulação de voz humana. Princípio pedagógico: artificialidade funcional. Substituição dos tipos de seção por sete operações elementares. Skills e orientações do Agente 1 e Agente 2 completamente reescritas.

---

## Decisões de arquitetura

**Separação de responsabilidades entre Agentes 2, 3 e 4**
O Agente 2 é responsável por conteúdo e didática — não por formatação exata. Pedir ao redator que acerte `ref=tipo` no AUTOR ou o formato exato de FONTE é pedir ao agente errado. O Agente 3 existe precisamente porque modelos de linguagem são inconsistentes em formatação, e isso é esperado. O Agente 4 existe porque fluência de prosa é uma operação separada de estrutura de conteúdo.

**VERIFICACAO removida do texto**
A verificação após cada seção foi removida do output do Agente 2. O campo `VERIFICACAO: Sim/Não` permanece no core (gerado pelo Agente 1) mas é ignorado pelos agentes de texto. A decisão pode ser revisitada se houver necessidade pedagógica futura.

**Processamento capítulo a capítulo**
Simplicidade e inspeção incremental. O custo de coerência entre capítulos é mitigado pelo Agente 1, que lê cores anteriores, e pelo encadeamento explícito no core.

**Prompt caching**
Reduz custo de input nas iterações internas. Implementado via `cache_control` no system prompt.

**Distinção entre orientação e skill**
`orientacoes/`: quem é o agente, sua função no processo, como se relaciona com os outros.
`skills/`: como o agente executa — passos, critérios, formatos.
Em caso de conflito, os princípios pedagógicos prevalecem.

---

## Estado dos componentes

**Implementado e integrado:**
- Agente 1 (Arquiteto Curricular) — `agente1-skill.md`, `agente1-orientacao.md`
- Agente 2 (Redator Funcional) — `agente2-skill.md`, `agente2-orientacao.md`
- Agente 3 (Normalizador de Marcação) — `agente3-skill.md`
- Agente 4 (Polidor de Prosa) — `agente4-skill.md`
- Agente 5 (Diagramador) — `agente5-skill.md`
- `pipeline.py` com flags `--agentes`, `--force`, `--cap`
- Contexto disciplinar completo: `historia.md`, `sociologia.md`, `filosofia.md`, `geografia.md`

**Em avaliação:**
- Qualidade didática do output do Agente 2 com exemplos reais
- Precisão do Agente 3 na detecção de variações de marcação não previstas

**Ainda não existe:**
- Correção automática a partir do output do Agente 3 (hoje é manual)
- Interface web para o professor preencher o CSV
