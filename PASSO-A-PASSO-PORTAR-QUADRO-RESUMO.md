# Passo a passo — portar o quadro-resumo da capa para este projeto

**Data:** 26/06/2026
**Arquivo-alvo:** `xml_to_pdf.py` (deste projeto)
**Referência:** `xml_to_pdf.py` do outro projeto (o que você colou) — já tem o recurso pronto

---

## Diagnóstico (o que descobri comparando os dois arquivos)

O `xml_to_pdf.py` deste projeto é, na prática, **a versão anterior** do mesmo
arquivo. O do outro projeto é idêntico em estrutura, só que com o quadro-resumo já
acrescentado. Portar é cirúrgico: **5 edições pontuais**, nenhuma reescrita.

Três fatos do seu projeto que tornam isso seguro:

1. **Seus XMLs já usam as 7 operações reais** (`Definir`, `Classificar`,
   `Sequenciar`, `Comparar`, `Mapear causalidade`, `Reconhecer perspectiva`,
   `Aplicar`). Confirmado nos XMLs de `output/.../formatado/`.
2. **O `OPERACAO_CORES` atual está desalinhado**: tem `Analisar` e `Avaliar`
   (que não existem no projeto) e está faltando `Classificar`, `Reconhecer
   perspectiva` e `Aplicar`. Hoje essas três operações já saem em **cinza**
   (cor de fallback), tanto no stepper quanto em qualquer lugar que use a cor.
   Corrigir isso é pré-requisito do quadro — e conserta um bug que já existe.
3. **Nenhum XML tem `<resumo-aluno>` ainda**, mas a função do outro projeto faz
   *fallback* automático para `<micro-habilidade>` (que todos os seus blocos
   têm). **Logo o quadro funciona imediatamente, sem tocar em nenhum agente.**

---

## Estratégia em 2 fases

- **Fase 1 — só o renderizador (xml_to_pdf.py).** Porta as 5 edições. O quadro
  passa a aparecer já na próxima geração de PDF, usando o texto da
  `<micro-habilidade>` de cada bloco. **É o mínimo necessário e já entrega valor.**
- **Fase 2 — qualidade do texto (opcional, depois).** Rodar um **agente
  Resumo-Aluno** que lê as `<micro-habilidade>` já fixadas no XML formatado e
  produz, por bloco, um `<resumo-aluno>` — a mesma micro-habilidade reescrita na
  linguagem do aluno ("o que você vai aprender"). Esse `<resumo-aluno>` é colado
  dentro do `<bloco>`, logo após a `<micro-habilidade>`. Quando o campo existir, o
  quadro usa ele automaticamente; enquanto não existir, usa a micro-habilidade.

> **Arquitetura (importante).** O `resumo-aluno` **não é informação nova** — é uma
> reescrita da micro-habilidade. Por isso ele não é trabalho do Agente 1
> (arquiteto) nem do Agente 5 (formatador): é um **agente de conteúdo próprio**,
> irmão do Decompositor na lógica (ambos operam no nível da micro-habilidade, sem
> nomear autores ou exemplos), mas que roda **depois** do formatador, porque
> precisa das micro-habilidades já fixadas. O **ponto de junção** dos dois lados
> (escrita e renderização) é o **XML formatado**: é o único lugar onde o
> `<resumo-aluno>` e a `<micro-habilidade>` convivem, dentro do mesmo `<bloco>`.
> Isso é o que mantém o quadro coerente — a mesma operação que pinta o stepper
> pinta a barra do quadro, e o texto é a versão amigável da mesma micro-habilidade
> que vira o cabeçalho do bloco adiante.

Faça e valide a Fase 1 inteira antes de pensar na Fase 2.

---

## FASE 0 — Cuidado com cache/sincronização (pasta no Google Drive)

Esta pasta é **sincronizada com o Google Drive** (há `.tmp.driveupload/` ativo e
locks de git). Isso cria um risco real: o **terminal/sandbox pode mostrar uma
cópia em cache** do arquivo, diferente da que está sendo editada. O chatbot do
outro projeto bateu exatamente nisso.

Regras para evitar editar o arquivo errado:

1. **Edite sempre o `xml_to_pdf.py` real pelas ferramentas de arquivo**
   (Read/Write/Edit), não por comando de terminal que reescreve o arquivo.
2. **Depois de editar, confirme** relendo o arquivo real — verifique que
   `OPERACAO_CORES` tem as 7 operações e que `render_quadro_resumo` existe.
3. **Para testar o PDF, rode numa cópia** (ex.: copie o `.py` + um XML para uma
   pasta de teste fora do Drive e gere o PDF lá). Assim você valida o resultado
   sem depender do que o terminal acha que é o arquivo.
4. Antes de mexer, **pause a sincronização do Drive** se possível, para não
   competir com locks durante as edições.

---

## FASE 1 — As 5 edições no `xml_to_pdf.py`

> Antes de começar: faça um backup. `cp xml_to_pdf.py xml_to_pdf.bak-pre-quadro.py`
> (você já mantém .bak no projeto, então é só seguir o costume).
>
> ⚠️ Veja a FASE 0: edite o arquivo real pelas ferramentas de arquivo e teste o
> PDF numa cópia — a pasta está no Drive e o terminal pode mostrar cache.

### Edição 1 — Corrigir e completar `OPERACAO_CORES` (≈ linha 41)

**Trocar** o dicionário atual:

```python
OPERACAO_CORES = {
    "Definir":            {"fundo": "#E3F2FD", "destaque": "#1565C0"},
    "Sequenciar":         {"fundo": "#E8F5E9", "destaque": "#2E7D32"},
    "Mapear causalidade": {"fundo": "#FFF3E0", "destaque": "#E65100"},
    "Comparar":           {"fundo": "#F3E5F5", "destaque": "#6A1B9A"},
    "Analisar":           {"fundo": "#FCE4EC", "destaque": "#AD1457"},
    "Avaliar":            {"fundo": "#FFFDE7", "destaque": "#F57F17"},
}
```

**Por** este (as 7 operações reais, copiado do outro arquivo):

```python
OPERACAO_CORES = {
    "Definir":                {"fundo": "#E3F2FD", "destaque": "#1565C0"},  # Nivel 1
    "Classificar":            {"fundo": "#E0F7FA", "destaque": "#00838F"},  # Nivel 1
    "Sequenciar":             {"fundo": "#E8F5E9", "destaque": "#2E7D32"},  # Nivel 1
    "Comparar":               {"fundo": "#F3E5F5", "destaque": "#6A1B9A"},  # Nivel 2
    "Mapear causalidade":     {"fundo": "#FFF3E0", "destaque": "#E65100"},  # Nivel 2
    "Reconhecer perspectiva": {"fundo": "#FCE4EC", "destaque": "#AD1457"},  # Nivel 3
    "Aplicar":                {"fundo": "#EFEBE9", "destaque": "#4E342E"},  # Nivel 3
}
```

> Efeito colateral bom: o stepper (`mapa-progressao`) também passa a colorir
> Classificar / Reconhecer perspectiva / Aplicar corretamente.

---

### Edição 2 — Adicionar o CSS do quadro (dentro de `build_css`, logo após o bloco `.mapa-passo`)

No seu arquivo, procure o comentário/regras de `/* MAPA PROGRESSAO */` e, logo
**depois** da última regra `.mapa-passo .num { ... }`, cole o bloco CSS abaixo
(idêntico ao do outro projeto):

```css
/* QUADRO RESUMO — "o que voce vai aprender", logo apos o stepper.
   Uma linha por micro-habilidade, com barra na cor da operacao. */
.quadro-resumo { margin: 12pt 0 4pt; border: 1pt solid #D0D6DC; border-radius: 6pt;
    overflow: hidden; break-inside: avoid; }
.quadro-resumo-titulo { background: #F5F7F9; font-family: Arial; font-size: 8.5pt;
    font-weight: 700; text-transform: uppercase; letter-spacing: .06em; color: #3A4654;
    padding: 7pt 12pt; border-bottom: 1pt solid #E2E7EC; }
.quadro-resumo-item { display: flex; align-items: stretch; border-bottom: 1pt solid #EEF1F4; }
.quadro-resumo-item:last-child { border-bottom: none; }
.quadro-resumo-barra { width: 4pt; flex: 0 0 4pt; }
.quadro-resumo-texto { padding: 7pt 12pt; font-size: 10pt; line-height: 1.45; color: #3A4654; }
.quadro-resumo-op { font-family: Arial; font-weight: 700; }
```

---

### Edição 3 — Acrescentar a função `render_quadro_resumo` (antes de `render_capitulo`)

Cole a função inteira logo **antes** de `def render_capitulo(...)` (no outro
projeto ela fica logo depois de `split_nome_capitulo`):

```python
def render_quadro_resumo(corpo_el):
    """Quadro 'O que voce vai aprender' na capa: uma linha por micro-habilidade,
    com a cor da operacao. O texto vem de <resumo-aluno> (escrito pelo Agente 1);
    se ausente, faz fallback para a <micro-habilidade> ja existente no bloco."""
    if corpo_el is None:
        return ""
    linhas = []
    for bl in corpo_el.findall("bloco"):
        op = bl.get("operacao", "")
        texto = txt(bl.find("resumo-aluno")) or txt(bl.find("micro-habilidade"))
        if not texto:
            continue
        c = OPERACAO_CORES.get(op, COR_PADRAO)
        op_h = (f'<span class="quadro-resumo-op" style="color:{c["destaque"]}">'
                f'{html_mod.escape(op)}</span> — ') if op else ""
        linhas.append(
            f'<div class="quadro-resumo-item">'
            f'<div class="quadro-resumo-barra" style="background:{c["destaque"]}"></div>'
            f'<div class="quadro-resumo-texto">{op_h}{md(html_mod.escape(texto))}</div>'
            f'</div>')
    if not linhas:
        return ""
    return ('<div class="quadro-resumo">'
            '<div class="quadro-resumo-titulo">O que você vai aprender neste capítulo</div>'
            + "".join(linhas) + '</div>')
```

---

### Edição 4 — Chamar a função e injetar o quadro na capa (dentro de `render_capitulo`, ≈ linha 475)

No seu arquivo a capa é montada assim (uma linha só):

```python
    capa = f'<div class="capa-capitulo">{eyebrow}{numero_h}{nome_h}{hab_h}{perg_h}{pqh}{mapa_html}</div>'

    corpo_el = root.find("corpo")
```

**Trocar** por (note que `corpo_el` sobe para *antes* da capa, porque o quadro
precisa dele):

```python
    # Quadro resumo "o que voce vai aprender", logo apos o stepper (mapa-progressao).
    corpo_el = root.find("corpo")
    quadro_html = render_quadro_resumo(corpo_el)

    capa = (f'<div class="capa-capitulo">{eyebrow}{numero_h}{nome_h}{hab_h}{perg_h}'
            f'{pqh}{mapa_html}{quadro_html}</div>')
```

> ⚠️ Cuidado: como você moveu `corpo_el = root.find("corpo")` para cima, **apague
> a linha `corpo_el = root.find("corpo")` que ficava logo abaixo** (a original),
> senão fica duplicada. O resto do corpo continua usando a mesma variável.

---

### Edição 5 — Não deixar `<resumo-aluno>` virar "tag desconhecida" (dentro de `render_bloco`)

Seu `render_bloco` tem o "guarda de contrato" que avisa em stderr toda tag não
consumida. Quando o `<resumo-aluno>` existir no XML (Fase 2), ele dispararia
falso alarme. Procure no loop de `render_bloco` a linha que ignora a
`micro-habilidade`:

```python
        elif t == "micro-habilidade":
            pass  # ...
```

e **inclua `resumo-aluno`** na mesma condição (igual ao outro projeto):

```python
        elif t in ("micro-habilidade", "resumo-aluno"):
            pass  # lidos via find() (cabecalho do bloco / quadro resumo); ignorar no loop
```

> Se no seu arquivo a `micro-habilidade` for ignorada de outra forma, o objetivo
> é o mesmo: garantir que `resumo-aluno` seja tratado como "lido via find(),
> ignorar no loop" e não caia em `avisar_tag_desconhecida`.

---

## Validação da Fase 1 (faça antes de seguir adiante)

1. **Sintaxe:** `python -c "import xml_to_pdf"` (ou `python xml_to_pdf.py --help`).
2. **Gerar um capítulo** com um XML real, nas duas versões:
   ```
   python xml_to_pdf.py --unidade output/apostila-ciencia-politica/formatado/politica-poder-e-estado --versao-aluno
   python xml_to_pdf.py --unidade output/apostila-ciencia-politica/formatado/politica-poder-e-estado --versao-professor
   ```
3. **Conferir no PDF, página 1 de cada capítulo:**
   - o quadro "O que você vai aprender neste capítulo" aparece abaixo do stepper;
   - há **uma linha por bloco**, cada uma com a barra colorida na cor da operação;
   - Classificar / Reconhecer perspectiva / Aplicar agora têm cor (não cinza);
   - nada foi empurrado/quebrado de forma estranha (o quadro ocupa a folga que já
     existia entre a capa e o primeiro bloco).
4. **stderr limpo:** nenhum aviso `[xml_to_pdf] AVISO: tag <...>`.
5. **Dica de inspeção rápida:** rode com `--html-only` e abra o HTML para iterar
   o visual sem gerar PDF a cada vez.

Se algo ficar feio (quadro muito alto, muitas linhas), o ajuste é só CSS:
`font-size` e `padding` de `.quadro-resumo-texto`. O outro projeto mediu
~45 mm para até 6 linhas dentro de ~138 mm livres — seus capítulos têm 4 blocos,
então sobra espaço.

---

## FASE 2 — Texto dedicado ao aluno (`<resumo-aluno>`), opcional

Só vale a pena depois que a Fase 1 estiver no ar. Hoje o quadro mostra a
`<micro-habilidade>`, que é técnica ("Classificar formas de dominação segundo
Weber"). O `<resumo-aluno>` permite uma frase mais direta ao aluno
("Você vai distinguir os três tipos de dominação e reconhecer cada um em exemplos").

A diferença entre o estado atual e o integrado é **só onde o resumo é escrito** —
o renderizador não muda em nenhum dos dois.

### Estado A — como funciona hoje no projeto que roda (manual)

1. Roda-se o **agente Resumo-Aluno** à parte (fora do pipeline). Ele recebe o XML
   formatado de um capítulo, lê cada `<bloco>` (sua `operacao` e sua
   `<micro-habilidade>`) e devolve **um arquivo de snippets** — o
   `{capitulo}-{hash}.xml` que você me mandou. Cada snippet é um comentário
   identificando o bloco + a tag `<resumo-aluno>` pronta:

   ```xml
   <!-- bloco-1 | operacao="Definir" -->
   <!-- micro-habilidade: Definir cidadania e democracia como formas históricas... -->
   <resumo-aluno>Você vai entender o que são cidadania e democracia, por que esses
   conceitos não são naturais e como cada sociedade define quem pertence à
   comunidade política e quem fica de fora.</resumo-aluno>
   ```

2. Um humano **cola** cada `<resumo-aluno>` dentro do `<bloco>` correspondente no
   XML formatado, logo após a `<micro-habilidade>`:

   ```xml
   <bloco id="bloco-1" palavras="434" operacao="Definir">
     <micro-habilidade>Definir cidadania e democracia como formas históricas...</micro-habilidade>
     <resumo-aluno>Você vai entender o que são cidadania e democracia...</resumo-aluno>
     ...
   </bloco>
   ```

3. Roda o `xml_to_pdf.py` normalmente. A Edição 3 já lê `<resumo-aluno>` com
   prioridade (fallback para `<micro-habilidade>`), então o quadro sai com as
   frases amigáveis.

> Para reproduzir o **Estado A** neste projeto basta: (a) ter a Fase 1 portada e
> (b) criar a skill do agente Resumo-Aluno aqui (ver abaixo). Nenhuma alteração no
> formatador (Agente 5) nem no arquiteto (Agente 1) é necessária.

### Estado B — integrado ao pipeline (quando quiser tirar o passo manual)

Inserir o **agente Resumo-Aluno como um passo entre o formatador (Agente 5) e o
`xml_to_pdf.py`** — ou dentro do próprio Agente 5 — gravando o `<resumo-aluno>`
**direto no XML formatado**, dentro de cada `<bloco>`, após a `<micro-habilidade>`.
O renderizador continua sem mudança. Capítulos antigos seguem funcionando pelo
fallback; os novos já saem com o campo preenchido — sem migração.

### Criar a skill do agente Resumo-Aluno neste projeto

Este projeto ainda **não tem** esse agente. Ele é um agente de conteúdo simples,
com um contrato estreito. Esboço de orientação (a salvar em
`orientacoes/agente-resumo-aluno-orientacao.md` quando você decidir avançar):

- **Entrada:** um XML formatado de capítulo.
- **Lê:** de cada `<bloco>`, o atributo `operacao` e o texto da `<micro-habilidade>`.
- **Produz:** um `<resumo-aluno>` por bloco, na ordem dos blocos, no formato de
  snippets do exemplo acima (com os comentários de identificação).
- **Não faz:** não nomeia autores, não cita exemplos, não inventa conteúdo, não
  muda a ordem nem o número de blocos. É reescrita da micro-habilidade, não
  conteúdo novo.
- **Regra de ouro do texto:** 1 frase, ~25–40 palavras, 2ª pessoa começando com
  "Você vai...", o verbo espelha a operação do bloco (Definir→"entender o que
  é..."; Sequenciar→"colocar em ordem..."; Comparar→"comparar..."; Reconhecer
  perspectiva→"perceber que existem interpretações diferentes..."; Aplicar→"usar
  os conceitos para analisar um caso..."). Use os exemplos do
  `01-01-...-f774cf87.xml` como referência de tom e tamanho.

---

## Resumo executivo

| Edição | Onde | O quê | Obrigatória p/ ver o quadro? |
|---|---|---|---|
| 1 | `OPERACAO_CORES` (~l.41) | 7 operações reais | Sim (e conserta bug de cor) |
| 2 | `build_css` | CSS `.quadro-resumo*` | Sim |
| 3 | antes de `render_capitulo` | função `render_quadro_resumo` | Sim |
| 4 | `render_capitulo` (~l.475) | chamar + injetar na capa | Sim |
| 5 | `render_bloco` | ignorar tag `resumo-aluno` | Recomendada (só pesa na Fase 2) |
| Fase 2 | **agente Resumo-Aluno** (novo) | gerar `<resumo-aluno>` e colar no `<bloco>` | Não (melhora o texto) |

Tudo na Fase 1 é copiar trechos prontos do arquivo que você colou — não há lógica
nova a inventar. O risco está concentrado na Edição 4 (não duplicar
`corpo_el = root.find("corpo")`).

Na Fase 2, o renderizador **nunca muda**: o único trabalho é escrever o
`<resumo-aluno>` (manual hoje, ou via agente integrado depois) dentro do `<bloco>`
no XML formatado. O quadro já funciona sem isso, pelo fallback.
