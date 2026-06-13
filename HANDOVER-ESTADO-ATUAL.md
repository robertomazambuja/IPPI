# HANDOVER — Estado atual do pipeline IPPI e próximas intervenções

**Data:** 13/06/2026  
**Escopo:** análise completa de `pipeline.py`, `normalizador.py`, `formatador.py`, `verificador.py`, skills, orientações e relatório de eficiência anterior.  
**Propósito:** instruir outro agente de IA a compreender o projeto e implementar as duas modificações pendentes (E6 e E9 do relatório de eficiência).

---

## 1. Como entender este projeto antes de intervir

Leia os arquivos nesta ordem. Cada um resolve uma camada diferente de compreensão.

### 1.1 O que o projeto faz (5 minutos)

Leia primeiro:
- `LEIAME.md` — descrição funcional do pipeline, arquitetura de pastas, fluxo dos agentes, bugs conhecidos e histórico de decisões.

### 1.2 O diagnóstico que orientou as mudanças recentes

Leia em seguida:
- `RELATORIO-EFICIENCIA-E-QUALIDADE.md` — auditoria completa escrita em 12/06/2026. Contém o diagnóstico de ineficiência (seções 2 e 3) e as recomendações E1–E10 e R-Q1–R-Q7. **Este documento é o mapa de origem de todas as decisões de refatoração recentes.** Leia-o inteiro antes de tocar em qualquer código.

### 1.3 O código central

Leia por inteiro, na ordem:
1. `pipeline.py` — orquestrador completo. Contém a lógica de todos os agentes, o loop agêntico `run_agent()`, o builder de system prompts, o parser de CSV, e a lógica de paralelização.
2. `normalizador.py` — substituto Python do antigo Agente 3 (LLM). Aplica 4 normalizações determinísticas em HTML comments.
3. `formatador.py` — substituto Python do antigo Agente 5 (LLM). Converte `texto.md` em XML para InDesign.
4. `verificador.py` — gerador de verificações fechadas e "Aplicar agora". Uma chamada Haiku por capítulo, sem loop agêntico.

### 1.4 As skills e orientações dos agentes

Leia para entender os contratos entre agentes:
- `skills/agente1-skill.md` — formato do core.md (campos YAML, estrutura por operação)
- `skills/agente2-skill.md` — formato do texto.md (HTML comments, blocos por operação)
- `skills/agente3-skill.md` — as 4 normalizações (já implementadas em normalizador.py, mas a skill é a especificação)
- `skills/agente4-skill.md` — polidor de prosa, retorna JSON de diffs
- `skills/agente5-skill.md` — especificação do XML (já implementada em formatador.py)

Opcionalmente, leia os outputs reais em `output/apostila-teste-historia-em1/` para entender o formato concreto do que os agentes produzem.

---

## 2. Estado atual do projeto (o que já foi implementado)

O relatório de eficiência listou 10 recomendações (E1–E10). A tabela abaixo mostra o que está feito e onde encontrar a evidência no código.

| Item | Descrição | Status | Evidência no código |
|------|-----------|--------|---------------------|
| E1 | Logging de usage (input, output, cache) | ✅ Implementado | `pipeline.py`: `_write_usage_csv()`, `USAGE_CSV`, acumulação em `run_agent()` linhas 317–321 |
| E2-A3 | Agente 3 virou Python | ✅ Implementado | `normalizador.py` — `run_agente3()` chama `normalizar_texto()`, sem LLM |
| E2-A5 | Agente 5 virou Python | ✅ Implementado | `formatador.py` — `run_agente5()` chama `formatar_capitulo()`, sem LLM |
| E3 | Matrizes fatiadas antes dos agentes | ✅ Implementado | `pipeline.py`: `extract_habilidade()` usada em `run_agente0()` e `run_agente1()` |
| E4 | Arquivos injetados no user_message | ✅ Implementado (parcial) | A0, A1, A2, A4 injetam conteúdo diretamente; cores anteriores do A1 ainda via `read_file` (pendente E9) |
| E5 | User messages não induzem releitura da skill | ✅ Implementado | A0: "não é necessário ler os arquivos"; A1: "não é necessário ler esses arquivos"; A4: "já está no seu system prompt" |
| E6 | Cache no histórico de mensagens | ❌ **Não implementado** | `run_agent()` tem cache só no system prompt (linha 292–296). Histórico de mensagens enviado sem cache a cada iteração. |
| E7 | Modelo configurável por agente | ✅ Implementado | `pipeline.py` linhas 59–72: `_DEFAULT_MODELS` com A0=Sonnet, A1=Opus, A2=Opus, A3=None, A4=Sonnet, A5=None. Sobrescrita por `IPPI_MODEL_A{n}`. |
| E8 | A4 retorna diffs, não reescreve arquivo inteiro | ✅ Implementado | `pipeline.py`: `_apply_diffs()` + contrato no user_message do A4 |
| E9 | Cores anteriores como sumário, não leitura completa | ❌ **Não implementado** | `run_agente1()`: comentário explícito "serão otimizados na Fase 2 com E9". Variável `arquivos_cores` ainda instrui read_file dos cores completos. |
| E10 | Paralelização de capítulos nos estágios 2–5 | ✅ Implementado | `pipeline.py`: `ThreadPoolExecutor`, flag `--workers`, `_run_cap_stages_2_5()` |

**Resumo:** 8 de 10 recomendações implementadas. Faltam E6 e E9.

---

## 3. As duas modificações pendentes

### 3.1 E9 — Cores anteriores como sumário em `run_agente1()`

**Problema atual (pipeline.py, função `run_agente1()`):**

O Agente 1 precisa consultar os capítulos anteriores da mesma unidade para manter coerência de progressão, evitar repetição de autores e garantir encadeamento. Hoje, o pipeline lista os caminhos dos cores anteriores no user_message e instrui o agente a lê-los via `read_file`. Para o capítulo N da unidade, isso significa N-1 leituras de arquivos completos.

Um core.md tem tipicamente 3–5 KB. Com 5 capítulos por unidade, o capítulo 5 paga 4 leituras de core (~12–16K tokens), quando precisa de no máximo três campos de cada: `SINTESE_FINAL`, `ENCADEAMENTO` e autores já usados.

**O que precisa ser feito:**

1. Criar a função `extract_core_summary(core_path: Path) -> str` em `pipeline.py`. Ela lê o core.md com Python puro (sem LLM) e extrai os três campos. O formato dos campos no core.md segue o padrão YAML dentro de blocos de código, como em `agente1-skill.md`. Antes de implementar o regex definitivo, leia um core real em `output/apostila-teste-historia-em1/core/` para ver o formato exato dos campos.

2. Substituir, em `run_agente1()`, a lógica que monta `cores_anteriores_section` e `arquivos_cores` pela chamada à função acima. O resultado deve ser um bloco de texto compacto (50–150 tokens no total) injetado diretamente no user_message, sem `read_file`.

3. Adicionar ao user_message do A1 a instrução: "Os sumários dos capítulos anteriores já estão acima — não leia os cores completos."

**Localização exata no código:**

Em `run_agente1()`, linhas 505–523 constroem `cores_anteriores_section` e `arquivos_cores`. Linhas 571 e seguintes montam o user_message e incluem `{arquivos_cores}`. Essas são as linhas a modificar.

**Validação:** após implementar, rodar com `--cap 5` numa apostila com 5+ capítulos e verificar no CSV de usage que `input_tokens` do A1 caiu em relação a uma execução anterior com a mesma apostila.

---

### 3.2 E6 — Cache no histórico de mensagens em `run_agent()`

**Problema atual (pipeline.py, função `run_agent()`):**

O loop agêntico roda 3–4 iterações para A1, A2 e A4. Em cada iteração, toda a lista `messages` é reenviada à API. A primeira mensagem — o user_message com os arquivos injetados — tem 4–10K tokens. Ela é reenviada como input não-cacheado a cada iteração.

O system prompt já tem `cache_control: ephemeral` (linha 292–296 de `run_agent()`). O histórico não tem.

A API da Anthropic suporta `cache_control: ephemeral` em blocos de mensagem do histórico, da mesma forma que no system prompt. O trecho que mais vale cachear é o user_message original (primeira mensagem), que é o maior e não muda entre iterações.

**O que precisa ser feito:**

Criar a função auxiliar `_with_cache(messages: list) -> list` em `pipeline.py`. Ela recebe a lista de mensagens atual e retorna uma cópia com `cache_control: ephemeral` adicionado ao último bloco do tipo `user`. A lógica precisa lidar com dois formatos de conteúdo:

- `content` como string simples → converter para lista com um bloco `{"type": "text", "text": ..., "cache_control": {"type": "ephemeral"}}`
- `content` como lista de blocos → adicionar `cache_control` ao último item da lista

Na chamada ao stream dentro do loop (linha ~287 de `run_agent()`), substituir `messages=messages` por `messages=_with_cache(messages)`.

**Ressalva:** a API exige mínimo de ~1.024 tokens no trecho a cachear para que o cache seja criado. O user_message do A1 (com principios + disciplina + entrada de habilidade + andaime) tipicamente tem 3–6K tokens, dentro do limiar. O user_message do A2 (core + disciplina) tem 2–4K tokens. O A4 (texto completo) tem 3–5K tokens. Todos qualificam. As mensagens de tool_result das iterações intermediárias são menores e podem não qualificar — isso é esperado e não prejudica.

**Validação:** após implementar, rodar um capítulo e verificar que `cache_read_tokens` > 0 nas iterações 2+ do A1, A2 e A4 no CSV de usage. Se `cache_read_tokens` permanecer 0 para esses agentes, o bloco cacheado pode não estar atingindo o limiar — inspecionar o tamanho real dos user_messages com um `log_print` temporário.

---

## 4. O que NÃO fazer

- **Não altere `normalizador.py`, `formatador.py` ou `verificador.py`.** Esses três módulos estão corretos e completos. Qualquer bug de output do A3/A5 deve ser investigado nas skills ou no texto produzido pelo A2, não nesses parsers.

- **Não altere os modelos configurados em `_DEFAULT_MODELS`.** A1 e A2 em Opus é uma decisão deliberada — são os agentes que produzem o conteúdo pedagógico central do produto.

- **Não altere o formato do user_message do A2.** O A2 recebe o core e o contexto disciplinar já injetados — está correto. Não há E4 pendente para o A2.

- **Não tente cachear o system prompt separadamente** — ele já tem `cache_control: ephemeral` implementado. E6 trata apenas do histórico de mensagens.

- **Não crie novos agentes LLM** para cobrir lacunas que podem ser resolvidas em Python. O padrão do projeto é: se a tarefa é determinística ou estruturalmente especificada, vira código.

---

## 5. Contexto pedagógico mínimo para não quebrar a lógica

O pipeline produz apostilas didáticas de Ciências Humanas para o Ensino Médio orientadas por habilidades do ENEM. O princípio central é que cada capítulo executa um **algoritmo de ensino**: uma sequência de operações cognitivas elementares (Definir, Classificar, Comparar, Sequenciar, Mapear causalidade, Reconhecer perspectiva, Aplicar) aplicadas a um conteúdo específico.

O fluxo de dados é:
```
CSV (professor) → Core.md (Agente 1) → Texto.md (Agente 2) → [normalizar] → [polir] → XML (formatador)
```

O `core.md` é a estrutura interna: campos YAML com operações, exemplos âncora, e metadados pedagógicos. O `texto.md` é a prosa com HTML comments invisíveis que carregam a estrutura. O XML final é o entregável para diagramação no InDesign.

As modificações E6 e E9 são puramente de infraestrutura — não afetam o conteúdo gerado, apenas a eficiência com que os tokens chegam à API.

---

## 6. Checklist de entrega

Antes de considerar as modificações concluídas:

- [ ] `extract_core_summary()` criada e testada manualmente em pelo menos um core.md real
- [ ] `run_agente1()` não usa mais `read_file` para cores anteriores
- [ ] `run_agente1()` instrui explicitamente o agente a não ler cores completos
- [ ] `_with_cache()` criada e aplicada em `run_agent()`
- [ ] Rodar `python pipeline.py input/apostila-teste-historia-em1/instrucoes.csv --cap 1` sem erros
- [ ] CSV de usage mostra `cache_read_tokens > 0` para A1 ou A2 (confirma E6)
- [ ] Para uma apostila com 3+ capítulos: `input_tokens` do A1 no capítulo 3 é menor que numa execução anterior (confirma E9)
- [ ] Nenhuma regressão nos outputs: `output/.../texto/` e `output/.../formatado/` continuam sendo gerados corretamente
