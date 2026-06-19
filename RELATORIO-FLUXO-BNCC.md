# Relatório do Fluxo — Pipeline IPPI sob a Matriz BNCC

**Data:** 2026-06-18
**Escopo:** revisão completa dos arquivos do projeto após a migração ENEM → BNCC, com descrição da função de cada agente, mapeamento do fluxo ponta a ponta e roteiro para deixar o pipeline impecável.

---

## 1. O que o projeto é, em uma frase

É uma linha de montagem de apostilas didáticas de Ciências Humanas para o Ensino Médio. O professor descreve o que quer ensinar; uma cadeia de agentes (uns são modelos de linguagem, outros código Python determinístico) transforma essa descrição em um capítulo estruturado, escrito, polido e formatado em XML pronto para diagramação. O princípio pedagógico é a "artificialidade funcional": o texto não imita voz humana — ele executa um algoritmo de ensino em que cada habilidade da BNCC é decomposta em operações cognitivas elementares (Definir, Classificar, Comparar, Sequenciar, Mapear causalidade, Reconhecer perspectiva, Aplicar) aplicadas repetidamente sobre o conteúdo.

A migração trocou a base curricular: antes as habilidades vinham da matriz de referência do ENEM (códigos H1–H30, competências C1–C6); agora vêm da BNCC de Ciências Humanas e Sociais Aplicadas (habilidades EM13CHS101–EM13CHS606, competências específicas CHS1–CHS6), com objetos de conhecimento do Currículo Paulista.

---

## 2. A função de cada agente

A peça que governa tudo é a **matriz**: dois arquivos JSON em `contexto/` (`matriz-bncc.json` e `matriz-conteudosbncc.json`) que, para cada habilidade, definem o enunciado, o foco cognitivo, a operação predominante, a sequência pedagógica de operações e os conteúdos por disciplina. É dessa sequência que nasce a estrutura de cada capítulo.

Antes do pipeline existe um agente de "porta de entrada", o **Mediador** (`system-prompt.md`), que é um chatbot separado: conversa com o professor, mapeia a intenção dele para uma habilidade BNCC e produz o `briefing.json`. Ele não roda dentro do `pipeline.py` — é a etapa humana de coleta.

A partir do briefing, o `pipeline.py` orquestra a cadeia:

| Agente | Tipo | Entra | Sai | Função |
|---|---|---|---|---|
| **A0 — Decompositor** | LLM (Sonnet) | `briefing.json` + matriz | `instrucoes.csv` | Fatia a unidade em capítulos; para cada capítulo escreve as micro-habilidades por seção, seguindo a `sequencia_pedagogica` da habilidade BNCC. |
| **A1 — Arquiteto Curricular** | LLM (Opus) | linha do CSV + `matriz-conteudosbncc` (injetada) + princípios + contexto da disciplina | `core.md` | Define a estrutura do capítulo: seções, operações, exemplos-âncora, conteúdos nucleares, marcação `VERIFICACAO: Sim/Não`, síntese final e encadeamento. **Roda sempre sequencial** (lê os cores anteriores para garantir encadeamento entre capítulos). |
| **A2 — Redator Funcional** | LLM (Opus) | `core.md` | `texto.md` | Converte a estrutura em prosa didática, com marcação em **HTML comments invisíveis** (não em rótulos visíveis). |
| **A3 — Normalizador** | Python (`normalizador.py`) | `texto.md` | `texto.md` normalizado | Conserta a marcação de forma determinística (CONTEXTO_OPERACAO, FONTE, AUTOR, tipos desconhecidos). É o contrato de interface entre a zona criativa (A2/A4) e a zona estrutural (A5). Sem custo de tokens. |
| **A4 — Polidor de Prosa** | LLM (Sonnet) | `texto.md` normalizado | lista JSON de diffs | Sugere apenas substituições (`[{"original","novo"}]`) aplicadas por `_apply_diffs()`. Melhora transições e fluência **sem tocar nos HTML comments nem criar conteúdo**. Nunca salva o arquivo direto — protege contra perda acidental de marcação. |
| **A5 — Formatador** | Python (`formatador.py`) | `texto.md` polido + verificações + micro-habilidades do CSV | `[capitulo].xml` | Gera o XML para InDesign: `<secao tipo=...>`, `<bloco>`, `<mapa-progressao>`, `<micro-habilidade>`, `<sidebar tipo="verificacao">`, `<sidebar tipo="aplicar-agora">`. Determinístico. |

Dois utilitários completam o conjunto:

- **`verificador.py`** (Haiku): chamado antes do A5, lê o `core.md` e gera as perguntas de verificação fechadas e o mini-exercício "Aplicar agora" — a partir da estrutura planejada, não do texto produzido.
- **`avaliar.py`** (Haiku como juiz): ferramenta independente de QA que pontua cada capítulo numa rubrica de 6 critérios e acumula a série histórica em `logs/qualidade_*.csv`.

Há ainda uma camada de saída em PDF (`xml_to_pdf.py`, `apostila_pdf.py`, documentada em `HANDOVER-DIAGRAMACAO-PDF.md` e `PLANO-LAYOUT-IMAGENS-PDF.md`) e `gerar_lista_imagens()`, para a diagramação visual a partir do XML.

---

## 3. O fluxo ponta a ponta

```
Professor → Mediador (system-prompt.md) → briefing.json
                                              │
                              A0 Decompositor │ (Sonnet)
                                              ▼
                                       instrucoes.csv
                                              │
                              A1 Arquiteto    │ (Opus, sequencial)
                                              ▼
                                          core.md ──► verificador.py (Haiku)
                                              │                 │
                              A2 Redator      │ (Opus)          │ verificações
                                              ▼                 │
                                         texto.md (HTML comments)│
                              A3 Normalizador │ (Python)         │
                                              ▼                 │
                                    texto.md normalizado         │
                              A4 Polidor      │ (Sonnet → diffs) │
                                              ▼                 │
                                     texto.md polido ◄───────────┘
                              A5 Formatador   │ (Python)
                                              ▼
                                       capitulo.xml ──► (PDF / InDesign)
```

No modo briefing o padrão executa `0,1,2,3,4,5`; no modo CSV manual, `1,2,3,4,5`. A1 é sempre sequencial; os estágios 2–5 podem rodar em paralelo por capítulo com `--workers N`.

---

## 4. Estado pós-migração: o que já está correto

A troca de base curricular já está consolidada e testada. As referências de arquivo do `pipeline.py` apontam para `matriz-bncc.json` e `matriz-conteudosbncc.json`; o campo do briefing é `habilidade_bncc`; a terminologia e os exemplos em `system-prompt.md`, skills e orientações foram convertidos para códigos BNCC reais (EM13CHS401, EM13CHS402); e a lógica de autores foi ajustada para o modelo "o professor sempre informa", já que a matriz BNCC não traz a camada `autores_referencia`. A função `extract_habilidade` localiza corretamente as entradas pelos novos códigos, e a suíte `test_pipeline.py` passa integralmente (31/31).

---

## 5. O que falta para o fluxo ficar perfeito

Os pontos abaixo estão ordenados por impacto. Nenhum deles impede o pipeline de rodar hoje; eles fecham as arestas que sobraram da migração e blindam o fluxo contra erros silenciosos.

### Prioridade alta

**5.1 — `ARQUITETURA_PIPELINE_V3.md` está desatualizado e contradiz o LEIAME.** Esse documento descreve um pipeline antigo: diz que o A3 é um validador em LLM opcional, que o A4 "humaniza" a prosa, e que os agentes 5 e 6 "não estão implementados". A realidade atual (corretamente descrita no LEIAME) é outra: A3 é normalizador em Python, A4 entrega diffs, A5 é o formatador XML em Python. A ordem-padrão também diverge (o doc diz `1,2,4`; o real é `0,1,2,3,4,5`). É a maior inconsistência documental do projeto. **Ação:** reescrever ou aposentar o arquivo, deixando o LEIAME como fonte única da arquitetura.

**5.2 — Validação fail-fast do código da habilidade.** Hoje, se o briefing trouxer um código inexistente (por exemplo, um `H18` que tenha sobrado, ou um `EM13CHS999` digitado errado), `extract_habilidade` não interrompe a execução: ela injeta a string `"ERRO: habilidade '...' não encontrada"` dentro do prompt do agente, que então gera conteúdo degradado sem ninguém perceber. **Ação:** validar o `habilidade_bncc` no carregamento do briefing — checar o padrão `EM13CHS\d{3}` e a existência da chave na matriz — e abortar com mensagem clara, como já se faz com o schema do CSV.

**5.3 — Confirmar as strings de modelo.** O `pipeline.py` define `claude-opus-4-6` para A1 e A2. O Opus mais recente é o **claude-opus-4-8**; convém verificar se `opus-4-6` ainda é um identificador válido e, em caso negativo, atualizar (ou definir via `IPPI_MODEL_A1`/`IPPI_MODEL_A2`). Sonnet 4.6 e Haiku 4.5 estão corretos.

### Prioridade média

**5.4 — Confirmar o mapeamento do briefing de exemplo.** A apostila de Sociologia/Trabalho teve o código migrado de `H18` (ENEM) para **EM13CHS401** ("novas formas de trabalho ao longo do tempo"), que cobre bem o arco da unidade. Alternativas defensáveis são EM13CHS402 (indicadores de emprego e renda) e EM13CHS404 (múltiplos aspectos do trabalho sobre as gerações). Vale uma confirmação pedagógica de qual habilidade é a âncora.

**5.5 — Documentar o escopo de séries.** A matriz BNCC fornecida cobre apenas 1ª e 2ª séries (32 habilidades, sem 3ª série, por decisão registrada nas observações do próprio JSON). O Mediador e o LEIAME deveriam explicitar isso, para que nenhum professor tente montar uma unidade de 3º ano e receba um erro de habilidade inexistente.

**5.6 — Fixtures de teste ausentes.** As suítes `test_normalizador.py` e `test_formatador.py` falham (49 testes) porque referenciam apostilas de teste que não estão no repositório (ex.: `output/apostila-teste-historia-em1/...`). Não tem relação com a migração, mas mantém o CI vermelho. **Ação:** restaurar os fixtures ou marcá-los como `skip`/`xfail` enquanto não existirem, para que o verde dos testes volte a ser sinal confiável.

**5.7 — Regerar a apostila de ponta a ponta.** A pasta `output/` está vazia no momento. Vale rodar `python pipeline.py --briefing input/apostila-sociologia-trabalho/briefing.json --apostila apostila-sociologia-trabalho` com o código BNCC confirmado, para validar a cadeia inteira (A0→A5) sob a nova matriz e inspecionar um capítulo real.

### Prioridade baixa (higiene)

**5.8 — `matriz-curricular-bncc.csv` na raiz.** É a fonte bruta do Currículo Paulista, não é lida pelo pipeline (que usa os dois JSON) e tem um erro de digitação no cabeçalho (`comeptencia`). Sugiro movê-la para `contexto/fontes/` como proveniência, ou removê-la, para não confundir quem abrir o projeto.

**5.9 — Duas matrizes derivadas da mesma fonte.** `matriz-bncc.json` (com `conteudos_por_area`) e `matriz-conteudosbncc.json` (com `conteudos_por_disciplina`/`conteudos_prioritarios`) repetem dados da mesma origem. Funciona, mas cria risco de divergência se uma for editada e a outra não. Vale uma nota no topo de cada arquivo apontando para a outra, ou um pequeno script de consistência.

**5.10 — Limpeza de artefatos de desenvolvimento.** Há um `xml_to_pdf.py.bak` e diretórios temporários (`.tmp.driveupload`) na árvore. Não afetam o funcionamento, mas vale o `.gitignore` cobri-los.

---

## 6. Roteiro sugerido

1. Reescrever/aposentar `ARQUITETURA_PIPELINE_V3.md` (5.1).
2. Adicionar a validação `EM13CHS\d{3}` + existência na matriz, com abort claro (5.2).
3. Verificar e, se preciso, atualizar as strings de modelo (5.3).
4. Confirmar o código BNCC da apostila-exemplo (5.4) e regerar a apostila inteira para validação ponta a ponta (5.7).
5. Documentar o escopo 1ª/2ª séries no Mediador e no LEIAME (5.5).
6. Restaurar ou marcar os fixtures de teste para zerar as falhas (5.6).
7. Higiene final: CSV-fonte, nota de consistência entre as matrizes, `.gitignore` (5.8–5.10).

Resolvidos 5.1 a 5.3, o fluxo já está sólido e à prova de erro silencioso; os demais itens são acabamento e confiança.
