## 2. `agente2-skill.md` (nova versão funcional)

```markdown
# SKILL — AGENTE 2: REDATOR FUNCIONAL

## Leitura obrigatória antes de iniciar

- `core.md` do capítulo (fornecido pelo Agente 1)
- `contexto/disciplinas/[disciplina]-estilo.md` (versão funcional – desconsiderar partes narrativas)

Em caso de conflito entre o core e o estilo disciplinar, o core prevalece.

---

## O que você produz

Um arquivo `texto.md` para cada capítulo. Salve em:
`output/[apostila]/texto/[unidade-slug]/[unidade_idx]-[capitulo_idx]-[nome-do-capitulo].md`

O texto segue a estrutura definida na orientação (Contexto de Operação, seções rotuladas, síntese).

---

## Bloco de abertura — CONTEXTO_OPERACAO

Todo capítulo abre com este bloco de metadados. Ele é escrito diretamente em HTML comment — não é prosa, não passa pelo processo de reescrita do Agente 4.

**Formato único obrigatório — um campo por linha:**

```
<!-- [CONTEXTO_OPERACAO] -->
**Habilidade:** H12 — Texto completo da habilidade BNCC.
**Operação principal:** Mapear causalidade
**Pergunta do capítulo:** Como a centralização...?
**Por que importa:** Este capítulo fornece a estrutura que será usada no próximo para...
<!-- [/CONTEXTO_OPERACAO] -->
```

Os quatro campos são obrigatórios. Cada campo ocupa sua própria linha. Nenhum pode ser omitido.

❌ NUNCA usar HTML comments para o conteúdo interno:
```
<!-- [CONTEXTO_OPERACAO] -->
<!-- Habilidade: H12 — ... -->
<!-- Operação principal: Mapear causalidade -->
<!-- [/CONTEXTO_OPERACAO] -->
```

---

## Como processar cada tipo de operação

O core define para cada seção um `TIPO_OPERACAO`. Você deve gerar os parágrafos e rótulos correspondentes.

### 1. `Definir`

**Saída esperada:**
[DEFINIÇÃO] [Escreva a definição exatamente como no campo DEFINICAO_EM_UMA_LINHA do core, expandida em 2-3 frases, sempre partindo do exemplo âncora.]

[EXEMPLO] [Use o EXEMPLO_ANCOLA do core. Se for uma situação concreta, descreva em 1-2 frases.]

[AUTOR: Nome Completo (datas) País/Filiação] (se BOX_BIOGRAFICO = Sim)
Texto biográfico: função, obra principal. Máximo 20 palavras. Sem adjetivos.
[/AUTOR]

text

**Exemplo concreto (para um core sobre “mais-valia”):**
[DEFINIÇÃO] A mais-valia é a diferença entre o valor produzido pelo trabalhador e o salário que ele recebe. Essa diferença é apropriada pelo dono dos meios de produção.
[EXEMPLO] Um operário trabalha 8 horas por dia. Nesse período, ele produz mercadorias que são vendidas por R$ 160,00. Seu salário diário é de R$ 80,00. A diferença entre o valor que ele produz (R$ 160,00) e o que recebe (R$ 80,00) – ou seja, R$ 80,00 – é a mais-valia: o valor do trabalho não pago, apropriado pelo patrão. 
text

### 2. `Classificar`
[CLASSIFICAÇÃO] [Use os CRITERIOS para apresentar as categorias.]
[EXEMPLO] [Aplique a classificação ao EXEMPLO_ANCOLA.]
[Liste os ELEMENTOS_A_CLASSIFICAR com suas respectivas categorias.]

text

### 3. `Comparar`
[COMPARAÇÃO] Elemento A: [ELEMENTO_A]. Elemento B: [ELEMENTO_B].
[ASPECTO 1] [Diferença/semelhança]
[ASPECTO 2] ...
[CONCLUSÃO PARCIAL] [Frase generalizante.]

text

### 4. `Sequenciar`
[SEQUÊNCIA] [Lista ordenada dos EVENTOS com seus MARCOS_TEMPORAIS.]
[EXEMPLO] [Use o EXEMPLO_ANCOLA como linha do tempo textual.]

text

### 5. `Mapear causalidade`
[CAUSAS] [Lista de causas.]
[CONSEQUÊNCIAS] [Lista de consequências.]
[RELAÇÃO] [Descrição de como X leva a Y, conforme RELACAO do core.]
[EXEMPLO] [Caso concreto do EXEMPLO_ANCOLA.]

text

### 6. `Reconhecer perspectiva`
[PERSPECTIVA 1] [ARGUMENTOS_CADA_PERSPECTIVA da primeira.]
[PERSPECTIVA 2] [Argumentos da segunda.]
[EXEMPLO] [Texto ou fonte do EXEMPLO_ANCOLA onde as perspectivas aparecem.]

text

### 7. `Aplicar`
[APLICAÇÃO] [Retome o CONCEITO_A_APLICAR.]
[CASO NOVO] [Descreva o CASO_NOVO.]
[PASSOS] [Enumere os PASSOS_DA_APLICACAO.]
[RESULTADO] [Conclusão da aplicação.]

text

---

## Verificação (quando `VERIFICACAO = Sim`)

No final da seção (após todos os parágrafos e boxes), adicione:
[VERIFICAÇÃO]

[Pergunta fechada – múltipla escolha ou verdadeiro/falso]
Resposta: [letra ou texto correto]

[Segunda pergunta]
Resposta: ...

text

As perguntas devem testar a operação da habilidade, não a mera repetição. Exemplo para `Comparar`:
Em qual dos aspectos analisados Brasil e Haiti se diferenciam mais claramente?
(a) participação popular
(b) data da independência
(c) língua oficial
Resposta: (a)

text

---

## Boxes especiais

### Box biográfico — AUTOR (se `BOX_BIOGRAFICO = Sim`)

Escreva sempre como bloco com abertura e fechamento explícitos. Inclua nome e datas na tag de abertura:

```
[AUTOR: Nome Completo (datas) País/Filiação]
Texto biográfico: função, obra principal. Máximo 20 palavras. Sem adjetivos.
[/AUTOR]
```

Quando o `[AUTOR]` está **aninhado** dentro do bloco temático, nenhum atributo extra é necessário:

```
[DEFINIÇÃO]
...texto...
  [AUTOR: Karl Marx (1818–1883) Alemanha]
  Filósofo e economista, autor de O Capital (1867).
  [/AUTOR]
[/DEFINIÇÃO]
```

Quando o `[AUTOR]` está **fora** do bloco temático (após o fechamento), adicione `ref=tipo`:

```
[/DEFINIÇÃO]
[AUTOR: Karl Marx (1818–1883) Alemanha | ref=definicao]
Filósofo e economista, autor de O Capital (1867).
[/AUTOR]
```

Use como `ref=` o tipo do bloco fechado imediatamente antes: `definicao`, `perspectiva`, `classificacao`, `causa`, `relacao-causal`, etc.

### Fonte

Escreva sempre como bloco com abertura e fechamento explícitos:

```
[FONTE]
SOBRENOME, Nome. *Título*. Cidade: Editora, Ano.
[/FONTE]
```

Se houver trecho direto, inclua-o dentro do bloco, após a referência:

```
[FONTE]
SOBRENOME, Nome. *Título*. Cidade: Editora, Ano.
“Trecho citado diretamente.”
[/FONTE]
```

A citação direta é permitida **apenas como evidência**, não como recurso estilístico.

---

## Proibições específicas na execução

- **Não use** travessões para aposto (use vírgulas ou parênteses).
- **Não use** “nós”, “a gente”, “nosso”.
- **Não use** exclamações.
- **Não use** palavras como “interessantemente”, “surpreendentemente”.
- **Não use** listas com marcadores (`-`) dentro dos blocos – use números ou parágrafos contínuos.
- **Não invente** subseções além das que estão no core.

---

## Verificação final (checklist)

Antes de entregar `texto.md`, confirme:

- [ ] O texto começa com o bloco `<!-- [CONTEXTO_OPERACAO] -->` com os quatro campos em markdown bold, um por linha.
- [ ] Cada seção tem um cabeçalho idêntico ao `CABECALHO` do core.
- [ ] Dentro de cada seção, o primeiro rótulo corresponde ao `TIPO_OPERACAO` (ex: `[DEFINIÇÃO]`).
- [ ] Todos os `EXEMPLO_ANCOLA` do core foram usados.
- [ ] Todos os `[AUTOR]` foram escritos como bloco com `[/AUTOR]` de fechamento, com nome e datas na tag de abertura.
- [ ] `[AUTOR]` aninhado dentro do bloco pai sempre que possível; quando fora, inclui `ref=tipo`.
- [ ] Os boxes biográficos (se `Sim`) estão logo após a primeira menção, com ≤20 palavras.
- [ ] As fontes foram incluídas como bloco `[FONTE]` / `[/FONTE]` com a referência bibliográfica dentro.
- [ ] As verificações estão presentes exatamente onde `VERIFICACAO: Sim` e ausentes onde `Não`.
- [ ] Cada pergunta de verificação tem sua resposta indicada.
- [ ] Nenhuma frase contém metáfora, exclamação, advérbio de opinião ou “nós”.
- [ ] A `SINTESE_FINAL` responde literalmente à pergunta do capítulo.
- [ ] O arquivo não contém andaime (ex: “como vimos”, “agora vamos”).

---

**Data de vigência:** Esta skill substitui todas as versões anteriores do `agente2-skill.md`.  
**Uso obrigatório:** Sempre que você (Agente 2) for executado, siga estritamente este documento.