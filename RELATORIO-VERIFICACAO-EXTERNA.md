# Relatório — Externalização da Verificação (Fases 0–5)

**Branch:** `verificacao-externa` (a partir de `modificacoes-agente0`)
**Objetivo:** retirar a geração de verificações de dentro do pipeline e transformá-la em um insumo externo — produzido fora do projeto por agentes qualificados e anexado só na montagem do PDF, exatamente como já acontece com as imagens.

Este documento compila **o que foi feito, como foi feito e os achados ao longo do processo**, servindo de registro e de guia para reproduzir/continuar o trabalho. O plano original está em `PLANO-VERIFICACAO-EXTERNA.md`; aqui está a execução real.

---

## 1. Visão geral do que mudou

Antes, a verificação era gerada **dentro do pipeline**, no Agente 5: o `run_agente5` chamava `gerar_verificacoes()` (uma chamada Haiku por capítulo), que lia o `core.md`, escrevia as perguntas de múltipla escolha e o "Aplicar agora" e injetava tudo como `<sidebar>` pronto no XML. O conteúdo ficava preso ao momento da formatação e à qualidade do Haiku.

Agora o fluxo é:

```
PIPELINE (sem custo de token na verificação)
  A0 → A1 → A2 → A3 → A4 → A5
                              ├─► capitulo.xml  (com MARCADORES, sem conteúdo)
                              │     <sidebar tipo="verificacao" ref="verif-01-01-s3" status="externo">
                              │       <o-que-verificar>…</o-que-verificar>
                              │     </sidebar>
                              └─► VERIFICACOES-NECESSARIAS.txt  (briefing externo)

  ─────────────  FORA DO PIPELINE  ─────────────
  Agentes qualificados leem o .txt e produzem um JSON por marcador:
        verificacoes/verif-01-01-s3.json
        verificacoes/aplicar-01-01.json

VALIDAÇÃO (opcional, antes do PDF)
  python pipeline.py --validar-verif <apostila>

MONTAGEM DO PDF
  python xml_to_pdf.py --unidade <dir> --imagens imagens/ --verificacoes verificacoes/ --versao-professor
        └─ para cada <sidebar … status="externo"> → carrega verificacoes/{ref}.json e renderiza
```

Ponto-chave: o **Agente 5 deixou de chamar o Haiku**. Ele apenas marca, de forma determinística, onde a verificação entra e o que verificar (lendo operação, micro-habilidade, conceito-âncora e exemplo-âncora do `core.md`). A renderização aluno/professor no PDF **não mudou** — só mudou a *fonte* do conteúdo.

---

## 2. Decisões tomadas

Antes de implementar as Fases 2→5, fechamos as decisões da seção 7 do plano, mais uma de produto:

1. **Granularidade do marcador:** *completo* — o `<o-que-verificar>` carrega operação, micro-habilidade/cabeçalho, conceito-âncora e exemplo-âncora, para guiar melhor os agentes externos.
2. **Formato do insumo:** *JSON* (um arquivo por `ref`, fácil de validar).
3. **Falta de verificação no PDF:** *aviso "pendente"* visível só na versão professor; nada na do aluno.
4. **Destino do `verificador.py`:** *manter como gerador de rascunho* opcional (Haiku), acionável sob demanda fora do pipeline.
5. **Estilo do `ref`:** *híbrido* `verif-{cap_id}-s{idx}` / `aplicar-{cap_id}` — prefixo de tipo (como `fig-` das imagens) + vocabulário "s" (seção) do plano. Nome de arquivo auto-explicativo.
6. **Número de alternativas:** *4* (A–D), em vez de 3.

### Achado que motivou o ajuste do `ref`

O plano sugeria `ref` no formato `{unidade}-{capitulo}-s{n}`. Ao inspecionar o código real, descobri que: `cap_id` vem do nome do arquivo no formato `NN-NN` (ex.: `01-01`); cada seção vira `<bloco id="bloco-N">` (N de 1 em diante); e o `core.md` usa `## SEÇÃO N` em correspondência **1:1** com `bloco-N` — é esse alinhamento que `coletar_pontos_verificacao` já assume (indexa por índice de seção e o formatador casa com `bloco.idx`). As imagens já usavam o padrão `fig-{cap_id}-{NN}`. Por isso o `ref` adotado espelha o padrão das imagens, com o número sendo o índice da seção/bloco (mesmo valor nos dois).

---

## 3. Execução, fase a fase

A implementação foi incremental: cada fase deixa o pipeline funcionando e tem um commit próprio, tocando só os arquivos da fase.

### Fase 0 — Preparação (commit `a207074`)

Criada a branch `verificacao-externa` a partir de `modificacoes-agente0`. O `PLANO-VERIFICACAO-EXTERNA.md` estava no diretório mas não versionado; foi adicionado ao repositório e commitado.

### Fase 1 — Pipeline que ignora a verificação (commit `e66f8d1`)

O objetivo era tirar a chamada ao Haiku da geração de verificações dentro do Agente 5. Em `verificador.py`, criei a função `coletar_pontos_verificacao(core_path)`, uma versão puramente determinística (zero chamadas à API) que lê o `core.md` e devolve apenas os pontos onde a verificação externa deve entrar (seção e operação/cabeçalho) e o contexto do "Aplicar agora" — sem gerar a verificação em si. A função antiga `gerar_verificacoes()` (a que chama Haiku) foi mantida no arquivo por ora, decisão a ser revisitada na Fase 5. Em `pipeline.py`, troquei o import e o corpo de `run_agente5` para usar essa nova função em vez da antiga; por enquanto ela só identifica e loga os pontos de verificação — ainda não passa nada para `formatar_capitulo` (isso é a Fase 2). Commitei isso, tocando só esses dois arquivos.

No meio do caminho, encontrei e resolvi um problema de infraestrutura: o sandbox bash estava lendo versões com cache truncado desses dois arquivos (faltavam as últimas linhas), o que teria corrompido um commit feito por bash. Diagnostiquei comparando contra a visão real dos arquivos (via Read tool e `git show HEAD`) e contra a estrutura de funções (via Grep), localizei a truncagem exatamente no final de cada arquivo, e corrigi reescrevendo o conteúdo correto diretamente. Confirmei com `py_compile` (ambos compilam) e `git diff` (mostrando exatamente as mudanças pretendidas, nada mais) antes de commitar.

Estado ao fim da Fase 1: branch com 2 commits acima da base, pipeline rodando sem custo de token na verificação, ainda sem marcadores no XML.

### Fase 2 — Marcadores no XML (commit `9be0986`)

Três mudanças, validadas num capítulo real:

- Em `verificador.py`, ampliei `coletar_pontos_verificacao` para devolver **contexto completo** por seção elegível (`tipo_operacao`, `cabecalho`, `conceito_central`, `exemplo_ancola`) e um contexto do "Aplicar agora" (`operacao_principal`, `pergunta_do_capitulo`, `sintese_final`, `exemplo_ancola_principal`, este último da seção principal segundo a mesma heurística que `_build_prompt` já usava).
- Em `formatador.py`, criei `render_marcador_verificacao()` e `render_marcador_aplicar()`, que emitem o **marcador** `<sidebar tipo="…" ref="…" status="externo"><o-que-verificar>…</o-que-verificar></sidebar>` no lugar onde antes entrava a sidebar pronta. Novos parâmetros `pontos_verif`/`aplicar_ctx` em `formatar_capitulo`/`render_xml`/`render_bloco`; o fluxo legado (sidebar pronta via Haiku) ficou como fallback. O `ref` é gerado onde o `cap_id` e o `bloco.idx` já existem (junto da geração do `ref` das imagens).
- Em `pipeline.py`, `run_agente5` passou a repassar `pontos_verif`/`aplicar_ctx` ao `formatar_capitulo` (antes passava `None`).

Validação: gerei o XML de um capítulo real, confirmei XML bem-formado, 5 marcadores (`verif-01-01-s1..s4` + `aplicar-01-01`), `ref` únicos, `<o-que-verificar>` preenchido e nenhum conteúdo pronto vazando.

### Fase 3 — Briefing externo (commit `3e61bbd`)

Em `pipeline.py`, criei `gerar_lista_verificacoes(apostila_dir)`, espelhando `gerar_lista_imagens()`: varre `formatado/**/*.xml`, extrai os `<sidebar status="externo">` e escreve `VERIFICACOES-NECESSARIAS.txt` com instruções, o schema de exemplo e, por capítulo, o `ref` + "o que verificar" de cada marcador. A função é chamada no fim de `run_pipeline`, ao lado da lista de imagens (só quando o A5 roda).

Validação: rodei a função sobre um diretório de teste montado com o XML da Fase 2 e conferi o `.txt` (5 marcadores, formato idêntico ao `IMAGENS-NECESSARIAS.txt`).

### Fase 4 — Inserção no PDF (commit `9ca183c`)

Em `xml_to_pdf.py`:

- Novo argumento `--verificacoes <pasta>`, resolvido para `verifdir` e propagado por `render_capitulo` → `render_bloco` → `render_secao` → `render_sb` (espelhando o `imdir` das imagens).
- Em `render_sb`, quando a sidebar tem `status="externo"`, chamo `render_sb_externo()`, que carrega `verificacoes/{ref}.json` e o converte (`_json_to_elem_verif` / `_json_to_elem_aplicar`) para os **mesmos elementos** que `sb_verif`/`sb_aplicar` já consomem — preservando integralmente a lógica aluno/professor.
- Se o arquivo do `ref` não existir (ou o JSON for inválido), `_sb_pendente()` rende um aviso "Verificacao pendente" **só na versão professor**; na do aluno não rende nada.

Validação: chamei `render_capitulo` nas duas versões (com o `weasyprint` stubado, pois não preciso dele para gerar HTML), usando uma pasta `verificacoes/` de teste com alguns refs faltando de propósito. Resultado: professor com pergunta + gabarito + enunciado + resposta + 3 avisos "pendente"; aluno só com pergunta + enunciado, zero gabarito/resposta/pendente.

### Mudança de 4 alternativas (commit `6437643`)

A pedido, troquei de 3 para **4 alternativas (A–D)**. O renderizador do PDF já era flexível (itera as alternativas presentes no JSON), então os pontos a mudar foram: o briefing em `gerar_lista_verificacoes` (`alternativas{A,B,C,D}`), o schema de exemplo no `PLANO-VERIFICACAO-EXTERNA.md` (com "D") e o gerador-rascunho `verificador.py` (loop A–D no render, system prompt "4 alternativas / 1 correta + 3 distratores", e o formato no `_build_prompt`).

Achado: ao commitar, o `PLANO-…md` não entrou de primeira — a cache do mount mostrava o doc sem alterações para o `git`. Resolvido com refresh de cache (ver seção 6) e `git commit --amend` para incluir o doc.

### Fase 5 — Validador, gerador de rascunho e docs (commit `af40738`)

- **Validador:** `validar_verificacoes(apostila_dir, verifdir)` em `pipeline.py` cruza os `ref` marcados (`status="externo"`) nos XMLs com os JSON da pasta e reporta pendências: arquivo ausente, JSON inválido e schema fora do esperado (verificação: exatamente `A,B,C,D` não-vazias + `correta` em `{A,B,C,D}` + `pergunta`; aplicar-agora: `enunciado`). `justificativa`/`resposta_comentada` ausentes geram **aviso** (não erro). CLI: `python pipeline.py --validar-verif <apostila> [--verif-dir <pasta>]`, com exit code 0/1.
- **Gerador de rascunho:** `gerar_rascunhos(core_path, client)` em `verificador.py` produz JSON no schema externo (`verif-{cap_id}-s{idx}.json` / `aplicar-{cap_id}.json`), reusando a chamada Haiku. CLI sob demanda: `python verificador.py <core|glob> --out verificacoes`. **Fora do pipeline** — é só um ponto de partida automático para humanos refinarem.
- **Docs:** `LEIAME.md` atualizado (A5 não gera mais verificação; verificação é insumo externo; fluxo, comandos, 4 alternativas).

Achado (bug real pego na validação): o `validar_verificacoes` usava `json.loads`, mas o `pipeline.py` **não importava `json`** no topo. A validação acusou `name 'json' is not defined` em todos os refs; corrigi com `import json` local na função (mesmo padrão do `import xml.etree.ElementTree as ET` já usado). Depois do fix, o validador acusou corretamente 3-alternativas, `correta` inválida e arquivo ausente, e retornou OK só com a pasta completa.

---

## 4. Formato exato do insumo (o que o pipeline entende)

Um arquivo JSON por marcador, em UTF-8, salvo na pasta passada em `--verificacoes` (padrão do validador: `output/<apostila>/verificacoes/`), com o nome **exatamente igual ao `ref`** do `VERIFICACOES-NECESSARIAS.txt`.

Tipo `verificacao`:

```json
{
  "tipo": "verificacao",
  "ref": "verif-01-01-s1",
  "pergunta": "texto da pergunta",
  "alternativas": { "A": "…", "B": "…", "C": "…", "D": "…" },
  "correta": "B",
  "justificativa": "por que a correta é correta (gabarito)"
}
```

Tipo `aplicar-agora`:

```json
{
  "tipo": "aplicar-agora",
  "ref": "aplicar-01-01",
  "enunciado": "caso novo + o que o aluno deve fazer",
  "resposta_comentada": "resposta modelo"
}
```

Regras que o validador exige (quebrar gera erro): nome `{ref}.json`; em `verificacao`, `alternativas` com **exatamente** as quatro chaves `A,B,C,D` não-vazias, `correta` ∈ `{A,B,C,D}`, `pergunta` não-vazia; em `aplicar-agora`, `enunciado` não-vazio. Recomendados (ausência = aviso): `justificativa` e `resposta_comentada` — gabarito/resposta que saem **só na versão professor**.

Detalhe importante: na prática quem casa o insumo com o XML é o **nome do arquivo** (`ref`); os campos `tipo`/`ref` dentro do JSON são documentação (o renderizador usa o `tipo` do marcador), mas devem ser incluídos. `correta` define a alternativa certa; o que o professor vê impresso como gabarito é o texto da `justificativa`.

---

## 5. Como testar sem gastar tokens de API

Toda a funcionalidade nova é Python puro, zero token de API. Como o `output/` já tem `texto/` e `core/` gerados, dá para testar tudo sem custo:

1. Regenerar os XMLs com marcadores + briefing (só o A5, sem LLM):
   `python pipeline.py input/apostila-sociologia-trabalho/instrucoes.csv --agentes 5 --force`
2. Produzir as verificações: ler `output/apostila-sociologia-trabalho/VERIFICACOES-NECESSARIAS.txt` e criar um `{ref}.json` por marcador em `output/apostila-sociologia-trabalho/verificacoes/`. Isso pode ser feito **num chat do Claude** (assinatura, não API) — o chat faz o papel do "agente externo".
3. Validar: `python pipeline.py --validar-verif apostila-sociologia-trabalho`
4. Montar o PDF: `python xml_to_pdf.py --unidade output/apostila-sociologia-trabalho/formatado/<unidade> --verificacoes output/apostila-sociologia-trabalho/verificacoes --versao-professor` (e `--versao-aluno`).

**Evitar (custa API):** rodar `--agentes` com 0/1/2/4 (reprocessa os LLM) e o gerador de rascunho `python verificador.py … --out` (Haiku). Criar o cliente Anthropic precisa da chave no `.env`, mas só consome token quando um agente de LLM de fato chama a API — o A5 não chama.

---

## 6. Achados de infraestrutura (e como foram resolvidos)

Vários problemas eram do ambiente, não do código — registro aqui porque podem reaparecer.

**Cache de tamanho truncada no mount do sandbox.** O bash lia os arquivos cortados no *tamanho antigo*: `grep` achava as edições novas, mas `stat -c%s` reportava o tamanho velho e qualquer leitura (`cat`, `wc`, `python read`) parava nesse limite, descartando o que eu havia adicionado no fim. Isso fazia o `py_compile` falhar com `SyntaxError` no fim do arquivo e, pior, arriscava commits truncados. `touch` e `sync` não resolviam. **Solução:** um *rename round-trip* (`mv f f.r && mv f.r f`) no mesmo filesystem refresca a cache de conteúdo — depois disso leituras e `py_compile` veem o arquivo inteiro. Sempre confirmei antes de commitar que o blob staged terminava certo (`git show :arquivo | tail`/`wc -l`).

**Cache de metadado fazendo o `git` não ver edições.** Numa ocasião, um arquivo editado (o `PLANO-…md`) não aparecia como modificado para o `git` — a cache do mount mostrava a versão antiga. **Solução:** o mesmo rename round-trip, depois `git status` confirmando o diff, e `git commit --amend` para anexar a mudança que tinha ficado de fora.

**Locks órfãos do git.** O mount recusa `unlink` (`Operation not permitted`), então o git deixava `.git/index.lock` e `.git/HEAD.lock` para trás, bloqueando commits seguintes. `rm` não removia. **Solução:** como o mount permite `rename`, mover o lock para fora do caminho (`mv .git/index.lock .git/index.lock.stale`) antes de cada operação de git. Os avisos "unable to unlink … tmp_obj" durante `git add`/`commit` são inofensivos — os objetos são gravados; o `git show`/`git log` confirmam.

**venv em formato Windows.** O `.venv` do projeto é Windows (`Scripts/`, não `bin/`), inutilizável no sandbox Linux. Para validar, instalei as dependências necessárias (`anthropic`) no Python do sandbox e, para gerar HTML sem `weasyprint`, stubei o módulo no teste.

**Bug real de código:** `json` não importado em `pipeline.py` (pego pela validação do validador). Corrigido.

---

## 7. Estado atual

Branch `verificacao-externa`, 7 commits acima da base `modificacoes-agente0`:

```
af40738  Fase 5: validador, gerador de rascunho e documentacao
6437643  Verificacao: 4 alternativas (A-D) em vez de 3
9ca183c  Fase 4: xml_to_pdf insere verificacao externa via --verificacoes
3e61bbd  Fase 3: gera VERIFICACOES-NECESSARIAS.txt (briefing externo)
9be0986  Fase 2: A5 emite marcadores de verificacao externa no XML
e66f8d1  Fase 1: Agente 5 deixa de chamar Haiku para verificacao
a207074  Fase 0: adiciona plano de verificacao externa ao repositorio
```

Cada commit tocou só os arquivos da sua fase. O pipeline roda sem custo de token na verificação; os marcadores e o briefing são emitidos pelo A5; o conteúdo entra na montagem do PDF a partir da pasta `verificacoes/`; o validador confere pendências antes do PDF.

**Arquivos tocados ao todo:** `verificador.py`, `formatador.py`, `pipeline.py`, `xml_to_pdf.py`, `LEIAME.md`, `PLANO-VERIFICACAO-EXTERNA.md`.

**Próximos passos opcionais (não feitos):** merge em `modificacoes-agente0`; versionar (ou não) os insumos de teste em `output/.../verificacoes/`.
