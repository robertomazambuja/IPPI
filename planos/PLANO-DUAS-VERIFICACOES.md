# Plano — Inserir uma 2ª verificação por bloco (modo local, sem rodar o pipeline)

**Apostila:** `apostila-sociologia-trabalho`
**Objetivo:** cada `<bloco>` dos capítulos formatados passa a ter **2 verificações** em vez de 1.
**Regra de ouro:** não reprocessar o pipeline. Toda a alteração é feita localmente, com agentes do Claude, diretamente sobre os arquivos `formatado/*.xml` e `VERIFICACOES-NECESSARIAS.txt`. Os textos do `core/` e `texto/` **não são tocados**.

---

## 1. O que existe hoje (diagnóstico)

**Escopo real:** 3 arquivos em `formatado/o-mundo-do-trabalho/`:

- `01-01-...teorias-classicas...xml` — 5 blocos (Definir, Classificar, Sequenciar, Comparar, Mapear causalidade)
- `01-02-...transformacoes...xml` — 5 blocos
- `01-03-...trabalho-genero...xml` — 5 blocos

Cada `<bloco>` termina com:

```xml
<sidebar tipo="verificacao" ref="verif-01-01-sN" status="externo">
  <o-que-verificar>Operação: ...
  Micro-habilidade / cabeçalho: "..."
  Conceito-âncora / Exemplo-âncora: ...</o-que-verificar>
</sidebar>
```

E o `<rodape>` tem um `<sidebar tipo="aplicar-agora" ref="aplicar-01-0X">`.

Resultado-alvo: cada bloco com **dois** `<sidebar tipo="verificacao">` (o atual + um novo), mantendo um único `aplicar-agora` por capítulo.

### Pendências pré-existentes que o plano precisa tratar antes de automatizar

1. **Lacunas de JSON:** faltam `verif-01-02-s1.json` e `verif-01-03-s1.json` na pasta `verificacoes/` (os capítulos 02 e 03 têm o item s1 listado no `.txt`, mas o JSON nunca foi gerado). Decidir se entram nesta leva.
2. **Colisão de refs:** o `VERIFICACOES-NECESSARIAS.txt` contém um 4º capítulo (o da `unidade-4-...`, que **não tem XML formatado**) reusando os refs `verif-01-01-s1..s4`. Qualquer renumeração global colidiria. Tratar a `unidade-4` como fora de escopo nesta etapa (ela não tem `formatado/`).

---

## 2. Convenção de numeração (decidir antes de tudo)

Recomendada — **zero renomeação de arquivos existentes**:

| Bloco | Verificação 1 (já existe) | Verificação 2 (nova) |
|-------|---------------------------|----------------------|
| bloco-1 | `verif-01-01-s1` | `verif-01-01-s1-b` |
| bloco-2 | `verif-01-01-s2` | `verif-01-01-s2-b` |
| ... | ... | ... |

O sufixo `-b` lê-se como "a segunda verificação do mesmo bloco". A primeira permanece sem sufixo (= `-a` implícito), então **nenhum JSON nem ref atual muda** — risco mínimo.

Alternativa (mais simétrica, porém exige renomear os 13 JSON existentes): `…-s1a` / `…-s1b`. Só vale a pena se você quiser uniformidade visual total. Recomendo a primeira opção.

---

## 3. Princípio pedagógico da 2ª verificação

A apostila é de aprendizagem algorítmica: cada bloco testa **uma** operação cognitiva (Definir, Classificar, Sequenciar, Comparar, Mapear causalidade, Reconhecer perspectiva, Aplicar). Portanto a 2ª verificação:

- testa a **mesma operação** do bloco (reforço, não nova habilidade);
- usa um **exemplo-âncora / ângulo diferente** do da 1ª, para impedir resposta por memória (mesma lógica da skill `provas-substitutivas-sociologia`);
- ancora-se **somente** em conteúdo já presente naquele bloco do XML (não inventa fato novo).

Essa etapa é regida pela skill **`verificacao-algoritmica-sociologia`** (que por sua vez apoia-se em `provas-sociologia` para distratores e checklist).

---

## 4. Pipeline de execução com agentes Claude

A ideia: **3 etapas automatizadas** (agente lê o formatado, insere os sidebars, numera, anota no `.txt`) + **1 etapa sua** (gerar os JSON) + **QA**. Modelo recomendado por etapa, com a justificativa.

### Etapa 0 — Preparação e backup *(você + 1 comando)*
- Copiar `formatado/` e `VERIFICACOES-NECESSARIAS.txt` para `formatado_backup/` antes de qualquer edição.
- Travar a convenção de numeração (seção 2) e decidir sobre as pendências (seção 1).
- **Modelo:** nenhum / trivial. É só cópia de arquivos.

### Etapa 1 — Agente "Desenhista" das especificações *(Opus)*
Para cada bloco de cada XML, escreve **apenas o texto** `<o-que-verificar>` da 2ª verificação: mesma operação, novo exemplo-âncora extraído do próprio bloco, cabeçalho/micro-habilidade coerentes. Saída intermediária (ex.: um `specs-2a-verificacao.md`), **sem ainda tocar no XML**.
- **Por que Opus:** é a etapa de julgamento pedagógico — garantir que a 2ª verificação não seja redundante com a 1ª e ainda teste a operação certa exige raciocínio fino. É o passo que mais afeta a qualidade final.
- **Skill:** `verificacao-algoritmica-sociologia`.

### Etapa 2 — Agente "Editor de XML" *(Sonnet)*
Insere, em cada bloco, um novo `<sidebar tipo="verificacao" ref="…-b" status="externo">` logo após o sidebar existente, colando o texto produzido na Etapa 1. Preserva indentação, encoding e schema. Ao final, valida que cada XML continua **well-formed** (ex.: `xmllint --noout`).
- **Por que Sonnet:** tarefa mecânica e estrutural (encontrar o fim de cada bloco, inserir nó idêntico em forma). Sonnet é rápido e preciso para edição estruturada; Opus seria desperdício.

### Etapa 3 — Agente "Atualizador do índice" *(Sonnet, ou Haiku se quiser economizar)*
Acrescenta no `VERIFICACOES-NECESSARIAS.txt`, sob cada capítulo, as novas entradas `REF + O QUE VERIFICAR` (na ordem dos blocos) e atualiza a linha `TOTAL`.
- **Por que Sonnet/Haiku:** é cópia estruturada de texto já pronto da Etapa 1 para um formato fixo. Pouco julgamento. Haiku dá conta se o formato for bem especificado; use Sonnet se quiser margem.

> Observação: Etapas 2 e 3 podem ser feitas pelo **mesmo agente Sonnet** numa só sessão, já que ambas só transcrevem a saída da Etapa 1. Separei por clareza de responsabilidade.

### Etapa 4 — Geração dos JSON das verificações *(Opus — feito por você/agente dedicado)*
Para cada novo REF (`…-b`), gerar o arquivo `verificacoes/verif-01-0X-sN-b.json` no schema vigente:
`{tipo, ref, pergunta, alternativas{A,B,C,D}, correta, justificativa}`.
Aproveitar para, se decidido na Etapa 0, preencher as lacunas `verif-01-02-s1` e `verif-01-03-s1`.
- **Por que Opus:** é a parte de maior risco pedagógico — enunciado, 3 distratores plausíveis e tipados, gabarito e justificativa comentada. Qualidade de distrator é exatamente o que a skill `provas-sociologia` exige e onde Opus rende mais.
- **Skill:** `verificacao-algoritmica-sociologia` + `provas-sociologia`.

### Etapa 5 — QA / verificação final *(Sonnet, idealmente como subagente isolado)*
Checklist automatizável:
- cada `<bloco>` tem exatamente 2 `<sidebar tipo="verificacao">`;
- todos os `ref` são únicos no arquivo e batem com nomes de JSON existentes;
- os 3 XML continuam well-formed;
- nº de entradas no `.txt` = nº de sidebars nos XML = nº de JSON na pasta;
- `correta` ∈ {A,B,C,D} e justificativa cobre os 3 distratores em cada JSON novo.
- **Por que Sonnet (subagente):** verificação cruzada barata e objetiva; rodar como subagente evita que o mesmo contexto que escreveu valide a si mesmo.

---

## 5. Resumo de modelos por etapa

| Etapa | Tarefa | Modelo | Motivo |
|-------|--------|--------|--------|
| 0 | Backup + decisões | — | Trivial |
| 1 | Desenhar specs das 2ªs verificações | **Opus** | Julgamento pedagógico |
| 2 | Inserir sidebars no XML | **Sonnet** | Edição estrutural mecânica |
| 3 | Atualizar `VERIFICACOES-NECESSARIAS.txt` | **Sonnet/Haiku** | Transcrição de formato fixo |
| 4 | Gerar JSON das verificações | **Opus** | Distratores + gabarito comentado |
| 5 | QA final | **Sonnet (subagente)** | Verificação cruzada barata |

---

## 6. Por que este desenho (e não "consertar o pipeline")

Reprocessar o pipeline reescreveria o `core/` e poderia alterar texto já revisado dos capítulos. O modo local proposto **só toca**: (a) os `<sidebar>` de verificação dentro do `formatado/*.xml`, (b) o `VERIFICACOES-NECESSARIAS.txt`, e (c) cria novos JSON em `verificacoes/`. O conteúdo didático permanece intacto, e cada etapa é reversível pelo backup da Etapa 0.

## 7. Decisões pendentes para você fechar antes de iniciar

1. Convenção de numeração: sufixo `-b` (recomendado, sem renomear nada) ou par `-a/-b` (renomeia 13 JSON)?
2. Incluir nesta leva os JSON faltantes `verif-01-02-s1` e `verif-01-03-s1`?
3. A `unidade-4-...` (sem XML formatado) fica fora de escopo? (recomendado: sim)
4. Quer que as Etapas 2 e 3 sejam um único agente Sonnet ou dois separados?
