# Plano — Inserir uma 2ª verificação por bloco (modo local, sem rodar o pipeline)

**Aplicabilidade:** qualquer apostila com a arquitetura padrão — uma pasta `formatado/` com os XML dos capítulos e uma pasta `verificacoes/` com os JSON. O plano é genérico; o agente que o executa **descobre** a estrutura da apostila-alvo antes de agir.
**Objetivo:** cada `<bloco>` dos capítulos formatados passa a ter **2 verificações** em vez de 1.
**Regra de ouro:** não reprocessar o pipeline. Toda alteração é local, feita por agentes do Claude diretamente sobre os arquivos `formatado/*.xml` e o índice de verificações necessárias. Os textos de `core/` e `texto/` **não são tocados**.

---

## 1. Arquitetura esperada (o que o agente deve reconhecer)

Em qualquer apostila no padrão, espera-se:

- `formatado/<unidade>/<NN-MM-...>.xml` — um XML por capítulo. Dentro de `<corpo>`, vários `<bloco id="bloco-N" operacao="...">`. Cada bloco termina com **um** sidebar de verificação:

```xml
<sidebar tipo="verificacao" ref="verif-<UU>-<CC>-s<N>" status="externo">
  <o-que-verificar>Operação: ...
  Micro-habilidade / cabeçalho: "..."
  Conceito-âncora / Exemplo-âncora: ...</o-que-verificar>
</sidebar>
```

- O `<rodape>` traz um `<sidebar tipo="aplicar-agora" ref="aplicar-<UU>-<CC>">`.
- `verificacoes/` — JSON nomeados pelo `ref` (`verif-...json`, `aplicar-...json`).
- Um índice de verificações necessárias (arquivo texto, tipo `VERIFICACOES-NECESSARIAS.txt`) listando, por capítulo, cada `REF` + `O QUE VERIFICAR` e um `TOTAL`.

Resultado-alvo: cada bloco com **dois** `<sidebar tipo="verificacao">` (o atual + um novo), mantendo um único `aplicar-agora` por capítulo.

---

## 2. Etapa 0 — Descoberta e diagnóstico da apostila-alvo *(o primeiro agente faz isto)*

Antes de qualquer edição, o agente que executa o plano deve **inspecionar a apostila indicada** e produzir um mini-relatório, sem assumir nada de cor:

1. **Inventariar o escopo:** listar todos os `formatado/**/*.xml`. Só entram capítulos que tenham XML em `formatado/` — capítulos que existam apenas em `core/`/`texto/` ficam **fora de escopo** (não há onde inserir o sidebar).
2. **Mapear blocos e verificações atuais:** para cada XML, contar `<bloco>` e os `<sidebar tipo="verificacao">` existentes; registrar os `ref` em uso.
3. **Detectar lacunas:** refs listados no índice ou nos XML que **não têm JSON** correspondente em `verificacoes/`. Decidir se entram nesta leva.
4. **Detectar colisões de ref:** o mesmo `ref` reutilizado por mais de um capítulo (acontece quando duas unidades começam em `01-01`). Resolver o esquema de numeração antes de automatizar, para não sobrescrever.
5. **Backup:** copiar `formatado/` e o índice para `*_backup/` antes de editar.

**Modelo:** Sonnet. É leitura/contagem estruturada com pouco julgamento. (Pode ser Opus se quiser que o mesmo agente já emende na Etapa 1.)

---

## 3. Convenção de numeração (decidir na Etapa 0)

Recomendada — **zero renomeação de arquivos existentes**:

| Bloco | Verificação 1 (já existe) | Verificação 2 (nova) |
|-------|---------------------------|----------------------|
| bloco-1 | `verif-<UU>-<CC>-s1` | `verif-<UU>-<CC>-s1-b` |
| bloco-2 | `verif-<UU>-<CC>-s2` | `verif-<UU>-<CC>-s2-b` |
| ... | ... | ... |

O sufixo `-b` lê-se como "a segunda verificação do mesmo bloco". A primeira permanece sem sufixo (= `-a` implícito): **nenhum JSON nem ref atual muda** — risco mínimo, e funciona mesmo quando há colisão de refs entre unidades.

Alternativa (par `-a/-b`, mais simétrica) exige renomear todos os JSON existentes; só vale a pena se quiser uniformidade visual total. Recomendo o sufixo `-b`.

---

## 4. Princípio pedagógico da 2ª verificação

Apostila de aprendizagem algorítmica: cada bloco testa **uma** operação cognitiva (Definir, Classificar, Sequenciar, Comparar, Mapear causalidade, Reconhecer perspectiva, Aplicar). Portanto a 2ª verificação:

- testa a **mesma operação** do bloco (reforço, não nova habilidade);
- usa um **exemplo-âncora / ângulo diferente** do da 1ª, para impedir resposta por memória (mesma lógica da skill `provas-substitutivas-sociologia`);
- ancora-se **somente** em conteúdo já presente naquele bloco do XML (não inventa fato novo).

Etapa regida pela skill **`verificacao-algoritmica-sociologia`** (que se apoia em `provas-sociologia` para distratores e checklist).

---

## 5. Pipeline de execução com agentes Claude

Três etapas automatizadas (descobrir → inserir → indexar) + uma etapa sua (gerar os JSON) + QA. Modelo recomendado por etapa, com justificativa.

### Etapa 1 — Agente "Desenhista" das especificações *(Opus)*
Para cada bloco de cada XML em escopo, escreve **apenas o texto** `<o-que-verificar>` da 2ª verificação: mesma operação, novo exemplo-âncora extraído do próprio bloco, cabeçalho/micro-habilidade coerentes. Saída intermediária (ex.: `specs-2a-verificacao.md`), **sem ainda tocar no XML**.
- **Por que Opus:** etapa de julgamento pedagógico — garantir que a 2ª verificação não seja redundante com a 1ª e ainda teste a operação certa. É o passo que mais afeta a qualidade final.
- **Skill:** `verificacao-algoritmica-sociologia`.

### Etapa 2 — Agente "Editor de XML" *(Sonnet)*
Insere, em cada bloco, um novo `<sidebar tipo="verificacao" ref="…-b" status="externo">` logo após o sidebar existente, colando o texto da Etapa 1. Preserva indentação, encoding e schema. Ao final valida que cada XML segue **well-formed** (ex.: `xmllint --noout`).
- **Por que Sonnet:** tarefa mecânica e estrutural (achar o fim de cada bloco, inserir nó idêntico em forma). Opus seria desperdício.

### Etapa 3 — Agente "Atualizador do índice" *(Sonnet, ou Haiku para economizar)*
Acrescenta no índice de verificações necessárias, sob cada capítulo, as novas entradas `REF + O QUE VERIFICAR` (na ordem dos blocos) e atualiza o `TOTAL`.
- **Por que Sonnet/Haiku:** transcrição de texto já pronto para um formato fixo, pouco julgamento.

> Etapas 2 e 3 podem ser um **único agente Sonnet** numa só sessão, já que ambas só transcrevem a saída da Etapa 1. Separadas por clareza de responsabilidade.

### Etapa 4 — Geração dos JSON das verificações *(Opus — feito por você/agente dedicado)*
Para cada novo REF (`…-b`), gerar `verificacoes/verif-...-b.json` no schema vigente:
`{tipo, ref, pergunta, alternativas{A,B,C,D}, correta, justificativa}`.
Aproveitar para preencher também as lacunas detectadas na Etapa 0, se decidido.
- **Por que Opus:** parte de maior risco pedagógico — enunciado, 3 distratores plausíveis e tipados, gabarito e justificativa comentada. É onde Opus rende mais.
- **Skill:** `verificacao-algoritmica-sociologia` + `provas-sociologia`.

### Etapa 5 — QA / verificação final *(Sonnet, idealmente como subagente isolado)*
Checklist automatizável:
- cada `<bloco>` tem exatamente 2 `<sidebar tipo="verificacao">`;
- todos os `ref` são únicos por arquivo e batem com nomes de JSON;
- os XML continuam well-formed;
- nº de entradas no índice = nº de sidebars nos XML = nº de JSON na pasta;
- `correta` ∈ {A,B,C,D} e a justificativa cobre os 3 distratores em cada JSON novo.
- **Por que Sonnet (subagente):** verificação cruzada barata e objetiva; rodar como subagente evita que o mesmo contexto que escreveu valide a si mesmo.

---

## 6. Resumo de modelos por etapa

| Etapa | Tarefa | Modelo | Motivo |
|-------|--------|--------|--------|
| 0 | Descoberta + diagnóstico + backup | **Sonnet** | Leitura/contagem estruturada |
| 1 | Desenhar specs das 2ªs verificações | **Opus** | Julgamento pedagógico |
| 2 | Inserir sidebars no XML | **Sonnet** | Edição estrutural mecânica |
| 3 | Atualizar índice de verificações | **Sonnet/Haiku** | Transcrição de formato fixo |
| 4 | Gerar JSON das verificações | **Opus** | Distratores + gabarito comentado |
| 5 | QA final | **Sonnet (subagente)** | Verificação cruzada barata |

---

## 7. Por que este desenho (e não "consertar o pipeline")

Reprocessar o pipeline reescreveria o `core/` e poderia alterar texto já revisado. O modo local só toca: (a) os `<sidebar>` de verificação dentro de `formatado/*.xml`, (b) o índice de verificações necessárias, e (c) cria novos JSON em `verificacoes/`. O conteúdo didático permanece intacto, e cada etapa é reversível pelo backup da Etapa 0.

## 8. Decisões a fechar antes de iniciar (por apostila)

1. Convenção de numeração: sufixo `-b` (recomendado, sem renomear nada) ou par `-a/-b` (renomeia os JSON)?
2. Incluir nesta leva as lacunas de JSON detectadas na Etapa 0?
3. Capítulos sem XML formatado ficam fora de escopo? (recomendado: sim)
4. Etapas 2 e 3 como um único agente Sonnet ou dois separados?
