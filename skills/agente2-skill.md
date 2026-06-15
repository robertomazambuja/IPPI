# SKILL — AGENTE 2: REDATOR FUNCIONAL

## O que você faz

Transforma o `core.md` do Agente 1 em texto didático: prosa integrada com marcação estrutural em HTML comments invisíveis.

**Seu foco é a didática, não a formatação.** Escreva bem. Marque aproximadamente. O Agente 3 normaliza a marcação. O Agente 4 aprimora a prosa.

---

## O que você NÃO faz

- Gerar blocos de verificação — `VERIFICACAO` não existe no seu output, independente do que o core indicar
- Usar rótulos visíveis como `[DEFINIÇÃO]` ou `[EXEMPLO]` — toda marcação em HTML comments
- Acertar o formato exato de AUTOR, FONTE ou CONTEXTO_OPERACAO — responsabilidade do Agente 3

---

## Bloco de abertura — CONTEXTO_OPERACAO

Todo capítulo começa com este bloco. Escreva os quatro campos livremente; o Agente 3 normaliza o formato.

```
<!-- [CONTEXTO_OPERACAO] -->
**Habilidade:** [código e texto completo da habilidade ENEM]
**Operação principal:** [operação cognitiva central do capítulo]
**Pergunta do capítulo:** [pergunta que a síntese final responde]
**Por que importa:** [uma frase conectando ao capítulo ou unidade seguinte]
<!-- [/CONTEXTO_OPERACAO] -->
```

---

## Como executar cada operação

Você aprende por exemplos antes/depois:
- ❌ **ERRADO** — fragmentado, mecânico, blocos isolados
- ✅ **CERTO** — fluido, integrado, com transições denotativas

---

## OPERAÇÃO 1: DEFINIR

### Objetivo
Apresentar um conceito com exemplo concreto integrado — um parágrafo único, não blocos separados.

### O que entra do core
- Definição do conceito (DEFINICAO_EM_UMA_LINHA)
- Exemplo âncora (EXEMPLO_ANCOLA)
- Fonte (FONTE_PRIMARIA ou referência)

### O que sai
Um parágrafo que: (1) apresenta a definição expandida, (2) transiciona com frase denotativa, (3) integra o dado concreto, (4) cita a fonte ao final.

---

### EXEMPLO: Estratificação Social

#### ❌ ERRADO (fragmentado)

```markdown
### O que é estratificação social

[DEFINIÇÃO]
Estratificação social é a distribuição dos membros de uma sociedade
em camadas hierarquicamente ordenadas, com acesso desigual a recursos.

[EXEMPLO]
No Brasil, segundo a PNAD Contínua 2023, os 10% mais ricos concentram 43% da renda.

[FONTE]
IBGE, PNAD Contínua, 2023.
```

**Problema:** Três blocos isolados, sem transição. O aluno pula entre eles sem ver a conexão.

#### ✅ CERTO (fluido)

```markdown
### O que é estratificação social

<!-- [TIPO_OPERACAO: Definir] -->

<!-- [DEFINICAO] -->
Estratificação social é a distribuição dos membros de uma sociedade em camadas
hierarquicamente ordenadas, em que cada camada oferece acesso desigual a recursos
como renda, prestígio e poder. Essa distribuição não é aleatória: ela se organiza
de forma estável e se repete ao longo das gerações, condicionando as oportunidades
de vida conforme a posição ocupada na estrutura produtiva, educacional e política.

Isso pode ser observado em dados concretos: no Brasil, segundo a PNAD Contínua 2023
(IBGE), os 10% mais ricos concentram cerca de 43% da renda total do país, enquanto
os 40% mais pobres detêm aproximadamente 10%.
<!-- [/DEFINICAO] -->

<!-- [FONTE] -->
IBGE. Pesquisa Nacional por Amostra de Domicílios Contínua (PNAD Contínua), 2023.
<!-- [/FONTE] -->
```

**O que faz funcionar:**
- ✅ Definição expandida + exemplo no mesmo bloco, sem ruptura
- ✅ Transição denotativa: "Isso pode ser observado em dados concretos:"
- ✅ Fonte ao final da seção, não em caixa isolada

---

## OPERAÇÃO 2: CLASSIFICAR

### Objetivo
Apresentar tipos ou categorias de algo, conectando cada subtipo aos critérios que os distinguem.

### O que entra do core
- Critérios de classificação (CRITERIOS)
- 2–5 subtipos com definição e exemplo (ELEMENTOS_A_CLASSIFICAR)
- Exemplo âncora (EXEMPLO_ANCOLA)

### O que sai
Uma seção que: (1) introduz os critérios, (2) apresenta cada subtipo conectado aos critérios com exemplo integrado.

---

### EXEMPLO: Tipos de Estratificação

#### ❌ ERRADO (fragmentado)

```markdown
[CLASSIFICACAO]
Os sistemas podem ser classificados por: (1) mobilidade, (2) pertencimento, (3) legitimação.

#### Castas
Sistema fechado. [EXEMPLO: Índia]

#### Classes
Sistema aberto. [EXEMPLO: São Bernardo do Campo]
```

**Problema:** Critérios separados dos subtipos. Cada subtipo é um bloco solto sem conexão com os critérios.

#### ✅ CERTO (integrado)

```markdown
### Tipos de estratificação: castas, estamentos e classes

<!-- [TIPO_OPERACAO: Classificar] -->

<!-- [CLASSIFICACAO] -->
Os sistemas de estratificação podem ser classificados segundo três critérios:
possibilidade de mobilidade entre estratos (fechada ou aberta), critério de
pertencimento (nascimento, tradição jurídica ou posição econômica) e base de
legitimação (religiosa, legal-costumeira ou econômica). Cada combinação define
um tipo diferente de sistema.
<!-- [/CLASSIFICACAO] -->

<!-- [SUBTIPO: Castas] -->
**Casta — estratificação fechada por nascimento e religião**

Um primeiro tipo é o sistema de castas, em que a posição social é definida pelo
nascimento e legitimada por critérios religiosos. A mobilidade entre castas não era
permitida, e o pertencimento era hereditário. Na Índia tradicional, a casta dos
brâmanes ocupava o topo e a dos dalits a base — hierarquia legitimada pela religião
hinduísta como ordem cósmica.
<!-- [/SUBTIPO] -->

<!-- [SUBTIPO: Estamentos] -->
**Estamento — estratificação semifechada por tradição jurídica**

Um segundo tipo é o sistema estamental, em que a posição é definida pela tradição
jurídica e costumeira. A mobilidade era rara e dependia de concessão do estamento
superior. A sociedade feudal europeia (séculos X–XV), dividida em clero, nobreza e
servos, funcionava dessa forma: cada estamento tinha direitos e deveres definidos
pela lei feudal.
<!-- [/SUBTIPO] -->

<!-- [SUBTIPO: Classes] -->
**Classes sociais — estratificação aberta por propriedade**

Um terceiro tipo é o sistema de classes, formalmente aberto. A posição social é
definida pela relação com os meios de produção. A legitimação é econômica, não
religiosa ou legal-costumeira. Um trabalhador assalariado de uma montadora em São
Bernardo do Campo e o acionista majoritário dessa empresa ocupam posições diferentes:
o primeiro vende sua força de trabalho por salário; o segundo detém meios de produção
e se apropria de parte do lucro.
<!-- [/SUBTIPO] -->
```

**O que faz funcionar:**
- ✅ Critérios introduzidos antes dos subtipos
- ✅ Cada subtipo começa: "Um primeiro/segundo/terceiro tipo..." — conecta aos critérios
- ✅ Exemplo integrado no parágrafo, não em caixa separada

---

## OPERAÇÃO 3: COMPARAR

### Objetivo
Apresentar perspectivas, conceitos ou autores diferentes, destacando onde convergem e divergem.

### O que entra do core
- 2–4 perspectivas (PERSPECTIVA_1, PERSPECTIVA_2...)
- Argumentos de cada perspectiva (ARGUMENTOS_CADA_PERSPECTIVA)
- Exemplo âncora (EXEMPLO_ANCOLA)

### O que sai
Uma seção que: (1) apresenta cada perspectiva com seus argumentos, (2) usa transições de contraste explícitas entre elas, (3) sintetiza convergências e divergências.

---

### EXEMPLO: Marx, Weber, Bourdieu

#### ❌ ERRADO (blocos sem contraste)

```markdown
[PERSPECTIVA: Marx]
Para Marx, a estratificação é determinada pela posição na produção.

[PERSPECTIVA: Weber]
Para Weber, há três dimensões: classe, status e partido.

[COMPARACAO]
[ASPECTO 1] ...
[ASPECTO 2] ...
```

**Problema:** Perspectivas como blocos isolados. O quadro comparativo repete o que foi lido sem acrescentar contraste.

#### ✅ CERTO (fluido, com contraste)

```markdown
### Três visões sobre estratificação

<!-- [TIPO_OPERACAO: Comparar] -->

Três autores formularam explicações diferentes para por que a estratificação existe
e como funciona. Comparar essas perspectivas permite entender o que cada uma ilumina
e o que deixa em segundo plano.

<!-- [PERSPECTIVA: Karl Marx (1818–1883)] -->
#### Marx: Classe como Posição na Produção

Para Marx, a estratificação é determinada pela posição na estrutura produtiva. A
divisão fundamental é entre proprietários dos meios de produção e trabalhadores que
vendem sua força de trabalho. O lucro do proprietário depende do trabalho não pago
ao trabalhador. Nessa visão, todas as outras formas de desigualdade — prestígio,
poder político — derivam da estrutura econômica.

<!-- [AUTOR: Karl Marx (1818–1883) Alemanha] -->
Karl Marx, filósofo e economista alemão, desenvolveu essa análise em *O Capital* (1867).
<!-- [/AUTOR] -->
<!-- [/PERSPECTIVA] -->

<!-- [PERSPECTIVA: Max Weber (1864–1920)] -->
#### Weber: Classe, Status e Partido

Diferindo dessa análise, Max Weber propõe que a estratificação não se reduz à dimensão
econômica. Weber identifica três dimensões independentes: classe (posição econômica no
mercado), status (prestígio social atribuído pelo grupo) e partido (acesso ao poder
político). Uma pessoa pode ter renda alta mas status baixo — como um empresário
"novo-rico" não aceito pela elite tradicional — ou o inverso. Isso significa que a
estratificação é multidimensional, não redutível à economia.

<!-- [AUTOR: Max Weber (1864–1920) Alemanha] -->
Max Weber, sociólogo alemão, distinguiu essas três ordens em *Economia e Sociedade* (1922).
<!-- [/AUTOR] -->
<!-- [/PERSPECTIVA] -->

<!-- [PERSPECTIVA: Pierre Bourdieu (1930–2002)] -->
#### Bourdieu: Capitais Econômico, Cultural e Social

Expandindo a lógica weberiana, Pierre Bourdieu propõe que a estratificação opera
através de múltiplos tipos de capital que se acumulam e se convertem entre si:
econômico (dinheiro, propriedade), cultural (diplomas, hábitos, linguagem) e social
(rede de relações). O aspecto inovador é que o capital cultural — frequentemente
invisível — desempenha papel tão importante quanto o econômico na reprodução das
desigualdades entre gerações. Um filho de professores herda capital cultural que o
coloca em vantagem na escola, mesmo que sua renda seja modesta.

<!-- [AUTOR: Pierre Bourdieu (1930–2002) França] -->
Pierre Bourdieu, sociólogo francês, desenvolveu essa teoria em *A Distinção* (1979).
<!-- [/AUTOR] -->
<!-- [/PERSPECTIVA] -->

<!-- [CONCLUSAO_PARCIAL] -->
**Convergências e divergências:** as três perspectivas convergem em identificar a
desigualdade como estrutural. Divergem quanto aos mecanismos: Marx enfatiza a
exploração econômica direta; Weber acrescenta que prestígio e poder político operam
com lógicas distintas; Bourdieu mostra que a reprodução das posições depende da
transmissão de capital cultural, que funciona de forma menos visível que a econômica.
<!-- [/CONCLUSAO_PARCIAL] -->
```

**O que faz funcionar:**
- ✅ Contraste explícito: "Diferindo dessa análise..." / "Expandindo a lógica weberiana..."
- ✅ Autores aparecem DEPOIS de suas ideias serem desenvolvidas, nunca antes
- ✅ Síntese nomeada mostra convergências E divergências

---

## OPERAÇÃO 4: SEQUENCIAR

### Objetivo
Apresentar eventos em ordem cronológica com encadeamento explícito — não como lista de datas, mas como processo com lógica interna.

### O que entra do core
- Eventos ordenados (EVENTOS)
- Marcos temporais (MARCOS_TEMPORAIS)
- Exemplo âncora (EXEMPLO_ANCOLA)

### O que sai
Uma narrativa cronológica que: (1) integra marcos temporais na prosa, (2) conecta cada evento ao anterior, (3) torna visível a lógica do processo.

---

### EXEMPLO: Independência do Brasil

#### ❌ ERRADO (lista de datas)

```markdown
[SEQUÊNCIA]
1. 1808 — Chegada da família real
2. 1815 — Elevação ao Reino Unido
3. 1820 — Revolução Liberal do Porto
4. 1822 — Independência

[EXEMPLO]
A independência foi um processo gradual...
```

**Problema:** Datas em lista. A lógica do encadeamento não aparece — o aluno vê cronologia, não processo.

#### ✅ CERTO (processo encadeado)

```markdown
### Etapas da Independência do Brasil

<!-- [TIPO_OPERACAO: Sequenciar] -->

<!-- [SEQUENCIA] -->
A independência do Brasil não foi um evento único, mas um processo com etapas
encadeadas. Em 1808, a chegada da família real portuguesa ao Rio de Janeiro
transferiu o centro do poder colonial para a colônia — rompimento sem precedentes
na história americana. Sete anos depois, em 1815, o Brasil foi elevado à condição
de Reino Unido a Portugal e Algarves, alterando formalmente sua posição na hierarquia
imperial.

O encadeamento seguinte veio da Europa: em 1820, a Revolução Liberal do Porto exigiu
o retorno de D. João VI a Lisboa e impôs restrições à autonomia brasileira conquistada
desde 1808. Essa pressão gerou resistência nas elites locais, que viram na manutenção
da corte no Brasil a condição para preservar seus interesses. Em setembro de 1822,
D. Pedro proclamou a independência — não como ruptura abrupta, mas como desfecho de
um processo que a transferência da corte havia iniciado quatorze anos antes.
<!-- [/SEQUENCIA] -->

<!-- [FONTE] -->
NOVAIS, Fernando A. *Portugal e Brasil na crise do antigo sistema colonial*. São Paulo: Hucitec, 1979.
<!-- [/FONTE] -->
```

**O que faz funcionar:**
- ✅ Marcos temporais integrados na prosa, não em lista
- ✅ Cada evento conectado ao anterior: "O encadeamento seguinte veio de..."
- ✅ O aluno vê a lógica do processo, não apenas a cronologia

---

## OPERAÇÃO 5: MAPEAR CAUSALIDADE

### Objetivo
Apresentar relações de causa-consequência de forma que a lógica X → Y seja explícita e sustentada por dado concreto.

### O que entra do core
- Causas (CAUSAS)
- Consequências (CONSEQUENCIAS)
- Relação causal (RELACAO)
- Exemplo âncora (EXEMPLO_ANCOLA)

### O que sai
Blocos de causas, relação e consequências em parágrafos contínuos. A relação causal aparece explicitamente — nunca como listas paralelas.

---

### EXEMPLO: Urbanização Brasileira

#### ❌ ERRADO (listas paralelas)

```markdown
[CAUSAS]
1. Industrialização nas cidades
2. Mecanização da agricultura
3. Expectativa de emprego urbano

[CONSEQUÊNCIAS]
1. Crescimento das cidades
2. Favelização
3. Déficit de infraestrutura
```

**Problema:** Listas paralelas. A relação causal entre os dois conjuntos não aparece.

#### ✅ CERTO (causalidade explícita)

```markdown
### Por que o Brasil urbanizou tão rapidamente

<!-- [TIPO_OPERACAO: Mapear causalidade] -->

<!-- [CAUSA] -->
A urbanização acelerada do Brasil entre 1950 e 1980 resultou da combinação de dois
processos simultâneos. No campo, a modernização da agricultura expulsou trabalhadores
rurais: a mecanização da lavoura e a concentração fundiária reduziram a demanda por
mão de obra manual, tornando insustentável a permanência de milhões de famílias no
interior. Nas cidades, a industrialização — especialmente no ABC paulista a partir
da década de 1950 — criou postos de trabalho assalariado e atraiu migrantes com a
promessa de salário fixo e acesso a serviços inexistentes no campo.
<!-- [/CAUSA] -->

<!-- [RELACAO_CAUSAL] -->
A combinação dessas forças — expulsão rural e atração urbana — produziu um
deslocamento populacional sem paralelo na história brasileira. Entre 1950 e 1980,
a proporção da população urbana passou de 36% para 67%, segundo o IBGE. Esse ritmo
excedeu a capacidade das cidades de absorver os novos habitantes com habitação e
infraestrutura adequadas.
<!-- [/RELACAO_CAUSAL] -->

<!-- [CONSEQUENCIA] -->
A consequência mais visível foi a expansão das favelas e periferias precárias. Sem
acesso a habitação formal, os migrantes ocuparam encostas e áreas de risco, formando
assentamentos sem saneamento básico ou transporte regular. O resultado foi uma
urbanização bifurcada: infraestrutura moderna no centro, déficit estrutural acumulado
na periferia.
<!-- [/CONSEQUENCIA] -->

<!-- [FONTE] -->
SANTOS, Milton. *A urbanização brasileira*. São Paulo: Hucitec, 1993.
<!-- [/FONTE] -->
```

**O que faz funcionar:**
- ✅ Causas em parágrafo narrativo, não em lista
- ✅ Relação causal explícita com dado concreto (36% → 67%)
- ✅ Consequência decorre visivelmente das causas, não é lista paralela

---

## OPERAÇÃO 6: RECONHECER PERSPECTIVA

### Objetivo
Identificar a posição de um autor ou grupo, os argumentos que a sustentam e os interesses subjacentes — não apenas o que defende, mas de onde fala e o que está em jogo.

### O que entra do core
- Perspectivas (PERSPECTIVA_1, PERSPECTIVA_2)
- Argumentos de cada perspectiva (ARGUMENTOS_CADA_PERSPECTIVA)
- Exemplo âncora — texto ou fonte onde a perspectiva se manifesta (EXEMPLO_ANCOLA)

### O que sai
Uma seção que: (1) explicita o que é a operação de reconhecer perspectiva, (2) apresenta cada perspectiva com argumentos E interesses subjacentes, (3) sintetiza por que as perspectivas diferem.

---

### EXEMPLO: Debate sobre a Abolição

#### ❌ ERRADO (opiniões sem sustentação)

```markdown
[PERSPECTIVA 1]
Para os abolicionistas, a escravidão era moralmente errada.

[PERSPECTIVA 2]
Para os escravocratas, a escravidão era economicamente necessária.
```

**Problema:** Perspectivas como afirmações soltas, sem argumentos nem interesses subjacentes. O aluno não aprende a operação — aprende apenas as posições.

#### ✅ CERTO (com argumentos e interesses)

```markdown
### Perspectivas sobre a abolição da escravidão no Brasil

<!-- [TIPO_OPERACAO: Reconhecer perspectiva] -->

Reconhecer uma perspectiva é identificar não apenas o que um grupo defende, mas a
posição social de quem defende e o que está em jogo para esse grupo.

<!-- [PERSPECTIVA: Abolicionistas] -->
#### A perspectiva abolicionista

Os abolicionistas defendiam o fim da escravidão com dois tipos de argumento. O
primeiro era moral: a escravidão violava a dignidade humana e era incompatível com
os princípios liberais que o Império proclamava. O segundo era econômico: o trabalho
escravo era menos produtivo que o trabalho assalariado e impedia a modernização.
Joaquim Nabuco (1849–1910) argumentou em *O Abolicionismo* (1883) que a escravidão
corrompía não apenas o escravo, mas toda a sociedade brasileira, inclusive os senhores.

<!-- [AUTOR: Joaquim Nabuco (1849–1910) Brasil] -->
Joaquim Nabuco, político e escritor pernambucano, foi o principal teórico do
abolicionismo brasileiro.
<!-- [/AUTOR] -->
<!-- [/PERSPECTIVA] -->

<!-- [PERSPECTIVA: Escravocratas] -->
#### A perspectiva escravocrata

Os fazendeiros escravocratas defendiam a manutenção do regime com argumentos
econômicos e jurídicos. Economicamente, argumentavam que a abolição sem indenização
destruiria o patrimônio investido na compra de escravos e inviabilizaria a produção
cafeeira. Juridicamente, o escravo era propriedade legal, e a abolição sem compensação
representaria confisco. Essa perspectiva expressava os interesses da elite agrária que
controlava o Parlamento e cuja produção dependia diretamente do trabalho escravo.
<!-- [/PERSPECTIVA] -->

<!-- [CONCLUSAO_PARCIAL] -->
As duas perspectivas não são apenas opiniões diferentes: expressam posições sociais
distintas e interesses materiais opostos. Reconhecer uma perspectiva exige identificar
quem fala, de onde fala e o que está em jogo para esse grupo.
<!-- [/CONCLUSAO_PARCIAL] -->

<!-- [FONTE] -->
NABUCO, Joaquim. *O Abolicionismo*. Petrópolis: Vozes, 1977 [1883].
<!-- [/FONTE] -->
```

**O que faz funcionar:**
- ✅ Introdução explicita o que é a operação cognitiva
- ✅ Cada perspectiva tem argumentos E interesses subjacentes
- ✅ Síntese explica por que as perspectivas diferem (posição social, não apenas opinião)

---

## OPERAÇÃO 7: APLICAR

### Objetivo
Usar conceitos já definidos para analisar uma situação concreta nova — não apresentada antes no capítulo.

### O que entra do core
- Conceito a aplicar (CONCEITO_A_APLICAR)
- Caso novo (CASO_NOVO)
- Passos da aplicação (PASSOS_DA_APLICACAO)

### O que sai
Uma seção que: (1) situa o caso concreto com dado específico, (2) aplica cada conceito ou perspectiva em sequência com contraste explícito, (3) sintetiza o que cada um explica.

---

### EXEMPLO: Desigualdade de Renda no Brasil

#### ❌ ERRADO (fragmentado)

```markdown
[APLICAÇÃO]
Os conceitos podem ser aplicados ao Brasil...

[CASO]
Em 2023, trabalhadores com ensino superior recebem 3,5x mais...

[PERSPECTIVA: Marx]
Ambos são assalariados, portanto proletariado...

[RESULTADO]
A desigualdade não se explica apenas por classe...
```

**Problema:** Caso, perspectivas e resultado como blocos isolados. A aplicação não mostra o raciocínio em movimento.

#### ✅ CERTO (analítico, com contraste)

```markdown
### Classe, Status e Capital na Desigualdade de Renda no Brasil

<!-- [TIPO_OPERACAO: Aplicar] -->

<!-- [CASO] -->
Em 2023, segundo o IBGE, o rendimento médio mensal de trabalhadores com ensino
superior completo foi aproximadamente 3,5 vezes maior que o de trabalhadores com
ensino médio completo. Ao mesmo tempo, filhos de pais no quintil mais pobre têm
probabilidade significativamente menor de alcançar o quintil mais rico — a
mobilidade intergeracional é limitada. Esses dois fatos indicam que a escolaridade
condiciona a renda e que a posição socioeconômica tende a se reproduzir.
<!-- [/CASO] -->

<!-- [PERSPECTIVA: Marx aplicada] -->
#### O que Marx nos diz

Trabalhadores com ensino médio e com ensino superior vendem igualmente sua força
de trabalho — ambos são assalariados. Pela lógica marxista, pertencem à mesma
classe. No entanto, recebem rendimentos muito diferentes. Isso revela uma limitação
da análise centrada apenas na propriedade dos meios de produção: ela não explica a
desigualdade entre trabalhadores de uma mesma classe.
<!-- [/PERSPECTIVA] -->

<!-- [PERSPECTIVA: Weber aplicada] -->
#### O que Weber nos diz

A análise weberiana oferece mais clareza. Embora ambos sejam assalariados, sua
posição de mercado é diferente: trabalhadores com ensino superior têm qualificações
mais valorizadas, maior poder de barganha e renda mais alta. Além disso, ocupações
que exigem ensino superior tendem a carregar maior prestígio social. Weber captura
essa diferença que Marx deixa em segundo plano.
<!-- [/PERSPECTIVA] -->

<!-- [RESULTADO] -->
**O que cada perspectiva explica:** Marx mostra a divisão estrutural entre
proprietários e assalariados — mas não explica a desigualdade entre assalariados.
Weber mostra que posição de mercado e prestígio criam hierarquias diferentes de
renda, mesmo dentro do trabalho assalariado. Aplicadas em conjunto, essas perspectivas
oferecem uma explicação mais completa de por que a desigualdade de renda no Brasil
é estrutural e se reproduz intergeracionalmente.
<!-- [/RESULTADO] -->

<!-- [FONTE] -->
IBGE. *Síntese de Indicadores Sociais*, 2023.
<!-- [/FONTE] -->
```

**O que faz funcionar:**
- ✅ Caso concreto situado com dado específico antes da análise
- ✅ Cada perspectiva aplicada em sequência com contraste explícito
- ✅ Síntese responde "o que cada perspectiva explica" — não repete, acrescenta

---

## TRANSIÇÕES DENOTATIVAS — Banco de Frases

### Definição → exemplo
```
Isso pode ser observado em...
Um exemplo concreto disso é...
Dados concretos ilustram essa distribuição:
Para ilustrar, consideremos...
```

### Classificação → subtipo
```
Um primeiro tipo, baseado em [critério], é...
Um segundo tipo ocorre quando [critério] determina...
Contrastando com os anteriores, o terceiro tipo...
```

### Perspectiva → perspectiva (contraste)
```
Diferindo dessa análise, [Autor B] propõe...
Expandindo a lógica de [Autor A], [Autor B] acrescenta...
Enquanto [Autor A] enfatiza..., [Autor B] identifica...
```

### Causa → relação → consequência
```
A combinação dessas forças produziu...
O resultado direto foi...
Isso gerou, como consequência imediata...
```

### Sequência → próximo evento
```
O encadeamento seguinte veio de...
Esse processo culminou em...
A etapa seguinte resultou de...
```

### Perspectiva/conceito → aplicação
```
Aplicando essa lógica ao contexto brasileiro...
Esses conceitos iluminam os dados da seguinte forma...
O caso brasileiro revela como...
```

### Perspectivas → síntese
```
As perspectivas convergem em... mas divergem quanto a...
Cada perspectiva captura algo que as outras deixam em segundo plano...
Tomadas em conjunto, essas análises revelam...
```

---

## MARCADORES DE IMAGEM

O pipeline não insere imagens no material — o professor as busca e o InDesign as posiciona. Seu papel é indicar **onde** deve haver uma imagem e **o que** ela deve mostrar, inserindo um marcador HTML comment no texto:

```
<!-- [IMAGEM: Descrição detalhada do que a imagem deve mostrar] -->
```

### Quando inserir

Insira um marcador **imediatamente após o parágrafo** que o visual ilustraria, nos seguintes casos:

- **Diagrama comparativo**: operação Comparar com 2 ou mais perspectivas → quadro com colunas por autor/perspectiva
- **Linha do tempo**: operação Sequenciar com 3+ etapas históricas → linha do tempo com marcos e datas
- **Processo em etapas**: operação Mapear causalidade com encadeamento claro → diagrama causa → efeito
- **Dados estatísticos**: percentuais, proporções ou evolução numérica ao longo do tempo → gráfico de barras ou linha
- **Mapa ou distribuição espacial**: fenômeno com dimensão geográfica explícita → mapa temático
- **Classificação com subtipos**: operação Classificar com 3+ subtipos → quadro ou tabela com critérios e exemplos

### Quando NÃO inserir

- Quando o parágrafo não tem dado visual concreto (apenas prosa argumentativa)
- Quando a operação não exige visualização (Definir com exemplo simples já é autoexplicativo)
- Quando já há um marcador no mesmo bloco para o mesmo tipo de visual

### Regras de quantidade e descrição

- **Máximo: 2 marcadores por bloco** (seção delimitada por `###`)
- **Mínimo de 1 bloco sem imagem** por capítulo — nem tudo precisa de visual
- A descrição deve ser **específica o suficiente** para o professor saber o que buscar ou criar:

```
<!-- [IMAGEM: Linha do tempo com 4 marcos: solidariedade mecânica (pré-industrial) → industrialização → solidariedade orgânica (sec. XIX) → sociedades complexas (atual)] -->
```

```
<!-- [IMAGEM: Quadro comparativo com 3 colunas (Durkheim / Marx / Weber) e 3 linhas (Foco analítico / Causa da desigualdade / Papel do indivíduo)] -->
```

```
<!-- [IMAGEM: Gráfico de barras mostrando proporção da população urbana no Brasil em 1950 (36%) e 1980 (67%)] -->
```

### Posição no texto

O marcador vai em linha separada, imediatamente **após** o parágrafo que ele ilustra, **antes** de qualquer `<!-- [AUTOR] -->` ou `<!-- [FONTE] -->` da seção:

```markdown
<!-- [CAUSA] -->
A urbanização acelerada resultou de dois processos simultâneos...
<!-- [/CAUSA] -->

<!-- [IMAGEM: Diagrama mostrando seta dupla entre expulsão rural (mecanização) e atração urbana (industrialização), convergindo para crescimento das cidades] -->

<!-- [RELACAO_CAUSAL] -->
A combinação dessas forças produziu um deslocamento sem paralelo...
```

---

## Proibições de estilo

- Travessões para aposto — use vírgulas ou parênteses
- "Nós", "a gente", "nosso"
- Exclamações (!)
- "Interessantemente", "surpreendentemente" e outros advérbios de opinião
- Adjetivos avaliativos ("o maior", "brilhante", "genial")
- Listas com marcadores (`-`) dentro dos blocos — use números ou parágrafos contínuos
- Andaime: "como vimos", "agora vamos", "vale lembrar que"
- Metáforas poéticas ou dramatizantes
- Perguntas retóricas

---

## Checklist de entrega

Antes de salvar `texto.md`:

- [ ] Começa com bloco `<!-- [CONTEXTO_OPERACAO] -->` com os quatro campos?
- [ ] Cada seção tem cabeçalho idêntico ao `CABECALHO` do core?
- [ ] Toda marcação estrutural está em HTML comments — nenhum rótulo visível?
- [ ] Definição e exemplo integrados no mesmo bloco com transição denotativa?
- [ ] Para Classificar: cada subtipo começa conectando aos critérios introduzidos?
- [ ] Para Comparar: cada perspectiva tem transição de contraste ("Diferindo...", "Expandindo...")?
- [ ] Para Sequenciar: marcos temporais na prosa, não em lista?
- [ ] Para Mapear causalidade: relação causal X → Y explícita com dado concreto?
- [ ] Para Reconhecer perspectiva: argumentos E interesses subjacentes presentes?
- [ ] AUTOREs aparecem APÓS suas ideias serem desenvolvidas, nunca antes?
- [ ] Nenhum bloco VERIFICACAO no texto?
- [ ] SINTESE_FINAL responde literalmente à pergunta do capítulo?
- [ ] Inseriu marcadores `<!-- [IMAGEM: ...] -->` nos momentos adequados (máx. 2 por bloco, descrição específica)?
- [ ] Nenhuma das proibições de estilo foi violada?
