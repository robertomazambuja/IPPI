# LEIAME — PIPELINE DE APOSTILAS DIDÁTICAS

## Estado atual do projeto

Pipeline funcional de geração de apostilas didáticas de ciências humanas para o Ensino Médio brasileiro, orientadas por habilidades do ENEM. O texto produzido não simula voz humana — é uma interface funcional clara e rastreável, escrita por máquinas para ser lida por humanos.

As três fases de desenvolvimento estão concluídas. O pipeline está pronto para uso em produção.

---

## O que é este projeto

O professor define os parâmetros de cada capítulo em um CSV. O pipeline lê esse CSV e aciona os agentes em sequência. Cada agente produz um output que serve de input para o seguinte.

Os agentes LLM (A0, A1, A2, A4) usam a API da Anthropic em modo agêntico. Os agentes A3 e A5 são código Python determinístico — não consomem tokens, não fazem chamadas à API, executam transformações precisas e auditáveis.

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
normalizador.py              — Agente 3 (Python, sem LLM)
formatador.py                — Agente 5 (Python, sem LLM)
verificador.py               — gerador de verificações e "Aplicar agora" (Haiku)
avaliar.py                   — rubrica de qualidade LLM-judge (Haiku)
.env                         — chave de API (não versionar)

skills/
  decompositor-skill.md
  agente1-skill.md
  agente2-skill.md
  agente3-skill.md           — especificação implementada em normalizador.py
  agente4-skill.md
  agente5-skill.md           — especificação implementada em formatador.py

orientacoes/
  decompositor-orientacao.md
  agente1-orientacao.md
  agente2-orientacao.md
  agente3-orientacao.md
  agente4-orientacao.md
  agente5-orientacao.md

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
    formatado/[unidade-slug]/[idx]-[capitulo].xml

logs/
  uso_YYYYMMDD.csv           — tokens e custo por agente/capítulo
  qualidade_YYYYMMDD.csv     — notas da rubrica (avaliar.py)
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
python pipeline.py input/teste-sociologia/instrucoes.csv --agentes 1,2,4

# Força regeneração mesmo que o output já exista
python pipeline.py input/teste-sociologia/instrucoes.csv --force

# Roda apenas o capítulo N (por ordem no CSV, começando em 1)
python pipeline.py input/teste-sociologia/instrucoes.csv --cap 1

# Paraleliza os capítulos (A2-A5 rodam em paralelo, A1 sempre sequencial)
python pipeline.py input/teste-sociologia/instrucoes.csv --workers 4
```

**Avaliar qualidade de um capítulo:**

```bash
python avaliar.py output/apostila-X/texto/unidade-Y/01-01-cap.md

# Avaliar todos os capítulos de uma apostila
python avaliar.py --apostila apostila-teste-historia-em1
```

Chave de API: o pipeline lê automaticamente o arquivo `.env` na raiz do projeto.

---

## Modelos por agente

Cada agente usa um modelo configurável via variável de ambiente:

| Agente | Padrão | Variável de ambiente |
|--------|--------|----------------------|
| A0 — Decompositor | claude-sonnet-4-6 | `IPPI_MODEL_A0` |
| A1 — Arquiteto | claude-opus-4-6 | `IPPI_MODEL_A1` |
| A2 — Redator | claude-opus-4-6 | `IPPI_MODEL_A2` |
| A3 — Normalizador | Python (sem LLM) | — |
| A4 — Polidor | claude-sonnet-4-6 | `IPPI_MODEL_A4` |
| A5 — Formatador | Python (sem LLM) | — |
| Verificador | claude-haiku-4-5-20251001 | — |
| Avaliador | claude-haiku-4-5-20251001 | `IPPI_AVALIADOR_MODEL` |

`IPPI_MODEL` (sem sufixo) serve de fallback global.

---

## Os agentes

### Agente 0 — Decompositor

Recebe: parâmetros da apostila (disciplina, unidades, habilidades).

Produz: `instrucoes.csv` completo com todos os capítulos e operações por seção.

Consulta: `skills/decompositor-skill.md` + `orientacoes/decompositor-orientacao.md`

---

### Agente 1 — Arquiteto Curricular

Recebe: linha do CSV + contexto da unidade + lista de todas as unidades + cores de capítulos anteriores.

Consulta: `contexto/principios-pedagogicos-agente1.md` + `contexto/disciplinas/[disciplina].md`

Produz: `core.md` — estrutura do capítulo com operações elementares, campos específicos por tipo de operação, síntese final e encadeamento. O core é um conjunto de dados estruturados, nunca narrativa.

O campo `VERIFICACAO: Sim/Não` no core indica quais seções receberão perguntas de verificação no XML final (geradas pelo `verificador.py`).

**A1 sempre roda sequencialmente** — lê os cores dos capítulos anteriores da mesma apostila para garantir encadeamento.

---

### Agente 2 — Redator Funcional

Recebe: `core.md` do Agente 1.

Consulta: `contexto/disciplinas/[disciplina].md`

Produz: `texto.md` — prosa didática integrada com marcação estrutural em **HTML comments invisíveis**. Não usa rótulos visíveis.

Formato obrigatório:
- Abre com `<!-- [CONTEXTO_OPERACAO] -->` (quatro campos)
- Cada seção tem cabeçalho idêntico ao core e marcação em HTML comments
- Definição e exemplo integrados em parágrafo único com transição denotativa
- Síntese final responde exatamente à pergunta do capítulo

Responsabilidade do Agente 2: **didática e conteúdo**. Formatação exata da marcação é responsabilidade do Agente 3.

---

### Agente 3 — Normalizador de Marcação (`normalizador.py`)

**Código Python — não usa LLM.**

Recebe: `texto.md` do Agente 2.

Produz: `texto.md` normalizado com quatro normalizações aplicadas de forma determinística:

1. **CONTEXTO_OPERACAO** — garante os quatro campos em markdown bold, um por linha
2. **FONTE** — garante citação bibliográfica dentro do bloco, tag de abertura sem conteúdo embutido
3. **AUTOR** — garante ancoragem ao bloco pai (aninhado ou com `ref=tipo`)
4. **Tipos desconhecidos** — sinaliza com `AVISO_AGENTE5` sem descartar o conteúdo

O A3 é o contrato de interface entre a zona criativa (A2 e A4) e a zona estrutural (A5). Existe porque modelos de linguagem não são consistentes em formatação — e isso é esperado.

---

### Agente 4 — Polidor de Prosa

Recebe: `texto.md` normalizado pelo Agente 3.

Produz: **uma lista JSON de trocas** no formato `[{"original": "...", "novo": "..."}]`. O pipeline aplica as trocas no arquivo automaticamente via `_apply_diffs()`. O A4 nunca salva o arquivo diretamente.

Melhora transições entre blocos, naturalidade das frases e encadeamento entre parágrafos. **Não toca nos HTML comments. Não cria conteúdo novo.**

---

### Agente 5 — Formatador (`formatador.py`)

**Código Python — não usa LLM.**

Recebe: `texto.md` (processado pelo Agente 4) + verificações geradas pelo `verificador.py`.

Produz: `[capitulo].xml` — capítulo estruturado para InDesign, com:
- Tags como `<secao tipo="Definir">`, `<bloco tipo="AUTOR">`, `<indicacao-imagem>`
- `<mapa-progressao>` — mapa visual das operações do capítulo (injetado após `</cabecalho>`)
- `<sidebar tipo="verificacao">` — pergunta de múltipla escolha ao final de cada seção com `VERIFICACAO: Sim`
- `<sidebar tipo="aplicar-agora">` — mini-caso no rodapé com resposta oculta para o professor

---

### Verificador (`verificador.py`)

Chamado internamente pelo pipeline antes do Agente 5. Lê o `core.md` de cada capítulo e gera, em uma única chamada ao Haiku:

- Perguntas de verificação fechadas (múltipla escolha, 3 alternativas) para cada seção com `VERIFICACAO: Sim`
- Mini-exercício "Aplicar agora" com caso concreto novo e resposta comentada

---

### Avaliador (`avaliar.py`)

Ferramenta independente para controle de qualidade. Avalia capítulos com uma rubrica de 6 critérios via LLM-judge (Haiku). Grava os resultados em `logs/qualidade_YYYYMMDD.csv` para série histórica.

**Critérios:**
1. Operação cognitiva executada
2. Exemplo âncora específico
3. Síntese responde à pergunta
4. Proibições de estilo respeitadas
5. Marcação estrutural preservada
6. Fluidez da prosa

Cada critério recebe nota 0-10 (aprovado ≥ 6). O CSV acumula avaliações ao longo do tempo para detectar regressões.

---

## Fluxo resumido

```
A0 → instrucoes.csv
A1 → core.md (sequencial, lê cores anteriores)
A2 → texto.md (prosa + HTML comments)
A3 → texto.md normalizado (Python, determinístico)
A4 → diffs JSON → _apply_diffs() → texto.md com prosa polida
verificador.py → verificações XML (Haiku)
A5 → XML formatado para InDesign (Python, determinístico)
```

A1 roda sequencialmente. A2–A5 podem rodar em paralelo por capítulo com `--workers N`.

---

## Decisões de arquitetura

**A3 e A5 como código Python**
Normalização de marcação e formatação XML são operações estruturais, não criativas. Converter para Python eliminou alucinações, tornou o comportamento auditável e zerou o custo de tokens dessas etapas.

**A4 entrega diffs, não salva arquivo**
O Agente 4 retorna apenas as substituições que quer fazer (JSON). O pipeline aplica e salva. Isso evita que o agente apague acidentalmente conteúdo ou marcação ao reescrever o arquivo inteiro.

**Verificações separadas do texto**
O `verificador.py` gera as verificações a partir do `core.md` — não do texto. Isso garante que as perguntas estejam alinhadas com a estrutura pedagógica planejada, não com o texto produzido.

**Paralelização de capítulos**
A1 deve ser sequencial (lê cores anteriores). A2–A5 são independentes por capítulo e rodam em `ThreadPoolExecutor`. Escrita do CSV de uso é thread-safe via `threading.Lock`.

**Separação de responsabilidades entre A2, A3 e A4**
O Agente 2 é responsável por conteúdo e didática — não por formatação exata. O A3 existe precisamente porque modelos de linguagem são inconsistentes em formatação, e isso é esperado. O A4 existe porque fluência de prosa é uma operação separada de estrutura de conteúdo.

**Prompt caching**
Reduz custo de input nas iterações internas. Implementado via `cache_control` no system prompt.

**Distinção entre orientação e skill**
`orientacoes/`: quem é o agente, sua função no processo, como se relaciona com os outros.
`skills/`: como o agente executa — passos, critérios, formatos.
Em caso de conflito, os princípios pedagógicos prevalecem.

---

## Histórico de modificações

**2026-06-13 — Fase 3: qualidade e eficiência**
- E7: modelo por agente (`AGENT_MODELS` dict, variáveis de ambiente por agente)
- E8: A4 entrega diffs JSON; `_apply_diffs()` aplica as trocas em Python
- E10: paralelização de capítulos com `--workers N` e `ThreadPoolExecutor`
- R-Q4: verificações fechadas e "Aplicar agora" via `verificador.py` (Haiku), injetados no XML pelo A5
- R-Q6: `<mapa-progressao>` XML com operações visíveis por seção
- R-Q7: rubrica de qualidade LLM-judge em `avaliar.py` com série histórica em CSV

**2026-06-10 — Fase 2: A3 e A5 convertidos para Python**
- `normalizador.py`: A3 como código Python determinístico
- `formatador.py`: A5 como código Python determinístico
- Pasta de output renomeada de `xml/` para `formatado/`

**2026-06-08 — Reformulação do Agente 2 e redefinição do Agente 4**
Skill do A2 reescrita: HTML comments diretos, exemplos antes/depois para todas as 7 operações, banco de transições denotativas. Skill do A4 reescrita: papel redefinido de "conversor de rótulos" para "polidor de prosa".

**2026-06-08 — Correção de campo: HABILIDADE_BNCC → HABILIDADE_ENEM**

**2026-05-30 — Reformulação para pipeline funcional**
Abandono da simulação de voz humana. Princípio pedagógico: artificialidade funcional. Substituição dos tipos de seção por sete operações elementares.
