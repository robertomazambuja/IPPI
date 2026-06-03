# SKILL — AGENTE 2: COMO EXECUTAR OPERAÇÕES DIDÁTICAS V3

## Introdução

Esta skill ensina **como fazer cada operação cognitiva** (Definir, Classificar, Comparar, Aplicar) de forma que o texto fique fluido, integrado e didático — sem blocos isolados, sem verificação.

Você aprenderá através de exemplos antes/depois:
- ❌ **ERRADO** — fragmentado, mecânico
- ✅ **CERTO** — fluido, integrado, didático

---

## OPERAÇÃO 1: DEFINIR

### Objetivo
Apresentar um conceito de forma clara, com exemplo concreto integrado, sem isolamento de blocos.

### O que entra

Do core, você recebe:
- A definição do conceito (campo DEFINICAO)
- Um ou mais exemplos âncora (campo EXEMPLO)
- Uma ou mais fontes (campo FONTE)

### O que sai

Um parágrafo único que:
1. Apresenta a definição
2. Transiciona para o exemplo ("Isso pode ser observado em...")
3. Integra o dado concreto
4. Depois cita a fonte

---

### EXEMPLO 1: Estratificação Social

#### ❌ ERRADO (V1/V2 — fragmentado)

```markdown
### O que é estratificação social

[DEFINIÇÃO]
Estratificação social é a distribuição dos membros de uma sociedade 
em camadas (estratos) hierarquicamente ordenadas, em que cada camada oferece 
acesso desigual a recursos como renda, prestígio e poder.

[EXEMPLO]
Os dados tornam isso visível. No Brasil, segundo a PNAD Contínua 2023 (IBGE), 
os 10% mais ricos concentram cerca de 43% da renda total do país...

[FONTE]
IBGE, Pesquisa Nacional por Amostra de Domicílios Contínua (PNAD Contínua), 2023.
```

**Problema:** Três blocos isolados. Aluno pula entre eles. Sem fluxo.

#### ✅ CERTO (V3 — fluido)

```markdown
### O que é estratificação social

<!-- [TIPO_OPERACAO: Definir] -->

<!-- [DEFINIÇÃO] -->
Estratificação social é a distribuição dos membros de uma sociedade 
em camadas (estratos) hierarquicamente ordenadas, em que cada camada oferece 
acesso desigual a recursos como renda, prestígio e poder. Essa distribuição 
não é aleatória: ela se organiza de forma estável e se repete ao longo das 
gerações, condicionando as oportunidades de vida dos indivíduos conforme a 
posição que ocupam na estrutura produtiva, educacional e política.

Isso pode ser observado em dados concretos: no Brasil, segundo a PNAD 
Contínua 2023 (IBGE), os 10% mais ricos concentram cerca de 43% da renda 
total do país, enquanto os 40% mais pobres detêm aproximadamente 10%. 
Essa distribuição desigual se repete de geração em geração e está associada 
a posições sociais que as pessoas ocupam na estrutura produtiva, educacional 
e política.
<!-- [/DEFINIÇÃO] -->

<!-- [FONTE] -->
**Fonte:** IBGE, Pesquisa Nacional por Amostra de Domicílios Contínua 
(PNAD Contínua), 2023. Síntese de Indicadores Sociais, 2023.
<!-- [/FONTE] -->
```

**O que mudou:**
- ✅ Um único parágrafo (comentários HTML invisíveis)
- ✅ Transição denotativa: "Isso pode ser observado em dados concretos:"
- ✅ Exemplo integrado, não em caixa
- ✅ Fonte ao final da seção, não em bloco isolado
- ✅ Leitura natural

---

### EXEMPLO 2: Mais-valia

#### ❌ ERRADO (fragmentado)

```markdown
### O que é mais-valia

[DEFINIÇÃO]
Mais-valia é o valor criado pelo trabalho que não é pago ao trabalhador. 
É a diferença entre o valor que o trabalhador produz e o salário que recebe.

[EXEMPLO]
Um trabalhador de fábrica produz 200 reais em valor por dia, mas recebe 
apenas 80 reais de salário. Os 120 reais restantes são apropriados pelo 
proprietário.

[AUTOR]
Karl Marx (1818–1883), formulou esse conceito.
```

#### ✅ CERTO (fluido)

```markdown
### O que é mais-valia

<!-- [TIPO_OPERACAO: Definir] -->

<!-- [DEFINIÇÃO] -->
Mais-valia é o valor criado pelo trabalho que não é pago ao trabalhador. 
É a diferença entre o valor que o trabalhador produz e o salário que recebe. 
Este conceito é central para entender como a exploração econômica funciona 
no capitalismo.

Considere um trabalhador de fábrica que produz 200 reais em valor por dia, 
mas recebe apenas 80 reais de salário. Os 120 reais restantes — a mais-valia — 
são apropriados pelo proprietário da fábrica. Esse mecanismo se repete 
diariamente, gerando o lucro do proprietário através do trabalho não pago.
<!-- [/DEFINIÇÃO] -->

<!-- [AUTOR] -->
Este conceito foi formulado por Karl Marx (1818–1883), filósofo e 
economista alemão, no *O Capital*.
<!-- [/AUTOR] -->

<!-- [FONTE] -->
**Fonte:** Karl Marx, *O Capital*, Vol. 1 (1867). Boitempo, 2013 [1867].
<!-- [/FONTE] -->
```

**O que faz funcionar:**
- ✅ Parágrafo 1: definição breve + contexto
- ✅ Parágrafo 2: exemplo integrado com "Considere..." + conexão à exploração
- ✅ Depois: autor + fonte contextualizados

---

## OPERAÇÃO 2: CLASSIFICAR

### Objetivo
Apresentar tipos ou categorias de algo, conectando cada tipo aos critérios de classificação que os distinguem.

### O que entra

Do core:
- A lógica de classificação (critérios, dimensões)
- 2–5 subtipos, cada um com definição e exemplos

### O que sai

Uma seção que:
1. Introduz os critérios/dimensões
2. Para cada subtipo:
   - Começa com uma frase que o conecta aos critérios
   - Integra definição + exemplo no parágrafo
3. Depois: autor/fonte

---

### EXEMPLO 1: Tipos de Estratificação

#### ❌ ERRADO (fragmentado)

```markdown
### Tipos de estratificação: castas, estamentos e classes

[CLASSIFICACAO]
Os sistemas podem ser classificados por três critérios: (1) mobilidade, 
(2) pertencimento, (3) legitimação.

#### Castas
O sistema de castas é um tipo fechado... [EXEMPLO: Índia]

#### Estamentos
O sistema estamental é semifechado... [EXEMPLO: Feudalismo]

#### Classes
O sistema de classes é aberto... [EXEMPLO: São Bernardo do Campo]
```

**Problema:** Cada subtipo é um bloco isolado. Não está claro como cada um relaciona aos 3 critérios.

#### ✅ CERTO (integrado)

```markdown
### Tipos de estratificação: castas, estamentos e classes

<!-- [TIPO_OPERACAO: Classificar] -->

<!-- [CLASSIFICACAO] -->
Os sistemas de estratificação podem ser classificados segundo três critérios: 
(1) possibilidade de mobilidade entre estratos (fechada ou aberta), 
(2) critério de pertencimento (nascimento, tradição jurídica ou posição econômica) 
e (3) base de legitimação (religiosa, legal-costumeira ou econômica). Cada 
combinação desses critérios define um tipo diferente de sistema.
<!-- [/CLASSIFICACAO] -->

**Casta – estratificação fechada por nascimento e religião**

<!-- [SUBTIPO_1] -->
Um primeiro tipo é o sistema de castas, em que a posição social é definida 
pelo nascimento e legitimada por critérios religiosos. Este é um sistema 
fechado: a mobilidade entre castas não era permitida, e o pertencimento era 
hereditário. Na Índia tradicional, a casta dos brâmanes (sacerdotes) ocupava 
o topo e a dos dalits (intocáveis) ocupava a base. A religião hinduísta 
legitimava essa hierarquia como ordem natural ou cósmica.
<!-- [/SUBTIPO_1] -->

**Estamento – estratificação semifechada por tradição jurídica**

<!-- [SUBTIPO_2] -->
Um segundo tipo é o sistema estamental, em que a posição social é definida 
pela tradição jurídica e costumeira. Este é um sistema semifechado: a mobilidade 
era rara e dependia de concessão do estamento superior. A legitimação se apoiava 
em leis e costumes, não em religião. A sociedade feudal europeia (séculos X–XV), 
dividida em clero, nobreza e servos, funcionava dessa forma: cada estamento 
tinha direitos e deveres definidos pela lei feudal.
<!-- [/SUBTIPO_2] -->

**Classes sociais – estratificação aberta por propriedade**

<!-- [SUBTIPO_3] -->
Um terceiro tipo é o sistema de classes, formalmente aberto. A posição social 
é definida pela relação com os meios de produção e pela posse de recursos 
econômicos. A legitimação é econômica, não religiosa ou legal-costumeira: o 
mercado é o critério de hierarquização. Nas sociedades capitalistas contemporâneas, 
a mobilidade é formalmente possível, embora condicionada por fatores estruturais. 
Um trabalhador assalariado de uma montadora de automóveis em São Bernardo do 
Campo (SP) e o acionista majoritário dessa mesma empresa ocupam posições 
diferentes no sistema de classes: o trabalhador vende sua força de trabalho 
por um salário mensal; o acionista detém parte dos meios de produção e se 
apropria de parte do lucro gerado pela produção.
<!-- [/SUBTIPO_3] -->

<!-- [AUTOR] -->
A análise dos sistemas de estratificação foi desenvolvida por Max Weber 
(1864–1920), sociólogo alemão, e retomada por sociólogos contemporâneos.
<!-- [/AUTOR] -->

<!-- [FONTE] -->
**Fonte:** [referências dos autores]
<!-- [/FONTE] -->
```

**O que faz funcionar:**
- ✅ Introdução clara dos 3 critérios
- ✅ Cada subtipo começa: "Um primeiro/segundo/terceiro tipo..." + conecta aos critérios
- ✅ Exemplo integrado no parágrafo, não em caixa
- ✅ Aluno vê a lógica: as distinções são baseadas nos critérios

---

## OPERAÇÃO 3: COMPARAR

### Objetivo
Apresentar perspectivas, conceitos ou autores diferentes, destacando onde convergem e onde divergem.

### O que entra

Do core:
- 2–4 perspectivas diferentes
- Para cada: um autor, suas ideias principais, exemplos
- Dados ou situações que permitem teste/contraste

### O que sai

Uma seção que:
1. Introduz as perspectivas
2. Para cada perspectiva:
   - Desenvolve a ideia
   - Destaca o que é diferente/único
   - Integra exemplos
3. Sintetiza convergências e divergências

---

### EXEMPLO: Marx, Weber, Bourdieu

#### ❌ ERRADO (repetitivo, fragmentado)

```markdown
### Três visões sobre estratificação

[Parágrafo introdutório apresentando os 3 autores]

[AUTOR: Max Weber]
> Max Weber (1864–1920)...

[AUTOR: Pierre Bourdieu]
> Pierre Bourdieu (1930–2002)...

[PERSPECTIVA: Marx]
#### Marx: classe como posição na produção
Para Marx...

[PERSPECTIVA: Weber]
#### Weber: classe, status e partido
Para Weber...

[PERSPECTIVA: Bourdieu]
#### Bourdieu: capitais
Para Bourdieu...

[COMPARACAO]
[ASPECTO 1] ...
[ASPECTO 2] ...
[ASPECTO 3] ...

[CONCLUSAO_PARCIAL]
As três perspectivas convergem em...
```

**Problema:** Muitos blocos. Boxes de autor antes de serem usados. Quadro comparativo repete o que foi lido. Sem contraste claro.

#### ✅ CERTO (fluido, com contraste)

```markdown
### Três visões sobre estratificação

<!-- [TIPO_OPERACAO: Comparar] -->

Três autores formularam explicações diferentes para por que a estratificação 
social existe e como funciona. Comparar essas perspectivas permite entender 
o que cada uma ilumina e o que deixa em segundo plano.

<!-- [PERSPECTIVA_A: Karl Marx] -->
#### Marx: Classe como Posição na Produção

Para Marx, a estratificação social é determinada **unicamente** pela posição 
na estrutura produtiva. A divisão fundamental é entre proprietários dos meios 
de produção (burguesia) e trabalhadores que vendem sua força de trabalho 
(proletariado). A desigualdade resulta da exploração econômica: o lucro do 
proprietário depende do trabalho não pago ao trabalhador. Nessa visão, todas 
as outras formas de desigualdade (prestígio, poder político) derivam da 
estrutura econômica.

<!-- [AUTOR] -->
Karl Marx (1818–1883), filósofo e economista alemão, desenvolveu essa análise 
no *Manifesto Comunista* (1848) e em *O Capital* (1867).
<!-- [/AUTOR] -->
<!-- [/PERSPECTIVA_A] -->

<!-- [PERSPECTIVA_B: Max Weber] -->
#### Weber: Classe, Status e Partido

Diferindo dessa análise, Max Weber (1864–1920) propõe que a estratificação 
**não se reduz à dimensão econômica**. Weber identifica três dimensões 
independentes de desigualdade:
- **Classe:** posição econômica no mercado
- **Status:** prestígio social atribuído pelo grupo
- **Partido:** acesso ao poder político

Uma pessoa pode ter renda alta mas status baixo (como um empresário "novo-rico" 
que não é respeitado), ou o inverso (como um professor de prestígio que ganha 
pouco). Essas dimensões operam com lógicas distintas e nem sempre se alinham. 
Isso significa que a estratificação é multidimensional, não redutível à economia.

<!-- [AUTOR] -->
Max Weber (1864–1920), sociólogo e economista alemão, fundador da sociologia 
compreensiva, distinguiu essas três ordens em *Economia e Sociedade* (1922).
<!-- [/AUTOR] -->
<!-- [/PERSPECTIVA_B] -->

<!-- [PERSPECTIVA_C: Pierre Bourdieu] -->
#### Bourdieu: Capitais Econômico, Cultural e Social

Expandindo a lógica weberiana, Pierre Bourdieu (1930–2002) propõe que a 
estratificação opera através de **múltiplos tipos de capital** que se acumulam 
e se convertem entre si:
- **Capital econômico:** dinheiro, propriedade, recursos materiais
- **Capital cultural:** diplomas, conhecimentos, hábitos culturais, linguagem
- **Capital social:** rede de relações, contatos influentes

A posição social de um indivíduo depende do volume e da composição desses 
capitais. Quem acumula mais de cada tipo ocupa posições mais altas. O aspecto 
inovador em Bourdieu é que o capital cultural — frequentemente invisível — 
desempenha papel tão importante quanto o econômico na reprodução das 
desigualdades entre gerações. Um filho de professores herda capital cultural 
(dom de linguagem acadêmica, familiaridade com livros) que o coloca em 
vantagem na escola, mesmo que sua renda seja modesta.

<!-- [AUTOR] -->
Pierre Bourdieu (1930–2002), sociólogo francês e professor no Collège de France, 
desenvolveu essa teoria em *A Distinção* (1979) e trabalhos posteriores.
<!-- [/AUTOR] -->
<!-- [/PERSPECTIVA_C] -->

<!-- [CONCLUSAO_PARCIAL] -->
**Convergências e divergências:**

As três perspectivas convergem na identificação de que a desigualdade é 
estrutural — não resultado apenas de esforço individual. Todas reconhecem que 
a posição social condiciona oportunidades de vida.

Mas divergem quanto aos mecanismos. Marx enfatiza a exploração econômica direta. 
Weber acrescenta que prestígio e poder político operam independentemente da 
renda, criando desigualdades diferentes. Bourdieu mostra que a reprodução das 
posições sociais depende da transmissão de diferentes tipos de capital, 
especialmente o cultural, que funciona de forma menos visível que a econômica.

Cada perspectiva captura algo que as outras deixam em segundo plano. Juntas, 
oferecem uma compreensão mais completa de por que a estratificação persiste.
<!-- [/CONCLUSAO_PARCIAL] -->

<!-- [FONTE] -->
**Fontes:**
- Karl Marx e Friedrich Engels, *Manifesto Comunista* (1848). Boitempo, 2010.
- Max Weber, *Economia e Sociedade* (1922). Brasília: Editora UnB, 2004.
- Pierre Bourdieu, *A Distinção* (1979). São Paulo: Edusp; Porto Alegre: Zouk, 2007.
<!-- [/FONTE] -->
```

**O que faz funcionar:**
- ✅ Autores aparecem DEPOIS de suas ideias serem desenvolvidas (não antes)
- ✅ Contraste explícito: "Diferindo dessa análise..." "Expandindo a lógica..."
- ✅ Cada perspectiva tem seu parágrafo único, não blocos isolados
- ✅ Síntese nomeada: "Convergências e divergências:" — deixa claro o movimento cognitivo
- ✅ Fluxo natural, não comparação tabulada

---

## OPERAÇÃO 4: APLICAR

### Objetivo
Usar conceitos anteriormente desenvolvidos para analisar uma situação concreta, caso-estudo ou contexto local.

### O que entra

Do core:
- Conceitos já definidos
- Dados ou situação específica do contexto local
- Perspectivas que "iluminam" o caso de formas diferentes

### O que sai

Uma seção que:
1. Situa o caso concreto
2. Analisa o caso através de cada perspectiva/conceito
3. Sintetiza: o que cada conceito explica

---

### EXEMPLO: Desigualdade de Renda no Brasil

#### ❌ ERRADO (fragmentado)

```markdown
### Aplicação ao Brasil

[APLICACAO]
Os conceitos podem ser aplicados ao Brasil...

[CASO]
Em 2023, o rendimento médio de trabalhadores com ensino superior foi 
3,5 vezes maior do que com ensino médio...

[PERSPECTIVA: Marx]
#### Leitura marxista
Ambos são assalariados, portanto proletariado...

[PERSPECTIVA: Weber]
#### Leitura weberiana
Embora assalariados, sua posição de mercado é diferente...

[PERSPECTIVA: Bourdieu]
#### Leitura de Bourdieu
A diferença se explica pelo capital cultural...

[RESULTADO]
A desigualdade não se explica apenas por classe...
```

#### ✅ CERTO (fluido e analítico)

```markdown
### Classe, Status e Capital na Desigualdade de Renda no Brasil

<!-- [TIPO_OPERACAO: Aplicar] -->

<!-- [APLICACAO] -->
Os conceitos de classe (Marx), status e posição de mercado (Weber) e capitais 
(Bourdieu) podem ser aplicados para entender a desigualdade de renda concreta 
no Brasil.
<!-- [/APLICACAO] -->

<!-- [CASO] -->
Em 2023, segundo dados do IBGE (Síntese de Indicadores Sociais), o rendimento 
médio mensal de trabalhadores com ensino superior completo foi aproximadamente 
3,5 vezes maior do que o de trabalhadores com ensino médio completo. Ao mesmo 
tempo, pesquisas mostram que filhos de pais no quintil mais pobre de renda 
têm probabilidade significativamente menor de alcançar o quintil mais rico do 
que filhos de pais já situados nos quintis superiores. Esses dois fatos indicam 
que a escolaridade condiciona a renda e que a posição socioeconômica tende a 
se reproduzir entre gerações.
<!-- [/CASO] -->

<!-- [PERSPECTIVA_A_APLICADA] -->
#### O que Marx nos diz

A análise marxista oferece uma primeira observação: trabalhadores com ensino 
médio e trabalhadores com ensino superior vendem igualmente sua força de 
trabalho, pois ambos são assalariados. Pela lógica de Marx, pertencem à mesma 
classe (proletariado). No entanto, recebem rendimentos muito diferentes. Isso 
indica uma **limitação** da análise marxista centrada apenas na propriedade dos 
meios de produção: não explica toda a desigualdade de renda entre trabalhadores 
de uma mesma classe.
<!-- [/PERSPECTIVA_A_APLICADA] -->

<!-- [PERSPECTIVA_B_APLICADA] -->
#### O que Weber nos diz

Aqui a análise weberiana oferece mais clareza. Embora ambos os grupos sejam 
assalariados (mesma classe, no sentido econômico), sua **posição de mercado** 
é diferente: trabalhadores com ensino superior têm qualificações mais valorizadas 
no mercado de trabalho, o que lhes confere maior poder de barganha e renda. 
Além disso, ocupações que exigem ensino superior tendem a carregar maior 
**prestígio social** (status), o que reforça a desigualdade além do aspecto 
puramente econômico. A análise weberiana captura essa diferença que Marx deixa 
em segundo plano.
<!-- [/PERSPECTIVA_B_APLICADA] -->

<!-- [PERSPECTIVA_C_APLICADA] -->
#### O que Bourdieu nos diz

A análise de Bourdieu oferece ainda outra dimensão: por que a mobilidade 
intergeracional é baixa? Por que filhos de pais pobres tendem a permanecer 
pobres? A resposta, segundo Bourdieu, está na transmissão desigual de capital 
cultural. Diplomas funcionam como capital cultural institucionalizado que 
confere acesso a posições mais bem remuneradas. Filhos de famílias com maior 
capital cultural (pais escolarizados, acesso a livros, domínio da norma culta) 
têm maior probabilidade de completar o ensino superior e, assim, de reproduzir 
sua posição social. Famílias pobres, mesmo que incentivem os filhos, não 
dispõem desse capital cultural herdado, o que torna a trajetória para o ensino 
superior mais difícil. Bourdieu explica por que a desigualdade se transmite de 
geração em geração: não apenas por falta de dinheiro, mas por falta de capital 
cultural acumulado.
<!-- [/PERSPECTIVA_C_APLICADA] -->

<!-- [RESULTADO] -->
**O que cada perspectiva explica:**

Marx nos mostra que existe uma divisão estrutural (proprietários vs. assalariados) 
que gera desigualdade. Mas não é suficiente para explicar a desigualdade entre 
assalariados.

Weber nos mostra que, mesmo entre assalariados, a posição de mercado (qualificação) 
e o prestígio (status) criam hierarquias diferentes de renda.

Bourdieu nos mostra por que essas desigualdades persistem entre gerações: a 
herança de capital cultural (educação, linguagem, hábitos) reproduz as posições 
sociais.

Aplicados em conjunto, esses conceitos oferecem uma explicação mais completa 
de por que a desigualdade de renda no Brasil é estrutural e se reproduz 
intergeracionalmente.
<!-- [/RESULTADO] -->

<!-- [FONTE] -->
**Fonte:** IBGE, PNAD Contínua 2023 e Síntese de Indicadores Sociais 2023. 
Os dados mostram que o rendimento médio do trabalho no Brasil varia fortemente 
conforme o nível de instrução e que a mobilidade intergeracional de renda é 
limitada, com alta persistência da posição socioeconômica entre gerações.
<!-- [/FONTE] -->
```

**O que faz funcionar:**
- ✅ Caso concreto situado no início (não isolado)
- ✅ Cada perspectiva é aplicada em sequência (não comparação tabulada)
- ✅ Contraste explícito: "Aqui a análise weberiana oferece mais clareza..." "A análise de Bourdieu oferece ainda outra dimensão..."
- ✅ Síntese final responde: "O que cada perspectiva explica:" e mostra complementaridade
- ✅ Fluxo de descoberta: do simples (Marx) ao complexo (Bourdieu)

---

## TRANSIÇÕES DENOTATIVAS: Exemplos Prontos

### Para conectar definição → exemplo:
```
Isso pode ser observado em...
Um exemplo concreto disso é...
Veja como esse conceito se manifesta...
Dados concretos ilustram essa distribuição:
Para ilustrar, consideremos...
```

### Para conectar classificação → subtipo:
```
Um primeiro tipo, baseado em [critério], é...
Um segundo tipo ocorre quando [critério] determina...
Contrastando com os anteriores, o terceiro tipo [critério]...
```

### Para conectar perspectiva → perspectiva:
```
Diferindo dessa análise, [Autor B] propõe...
Expandindo a lógica de [Autor A], [Autor B] acrescenta...
Enquanto [Autor A] enfatiza..., [Autor B] identifica...
```

### Para conectar perspectiva/conceito → aplicação:
```
Aplicando essa lógica ao contexto brasileiro...
Esses conceitos iluminam os dados brasileiros da seguinte forma...
Para entender a desigualdade no Brasil, essa perspectiva oferece...
O caso brasileiro revela como...
```

### Para introduzir síntese/convergência:
```
As três perspectivas convergem em... mas divergem quanto a...
Cada perspectiva captura algo que as outras deixam em segundo plano...
Tomadas em conjunto, essas análises revelam...
```

---

## Checklist de Execução

Antes de entregar seu texto, verifique:

- [ ] Nenhum bloco `[VERIFICACAO]` no texto
- [ ] `[DEFINIÇÃO]` + `[EXEMPLO]` fundidos em um parágrafo único?
- [ ] Cada subtipo em `[CLASSIFICACAO]` começa com frase que o conecta aos critérios?
- [ ] Cada `[PERSPECTIVA]` contrasta com a anterior (frases como "Diferindo...", "Expandindo...")?
- [ ] `[AUTOR]` e `[FONTE]` aparecem APÓS a perspectiva ser desenvolvida, não antes?
- [ ] Há transição denotativa entre cada grande bloco?
- [ ] Um aluno do ensino médio consegue ler e entender **sem ajuda externa**?
- [ ] Rótulos estruturais estão **apenas em comentários HTML**, invisíveis ao leitor final?
- [ ] Nenhuma narrativa proibida (metáforas, perguntas retóricas, "vamos...", "como vimos")?

---

## Resumo: O Que Mudou em V3

| Aspecto | V1/V2 | V3 |
|---------|-------|----|
| **[VERIFICACAO]** | Sim | ❌ Removida |
| **Blocos visíveis** | Sim | ❌ Apenas comentários |
| **Integração** | Não (isolados) | ✅ Parágrafo único |
| **Transições** | Recomendadas | ✅ Obrigatórias |
| **Leitura** | Robótica | ✅ Fluida, didática |
| **Rastreabilidade** | Blocos visíveis | ✅ Comentários HTML |

