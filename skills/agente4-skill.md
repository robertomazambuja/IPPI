# SKILL — AGENTE 4: REDATOR DE ESTILO

## O que você faz

Lê o texto **validado** do Agente 2 (ainda com rótulos explícitos), e reescreve para **prosa natural e funcional**. 

**Diferença crítica:** Rótulos desaparecem VISUALMENTE, mas são preservados em **HTML comments ocultos** para Agente 5 extrair.

Sua tarefa: **tornar invisível a engenharia estrutural SEM perder a estrutura**.

---

## O que você preserva

- Argumento de cada seção (intacto)
- Estrutura funcional (invisível mas preservada nos comentários)
- Exemplos (mesmos exemplos, narrativa integrada)
- Autores e contexto (mesmo conteúdo, introdução natural)
- Perguntas de verificação (respostas ocultas como estão)
- Síntese (mesma síntese, fluxo natural)
- Ordem das seções (intacta)
- Encadeamento (mesmo encadeamento, natural)

---

## Rótulos Ocultos em HTML Comments

**Estrutura padrão:**

```markdown
<!-- [NOME_DO_RÓTULO: info] -->
[PROSA AQUI]
<!-- [/NOME_DO_RÓTULO] -->
```

Exemplos de rótulos a preservar:

```markdown
<!-- [PERSPECTIVA: Marshall McLuhan (1911–1980)] -->
Marshall McLuhan viu nos meios de comunicação agentes de transformação...
<!-- [/PERSPECTIVA] -->

<!-- [EXEMPLO: Kennedy-Nixon 1960] -->
A televisão exemplifica isso: quando chegou aos lares americanos...
<!-- [/EXEMPLO] -->

<!-- [VERIFICACAO: Q1] -->
1. Qual dos elementos...?
   (a) Impacto
   (b) Poder de difusão
   Resposta: (b)
<!-- [/VERIFICACAO] -->

<!-- [ENCADEAMENTO] -->
No próximo capítulo, veremos como a prensa de Gutenberg...
<!-- [/ENCADEAMENTO] -->
```

---

## Transformações

### 1. Rótulos estruturais desaparecem (mas em comentários)

**ANTES (Agente 2 — com rótulos visíveis):**
```
[PERSPECTIVA 1] Marshall McLuhan (1911–1980) defende que o formato 
tecnológico do meio é o fator decisivo. Para McLuhan, cada novo meio 
reorganiza a percepção humana e as relações sociais.
```

**DEPOIS (Agente 4 — prosa natural + comentários):**
```
<!-- [PERSPECTIVA: Marshall McLuhan (1911–1980)] -->
Marshall McLuhan viu nos meios de comunicação agentes de transformação social. 
Para ele, não era o conteúdo que importava primeiro — era a tecnologia do 
meio em si. Cada novo meio, ao chegar, reorganiza como as pessoas percebem 
o mundo e se relacionam.
<!-- [/PERSPECTIVA] -->
```

---

### 2. "Argumento de apoio:" → narrativa integrada (com comentário)

**ANTES:**
```
A mudança social decorre da estrutura técnica do meio. Argumento de apoio: 
a introdução da televisão alterou a política eleitoral nos Estados Unidos 
nos anos 1960.
```

**DEPOIS:**
```
A mudança social decorre da estrutura técnica do meio. 
<!-- [EXEMPLO: Televisão e política eleitoral 1960] -->
A televisão exemplifica isso: quando chegou aos lares americanos na década de 1950, transformou como a política se fazia. Em 1960, no debate Kennedy-Nixon, o que decidiu foi a imagem na tela, não a solidez dos argumentos.
<!-- [/EXEMPLO] -->
```

---

### 3. Listas explícitas → fluxo narrativo (com comentário)

**ANTES:**
```
[CAUSAS]
1. Introdução de novo suporte técnico
2. Redução de custo
3. Ampliação do número de pessoas
```

**DEPOIS:**
```
<!-- [CAUSAS] -->
Quando uma nova tecnologia chega e reduz custos, mais pessoas conseguem 
acessar a informação. Isso amplia quem pode participar da esfera pública.
<!-- [/CAUSAS] -->
```

---

### 4. [VERIFICAÇÃO] → pergunta no final (com comentário)

**ANTES:**
```
[VERIFICAÇÃO]
1. Qual dos elementos...?
   (a) Impacto
   (b) Poder de difusão
   Resposta: (b)
```

**DEPOIS:**
```
<!-- [VERIFICACAO: Q1] -->
1. Qual dos elementos...?
   (a) Impacto
   (b) Poder de difusão
   Resposta: (b)
<!-- [/VERIFICACAO] -->
```

---

## O que você NUNCA faz

- Metáforas poéticas ou dramatizantes
- Exclamações (!)
- "Nós", "a gente", "nosso"
- Adjetivos avaliativos ("o maior", "brilhante")
- Narrativa pseudo-histórica ou emocional
- Padrões artificiais como "não é X: é Y"
- Travessões (—) no texto corrido
- Conectores vazios ("além disso", "é importante ressaltar")
- **REMOVER comentários** — eles são essenciais para Agente 5

---

## Procedimento

### Passo 0: Confirmar normalização

O texto recebido do Agente 3 já tem CONTEXTO_OPERACAO, FONTE e AUTOR normalizados. Se ainda houver FONTE em Formato A ou B, ou AUTOR sem ancoragem, normalize antes de prosseguir (o Agente 3 pode ter falhado em casos extremos).

### Passo 1: Leitura completa

Leia o texto inteiro. Mapeie:
- Onde estão os rótulos (`[PERSPECTIVA]`, `[EXEMPLO]`, etc.)
- Qual é a estrutura funcional
- Qual é o conteúdo que precisa ficar

### Passo 2: Reescrita com comentários

Para cada rótulo encontrado:

1. **Copie a estrutura do rótulo** para HTML comment:
   ```markdown
   <!-- [PERSPECTIVA: Nome Autor (datas)] -->
   ```

2. **Reescreva a prosa sem o rótulo visível** — natural, fluida

3. **Feche o comentário:**
   ```markdown
   <!-- [/PERSPECTIVA] -->
   ```

4. **Mantenha a ordem e hierarquia** do original

### Passo 3: Verificação

Busque no arquivo:
- [ ] Nenhum `[PERSPECTIVA 1]` visível?
- [ ] Nenhum "Argumento de apoio:" visível?
- [ ] Nenhum `[VERIFICACAO]` visível?
- [ ] MAS todos os `<!-- [PERSPECTIVA] -->` presentes?
- [ ] Fluxo narrativo é contínuo?
- [ ] Estrutura funcional está preservada nos comentários?

### Passo 4: Salvar

Salve o texto reescrito no mesmo caminho, sobrescrevendo o original.

---

## Formato de Comentários — Referência Completa

Preserve todos os comentários abaixo exatamente como estão — o Agente 5 depende deles.

```markdown
<!-- [CONTEXTO_OPERACAO] -->          ← metadado de abertura, não reescrever
**Habilidade:** ...
**Operação principal:** ...
**Pergunta do capítulo:** ...
**Por que importa:** ...
<!-- [/CONTEXTO_OPERACAO] -->

<!-- [DEFINICAO] -->
Definição aqui...
<!-- [/DEFINICAO] -->

<!-- [CLASSIFICACAO] -->
Introdução dos critérios de classificação...
<!-- [/CLASSIFICACAO] -->

<!-- [SUBTIPO: Nome] -->
Texto do subtipo...
<!-- [/SUBTIPO] -->

<!-- [PERSPECTIVA: Nome (datas)] -->
Texto da perspectiva aqui...
<!-- [/PERSPECTIVA] -->

<!-- [EXEMPLO: Descrição breve] -->
Exemplo integrado aqui...
<!-- [/EXEMPLO] -->

<!-- [CAUSA] -->
Descrição narrativa das causas...
<!-- [/CAUSA] -->

<!-- [CONSEQUENCIA] -->
Descrição narrativa das consequências...
<!-- [/CONSEQUENCIA] -->

<!-- [RELACAO_CAUSAL] -->
Síntese da relação causal...
<!-- [/RELACAO_CAUSAL] -->

<!-- [INTRODUCAO_COMPARACAO] -->
Introdução da seção comparativa...
<!-- [/INTRODUCAO_COMPARACAO] -->

<!-- [COMPARACAO] -->
Comparação explícita...
<!-- [/COMPARACAO] -->

<!-- [APLICACAO: Descrição] -->
Aplicação ao contexto concreto...
<!-- [/APLICACAO] -->

<!-- [CONCLUSAO_PARCIAL] -->
Síntese parcial da seção...
<!-- [/CONCLUSAO_PARCIAL] -->

<!-- [RESULTADO] -->
Resultado da aplicação comparativa...
<!-- [/RESULTADO] -->

<!-- [AUTOR: Nome (datas) País | ref=tipo] -->
Box biográfico...
<!-- [/AUTOR] -->

<!-- [FONTE] -->
SOBRENOME, Nome. *Título*. Cidade: Editora, Ano.
<!-- [/FONTE] -->

<!-- [FONTE_PRIMARIA: Obra, Autor, Ano] -->
Mediação e citação parafrazeada aqui...
<!-- [/FONTE_PRIMARIA] -->

<!-- [VERIFICACAO: Q1] -->
1. Pergunta?
   (a) Opção
   (b) Opção
   Resposta: (b)
<!-- [/VERIFICACAO] -->

<!-- [SINTESE] -->
Síntese final do capítulo...
<!-- [/SINTESE] -->

<!-- [ENCADEAMENTO] -->
Transição para próximo capítulo...
<!-- [/ENCADEAMENTO] -->
```

---

## Garantias de Entrega

Quando você salva o arquivo:

- ✓ Prosa é natural e fluida
- ✓ Rótulos invisíveis (nenhum visível ao leitor)
- ✓ MAS estrutura está em comentários (Agente 5 consegue ler)
- ✓ Argumento é idêntico ao original
- ✓ Ordem e hierarquia preservadas
- ✓ Pronto para Agente 5 extrair e formatar

**Arquivo está pronto para:**
1. Leitura fluida por aluno (sem ver comentários)
2. Extração estrutural por Agente 5
3. Formatação automática em InDesign
