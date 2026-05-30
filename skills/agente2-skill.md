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

## Como processar cada tipo de operação

O core define para cada seção um `TIPO_OPERACAO`. Você deve gerar os parágrafos e rótulos correspondentes.

### 1. `Definir`

**Saída esperada:**
[DEFINIÇÃO] [Escreva a definição exatamente como no campo DEFINICAO_EM_UMA_LINHA do core, expandida em 2-3 frases, sempre partindo do exemplo âncora.]

[EXEMPLO] [Use o EXEMPLO_ANCOLA do core. Se for uma situação concreta, descreva em 1-2 frases.]

[AUTOR] (se houver) [Nome completo, datas, filiação. Ex: “Pierre Bourdieu (1930–2002), sociólogo francês.”] – se BOX_BIOGRAFICO = Sim, adicione uma segunda frase com a contribuição relevante (máx 20 palavras).

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

### Box biográfico (se `BOX_BIOGRAFICO = Sim`)

Imediatamente após a primeira menção do autor, em uma nova linha, entre colchetes ou em itálico:

`> *[Karl Marx (1818–1883), filósofo alemão, autor de O Capital.]*`

Máximo 20 palavras. Sem adjetivos.

### Fonte primária (se `FONTE_PRIMARIA` preenchida)

Use o formato:

`[FONTE] [Identificação: autor, obra, ano.] “[Trecho direto com aspas, se for breve]” – ou – [Paráfrase em nossa voz.]`

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

- [ ] O texto começa com `**CONTEXTO DE OPERAÇÃO**` e os quatro subitens preenchidos.
- [ ] Cada seção tem um cabeçalho idêntico ao `CABECALHO` do core.
- [ ] Dentro de cada seção, o primeiro rótulo corresponde ao `TIPO_OPERACAO` (ex: `[DEFINIÇÃO]`).
- [ ] Todos os `EXEMPLO_ANCOLA` do core foram usados.
- [ ] Todos os `AUTOR` foram introduzidos com nome, datas e filiação.
- [ ] Os boxes biográficos (se `Sim`) estão logo após a primeira menção, com ≤20 palavras.
- [ ] As `FONTE_PRIMARIA` foram incluídas conforme formato.
- [ ] As verificações estão presentes exatamente onde `VERIFICACAO: Sim` e ausentes onde `Não`.
- [ ] Cada pergunta de verificação tem sua resposta indicada.
- [ ] Nenhuma frase contém metáfora, exclamação, advérbio de opinião ou “nós”.
- [ ] A `SINTESE_FINAL` responde literalmente à pergunta do capítulo.
- [ ] O arquivo não contém andaime (ex: “como vimos”, “agora vamos”).

---

**Data de vigência:** Esta skill substitui todas as versões anteriores do `agente2-skill.md`.  
**Uso obrigatório:** Sempre que você (Agente 2) for executado, siga estritamente este documento.