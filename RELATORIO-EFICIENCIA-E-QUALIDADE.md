# RELATÓRIO — Eficiência de Tokens e Qualidade Didática do Pipeline IPPI

**Data:** 12/06/2026 **Escopo:** análise completa de pipeline.py, skills, orientações, contextos, inputs, outputs reais e logs de execução. Nenhum arquivo do projeto foi alterado. **Objetivo:** base de decisão para reduzir o custo por capítulo e, simultaneamente, elevar a qualidade das apostilas.

## 1. Sumário executivo

O pipeline está funcional e o output didático do Agente 2 já tem qualidade real — a prosa integrada com transições denotativas funciona. Os problemas estão em três planos:

- **Desperdício estrutural de tokens.** Tudo roda em Opus (claude-opus-4-6), inclusive tarefas mecânicas (normalizar marcação, converter markdown em XML, contar palavras) que código Python faz de graça e melhor. Agentes releem arquivos inteiros que o pipeline já conhece, releem a própria skill que já está no system prompt, e leem matrizes de 50–59 KB para extrair uma única entrada de ~1,2 KB.

- **Contratos quebrados entre agentes.** A agente2-orientacao.md contradiz frontalmente a agente2-skill.md dentro do mesmo system prompt. O marcador TIPO_OPERACAO — que carrega exatamente a informação pedagógica central do projeto — não está na lista de tipos conhecidos do Agente 3 e é descartado como "genérico" no XML. O diferencial do produto está sendo perdido na última milha.

- **A aprendizagem algorítmica está incompleta no produto final.** O aluno vê a operação cognitiva ser demonstrada, mas nunca a executa: a VERIFICACAO foi removida do texto e nada a substituiu. Para um material cujo diferencial é "algoritmo de ensino", falta o passo em que o algoritmo roda *no aluno*.

Estimativa: as ações deste relatório reduzem o custo por capítulo em **60–75%** e eliminam as duas maiores fontes de degradação de qualidade (instruções contraditórias e perda da operação no XML).

## 2. Como o pipeline gasta tokens hoje (diagnóstico)

### 2.1 Anatomia do custo por capítulo

Fluxo atual: 5 chamadas de agente por capítulo (0 é por apostila), todas em Opus, todas em loop agêntico de 3–4 iterações (evidência: logs de 30/05 a 08/06). Em cada iteração do loop, **todo o histórico da conversa é reenviado** — incluindo o conteúdo integral dos arquivos retornados por read_file. Um capítulo de ~2.500 palavras (~4–6 mil tokens) é pago como input várias vezes dentro do mesmo agente, e de novo em cada agente seguinte.

| **Agente** | **O que faz** | **Leituras típicas (logs)** | **Natureza da tarefa** |
| --- | --- | --- | --- |
| 0 Decompositor | briefing → CSV | briefing + **matriz-bncc.json inteira (59 KB)** | Semântica (precisa de LLM) |
| 1 Arquiteto | CSV → core.md | princípios + disciplina + **matriz-conteudosbncc.json inteira (52 KB)** + cores anteriores completos | Semântica (precisa de LLM) |
| 2 Redator | core → texto.md | core + disciplina | Semântica (precisa de LLM) |
| 3 Normalizador | corrige 4 padrões de marcação | texto completo, reescreve texto completo | **Mecânica (regex/parser)** |
| 4 Polidor | melhora prosa | texto completo, reescreve texto completo (e releu a própria skill — log 08/06 17:11) | Semântica leve (não precisa de Opus) |
| 5 Formatador | texto → XML + contagem de palavras + quebras de página | texto completo | **Mecânica/determinística** |

### 2.2 Os cinco vazamentos principais

**V1 — Agentes mecânicos rodando em Opus.** O Agente 3 aplica quatro normalizações descritas com precisão de máquina na própria skill (formatos errados → formato correto). Isso é um parser. O Agente 5 extrai HTML comments, monta XML, **conta palavras** e calcula quebras a cada 1.300 palavras — LLMs são notoriamente ruins em contar palavras; Python é exato. Cada um desses agentes custa uma passada completa de Opus por capítulo (ler ~5K tokens, reescrever ~5K tokens, 3 iterações de histórico reenviado) para um trabalho que código faz em milissegundos, com resultado determinístico e XML garantidamente válido.

**V2 — Matrizes lidas inteiras para usar uma entrada.** As matrizes de referência têm dezenas de KB (~15K tokens cada — medições originais com `matriz-enem.json`/`matriz-conteudosenem.json`, hoje substituídas por `matriz-bncc.json`/`matriz-conteudosbncc.json`). A entrada de uma única habilidade, medida, tem **~1.200 caracteres** (~300 tokens). O Agente 0 e o Agente 1 pagam ~98% de desperdício em cada leitura — e o Agente 1 faz isso **por capítulo**.

**V3 — Modo agêntico onde não há decisão a tomar.** O user message já lista os arquivos exatos que o agente deve ler ("ARQUIVOS QUE VOCÊ DEVE LER... 1. ... 2. ..."). Cada read_file custa uma iteração inteira (reenvio de todo o histórico + roundtrip). Injetar o conteúdo diretamente no user message elimina 1–3 iterações por agente sem perda nenhuma — o agente não estava decidindo nada, só obedecendo uma lista.

**V4 — Agente relê a própria skill.** Log de 08/06 17:11: o Agente 4 executa read_file: skills/agente4-skill.md — arquivo que **já está no seu system prompt** via build_system_prompt(). Causa: o user message diz "Siga o procedimento da skill (skills/agente4-skill.md)", o que induz a leitura. Duplicação pura de ~3K tokens + uma iteração.

**V5 — Cache subutilizado e reescrita integral de arquivos.** O cache_control cobre só o system prompt. O histórico de mensagens — que cresce a cada iteração com conteúdos de arquivo — é reenviado sem cache. E os Agentes 3 e 4 **reescrevem o arquivo inteiro** via write_file: tokens de output (os mais caros, ~5× o input) pagos para repetir 90% de texto inalterado.

### 2.3 Crescimento O(n²) com capítulos anteriores

O Agente 1 lê todos os cores anteriores completos da unidade. Com 5 capítulos, o capítulo 5 paga 4 cores inteiros (~12–16K tokens) quando precisa de duas linhas de cada: SINTESE_FINAL e ENCADEAMENTO (mais a lista de autores já usados, para a regra de não-repetição).

### 2.4 Nenhuma medição

response.usage (input_tokens, output_tokens, cache_read) está disponível em toda resposta da API e **não é logado**. Não existe custo por capítulo, por agente, nem taxa de acerto de cache. Não se otimiza o que não se mede — esta é a primeira ação a implementar, antes de qualquer outra.

## 3. Achados críticos de qualidade

### Q-CRÍTICO 1 — A operação cognitiva é perdida no XML

Evidência no output real (apostila-teste-historia-em1, capítulo 1): **toda seção** sai assim:

<!-- [TIPO_OPERACAO: Definir] -->

<!-- AVISO_AGENTE5: tipo TIPO_OPERACAO não mapeado — gerar secao tipo="generico" -->

A skill do Agente 2 manda escrever <!-- [TIPO_OPERACAO: ...] --> em cada seção; a lista de tipos conhecidos do Agente 3 **não inclui** TIPO_OPERACAO; o mapeamento do Agente 5 também não. Resultado: a informação que define o projeto — qual operação elementar a seção executa — é degradada para "genérico" exatamente na camada que chega ao InDesign. O diferencial pedagógico desaparece do produto físico. Correção: uma linha na lista do Agente 3 + uma linha no mapeamento do Agente 5 (ou, melhor, item E2 abaixo).

### Q-CRÍTICO 2 — Orientação e skill do Agente 2 se contradizem no mesmo system prompt

agente2-orientacao.md (versão antiga, nunca atualizada na reformulação de 08/06) instrui: produzir blocos visíveis [DEFINIÇÃO], [COMPARAÇÃO], [VERIFICAÇÃO]; "se VERIFICACAO: Sim, você deve incluir o bloco [VERIFICAÇÃO]". A agente2-skill.md (atual) proíbe exatamente isso: "Não usar rótulos visíveis", "VERIFICACAO não existe no seu output". Os dois arquivos são **concatenados no mesmo system prompt** por build_system_prompt(). O modelo recebe ordens opostas a cada capítulo — quando obedece, é por sorte ou pela skill vir por último. O mesmo problema existe em agente4-orientacao.md ("transformar rótulos visíveis em HTML comments", papel da v2) versus agente4-skill.md (polidor de prosa, rótulos já convertidos).

### Q-CRÍTICO 3 — Documentação canônica em três versões conflitantes

| **Afirmação** | **ARQUITETURA_PIPELINE_V3.md** | **LEIAME.md** | **Realidade (pipeline.py + outputs)** |
| --- | --- | --- | --- |
| Papel do Agente 3 | Validador opcional, "muito custoso", fora do fluxo | Normalizador, no fluxo | Normalizador, no fluxo padrão 1–5 |
| Agente 5 | "Não implementado" | Diagramador implementado | Implementado, grava em formatado/ |
| Pasta do XML | — | output/.../xml/ | output/.../formatado/ |
| Colunas do CSV | — | 19 colunas | **20 colunas** (CSV real tem elementos_obrigatorios) |
| estilos-indesign.md | — | "gerado uma vez por apostila" | Não existe no código nem na skill do A5 |

Num projeto operado por agentes de IA, documentação desatualizada não é só risco humano: é **contexto envenenado** que qualquer agente futuro (inclusive sessões do Claude trabalhando no repositório) vai ler e usar para tomar decisões erradas. Manter um único documento canônico e arquivar os históricos com aviso explícito de obsolescência no topo.

### Q-CRÍTICO 4 — O algoritmo de ensino nunca roda no aluno

O princípio do projeto: "o aluno aprende a habilidade vendo o algoritmo sendo aplicado repetidamente". Vendo — mas nunca executando. A VERIFICACAO foi removida do texto (decisão de 30/05–08/06) e nada a substituiu. A ciência da aprendizagem é inequívoca: prática de recuperação e aplicação ativa são os maiores preditores de retenção. Um material que se define como "aprendizagem algorítmica que guia o aluno em uma progressão" precisa do passo em que o aluno executa a operação sobre um caso novo. Hoje a progressão existe na estrutura, mas é invisível e passiva para quem estuda. Ver R-Q4.

### Achados menores

- ref=subtipo no output real ancora um AUTOR a um tipo que não existe como seção no mapeamento do A5 (subtipo é <item>, não <secao>), gerando ambiguidade de posicionamento de sidebar.

- O XML existente de apostila-historia-midia segue o esquema antigo (sem palavras=, com "Habilidade BNCC EM13CHS201") — não foi regenerado após a refatoração; serve de teste enganoso.

- principios-pedagogicos-agente1.md diz "3 a 5 seções"; a skill do A1 e o CSV trabalham com 4 a 6. Conflito direto no documento que "prevalece sobre qualquer outro arquivo".

- Repositório carrega ~42 MB com .tmp.driveupload/, caches de pytest e arquivos .gdoc duplicados — higiene, e ruído para qualquer agente que explore o repositório.

## 4. Recomendações de eficiência (ordenadas por retorno/esforço)

### E1 — Logar usage de toda chamada (fazer primeiro)

Registrar input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens por chamada, agregado por agente e por capítulo, no log e num CSV de custos. Esforço: ~15 linhas em run_agent(). Sem isso, todo o resto é estimativa.

### E2 — Agentes 3 e 5 viram código Python

- **Agente 3:** as quatro normalizações são especificadas como transformações de texto exatas. Implementar como módulo normalizador.py (regex + parser de blocos). Manter fallback LLM (Haiku/Sonnet) apenas quando o parser encontrar estrutura irrecuperável — e logar esses casos para corrigir a skill do A2 na origem.

- **Agente 5:** parser markdown→XML em Python, usando a skill atual como especificação. Ganhos além do custo: XML **sempre** bem-formado, contagem de palavras exata (LLM não conta palavras com confiabilidade — risco direto para a diagramação A4, que era o problema raiz da auditoria), quebras de página determinísticas, e correção definitiva do Q-CRÍTICO 1 (o parser conhece TIPO_OPERACAO e o grava como atributo da seção).

Economia: elimina **duas passadas de Opus por capítulo** (~40–60% do custo total). É a maior alavanca isolada do projeto.

### E3 — Fatiar as matrizes no pipeline

pipeline.py extrai a entrada da habilidade (json.load + acesso por chave, ~5 linhas) e injeta só ela no user message do Agente 0 e do Agente 1. Economia: ~13–15K tokens por leitura; no A1, por capítulo. Remove também as instruções "leia matriz-X.json" das skills.

### E4 — Injetar arquivos conhecidos no user message

Core, contexto disciplinar, princípios pedagógicos: o pipeline sabe os caminhos (ele mesmo os lista). Injetar o conteúdo direto e manter read_file apenas para o que o agente decide sozinho (hoje, quase nada). Reduz 1–3 iterações por agente — cada iteração evitada economiza um reenvio integral do histórico.

### E5 — Corrigir os user messages que induzem releitura

Trocar "Siga o procedimento da skill (skills/agenteN-skill.md)" por "Sua skill e orientação já estão no seu system prompt". Elimina o V4.

### E6 — Cache no histórico de mensagens

Adicionar cache_control: ephemeral ao último bloco de conteúdo do histórico antes de cada iteração do loop. Com 3–4 iterações por agente, o prefixo (system + user message com arquivos injetados) passa a ser lido do cache (~90% de desconto sobre o trecho cacheado).

### E7 — Modelo por agente

Hoje IPPI_MODEL é global. Tornar configurável por agente:

| **Agente** | **Modelo recomendado** | **Justificativa** |
| --- | --- | --- |
| 0 Decompositor | Sonnet | tarefa estruturada com template (sequencia_pedagogica) |
| 1 Arquiteto | **Opus** | decisões pedagógicas — onde Opus paga seu preço |
| 2 Redator | **Opus** (testar Sonnet A/B) | qualidade da prosa é o produto |
| 3 (fallback) | Haiku | mecânico |
| 4 Polidor | Sonnet | reescrita local, sem criação de conteúdo |
| 5 | — (código) | — |

### E8 — Agente 4: medir antes de manter; se mantiver, emitir diffs

A skill do A2 já exige prosa fluida, transições denotativas e integração — e o output real do A2 confirma boa qualidade. Rodar A/B (com/sem A4) num conjunto de capítulos e medir o delta com a rubrica de R-Q5. Se o A4 continuar, mudar o contrato: em vez de reescrever o arquivo inteiro, retornar **lista de substituições** (trecho_original → trecho_melhorado) aplicadas por código. Output cai de ~5K tokens para ~500–1.000, e elimina o risco de o A4 tocar na marcação.

### E9 — Contexto de capítulos anteriores em resumo

O pipeline extrai dos cores anteriores apenas SINTESE_FINAL, ENCADEAMENTO e a lista de autores usados (parsing trivial, os campos são nomeados) e injeta isso no A1. Contexto limitado e constante por capítulo, em vez de O(n²).

### E10 — Paralelizar capítulos (tempo, não tokens)

Após o A1 (que depende dos cores anteriores), os estágios 2→3→4→5 de capítulos diferentes são independentes. Paralelizar com 2–3 workers corta o tempo de apostila pela metade ou mais. Atenção a rate limits.

### Estimativa consolidada por capítulo

Valores aproximados (PT-BR ≈ 3,5–4 chars/token; capítulo ≈ 2.400–2.700 palavras; antes de medição real do E1):

|  | **Hoje (tudo Opus)** | **Após E1–E9** |
| --- | --- | --- |
| Passadas LLM | 5 | 2–3 (A1, A2, A4 opcional) |
| Input acumulado | ~150–250K tokens | ~40–70K (boa parte com desconto de cache) |
| Output | ~20–25K tokens | ~8–12K |
| Custo relativo | 100% | **~25–40%** |

## 5. Recomendações de qualidade pedagógica

### R-Q1 — Consertar o contrato TIPO_OPERACAO (urgente, custo quase zero)

Enquanto E2 não estiver pronto: adicionar TIPO_OPERACAO à lista de tipos conhecidos do A3 e ao mapeamento do A5 (tipo como atributo da <secao>). Isso devolve ao XML — e portanto ao InDesign — a informação que materializa o diferencial do projeto.

### R-Q2 — Reescrever agente2-orientacao.md e agente4-orientacao.md

Alinhar à arquitetura atual (HTML comments, sem VERIFICACAO no A2; A4 polidor). Instituir a regra: **toda mudança de skill obriga revisão da orientação correspondente no mesmo commit.** Instruções contraditórias no system prompt são o defeito de qualidade mais barato de corrigir e um dos mais danosos — o custo se paga em variância de output a cada capítulo.

### R-Q3 — Um documento canônico de arquitetura

Consolidar LEIAME + ARQUITETURA_V3 + HANDOVER num único documento vivo; mover os outros para docs/historico/ com aviso de obsolescência na primeira linha. Corrigir: pasta formatado/, 20 colunas (ou remover elementos_obrigatorios se for resíduo), faixa "4 a 6 seções" nos princípios pedagógicos, e decidir o destino de estilos-indesign.md (implementar como template estático gerado pelo código do E2 — é uma lista fixa de estilos — ou retirar da documentação).

### R-Q4 — Devolver a execução ao aluno (o passo que falta do algoritmo)

Proposta de baixo custo e alto valor pedagógico, sem tocar no A2:

- **Verificações fechadas por seção** geradas numa passada barata (Haiku/Sonnet) a partir do **core** (que já tem VERIFICACAO: Sim/Não por seção — o campo existe e é ignorado hoje). Inseridas pelo formatador (código do E2) como <sidebar tipo="verificacao"> — o esquema XML atual já prevê isso.

- **Fechamento ****"****Aplicar agora****"****:** o capítulo termina com o aluno executando a operação principal sobre um caso novo curto (o core já tem CASO_NOVO/EXEMPLO_ANCOLA como matéria-prima), com resposta comentada oculta.

Com isso a progressão vira: *ver a operação → ver de novo em outro conteúdo → executar*. É a tese do projeto, completa.

### R-Q5 — Validador estrutural em código + portão de correção automática

Após o A2 (e o A4), um validador Python verifica: todos os blocos abrem e fecham; seções correspondem 1:1 aos CABECALHO do core; CONTEXTO_OPERACAO com 4 campos; proibições de estilo detectáveis por regex (travessões de aposto, "nós/a gente", exclamações, marcadores - dentro de blocos). Se reprovar, o pipeline reenvia ao A2 **somente a lista de violações** para correção dirigida — implementando a "correção automática" que o LEIAME registra como inexistente, e barrando capítulos defeituosos antes de gastarem tokens nos estágios seguintes.

### R-Q6 — Tornar a progressão visível para o aluno

O XML carregando tipo por seção (R-Q1) permite ao InDesign exibir um selo da operação ("DEFINIR", "COMPARAR"...) em cada seção e um mapa da progressão na abertura do capítulo ("Neste capítulo você vai: Definir → Classificar → Comparar → Mapear causalidade"). A rastreabilidade que hoje é só interna vira recurso metacognitivo do aluno — honestidade cognitiva como vantagem, exatamente o princípio do projeto.

### R-Q7 — Avaliação contínua de qualidade

Transformar o checklist da skill do A2 numa rubrica por operação (a operação foi executada de fato? o exemplo âncora é específico? a síntese responde literalmente à pergunta?). Aplicar via LLM-judge barato em amostra de capítulos + revisão humana do professor, com nota registrada por capítulo. Cria a série histórica que permite testar mudanças de skill/modelo (A/B do E8) com critério, em vez de impressão.

## 6. Roteiro de implementação

**Fase 1 — uma sessão de trabalho (ganho imediato, risco zero):** E1 (logging de usage) · E3 (fatiar matrizes) · E4/E5 (injeção de arquivos e user messages) · R-Q1 (TIPO_OPERACAO nas listas) · R-Q2 (orientações contraditórias) · higiene do repositório.

**Fase 2 — cerca de uma semana:** E2 (A3 e A5 em código, com testes usando os outputs reais existentes como fixtures) · R-Q5 (validador + portão de correção) · E6 (cache no histórico) · R-Q3 (documento canônico).

**Fase 3 — evolução:** E7 (modelo por agente) · E8 (A/B do Agente 4) · R-Q4 (verificações + Aplicar agora) · R-Q6 (progressão visível) · E10 (paralelização) · R-Q7 (rubrica e série histórica).

Critério de sucesso mensurável: custo por capítulo ≤ 35% do atual (medido pelo E1), 100% das seções com operação preservada no XML, zero instruções contraditórias nos system prompts, e todo capítulo terminando com o aluno executando a operação principal.

## 7. Apêndice — evidências citadas

- Opus global: pipeline.py linha 50 (MODEL = "claude-opus-4-6").

- A4 relendo a própria skill: logs/pipeline_20260608_171111.log, 17:11:19.

- AVISO_AGENTE5 em toda seção: output/apostila-teste-historia-em1/texto/.../01-01-...md.

- Lista de tipos sem TIPO_OPERACAO: skills/agente3-skill.md, seção "Tipos desconhecidos".

- Contradição do A2: orientacoes/agente2-orientacao.md (linhas 13, 74–79, 137) vs skills/agente2-skill.md (seção "O que você NÃO faz").

- Matrizes (medições originais ENEM, hoje substituídas pelas matrizes BNCC): ~59 KB / ~52 KB; entrada de uma habilidade ≈ 1.200 caracteres (medido).

- CSV com 20 colunas: input/apostila-teste-historia-em1/instrucoes.csv (header inclui elementos_obrigatorios).

- Iterações por agente: contagem nos 22 logs — A0: 3–7; A1: 3–4; A2: 3–4; A3: 3; A4: 3–4.

- "3 a 5 seções" vs "4 a 6": contexto/principios-pedagogicos-agente1.md §3.2 vs skills/agente1-skill.md (checklist).