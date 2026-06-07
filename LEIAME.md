# LEIAME — PIPELINE DE APOSTILAS DIDÁTICAS (VERSÃO FUNCIONAL)

## Estado atual do projeto

Pipeline de **dois** tem um paradigma **funcional** (texto rotulado, sem narrativa, sem simulação de voz humana). Precisamos fazer o código rodar e o foco atual é ajustar as skills, reduzir custo de tokens via prompt caching e validar a clareza didática do formato funcional. O desafio é fazer uma apostila criada por IA que não busque ser como uma apostila feita por humano mas que seja extremamente funcional justamente por ter sido feita por máquinas. 

---

## O que é este projeto

Pipeline de geração de apostilas didáticas de ciências humanas para o Ensino Médio brasileiro, orientadas por habilidades da BNCC. O propósito é que o aluno pratique **operações cognitivas elementares** (definir, classificar, comparar, sequenciar, mapear causalidade, reconhecer perspectiva, aplicar) aplicadas a conteúdos nucleares. O texto não tenta soar humano – é uma **interface funcional clara e rastreável**.

O professor define os parâmetros de cada capítulo em um CSV. O pipeline lê esse CSV e aciona os agentes em sequência. Cada agente produz um output que serve de input para o seguinte. Os agentes são construídos em Python e usam a API da Anthropic (modelo claude-sonnet/opus). Os agentes operam em modo agêntico: leem os arquivos de instrução por conta própria a partir dos caminhos que o pipeline informa – não há injeção de prompt via código.

---

## Princípio pedagógico central

O texto final não conta uma história – ele executa um **algoritmo de ensino**. Cada habilidade da BNCC é decomposta em operações elementares. O aluno aprende a habilidade vendo o algoritmo sendo aplicado repetidamente sobre o conteúdo.

As sete operações elementares são:
- **Definir** – apresentar um conceito com seus elementos essenciais
- **Classificar** – atribuir itens a categorias segundo critérios explícitos
- **Comparar** – listar diferenças e semelhanças entre elementos
- **Sequenciar** – ordenar eventos no tempo
- **Mapear causalidade** – identificar relações de causa‑consequência
- **Reconhecer perspectiva** – identificar visão de mundo ou posição de um autor/grupo
- **Aplicar** – usar um conceito para analisar um caso novo

**Não há** “situação-problema narrativa”, “tensão”, “mobilização”, “pergunta retórica” ou qualquer recurso de simulação humana.

---

## Arquitetura de pastas
pipeline.py — orquestrador principal
teste_cache.py — script para testar prompt caching da API
.env — chave de API (ANTHROPIC_API_KEY=...) — não versionar

skills/
agente1-skill.md — como o Agente 1 executa (arquiteto funcional)
agente2-skill.md — como o Agente 2 executa (redator funcional)

orientacoes/
agente1-orientacao.md — identidade e papel do Agente 1
agente2-orientacao.md — identidade e papel do Agente 2

contexto/
principios-pedagogicos-agente1.md — governa as decisões do Agente 1 (funcional)
disciplinas/
historia.md — conceitos, autores, regras para História
sociologia.md — conceitos, autores, regras para Sociologia
filosofia.md — conceitos, autores, regras para Filosofia
geografia.md — conceitos, autores, regras para Geografia

input/
[nome-da-apostila]/
instrucoes.csv — preenchido pelo professor; uma linha por capítulo

output/
[nome-da-apostila]/
core/
[unidade-slug]/
[unidade_idx]-[capitulo_idx]-[nome-do-capitulo].md
texto/
[unidade-slug]/
[unidade_idx]-[capitulo_idx]-[nome-do-capitulo].md
validacao/
[unidade-slug]/
[unidade_idx]-[capitulo_idx]-[nome-do-capitulo].md
imagens/
[unidade-slug]/
[unidade_idx]-[capitulo_idx]-[nome-do-capitulo].md
xml/
[unidade-slug]/
[unidade_idx]-[capitulo_idx]-[nome-do-capitulo].xml
estilos-indesign.md — gerado uma só vez; lista os estilos InDesign

text

**Nota:** Ainda é necessário considerar a criação de um Agente 3 (Revisor de Estilo) que opere mesmo sob um texto ao mesmo tempo que é um **Validador Técnico** que apenas certifica conformidade, não reescreve. Pensar se vamos ter Agente 3 e Agente 4, um para analisar conformidade e outro para reescrever.
Além disso será necessário um agente 5 que será o diagramador que prepara o arquivo para ser um xml para ser usado no indesign 

---

## O CSV — input do professor

**Colunas obrigatórias:**  
`disciplina`, `unidade`, `pergunta_unidade`, `capitulo`, `habilidade`,  
`conteudos_nucleares`, `autores`, `elementos_obrigatorios`

Cada linha é um capítulo. Capítulos da mesma unidade compartilham os campos `unidade` e `pergunta_unidade`. O pipeline organiza o output por unidade (slug gerado automaticamente) e por capítulo dentro da unidade.

---

## Como rodar o pipeline

```bash
# Roda todos os agentes em todos os capítulos
python pipeline.py input/teste-sociologia/instrucoes.csv

# Roda apenas agentes específicos (ex: 1,2,3)
python pipeline.py input/teste-sociologia/instrucoes.csv --agentes 1,2,3

# Força regeneração mesmo que o arquivo de output já exista
python pipeline.py input/teste-sociologia/instrucoes.csv --force

# Roda apenas o capítulo N (por ordem no CSV, começando em 1)
python pipeline.py input/teste-sociologia/instrucoes.csv --cap 1

# Pular Agente 5 (curador de imagens) – o Agente 6 opera em modo placeholder
python pipeline.py input/teste-sociologia/instrucoes.csv --agentes 1,2,3,6
Ordem padrão dos agentes: 1 → 2 → 3 → 5 → 6

O Agente 3 valida o texto produzido pelo Agente 2 antes de seguir para imagens e diagramação.

Chave de API: o pipeline lê automaticamente o arquivo .env na raiz do projeto. Formato:

text
ANTHROPIC_API_KEY=sk-ant-api03-...
Os seis agentes (0–5)
Agente 1 — Arquiteto Curricular (funcional)
Recebe: linha do CSV + contexto da unidade + lista de todas as unidades + cores de capítulos anteriores (se houver).

Consulta: contexto/principios-pedagogicos-agente1.md + contexto/disciplinas/[disciplina].md

Produz: core.md – arquitetura do capítulo baseada em operações elementares. O core contém:

Cabeçalho: habilidade, operação principal, pergunta do capítulo, contribuição à unidade

Sequência de 3 a 5 seções, cada uma com TIPO_OPERACAO (Definir, Classificar, etc.), campos específicos (ex: para Comparar: ELEMENTO_A, ELEMENTO_B, ASPECTOS_DA_COMPARACAO, EXEMPLO_ANCOLA)

Síntese final (resposta direta à pergunta) e encadeamento

Checklist de verificação interna

Regra: o core nunca contém campos como TENSAO, MOBILIZACAO, PERGUNTA_RETORICA. É um conjunto de dados estruturados.

Agente 2 — Redator Funcional
Recebe: core.md do Agente 1.

Consulta: apenas o documento de contexto disciplinar funcional (ex: historia.md) – não consulta os princípios pedagógicos.

Produz: texto.md – capítulo em texto funcional rotulado, sem narrativa, sem metáforas, sem perguntas retóricas.

Formato obrigatório:

Começa com **CONTEXTO DE OPERAÇÃO** (habilidade, operação principal, pergunta, opcional “por que importa”)

Cada seção tem cabeçalho idêntico ao core e blocos rotulados ([DEFINIÇÃO], [COMPARAÇÃO], [EXEMPLO], [VERIFICAÇÃO], etc.)

Onde VERIFICACAO: Sim, há perguntas fechadas (múltipla escolha ou V/F) com a resposta correta indicada.

Síntese final responde exatamente à pergunta do capítulo.

Proibições: nenhum recurso narrativo, nenhum “nós”, nenhum andaime, nenhuma exclamação, nenhuma metáfora, nenhum advérbio de opinião.

Agente 3 — Normalizador de Marcação
Recebe: texto.md (Agente 2).

Produz: texto.md normalizado — aplica as quatro normalizações de marcação HTML estrutural e salva de volta no mesmo caminho. Não altera prosa nem a ordem das seções.

Agente 4 — Redator de Estilo
Recebe: texto.md (normalizado pelo Agente 3).

Produz: texto.md reescrito em prosa natural — os rótulos estruturais desaparecem, tornando invisível a engenharia funcional para o leitor final.

Agente 5 — Diagramador
Recebe: texto.md + core.md (para identificar tipos de operação) + imagens.md (se existir).

Produz dois arquivos:

[capitulo].xml – capítulo estruturado para InDesign, com tags como <secao tipo="Definir">, <bloco tipo="VERIFICACAO">, <indicacao-imagem>.

estilos-indesign.md – gerado uma vez por apostila; lista os estilos de parágrafo necessários.

Modo placeholder: se imagens.md não existe (ex: --agentes 1,2,3,6), insere uma tag genérica <indicacao-imagem ref="?"/> por seção Principal.

Histórico de modificações
(mantenha as entradas anteriores conforme necessário; aqui apenas um exemplo da transição)

2026-05-30 – Reformulação para pipeline funcional (eliminação do Agente 4, novo paradigma)
Mudanças fundamentais:

Abandono da simulação de voz humana. Princípio pedagógico agora é artificialidade funcional.

Substituição dos tipos de seção (Argumentativa/Demonstrativa/Expositiva) por sete operações elementares.

Eliminação do Agente 4 (Revisor de Estilo) – texto funcional não tem estilo a revisar.

Agente 3 transformado em Validador Técnico (não reescreve, apenas certifica).

Novos documentos de contexto: principios-pedagogicos-agente1.md, historia.md, sociologia.md (renomeados de historia-contexto-funcional.md e sociologia-contexto-funcional.md).

Skills e orientações do Agente 1 e Agente 2 completamente reescritas.

Impacto esperado: redução de custo (menos agentes, prompts mais curtos), maior clareza didática, eliminação do “vale da estranheza” de textos que tentam soar humanos.

Decisões de arquitetura (relevantes para a versão funcional)
Decisão 1 – Eliminação do Agente 4
Motivo: revisão de estilo pressupunha uma “voz” a ser polida. No texto funcional rotulado, não há voz – apenas blocos de informação. A verificação estrutural foi incorporada ao Agente 3.

Decisão 2 – Processamento capítulo a capítulo (mantida)
Motivo: simplicidade e inspeção incremental. O custo de coerência entre capítulos é mitigado pelo Agente 1 que lê cores anteriores e pelo encadeamento explícito no core.

Decisão 3 – Prompt caching (mantida)
Motivo: reduz custo de input nas iterações internas de cada agente. Implementado via cache_control no system prompt.

Distinção entre orientação e skill (mantida)
Orientação (orientacoes/): quem é o agente, sua função no processo, como se relaciona com os outros.
Skill (skills/): como o agente executa – passos, critérios, formatos.

Em caso de conflito, os princípios pedagógicos funcionais prevalecem.

Estado dos componentes
Implementado e integrado:

Agente 1 (Arquiteto Curricular funcional) – agente1-skill.md, agente1-orientacao.md

Agente 2 (Redator Funcional) – agente2-skill.md, agente2-orientacao.md

Agente 3 e 4 (Validador Técnico e redator) - analisar necessidade e como fazer

Agente 5 (Diagramador) – agente5-skill.md, agente5-orientacao.md

pipeline.py com flags --agentes, --force, --cap

.env e teste_cache.py

Disciplinas com contexto funcional completo:

História – historia.md

Sociologia – sociologia.md

Filosofia – filosofia.md

Geografia – geografia.md

Em avaliação:

Qualidade das verificações fechadas (se realmente testam a habilidade)

Precisão do Agente 3 na detecção de violações e se necessário outro agente para redator, 


Ainda não existe:

Correção automática a partir do output do Agente 3 e reescrita (hoje é manual)

Interface web para o professor preencher o CSV