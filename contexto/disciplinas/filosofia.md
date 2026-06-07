# CONTEXTO DISCIPLINAR FUNCIONAL — FILOSOFIA
## Para uso do Agente 1 (Arquiteto Curricular) e Agente 2 (Redator Funcional)

Este documento define as especificidades da disciplina de Filosofia dentro do pipeline funcional. Ele não substitui os princípios pedagógicos ou as skills – complementa com o que é particular da Filosofia.

**Em caso de conflito, os princípios pedagógicos (arquivo `principios-pedagogicos-agente1.md`) e as skills (agente1-skill.md, agente2-skill.md) prevalecem.**

---

## 1. A especificidade da Filosofia

A Filosofia organiza-se em torno da **argumentação racional** como prática central. Diferentemente da História (processos no tempo) ou da Sociologia (estruturas sociais), a Filosofia examina os fundamentos, conceitos e pressupostos que sustentam o conhecimento, a ética e a política.

**Conceito central para o pipeline:** **estranhamento filosófico** – capacidade de questionar o que parece óbvio, identificar pressupostos ocultos e distinguir opiniões de argumentos justificados.

**Pergunta estruturante da disciplina:** O que podemos conhecer, como devemos agir e o que é uma sociedade justa — e com que argumentos defendemos nossas respostas?

---

## 2. Conceitos estruturantes (para referência do Agente 1)

A ordem indica dependência lógica. Use estes conceitos nos cores conforme necessário.

| Ordem | Conceito | Definição funcional |
|-------|----------|---------------------|
| 1 | Argumento | Conjunto de premissas que justificam uma conclusão. Distingue-se de opinião e de retórica. |
| 2 | Premissa / Conclusão | Estrutura básica do raciocínio dedutivo. Premissas sustentam a conclusão. |
| 3 | Validade e Solidez | Argumento válido: conclusão segue das premissas. Sólido: válido + premissas verdadeiras. |
| 4 | Conhecimento / Crença justificada | Epistemologia básica: diferença entre saber e crer, critérios de justificação. |
| 5 | Ética e Moral | Ética como reflexão sobre os princípios; moral como normas em prática. |
| 6 | Liberdade | Conceito central da política e da ética: liberdade negativa (ausência de coerção) vs. positiva (capacidade de agir). |
| 7 | Justiça | O que é distribuir de forma justa — diferentes teorias (mérito, necessidade, igualdade). |
| 8 | Estado e Poder | Legitimidade do poder político; contrato social; soberania. |
| 9 | Razão e Experiência | Debate entre racionalismo e empirismo como fontes do conhecimento. |
| 10 | Ideologia | Conjuntos de crenças que moldam a percepção da realidade e justificam relações de poder. |
| 11 | Dialética | Método de confronto de teses opostas para avançar na compreensão (Platão, Hegel, Marx). |
| 12 | Metafísica | Questões sobre a natureza do ser, da realidade, da identidade e do tempo. |

### Conceitos-armadilha (evitar usos simplistas)

- **Liberdade:** não usar como "fazer o que quero". Exigir distinção entre liberdade negativa e positiva, e discussão de limites.
- **Verdade:** não tratar como sinônimo de opinião. Trabalhar com critérios de justificação.
- **Ética e Moral:** não usar como sinônimos indiscriminados. Apresentar a distinção antes de usá-los.
- **Platão:** evitar resumir sua filosofia a "mundo das ideias vs. mundo das sombras" sem articular com o problema do conhecimento.
- **Nietzsche:** evitar usos fragmentados de aforismos sem contexto argumentativo.

---

## 3. Autores com função pedagógica real (referência para o Agente 1)

| Autor | Obra/conceito útil | Quando usar |
|-------|--------------------|--------------|
| Platão (428–348 a.C.) | Alegoria da caverna, teoria das formas, diálogos socráticos | Epistemologia, método filosófico, aparência vs. realidade |
| Aristóteles (384–322 a.C.) | Ética a Nicômaco (eudaimonia, virtude), Política (zoon politikon) | Ética, política, conceito de bem comum |
| Immanuel Kant (1724–1804) | Imperativo categórico, autonomia da vontade, crítica ao conhecimento | Ética deontológica, limites do conhecimento |
| John Rawls (1921–2002) | "Uma Teoria da Justiça": véu da ignorância, princípios de justiça | Política, justiça distributiva |
| Hannah Arendt (1906–1975) | "A Condição Humana": vita activa, banalidade do mal | Política, totalitarismo, ação humana |
| Marilena Chauí (1941–) | "Convite à Filosofia": introdução à tradição filosófica brasileira | Contextualização nacional, ideologia |

### Autores a evitar (uso decorativo)

- Citações de Nietzsche sem contexto argumentativo (aforismos soltos)
- Referências a Sócrates apenas como "aquele que disse que só sabia que nada sabia"
- Descartes reduzido ao "penso, logo existo" sem a dúvida metodológica

---

## 4. Operações cognitivas da Filosofia (alinhadas às operações elementares do pipeline)

| Operação | Como se manifesta na Filosofia |
|----------|-------------------------------|
| Definir | Precisar conceitos com rigor; distinguir de usos correntes |
| Comparar | Confrontar teses filosóficas opostas (ex: Hobbes vs. Rousseau sobre natureza humana) |
| Argumentar | Reconstruir argumentos em premissas + conclusão; avaliar validade |
| Identificar perspectiva | Localizar de onde fala um filósofo — período, problema central, tradição |
| Aplicar | Usar conceito filosófico para analisar situação concreta (ex: liberdade em dilemas atuais) |
| Questionar pressuposto | Explicitar o que uma afirmação assume sem dizer; prática filosófica central |

---

## 5. Regras de formatação e vocabulário para o Agente 2

- **Não usar "obviamente" ou "claramente"** — a Filosofia parte justamente do não-óbvio.
- **Sempre atribuir teses a autores:** "Para Kant, ..." nunca "A Filosofia diz que...".
- **Apresentar objeções:** todo argumento filosófico forte merece ao menos uma objeção genuína.
- **Vocabulário técnico com definição imediata:** ao usar "a priori", "dedução", "ontologia" — definir na mesma frase ou no parágrafo.
- **Evitar exemplos de tribunal ou dilema do bonde** sem relacioná-los ao conceito em questão.

---

## 6. Exemplo de texto funcional bem formatado para Filosofia

```
[DEFINIÇÃO]
Liberdade, em sentido filosófico, é a capacidade de agir segundo princípios que o próprio agente escolhe por razão — não por impulso ou coerção externa. Kant chama isso de autonomia da vontade.

[COMPARAÇÃO]
Isaiah Berlin distingue dois sentidos: liberdade negativa (ausência de impedimento externo) e liberdade positiva (capacidade efetiva de agir). Um preso libertado tem liberdade negativa restaurada; um analfabeto pode ter liberdade negativa plena e liberdade positiva reduzida.

[APLICAR]
Aplique essa distinção ao acesso à educação: garantir que "ninguém proíbe estudar" é liberdade negativa. Garantir que todos possam efetivamente estudar exige liberdade positiva — e políticas públicas diferentes.
```
