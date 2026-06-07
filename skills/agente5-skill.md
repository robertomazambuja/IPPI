# SKILL — AGENTE 5: FORMATADOR (XML para InDesign)

## O que você faz

Lê o texto qualificado do Agente 4 (prosa com marcação em HTML comments, normalizada pelo Agente 3), extrai a estrutura, conta palavras por bloco e produz XML padronizado que o InDesign consegue ler e distribuir em páginas A4 equilibradas.

---

## Input: O que você recebe

Arquivo `texto/01-0X-...md` com HTML comments normalizados. Estrutura típica:

```markdown
<!-- [CONTEXTO_OPERACAO] -->
**Habilidade:** H12 — Texto da habilidade.
**Operação principal:** Mapear causalidade
**Pergunta do capítulo:** Como...?
**Por que importa:** Este capítulo...
<!-- [/CONTEXTO_OPERACAO] -->

### Título da primeira seção

<!-- [DEFINICAO] -->
Texto da definição...
<!-- [/DEFINICAO] -->

<!-- [AUTOR: Nome (datas) País | ref=definicao] -->
Box biográfico...
<!-- [/AUTOR] -->

<!-- [FONTE] -->
SOBRENOME, Nome. *Título*. Cidade: Editora, Ano.
<!-- [/FONTE] -->

### Título da segunda seção

<!-- [CLASSIFICACAO] -->
Introdução dos critérios...
<!-- [/CLASSIFICACAO] -->

<!-- [SUBTIPO: Nome do subtipo] -->
Texto do subtipo...
<!-- [/SUBTIPO] -->

## Síntese

<!-- [SINTESE] -->
Texto da síntese...
<!-- [/SINTESE] -->

<!-- [ENCADEAMENTO] -->
Texto do encadeamento...
<!-- [/ENCADEAMENTO] -->
```

---

## Output: O que você produz

Arquivo `formatado/01-0X-...xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<capitulo id="01-01" titulo="Título do capítulo" palavras_total="2600">

  <cabecalho>
    <habilidade>H12 — Texto completo.</habilidade>
    <operacao_principal>Mapear causalidade</operacao_principal>
    <pergunta_capitulo>Como...?</pergunta_capitulo>
    <por_que_importa>Este capítulo...</por_que_importa>
  </cabecalho>

  <corpo>

    <bloco id="bloco-1" palavras="406">
      <secao id="sec-1" tipo="definicao">
        <titulo>Título da seção ###</titulo>
        <conteudo>
          <paragrafo>Texto do parágrafo.</paragrafo>
        </conteudo>
        <sidebar tipo="autor">
          <nome>Nome Completo (datas)</nome>
          <pais>Brasil</pais>
          <instituicao>Instituição</instituicao>
          <descricao>Texto biográfico.</descricao>
        </sidebar>
      </secao>
      <nota_fonte>SOBRENOME, Nome. Título. Cidade: Editora, Ano.</nota_fonte>
    </bloco>

    <quebra tipo="pagina" sugestao="forte"/>

    <bloco id="bloco-2" palavras="700">
      <secao id="sec-2" tipo="classificacao">
        <titulo>Título da seção ###</titulo>
        <introducao>Parágrafo introdutório da classificação.</introducao>
        <lista-subtipos>
          <item tipo="subtipo" nome="Nome do Subtipo">
            <conteudo>Texto do subtipo.</conteudo>
            <exemplo nome="Nome do Exemplo">Texto do exemplo.</exemplo>
          </item>
        </lista-subtipos>
        <sidebar tipo="autor">
          <nome>Nome (datas)</nome>
          <pais>País</pais>
          <instituicao>Instituição</instituicao>
          <descricao>Texto biográfico.</descricao>
        </sidebar>
      </secao>
      <nota_fonte>SOBRENOME, Nome. Título. Cidade: Editora, Ano.</nota_fonte>
    </bloco>

    <bloco id="bloco-3" palavras="500">
      <secao id="sec-3" tipo="perspectiva">
        <titulo>Título</titulo>
        <conteudo>
          <paragrafo>Texto...</paragrafo>
        </conteudo>
        <sidebar tipo="autor">
          <nome>Nome (datas)</nome>
          <pais>País</pais>
          <instituicao>Instituição</instituicao>
          <descricao>Texto biográfico.</descricao>
        </sidebar>
      </secao>
      <verificacoes>
        <sidebar id="v1" tipo="verificacao">
          <pergunta>Qual dos elementos...?</pergunta>
          <opcoes>
            <opcao letra="a">Opção A</opcao>
            <opcao letra="b" correta="true">Opção B</opcao>
            <opcao letra="c">Opção C</opcao>
          </opcoes>
          <resposta_oculta>b</resposta_oculta>
          <justificativa>Explicação da resposta correta.</justificativa>
        </sidebar>
      </verificacoes>
      <nota_fonte>SOBRENOME, Nome. Título. Cidade: Editora, Ano.</nota_fonte>
    </bloco>

  </corpo>

  <rodape>
    <sintese>Texto da síntese final.</sintese>
    <encadeamento>Texto do encadeamento para o próximo capítulo.</encadeamento>
  </rodape>

</capitulo>
```

---

## Procedimento

### Passo 1: Ler o arquivo

Leia o arquivo `.md` completo antes de começar.

### Passo 2: Extrair o cabeçalho

Do bloco `<!-- [CONTEXTO_OPERACAO] -->`, extraia os quatro campos em markdown bold e monte o `<cabecalho>`. Se um campo tiver valor `[AUSENTE]`, omita o elemento correspondente e insira um comentário XML `<!-- WARNING: campo ausente -->`.

### Passo 3: Identificar os blocos

Cada seção `###` do markdown é um `<bloco>`. Conte as palavras do texto visível de cada bloco — excluindo o conteúdo dos HTML comments, apenas o texto que o aluno leria. Registre o total em `palavras=`.

### Passo 4: Montar cada bloco

Para cada seção `###`, em ordem:

1. Identifique os tipos de bloco presentes (use a tabela de mapeamento abaixo)
2. Monte as `<secao>` na ordem em que aparecem no texto
3. Posicione o `<sidebar tipo="autor">` dentro da `<secao>` correta:
   - AUTOR aninhado no bloco pai no markdown → insira dentro da secao correspondente
   - AUTOR com `ref=tipo` → insira dentro da secao daquele tipo
   - Quando dois AUTOREs têm o mesmo `ref=`, gere dois `<sidebar tipo="autor">` dentro da mesma `<secao>`, na ordem em que aparecem
4. Se houver `<!-- [VERIFICACAO] -->` no bloco, agrupe todas as verificações do bloco em `<verificacoes>`, posicionada após as `<secao>` e antes de `<nota_fonte>`
5. Posicione `<nota_fonte>` como último filho do `<bloco>`, fora das `<secao>`

### Passo 5: Inserir quebras de página

Calcule a acumulação de palavras bloco a bloco. Quando o acumulado ultrapassar **1.300 palavras**, insira `<quebra tipo="pagina" sugestao="forte"/>` após o bloco que cruzou o limiar e zere o contador para o próximo bloco.

Use `sugestao="fraca"` quando a diferença entre o limiar e o acumulado for menor que 150 palavras — indica que a quebra pode ser ajustada pelo diagramador sem problema.

Exemplo com blocos de 400, 700, 700, 800 palavras:
- bloco-1: acumulado 400 → sem quebra
- bloco-2: acumulado 1.100 → sem quebra (não ultrapassou)
- Antes de bloco-3: 1.100 + 700 = 1.800 → inserir quebra após bloco-2, zerar contador
- bloco-3: acumulado 700 → sem quebra
- bloco-4: acumulado 1.500 → inserir quebra após bloco-4 se houver mais conteúdo

### Passo 6: Montar o rodapé

`<!-- [SINTESE] -->` → `<sintese>` dentro de `<rodape>`.
`<!-- [ENCADEAMENTO] -->` → `<encadeamento>` dentro de `<rodape>`.

Esses dois elementos **nunca** aparecem dentro de `<corpo>`. Se estiverem posicionados dentro de uma seção `###` no markdown, extraia-os para o rodapé mesmo assim.

### Passo 7: Calcular palavras_total

Some todas as palavras de todos os blocos e registre em `palavras_total=` no elemento raiz `<capitulo>`.

### Passo 8: Salvar

Salve em: `output/{apostila}/formatado/{unidade-slug}/{filename}.xml`

---

## Mapeamento de Tipos de Seção

```
<!-- [DEFINICAO] -->               → <secao tipo="definicao">
<!-- [CLASSIFICACAO] -->           → <secao tipo="classificacao"> com <lista-subtipos> para os SUBTIPO filhos
<!-- [SUBTIPO: Nome] -->           → <item tipo="subtipo" nome="Nome"> dentro de <lista-subtipos>
<!-- [PERSPECTIVA: Nome] -->       → <secao tipo="perspectiva">
<!-- [PERSPECTIVA_A: Nome] -->     → <secao tipo="perspectiva">
<!-- [PERSPECTIVA_B: Nome] -->     → <secao tipo="perspectiva">
<!-- [PERSPECTIVA_C: Nome] -->     → <secao tipo="perspectiva">
<!-- [EXEMPLO: Desc] -->           → <exemplo nome="Desc"> filho da secao ou item que o contém
<!-- [CAUSA] -->                   → <secao tipo="causa">
<!-- [CONSEQUENCIA] -->            → <secao tipo="consequencia">
<!-- [RELACAO_CAUSAL] -->          → <secao tipo="relacao-causal">
<!-- [INTRODUCAO_COMPARACAO] -->   → <secao tipo="introducao-comparacao">
<!-- [COMPARACAO] -->              → <secao tipo="comparacao">
<!-- [APLICACAO: Desc] -->         → <secao tipo="aplicacao">
<!-- [CONCLUSAO_PARCIAL] -->       → <secao tipo="conclusao-parcial">
<!-- [RESULTADO] -->               → <secao tipo="resultado">
<!-- [AUTOR: ...] -->              → <sidebar tipo="autor"> filho da secao correta
<!-- [FONTE] -->                   → <nota_fonte> filho do bloco
<!-- [FONTE_PRIMARIA: ...] -->     → <nota_fonte tipo="primaria"> filho do bloco
<!-- [VERIFICACAO: Qn] -->         → <sidebar tipo="verificacao"> dentro de <verificacoes>
<!-- [APRESENTACAO] -->            → <secao tipo="definicao"> (compatibilidade com apostilas legadas)
<!-- [SINTESE] -->                 → <sintese> dentro de <rodape>
<!-- [ENCADEAMENTO] -->            → <encadeamento> dentro de <rodape>
```

**Tipo não reconhecido** (sinalizado pelo Agente 3 com `AVISO_AGENTE5`):
→ Gerar `<secao tipo="generico" aviso="tipo X nao mapeado">`. Nunca descartar conteúdo.

---

## Regras específicas

### VERIFICACAO ausente
Se nenhum bloco `<!-- [VERIFICACAO] -->` for encontrado no arquivo inteiro, o elemento `<verificacoes>` é omitido de todos os blocos. Não gere `<verificacoes/>` vazio.

### EXEMPLO aninhado dentro de SUBTIPO ou CONCLUSAO_PARCIAL
Gere o `<exemplo>` como filho direto do `<item tipo="subtipo">` ou da `<secao tipo="conclusao-parcial">`, não como secao irmã no `<corpo>`.

### CLASSIFICACAO com SUBTIPOs
O texto introdutório da CLASSIFICACAO (antes do primeiro SUBTIPO) vai em `<introducao>`. Cada SUBTIPO vira um `<item>` dentro de `<lista-subtipos>`. O `<sidebar tipo="autor">` da seção vai depois da `<lista-subtipos>`, ainda dentro da `<secao tipo="classificacao">`.

### AUTOR com múltiplos autores no mesmo bloco
Dois AUTOREs com o mesmo `ref=` geram dois `<sidebar tipo="autor">` dentro da mesma `<secao>`, na ordem em que aparecem no texto.

---

## Checklist de validação antes de salvar

- [ ] `palavras_total=` calculado e presente no `<capitulo>`?
- [ ] Cada `<bloco>` tem `palavras=` calculado?
- [ ] `<cabecalho>` tem os quatro campos (ou WARNING para ausentes)?
- [ ] Todo AUTOR está dentro de uma `<secao>`, nunca solto no `<corpo>`?
- [ ] Toda FONTE está como `<nota_fonte>` filho do `<bloco>`, fora das `<secao>`?
- [ ] `<verificacoes>` presente apenas nos blocos que têm VERIFICACAO?
- [ ] `<sintese>` e `<encadeamento>` estão em `<rodape>`, nunca em `<corpo>`?
- [ ] Nenhum tipo foi descartado (generico para os não mapeados)?
- [ ] Quebras de página inseridas na posição correta?
- [ ] XML válido (sem tags abertas, sem caracteres especiais não escapados)?
