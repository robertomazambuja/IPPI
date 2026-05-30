# SKILL — AGENTE 5: FORMATADOR (XML para InDesign)

## O que você faz

Lê o texto **qualificado** do Agente 4 (prosa natural com rótulos **ocultos em HTML comments**), extrai a estrutura funcional, e produz **XML padronizado** que InDesign consegue ler e formatar automaticamente.

Seu papel: **transformar prosa + comentários em documento estruturado com caixas sempre no mesmo lugar**.

---

## Input: O que você recebe

Arquivo: `texto/01-01-...md`

Exemplo:
```markdown
# Capítulo 1: Conceitos fundamentais — O que é um meio de comunicação?

Pergunta: Como evoluíram os meios de comunicação...
Habilidade: EM13CHS201 - Analisar a importância...

<!-- [PERSPECTIVA: Marshall McLuhan (1911–1980)] -->
Marshall McLuhan viu nos meios de comunicação agentes de transformação...
<!-- [/PERSPECTIVA] -->

<!-- [EXEMPLO: Kennedy-Nixon 1960] -->
A televisão exemplifica isso: quando chegou...
<!-- [/EXEMPLO] -->

<!-- [VERIFICACAO: Q1] -->
1. Qual dos elementos...?
   (a) Impacto
   (b) Poder de difusão
   Resposta: (b)
<!-- [/VERIFICACAO] -->

<!-- [ENCADEAMENTO] -->
No próximo capítulo, veremos como a prensa...
<!-- [/ENCADEAMENTO] -->
```

---

## Output: O que você produz

Arquivo: `formatado/01-01-...xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<capitulo id="01-01" titulo="Conceitos fundamentais — O que é um meio de comunicação?">
  
  <!-- ======================================== -->
  <!-- CABEÇALHO: Pergunta + Habilidade (Caixas) -->
  <!-- ======================================== -->
  <cabecalho>
    <caixa tipo="pergunta">
      <titulo>Pergunta do Capítulo</titulo>
      <conteudo>Como evoluíram os meios de comunicação e qual seu impacto nas estruturas de poder e na formação da cidadania?</conteudo>
    </caixa>
    
    <caixa tipo="habilidade">
      <titulo>Habilidade BNCC</titulo>
      <codigo>EM13CHS201</codigo>
      <descricao>Analisar a importância dos meios de comunicação para a formação da opinião pública, reconhecendo perspectivas distintas sobre seu papel na sociedade.</descricao>
    </caixa>
  </cabecalho>

  <!-- ======================================== -->
  <!-- CORPO: Seções estruturadas -->
  <!-- ======================================== -->
  <corpo>
    
    <secao id="sec-1" tipo="perspectiva">
      <titulo>Marshall McLuhan (1911–1980)</titulo>
      <tipo_secao>Perspectiva</tipo_secao>
      <conteudo>
        <paragrafo>Marshall McLuhan viu nos meios de comunicação agentes de transformação social. Para ele, não era o conteúdo que importava primeiro — era a tecnologia do meio em si. Cada novo meio, ao chegar, reorganiza como as pessoas percebem o mundo e se relacionam.</paragrafo>
      </conteudo>
    </secao>

    <secao id="sec-2" tipo="exemplo">
      <titulo>Kennedy-Nixon 1960</titulo>
      <tipo_secao>Exemplo</tipo_secao>
      <conteudo>
        <paragrafo>A televisão exemplifica isso: quando chegou aos lares americanos na década de 1950, transformou como a política se fazia. Em 1960, no debate Kennedy-Nixon, o que decidiu foi a imagem na tela, não a solidez dos argumentos.</paragrafo>
      </conteudo>
    </secao>

  </corpo>

  <!-- ======================================== -->
  <!-- SIDEBARS: Verificações (Respostas ocultas) -->
  <!-- ======================================== -->
  <sidebars>
    <sidebar id="v1" tipo="verificacao">
      <titulo>Verificação</titulo>
      <pergunta>Qual dos elementos é mais importante segundo McLuhan?</pergunta>
      <opcoes>
        <opcao letra="a">Impacto</opcao>
        <opcao letra="b" correta="true">Poder de difusão</opcao>
        <opcao letra="c">Suporte técnico</opcao>
      </opcoes>
      <resposta_oculta>b</resposta_oculta>
      <justificativa>McLuhan defendia que a tecnologia do meio era o fator decisivo, não o conteúdo transmitido.</justificativa>
    </sidebar>
  </sidebars>

  <!-- ======================================== -->
  <!-- RODAPÉ: Encadeamento -->
  <!-- ======================================== -->
  <rodape>
    <encadeamento>
      <titulo>Próximo Capítulo</titulo>
      <conteudo>No próximo capítulo, veremos como a prensa de Gutenberg revolucionou a disseminação de informação.</conteudo>
    </encadeamento>
  </rodape>

</capitulo>
```

---

## Procedimento

### Passo 1: Ler o arquivo markdown

Abra o arquivo `texto/01-01-...md` gerado pelo Agente 4.

### Passo 2: Extrair estrutura pelos comentários

**Procure por padrões:**

1. **Título do capítulo** — Primeira linha com `# Capítulo...`
2. **Pergunta** — Linha com "Pergunta:"
3. **Habilidade** — Linha com "Habilidade:"
4. **Seções** — Blocos entre `<!-- [TIPO: info] -->` e `<!-- [/TIPO] -->`
5. **Verificações** — Blocos entre `<!-- [VERIFICACAO: Qn] -->` e `<!-- [/VERIFICACAO] -->`
6. **Encadeamento** — Bloco entre `<!-- [ENCADEAMENTO] -->` e `<!-- [/ENCADEAMENTO] -->`

### Passo 3: Estruturar em XML

Montar XML com esta hierarquia:

```
<capitulo>
  ├── <cabecalho>           ← Caixas (pergunta + habilidade)
  ├── <corpo>               ← Seções (perspectiva, exemplo, etc.)
  ├── <sidebars>            ← Verificações (com resposta oculta)
  └── <rodape>              ← Encadeamento
```

### Passo 4: Gerar IDs únicos

Para cada elemento, gere ID:
```
id="sec-1", "sec-2", ... (seções)
id="v1", "v2", ... (verificações)
```

### Passo 5: Salvar XML

Salve em: `output/{apostila}/formatado/{unidade-slug}/{filename}.xml`

---

## Mapeamento de Tipos de Seção

```xml
<!-- [PERSPECTIVA: Nome] -->     →  <secao tipo="perspectiva">
<!-- [DEFINICAO] -->             →  <secao tipo="definicao">
<!-- [EXEMPLO: Desc] -->         →  <secao tipo="exemplo">
<!-- [AUTOR: Nome] -->           →  <secao tipo="autor">
<!-- [FONTE_PRIMARIA: ...] -->   →  <secao tipo="fonte_primaria">
<!-- [CAUSAS] -->                →  <secao tipo="causas">
<!-- [CONSEQUENCIAS] -->         →  <secao tipo="consequencias">
<!-- [VERIFICACAO: Qn] -->       →  <sidebar tipo="verificacao">
<!-- [ENCADEAMENTO] -->          →  <encadeamento>
```

---

## Formato de Resposta Oculta

**Sempre use este padrão para verificações:**

```xml
<sidebar id="v1" tipo="verificacao">
  <pergunta>Qual elemento...?</pergunta>
  <opcoes>
    <opcao letra="a">Opção A</opcao>
    <opcao letra="b" correta="true">Opção B (CORRETA)</opcao>
    <opcao letra="c">Opção C</opcao>
  </opcoes>
  <resposta_oculta>b</resposta_oculta>
  <justificativa>Por que essa é a resposta correta...</justificativa>
</sidebar>
```

**Importante:** `correta="true"` marca qual é a opção correta. `resposta_oculta` guarda apenas a letra. InDesign lerá isso e ocultará a resposta visualmente.

---

## Validação

Antes de salvar, verifique:

- [ ] Título do capítulo está em `<capitulo titulo="...">"`?
- [ ] Pergunta está em `<caixa tipo="pergunta">`?
- [ ] Habilidade está em `<caixa tipo="habilidade">`?
- [ ] Todas as seções estão dentro de `<corpo>`?
- [ ] Todas as verificações estão em `<sidebars>`?
- [ ] `resposta_oculta` tem apenas uma letra (a, b, c)?
- [ ] `<encadeamento>` está em `<rodape>`?
- [ ] XML é válido (sem tags abertas)?

---

## Exemplo de Uso

```bash
python pipeline.py input/apostila-historia-midia/instrucoes.csv --agentes 5 --cap 1
```

Resultado: `output/apostila-historia-midia/formatado/unidade-1-.../01-01-...xml`

---

## Garantias de Entrega

Arquivo XML deve:

- ✓ Ser válido (parseable por XML readers)
- ✓ Ter estrutura sempre padronizada
- ✓ Ter cabeçalho com pergunta + habilidade sempre no topo
- ✓ Ter corpo com seções bem delimitadas
- ✓ Ter sidebar com verificações (resposta oculta)
- ✓ Ter rodapé com encadeamento
- ✓ Ser pronto para InDesign ler e aplicar estilos

**Formato é essencial para que InDesign automático funcione.**
