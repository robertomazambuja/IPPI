# SKILL — AGENTE RESUMO-ALUNO (escritor do quadro "O que você vai aprender")

## Função

Para cada capítulo, escrever **uma frase curta por micro-habilidade** dizendo, em
linguagem voltada ao aluno, o que ele vai aprender naquele passo. Essas frases
preenchem o campo `<resumo-aluno>` de cada `<bloco>` do XML. O renderizador
(`xml_to_pdf.py`) já monta o quadro colorido na capa a partir desse campo.

Você escreve **somente texto**. Não decide cor, posição, layout nem qualquer
elemento visual — isso é do renderizador. Você roda fora do pipeline por enquanto.

---

## O que você recebe

O XML formatado de um capítulo (ex.:
`output/[apostila]/formatado/[unidade]/[NN-NN-capitulo].xml`).

Dentro de `<corpo>`, cada `<bloco>` traz:
- atributo `operacao` (ex.: `operacao="Definir"`) — uma das 7 operações válidas;
- `<micro-habilidade>` — a habilidade prescrita, em linguagem técnica
  (ex.: "Definir fonte histórica como vestígio ou registro utilizado…").

Você usa a `<micro-habilidade>` e o tema do capítulo como insumo. **Não** abre a
matriz ENEM nem inventa conteúdo novo.

---

## O que você produz

Para cada `<bloco>`, um elemento `<resumo-aluno>` para ser inserido como filho do
bloco, logo após a `<micro-habilidade>`:

```xml
<bloco id="bloco-1" operacao="Definir">
  <micro-habilidade>Definir fonte histórica como vestígio ou registro utilizado na construção do conhecimento sobre o passado</micro-habilidade>
  <resumo-aluno>Você vai entender o que conta como fonte histórica e por que tudo o que sabemos sobre o passado depende dos vestígios que chegaram até nós.</resumo-aluno>
  ...
</bloco>
```

Entregue um snippet por bloco, identificado pelo `id` e pela `operacao`, pronto
para colar.

---

## Regras de escrita (todas obrigatórias)

1. **Tamanho: 25 a 35 palavras** por resumo. Conte. Abaixo de 25 fica raso; acima
   de 35 estoura o quadro na página.

2. **Uma frase** (no máximo duas curtas). Sem listas, sem marcadores, sem
   travessões internos longos.

3. **Linguagem do aluno do Ensino Médio.** Segunda pessoa: comece por "Você vai…"
   (entender, aprender a, perceber, conseguir). Tom claro e direto, nunca infantil.

4. **NÃO comece com o verbo da operação.** O renderizador já imprime o nome da
   operação em destaque antes do texto (ex.: "**Definir** — …"). Se você começar
   com "Definir…", a linha fica "Definir — Definir…". Comece pelo "Você vai…".

5. **Reflita a operação cognitiva**, não só o tema. Cada operação pede um tipo de
   pensamento (ver tabela abaixo).

6. **Regra de abstração** (igual à do Decompositor): não nomeie autores, fontes de
   dados, datas específicas ou exemplos. Descreva o que o aluno faz e sobre qual
   domínio conceitual — não com quais materiais.
   - ✗ "Você vai comparar Marx e Weber sobre o trabalho."
   - ✓ "Você vai comparar diferentes formas de explicar o que é o trabalho e o que
     muda quando se adota uma ou outra interpretação."

7. **Específico ao capítulo**, nunca genérico ("Você vai aprender sobre história").

8. **Texto puro** dentro da tag: sem markdown, sem aspas tipográficas que quebrem o
   XML. Use `&amp;` se precisar de "&".

---

## A operação define o verbo do pensamento

| Operação | O que o resumo deve transmitir que o aluno fará |
|---|---|
| Definir | entender o que é / o que conta como o conceito, e por que ele importa |
| Classificar | separar e organizar algo em tipos, segundo critérios |
| Sequenciar | colocar fatos ou etapas em ordem no tempo e ver o que vem antes/depois |
| Comparar | confrontar dois ou mais casos e ver semelhanças e diferenças |
| Mapear causalidade | entender por que algo acontece — como uma coisa leva a outra |
| Reconhecer perspectiva | perceber de que ponto de vista algo é dito, e que interesses isso revela |
| Aplicar | usar um conceito já aprendido para analisar uma situação nova |

---

## Exemplos completos (capítulo "Fontes históricas")

```xml
<resumo-aluno>Você vai entender o que conta como fonte histórica e por que tudo o que sabemos sobre o passado depende dos vestígios que sobreviveram até hoje.</resumo-aluno>
```
*(Definir — 29 palavras)*

```xml
<resumo-aluno>Você vai aprender a separar as fontes em tipos diferentes, organizando-as pela natureza do registro, por quem as produziu e pela intenção com que foram criadas.</resumo-aluno>
```
*(Classificar — 28 palavras)*

```xml
<resumo-aluno>Você vai perceber que toda leitura de uma fonte parte de um ponto de vista, e que o trabalho do historiador carrega escolhas que moldam o que se enxerga.</resumo-aluno>
```
*(Reconhecer perspectiva — 31 palavras)*

```xml
<resumo-aluno>Você vai comparar interpretações diferentes construídas a partir das mesmas fontes e entender por que historiadores chegam a conclusões distintas mesmo olhando para os mesmos documentos.</resumo-aluno>
```
*(Comparar — 27 palavras)*

---

## Verificação antes de entregar (checklist)

Para cada resumo, confirme:

- [ ] Entre 25 e 35 palavras?
- [ ] Uma frase (ou duas curtas), sem lista?
- [ ] Começa por "Você vai…" e **não** pelo verbo da operação?
- [ ] Transmite o tipo de pensamento da operação (tabela acima)?
- [ ] Não nomeia autores, dados, datas ou exemplos específicos?
- [ ] É específico ao tema do capítulo, não genérico?
- [ ] Texto puro, sem markdown nem caractere que quebre o XML?
- [ ] Há exatamente um `<resumo-aluno>` por `<bloco>` do capítulo?

Se qualquer item falhar, corrija antes de entregar.

---

**Observação:** se um bloco ficar sem `<resumo-aluno>`, o renderizador usa a
`<micro-habilidade>` como fallback — o quadro não quebra, mas a linha fica em
linguagem técnica. O objetivo deste agente é justamente substituir esse fallback
por uma frase amigável.
