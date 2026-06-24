# Handover — Diagramação do PDF da apostila (projeto IPPI)

> Documento para o próximo assistente continuar a qualificação da diagramação
> do PDF. Lê isto antes de mexer em qualquer coisa.
> Última atualização: 2026-06-22 (cap. 01-02 ALUNO diagramado + XML truncado reparado — ver seção 15).

## 1. O que é o projeto

O IPPI é um pipeline que transforma conteúdo pedagógico de Sociologia (Ensino
Médio) em apostilas. Os capítulos existem como **XML estruturado** e são
convertidos em **PDF**. O foco atual NÃO é o conteúdo — é a **diagramação**
(layout, legibilidade, design para o aluno) do PDF gerado.

### Arquivo de trabalho (a unidade de exemplo)
```
output/apostila-sociologia-trabalho/formatado/unidade-x-o-trabalho-na-perspectiva-sociologica/
  ├── 01-01-...-forca-de-trabalho-e-alienacao.xml
  ├── 01-02-...-do-taylorismo-ao-toyotismo.xml
  └── 01-03-...-uberizacao-plataformizacao-e-divisao-sexual-do-trabalho.xml
```
São 3 capítulos. Cada XML é um `<capitulo>` com:
- `<cabecalho>`: habilidade (BNCC), operação principal, pergunta-capítulo, por-que-importa
- `<mapa-progressao>`: passos (Definir / Sequenciar / Mapear causalidade / Comparar...)
- `<corpo>`: sequência de `<bloco operacao="...">`, `<quebra tipo="pagina">`, `<nota_fonte>`, `<sidebar>`
- `<rodape>`: atividade final (`sidebar tipo="aplicar-agora"`)

Dentro de cada `<bloco>`: `<micro-habilidade>`, `<secao>` (com `<titulo>`,
`<conteudo>` de `<paragrafo>`s, e sidebars de autor), `<imagem>`, `<nota_fonte>`,
`<sidebar tipo="verificacao">`.

A `<sidebar tipo="verificacao">` tem `<pergunta>`, `<alternativas>` (cada
`<alternativa letra="A" correta="sim">`) e `<justificativa>`. **REGRA INVIOLÁVEL:
o atributo `correta="sim"` existe no XML mas NUNCA marca visualmente a resposta
no PDF.** Todas as alternativas usam a mesma classe neutra `.alternativa`.

## 2. Motor: `xml_to_pdf.py` (WeasyPrint) — fonte da verdade

Existem dois motores no repo. **Use só o `xml_to_pdf.py`** (WeasyPrint, HTML/CSS).
O `apostila_pdf.py` (ReportLab) está **aposentado** nesta linha de trabalho — não
volte a ele.

### Por que WeasyPrint e não ReportLab
O pedido central era **texto em duas colunas** com elementos em largura total
(header de bloco, verificação). Em CSS isso é nativo (`column-count`, hifenização,
controle de viúvas/órfãs). No ReportLab seria na mão e — decisivo — **ReportLab
não tem hifenização automática**, o que estraga texto justificado em coluna
estreita. Por isso CSS (`hyphens: auto` + `<html lang="pt-BR">` + pyphen `pt_BR`).

## 3. Arquitetura-chave: "segmentação multicol" (NÃO mudou — entenda antes de editar)

O suporte a `column-span: all` no WeasyPrint é instável, então **não dependemos
dele**. Em vez disso, `render_bloco()` percorre os filhos do bloco em ordem e
**segmenta**:
- Conteúdo que flui (títulos de seção, parágrafos, box de autor, nota de fonte)
  é acumulado num `buffer`.
- Quando aparece um elemento de largura total (verificação, imagem real), o buffer
  é "descarregado" (`flush()`) como um `<div class="bloco-multicol">` (2 colunas),
  e o elemento full-width é emitido solto, fora das colunas. Depois recomeça.

`render_secao()` devolve uma lista de tuplas `(kind, html)` onde `kind` é `'col'`
(vai pro buffer) ou `'full'` (força flush + emite solto). Box de autor fica DENTRO
da coluna (é curto); verificação e imagens são sempre `'full'`.

## 4. O QUE FOI FEITO NESTA SESSÃO (6 demandas do usuário)

Todas implementadas no `xml_to_pdf.py` e validadas renderizando páginas em PNG.

1. **Moldura da página → REMOVIDA.** Ver seção 5 (decisão importante).
2. **Habilidades em bold.** A `.micro-habilidade` (sob a barra de operação) agora é
   `font-weight: 700` e branca; o badge BNCC já era bold. Em `build_css()`.
3. **Sem imagens no MVP.** Removida toda a geração de linha do tempo, quadro
   comparativo e placeholder. `render_imagem()` agora retorna `""` a menos que
   exista um arquivo REAL em `--imagens` (`<ref>.png/jpg/jpeg/svg`). Quando as
   imagens reais existirem, é só passar `--imagens <pasta>`.
4. **Seções não quebram entre páginas.** `break-inside: avoid` na
   `.aplicar-agora` (e já havia em `.sidebar-verificacao`, `.sidebar-autor`,
   `.nota-fonte`, `.imagem-container`). A "Aplicar agora" que antes rachava na
   antiga p.9 agora vai inteira para a página seguinte. **ATENÇÃO:** isso NÃO
   resolve o cabeçalho de bloco órfão — ver seção 9 (problema em aberto).
5. **Aluno × professor como processos separados.** Era um BUG: `sb_aplicar`
   ignorava a flag e sempre imprimia a resposta-modelo no aluno. Corrigido
   (`sb_aplicar(el, incluir_gabarito)`). Ver seção 6.
6. **Identificação do capítulo.** Capa redesenhada com Unidade → Capítulo N →
   nome do capítulo → habilidade → pergunta norteadora. O nome vem de FORA do
   XML (`briefing.json`). Ver seção 7.

## 5. DECISÃO IMPORTANTE: a moldura foi removida (histórico do raciocínio)

Havia um `<div class="moldura-pagina">` `position: fixed` desenhando um retângulo
em volta de cada página. Histórico:

1. O usuário reclamou que "existe uma borda azul clara... mas ela não é respeitada
   e o texto passa por cima dela".
2. **Primeira hipótese (tentada):** o problema era o `position: fixed` com
   `right`/`bottom`, que o WeasyPrint posicionava de forma **inconsistente entre
   páginas** (medições: na p.1 a linha caía a ~26mm, DENTRO da margem de texto de
   18mm; logo o texto "vazava" pra fora dela). Troquei por um frame de **tamanho
   explícito** (`width`/`height` fixos a partir do A4) + margens simétricas, pra
   garantir o texto sempre dentro.
3. **O usuário ainda via a linha** (agora azul, `#AEC4E0`) e decidiu: como o texto
   não obedece a moldura e já existe uma barra colorida no topo de cada bloco,
   **o melhor é tirar a moldura**.

**Estado atual: a moldura não existe mais.** Removi a injeção do
`<div class="moldura-pagina">` em `build_html()` e a regra CSS `.moldura-pagina`.
O "limite" da página passou a ser o espaço em branco das margens
(`@page margin: 18mm 16mm 20mm 16mm`) + a barra de operação no topo de cada bloco
+ o número de página no rodapé.

**Se um dia quiserem moldura de volta:** NÃO use `position: fixed` com
`right`/`bottom` (foi a causa da inconsistência). Use ou (a) `position: fixed`
com `width`/`height` EXPLÍCITOS, ou — melhor — (b) filetes parciais (só um traço
no rodapé e/ou topo), que evitam a tensão "barra colorida full-width cruza a
linha vertical da moldura". Um retângulo fechado SEMPRE vai brigar com as faixas
coloridas full-width que chegam perto das bordas (era exatamente o que deixava a
linha com cara de "cortada" no topo de páginas continuadas).

## 6. Versões ALUNO × PROFESSOR (dois processos separados)

- A flag agora é **OBRIGATÓRIA**: o script **erra** se você não passar
  `--versao-aluno` OU `--versao-professor`. Isso é proposital — evita gerar a
  versão errada por esquecimento. Rode **um de cada vez**.
- `incluir_gabarito = args.versao_professor`. Esse booleano atravessa todas as
  funções e controla DUAS coisas: o gabarito (`<justificativa>`) das verificações
  E a resposta-modelo (`<resposta>`) da "Aplicar agora".
- Saída ganha sufixo da versão automaticamente (`...-professor.pdf` /
  `...-aluno.pdf`) e um rótulo de versão no rodapé (`@bottom-right`), pra nunca
  misturar os dois.
- Verificado: aluno = 0 gabaritos e 0 respostas; professor = 12 gabaritos e 3
  respostas.

## 7. Identificação de capítulo + `briefing.json`

- A capa do capítulo é montada em `render_capitulo()` a partir de um `meta`
  (`numero`, `nome`, `unidade`). O número vem do `id` do XML
  (`numero_capitulo_do_xml`: `01-02` → 2). O **nome** vem de fora do XML.
- `carregar_briefing()` lê `input/.../briefing.json` (auto-detectado subindo a
  partir de `--unidade`, ou via `--briefing`). Usa as chaves `unidade` e
  `capitulos` (lista "Capítulo N — Nome").
- **ATENÇÃO — dado quebrado:** o `briefing.json` no disco está **truncado/inválido**
  (corta no meio de `conteudos_por_capitulo`). Por isso o loader é **tolerante**:
  se o `json.loads` falhar, ele extrai `unidade` e `capitulos` por regex e segue.
  Imprime `AVISO: briefing.json invalido`. **Recomendação:** consertar o arquivo
  na origem; o loader tolerante é só uma rede de segurança.

## 8. Como rodar

Dependências: `pip install weasyprint` (puxa pango/cairo; pyphen vem junto).
No sandbox Linux desta sessão foi preciso `pip install weasyprint
--break-system-packages` (a `.venv` do repo é do Windows e não roda no Linux).

```bash
# PROCESSO DO PROFESSOR (com gabarito e resposta-modelo)
python xml_to_pdf.py --unidade <pasta_xml> --versao-professor

# PROCESSO DO ALUNO (sem gabarito nem resposta)
python xml_to_pdf.py --unidade <pasta_xml> --versao-aluno

# imagens reais (quando existirem)
python xml_to_pdf.py --unidade <pasta_xml> --versao-aluno --imagens <pasta_imgs>

# só HTML para inspecionar
python xml_to_pdf.py --unidade <pasta_xml> --versao-aluno --html-only --output saida.html

# um capítulo só
python xml_to_pdf.py arquivo.xml --versao-aluno
```

Sem `--versao-*` o script PARA com erro. Validação visual:
`pdftoppm -png -r 150 saida.pdf prefixo` e abra as PNGs.

## 9. PROBLEMA EM ABERTO: cabeçalho de bloco órfão (ex.: "SEQUENCIAR" sozinho no pé da página)

**Sintoma:** a faixa colorida de um bloco (ex.: "SEQUENCIAR") cai isolada no fim
de uma página e o conteúdo (as 2 colunas) só começa na página seguinte.

**Hipótese de causa (a mais provável):**
- O `.bloco-header` JÁ tem `break-after: avoid`, cujo papel é exatamente impedir
  a quebra logo depois dele (empurrando header + começo do conteúdo pra próxima
  página).
- Mas o que vem depois do header é o `.bloco-multicol` — um **container de 2
  colunas** (`column-count: 2`), que é um *contexto de formatação à parte*. O
  WeasyPrint **não honra de forma confiável `break-after/break-before: avoid` na
  fronteira para um bloco multicoluna**. Resultado: ele permite a quebra bem ali,
  entre a barra e as colunas.
- **Tensão estrutural:** header e multicol são dois irmãos separados
  (`<div header>` + `<div multicol>`), sem nada amarrando-os. Não dá pra pôr
  `break-inside: avoid` no `.bloco` inteiro, porque o bloco é longo e PRECISA
  poder quebrar entre páginas (senão um bloco grande estoura a página). O
  `break-after: avoid` que deveria mediar isso é justamente o que não pega.
- O encadeamento das páginas anteriores só decide *qual* barra calha de cair no
  finalzinho da página; o motivo de ela ficar órfã é o `avoid` ignorado.

**Direções de solução (NÃO implementadas — o usuário só quis entender):**
1. Amarrar o header à PRIMEIRA fatia do conteúdo num "keep-together" — ex.: emitir
   o `.bloco-header` DENTRO do primeiro `.bloco-multicol` (a unidade
   header+1ª-fatia ganha `break-inside: avoid`), em vez de irmão solto.
2. Ou envolver `header + primeiro segmento curto` num wrapper com
   `break-inside: avoid`, deixando o RESTANTE do bloco livre para quebrar.
3. Testar `box-decoration-break` / repetir o cabeçalho — menos provável de ajudar.
   Qualquer caminho exige render visual em vários pontos de quebra para validar.

**Outros refinos ainda em aberto (herdados):**
- Balanceamento da última coluna em blocos curtos (coluna 2 pela metade).
- Dois `nota_fonte` logo após um full-width podem ficar lado a lado (2 colunas).
- O filete colorido (`border-top` do `.bloco-multicol`) pode aparecer no topo de
  páginas continuadas quando um bloco atravessa a quebra.

## 9-bis. SESSÃO 2026-06-16 — entrada das imagens reais e compactação

As 3 imagens reais do cap. 01-01 (`fig-01-01-01/02/03`, infográficos em
paisagem) entraram em `output/apostila-sociologia-trabalho/imagens/`. Com elas,
apareceu **muito espaço em branco**: cada imagem e cada verificação são
elementos full-width com `break-inside: avoid`; quando imagem + verificação não
cabiam juntas, cada uma orfanava numa página (ex.: antiga p.5 com 63% de branco,
p.8 com 68%). Medição baseline do cap.1: média 22,9% de branco de rodapé.

**O que foi feito nesta sessão (todas no `xml_to_pdf.py`):**
1. **Bug de caminho corrigido.** `render_imagem()` fazia `Path(...).as_uri()` em
   caminho relativo → `ValueError`. Agora `.resolve()` + `imdir` absoluto em
   `main()`.
2. **Legenda escondida** (decisão do usuário). A `<descricao>` do XML é briefing
   de produção, não texto para o aluno. `render_imagem()` emite só `<figure><img>`,
   sem `<p class="imagem-legenda">`. (CSS `.imagem-legenda` ficou órfão, inócuo.)
3. **Imagem compactada.** `.imagem-container img { max-height: 74mm; max-width:
   100%; width:auto }` + margens reduzidas (14pt→7pt) + `break-before: avoid`
   (puxa a imagem para junto do texto anterior).
4. **Verificação puxada para cima.** `.sidebar-verificacao` ganhou
   `break-before: avoid` e padding/margem um pouco menores. Continua full-width
   (decisão do usuário: "verificação segue como está").

**Resultado (cap.1 aluno):** 12→10 páginas; branco médio 22,9%→12,2%; as
verificações órfãs (p.5/p.8) sumiram e agora empacotam com a imagem/texto.
Validado por render PNG das páginas + medição programática de branco de rodapé.

**Resíduo conhecido (versão PROFESSOR):** com o box de gabarito, a verificação
fica mais alta e volta a orfanar em ~2 páginas (branco ~41–47%). Como é uso
interno, não foi tratado. Se incomodar: reduzir a imagem (`max-height`) só
quando `incluir_gabarito`, ou permitir a verificação-com-gabarito quebrar entre
páginas (`break-inside: auto` no `.verif-gabarito`).

## 10. AVISO técnico (truncamento de arquivo) — CONFIRMADO de novo nesta sessão

A ferramenta de **edição** de arquivos truncou o `xml_to_pdf.py` de novo nesta
sessão: ao aplicar um patch, cortou o arquivo na ~linha 474, gerando
`SyntaxError: unterminated string literal`. (O handover anterior já alertava
sobre isso.)

**Recomendação forte:** para mudanças grandes neste arquivo, **reescreva pelo
shell** (heredoc com delimitador entre aspas: `cat > arquivo <<'EOF' ... EOF`)
e SEMPRE confira depois com `wc -l xml_to_pdf.py` e
`python3 -m py_compile xml_to_pdf.py`. Para patches pequenos, prefira um script
Python de `replace` no shell e valide igual. Não confie cegamente no "sucesso"
reportado pela ferramenta de edição em arquivos grandes.

## 11. Artefatos atuais (C:\Users\Roberto\Desktop\IPPI)

- `xml_to_pdf.py` — motor com TODAS as mudanças desta sessão e **sem moldura**.
  **Fonte da verdade.**
- `apostila-sociologia-aluno-v3.pdf` — versão do ALUNO, **sem moldura**, atual.
- `apostila-sociologia-professor-v2.pdf` — versão do PROFESSOR, mas gerada ANTES
  da remoção da moldura → **ainda tem a moldura**. Precisa regenerar com
  `--versao-professor` para ficar sem.
- Os nomes "limpos" (`apostila-sociologia-aluno.pdf` / `-professor.pdf`) e o
  `-v2` do aluno ficaram **travados** (abertos num leitor de PDF) e não puderam
  ser sobrescritos — por isso os sufixos `-v2`/`-v3`. Quando os PDFs estiverem
  fechados, consolidar nos nomes finais.

## 12. Princípios a manter

- Não voltar para o motor ReportLab (`apostila_pdf.py`) nesta linha de trabalho.
- Nunca marcar a resposta correta no PDF (jamais usar `correta="sim"` para
  destaque visual).
- Aluno e professor são DOIS processos: rodar um de cada vez; a flag é obrigatória.
- No MVP, sem imagens (só entram com `--imagens` e arquivo real).
- Priorizar legibilidade do aluno: hifenização, coluna ~50-60 caracteres,
  contraste alto, hierarquia (barra de operação > seção > corpo).
- Após qualquer edição grande no `xml_to_pdf.py`: `py_compile` + render visual.

## 13. SESSÃO 2026-06-20 — capítulo 1 de História (unidade 1) + bug grave de perda de conteúdo CORRIGIDO

**Tarefa:** diagramar em PDF a versão ALUNO do cap. 01-01 ("Formação do Estado
Imperial e organização da justiça", `apostila-historia-unidade1-2serie`), com
imagens reais (`output/apostila-historia-unidade1-2serie/imagens/`) e
verificações externas (`output/apostila-historia-unidade1-2serie/verificacao/`,
modelo Fase 4 do `PLANO-VERIFICACAO-EXTERNA.md`).

**Comando final usado:**
```bash
python3 xml_to_pdf.py \
  output/apostila-historia-unidade1-2serie/formatado/unidade-1-justica-estado-e-poder-no-brasil-imperial/01-01-capitulo-1-formacao-do-estado-imperial-e-organizacao-da-justica.xml \
  --versao-aluno \
  --imagens output/apostila-historia-unidade1-2serie/imagens \
  --verificacoes output/apostila-historia-unidade1-2serie/verificacao \
  --output 01-01-capitulo-1-formacao-do-estado-imperial-e-organizacao-da-justica-aluno.pdf
```

**BUG NOVO encontrado (mais grave que o §9): perda silenciosa de conteúdo em
seções `tipo="classificacao"`.** `render_secao()` só lia `<conteudo>` direto da
seção. Seções com `tipo="classificacao"` (operação "Classificar") usam
`<introducao>` + `<lista-subtipos><item nome="...">` em vez de `<conteudo>` —
esse texto era descartado sem erro nenhum. No cap. 01-01 isso apagava quase
todo o bloco-2 (~300 palavras: "Centralização administrativa/jurídica/militar",
nomeação de presidentes de província, Código Criminal, Guarda Nacional etc.),
inflando o branco da página 3 para 33,8% e disfarçado como se fosse só o
problema do §9. Confirmado **sistêmico**: o mesmo padrão (`<lista-subtipos>`,
`tipo="classificacao"`) existe no cap. 01-02 (escravidão/crise do Império) —
não tratado ainda, mas vai precisar do mesmo fix quando esse capítulo for
diagramado.

**Diagnóstico:** `grep` direto no HTML gerado (`--html-only`) e
`pdftotext -layout` por página confirmaram a ausência do texto — não foi
impressão visual, foi perda real de conteúdo.

**Fix aplicado (decisão do usuário: corrigir agora, não só documentar).**
Patch em `xml_to_pdf.py` feito por script Python (`str.replace` com
`assert count==1` antes de cada substituição), **não pela ferramenta de
edição**, por causa do aviso do §10:
1. Nova função `lista_subtipos_html(el)` — renderiza
   `<lista-subtipos><item nome="..."><conteudo>` como
   `<div class="lista-subtipos"><div class="subtipo-item">`.
2. `render_secao()` passou a chamar também `conteudo_html(el.find("introducao"))`
   e `lista_subtipos_html(el.find("lista-subtipos"))`, além do `<conteudo>`
   original.
3. CSS novo em `build_css()`: `.lista-subtipos`, `.subtipo-item`,
   `.subtipo-nome` (nome do subtipo em negrito, 9pt, antes do texto).

**Verificação do patch:** `xml_to_pdf.py` foi de 545 → 569 linhas (+24, do
tamanho esperado). `python3 -m py_compile xml_to_pdf.py` limpo.
`diff` contra o backup pré-patch (`/tmp/xml_to_pdf.py.before_fix`) mostrou
exatamente essas três adições, nada mais (sem truncamento).

**Revalidação pós-fix:**
- `--html-only` confirmou os termos antes ausentes agora presentes
  ("Centralização administrativa", "Código Criminal", "Guarda Nacional" etc.).
- PDF regenerado: ainda **9 páginas**.
- Branco de rodapé por página (medição PIL restrita à área de conteúdo, exclui
  faixa do `@bottom-center` de ~20mm): p.1=4,1% · p.2=2,8% (era 18,1%) ·
  p.3=17,6% (era 33,8%) · p.4=2,9% · p.5=45,8% · p.6=45,2% · p.7=5,3% ·
  p.8=4,1% · p.9=10,8%. Média geral 15,4%.
- Inspeção visual (render PNG 150dpi de todas as 9 páginas): cabeçalho de bloco
  "CLASSIFICAR" na p.2 agora emenda direto no conteúdo (o §9 não se manifestou
  nesta página depois do fix — o bloco passou a ter conteúdo suficiente pra não
  sobrar header solto). p.3 mostra o infográfico `fig-01-01-02` compacto, sem
  legenda visível, com o texto de `lista-subtipos` fluindo normalmente nas 2
  colunas acima dele — sem sobreposição, sem bug visual na CSS nova.
- **Resíduo conhecido, NÃO é regressão deste fix:** p.5/p.6 (45,8%/45,2% de
  branco) repetem o limite já registrado no §9-bis — imagem (`fig-01-01-03` da
  votação censitária) e a verificação que vem depois não cabem juntas na mesma
  página, cada uma orfana na sua. Já era um problema conhecido antes desta
  sessão; não foi pedido para corrigir agora.
- Conformidade de regras: `grep` no HTML confirmou as 16 alternativas (4
  questões × 4 letras) usam todas a mesma classe (`alternativa`/`alt-letra`),
  nenhuma classe distinta para a resposta correta. `pdftotext` no PDF aluno
  confirmou **zero** ocorrência de "gabarito" / "justificativa" /
  "resposta comentada" — a versão aluno não vaza nenhum gabarito.

**Artefato final:** `01-01-capitulo-1-formacao-do-estado-imperial-e-organizacao-da-justica-aluno.pdf`
(9 páginas, 1,02 MB), em `C:\Users\Roberto\Desktop\IPPI`.

## 14. SESSÃO 2026-06-22 — quebra de página por micro-habilidade + imagens maiores

**Tarefa (2 demandas do usuário):** (1) cada micro-habilidade deve começar em
página nova, para separar visualmente as micro-habilidades; (2) ampliar as
imagens, que estavam pequenas demais. Tudo no `xml_to_pdf.py` (motor WeasyPrint,
fonte da verdade), versão ALUNO do cap. 01-01.

**Nota de modelagem:** no XML, cada `<bloco>` tem exatamente uma
`<micro-habilidade>` (a faixa colorida de operação). Logo "quebra por
micro-habilidade" = "quebra por bloco".

**O que foi feito (5 patches no `xml_to_pdf.py`, aplicados por script Python com
`assert count==1`, conforme o aviso do §10 — NÃO pela ferramenta de edição):**

1. **Quebra de página por bloco.** Nova classe CSS `.bloco-quebra
   { break-before: page; }`. `render_bloco()` ganhou o parâmetro
   `quebrar_pagina=False` e aplica a classe quando `True`. Em
   `render_capitulo()`, o loop do `<corpo>` marca `quebrar_pagina=True` em todos
   os blocos **menos o primeiro** (o primeiro segue logo após a capa; na prática
   o wrapper keep-together do item 3 acaba empurrando-o para a página seguinte à
   capa, o que ficou limpo).
2. **`<quebra tipo="pagina">` deixou de causar página em branco dupla.** Com a
   quebra automática por bloco, uma `<quebra>` seguida de `<bloco>` geraria duas
   quebras em sequência (página vazia). O loop agora faz *lookahead*: só emite o
   `<div class="quebra-pagina">` se o próximo elemento NÃO for um `<bloco>`.
   (O cap. 01-01 tem uma `<quebra>` antes do bloco-4; ela passou a ser inócua.)
3. **Cabeçalho de bloco amarrado à primeira fatia de conteúdo — RESOLVE o §9.**
   Era o problema do cabeçalho órfão (faixa "CLASSIFICAR"/"COMPARAR" sozinha no
   topo de uma página). A quebra forçada do item 1 tornou o §9 **muito visível**
   (o header caía sozinho numa página quase vazia). Fix: `render_bloco()` agora
   embrulha `header + segments[0]` (cabeçalho + primeiro multicol) num
   `<div class="bloco-keep">` com `break-inside: avoid`; o resto do bloco fica
   livre para quebrar. Validado: nenhum header órfão restante. (Observação: como
   `break-inside: avoid` é best-effort, um bloco cujo primeiro multicol seja
   maior que a página ainda quebraria — aceitável.)
4. **Imagens maiores.** `.imagem-container img` teve `max-height: 74mm → 140mm`.
   Os infográficos são paisagem (proporções medidas: fig-01=1.58, fig-02=1.50,
   fig-03=1.22). O limite de 74mm os prendia em ~90–117mm de largura mesmo com
   178mm de área útil (margens 16mm); por isso pareciam pequenos. Com 140mm,
   fig-01/02 enchem a largura (limitados pelo `max-width:100%`) e fig-03 fica
   ~159mm. **Cuidado:** o 74mm do §9-bis existia para *compactar* a imagem e
   empacotá-la com a verificação na mesma página. Aumentar para 140mm desfaz
   essa compactação de propósito (ver resíduo abaixo).
5. **Removidos os `break-before: avoid` de imagem e verificação.** Eram da lógica
   antiga de compactação (§9-bis, "puxar a imagem para junto do texto anterior").
   Com a quebra por bloco + imagens grandes, essas dicas passaram a **gerar
   páginas totalmente em branco** (constraints conflitantes empurrando os
   full-width de um lado para o outro). Removê-las e deixar o fluxo natural
   eliminou as páginas em branco. Mantido apenas `break-inside: avoid` nos dois.

**Verificação (versão aluno, cap. 01-01):**
- `py_compile` limpo; `xml_to_pdf.py` foi de 569 → 637 linhas.
- 9 → **12 páginas** (esperado: o objetivo é separar as 4 micro-habilidades).
- Render PNG de todas as páginas: capa sozinha (p.1); cada bloco abre com
  cabeçalho + conteúdo juntos (DEFINIR p.2, CLASSIFICAR p.4, COMPARAR p.6,
  MAPEAR p.9) — **zero cabeçalho órfão**; **zero página totalmente em branco**;
  os 3 infográficos grandes e legíveis em largura quase total.
- Regras invioláveis: `pdftotext` no PDF aluno = **0** ocorrências de
  "gabarito"/"justificativa"/"resposta modelo"; as 16 alternativas (4 questões ×
  4) usam todas `class="alternativa"`/`alt-letra`, nenhuma classe distinta para a
  correta.

**Resíduo conhecido (tradeoff aceito, NÃO é bug):** as páginas só-de-imagem de
fig-02 (p.7) e fig-03 (p.11) ficam com espaço em branco abaixo da imagem, porque
imagem grande (140mm) + verificação (full-width, alta) não cabem juntas na mesma
página. É o custo direto de ampliar as imagens — decisão do usuário. Se incomodar:
reduzir o `max-height` (ex.: 110–120mm) reequilibra imagem × branco.

**Pendências herdadas / a fazer quando pedirem:**
- Aplicar os mesmos 5 patches ao **cap. 01-02** (já existe no `formatado/`; lembrar
  do fix de `<lista-subtipos>`/`classificacao` do §13, que vale para ele também).
- Gerar a **versão PROFESSOR** com as mesmas mudanças (o box de gabarito deixa a
  verificação mais alta — ver resíduo do §9-bis sobre orfanamento na versão
  professor; pode interagir com as imagens de 140mm).

**Artefato final:** `apostilas/01-01-capitulo-1-formacao-do-estado-imperial-e-organizacao-da-justica-aluno.pdf`
(12 páginas, ~1,05 MB). Backup pré-patch do motor em `/tmp/xml_to_pdf.py.before_diagram`
(sandbox; some entre sessões — se precisar de backup durável, copiar para o repo).

## 15. SESSÃO 2026-06-22 (tarde) — capítulo 1-02 ALUNO (escravidão, direitos e crise do Império) + XML truncado reparado

**Tarefa:** diagramar em PDF a versão ALUNO do cap. 01-02
("Escravidão, direitos e crise do Império", `apostila-historia-unidade1-2serie`),
com imagens reais (`output/apostila-historia-unidade1-2serie/imagens`) e
verificações externas (`output/apostila-historia-unidade1-2serie/verificacao`).
Motor: `xml_to_pdf.py` (WeasyPrint), já com TODOS os fixes do §13 (lista-subtipos)
e do §14 (quebra por bloco, bloco-keep, imagens 140mm). **Nenhuma alteração no
motor foi necessária nesta sessão** — os fixes anteriores já cobrem este capítulo.

**PROBLEMA ENCONTRADO ANTES DE RODAR: o XML do cap. 01-02 estava TRUNCADO.**
A cópia de trabalho (`...01-02-...xml`) terminava no meio da última frase do
`<o-que-verificar>` do "aplicar-agora" do `<rodape>` ("...em 15 ") — faltavam o
resto da frase e as tags de fechamento `</o-que-verificar></sidebar></rodape></capitulo>`.
`ET.parse` falhava com `no element found: line 184`.
- **Diagnóstico:** `git diff HEAD` mostrou que a cópia de trabalho NÃO é uma cópia
  velha do commit — é uma versão **mais nova e editada** (prosa revisada em 6
  parágrafos; `palavras_total` 1991→2025; contagens por bloco atualizadas). Logo
  **`git checkout` estava DESCARTADO** (apagaria as edições novas). A perda foi só
  a cauda truncada (texto de briefing que NÃO vai para o aluno — o conteúdo real
  do aplicar-agora vem do JSON externo `aplicar-01-02.json`).
- **Reparo (sem ferramenta de edição, via script Python no shell):** o bloco
  `<rodape>` é byte-a-byte idêntico ao do HEAD até o ponto do truncamento, então
  recolei `work[:idx("<rodape>")] + head[idx("<rodape>"):]`, preservando CRLF e
  todas as edições novas. Backup pré-reparo em `/tmp/cap0102.before_repair.xml`
  (sandbox, some entre sessões). Validado: `ET.parse` OK; `palavras_total="2025"`
  preservado; arquivo fecha em `</capitulo>`. **Pendência para a origem:** consertar
  o truncamento no pipeline que gera/salva esse XML — pode reincidir em outros caps.

**Comando final usado:**
```bash
python3 xml_to_pdf.py \
  output/apostila-historia-unidade1-2serie/formatado/unidade-1-justica-estado-e-poder-no-brasil-imperial/01-02-capitulo-2-escravidao-direitos-e-crise-do-imperio.xml \
  --versao-aluno \
  --imagens output/apostila-historia-unidade1-2serie/imagens \
  --verificacoes output/apostila-historia-unidade1-2serie/verificacao \
  --output apostilas/01-02-capitulo-2-escravidao-direitos-e-crise-do-imperio-aluno.pdf
```

**Verificação (versão aluno, cap. 01-02):**
- **12 páginas** (capa + 4 blocos, cada micro-habilidade/bloco abre em página nova —
  comportamento esperado do §14). PDF ~0,95 MB.
- **Render PNG 150dpi de todas as 12 páginas, conferido:**
  - p1 capa (Unidade → Capítulo 2 → pergunta norteadora → mapa de progressão).
  - p2 DEFINIR · p4 CLASSIFICAR · p6 COMPARAR · p9 MAPEAR CAUSALIDADE — os 4
    cabeçalhos de bloco **emendam direto no conteúdo; ZERO cabeçalho órfão**
    (o bug do §9 NÃO se manifestou; o wrapper `bloco-keep` do §14 segura).
  - **ZERO página totalmente em branco.**
  - As 3 imagens reais grandes e legíveis, **sem legenda** (`<descricao>` oculta);
    `nota_fonte` (citação bibliográfica) aparece corretamente abaixo das figuras.
  - Conferido que cada figura está no bloco certo: fig-01-02-01 (linha do tempo
    "Dois Caminhos da Crise") no bloco-2; fig-01-02-02 (quadro "Duas Vertentes")
    no bloco-3; fig-01-02-03 (diagrama causal → golpe de 1889) no bloco-4. Bate
    com a `<descricao>` e a operação de cada bloco.
  - O fix do §13 (`<lista-subtipos>`/`tipo="classificacao"`) está ativo: o bloco-2
    (leis abolicionistas graduais + resistência) renderiza o texto completo nas 2
    colunas — sem a perda silenciosa de conteúdo descrita no §13.
- **Branco de rodapé por página (PIL, exclui faixa ~20mm do `@bottom-center`):**
  p1=50,1%(capa) · p2=30,0% · p3=56,9% · p4=21,6% · p5=5,2% · p6=27,1% ·
  p7=39,9% · p8=55,1% · p9=5,3% · p10=50,1% · p11=33,7% · p12=14,8%. **Média 32,5%.**
- **Regras invioláveis — conferidas:** `pdftotext` no PDF aluno = **0** ocorrências
  de gabarito / justificativa / "resposta comentada" / "resposta modelo". As **16**
  alternativas (4 verificações × 4 letras) usam todas a mesma classe
  (`alternativa`/`alt-letra`); **nenhuma** classe distinta para a correta. A única
  string "correta" no HTML é "corretamente" dentro de uma pergunta (texto), não
  atributo nem marcação.

**Resíduo conhecido (tradeoff aceito do §14, NÃO é bug/regressão):** as páginas
de branco mais alto são exatamente onde imagem grande (140mm, full-width,
`break-inside: avoid`) e verificação full-width não cabem juntas e cada uma
orfana com branco abaixo — p3 (verif-s1 do bloco sem imagem), p7→p8 (fig-02 +
verif-s3) e p10→p11 (texto do bloco-4 + fig-03). É o custo direto de ampliar as
imagens, já registrado no §14. Se incomodar: reduzir `max-height` (110–120mm)
reequilibra imagem × branco. Não foi pedido tratar agora.

**Artefato final:** `apostilas/01-02-capitulo-2-escravidao-direitos-e-crise-do-imperio-aluno.pdf`
(12 páginas, ~0,95 MB), em `C:\Users\Roberto\Desktop\IPPI\apostilas`.

**Pendências herdadas / a fazer quando pedirem:**
- Gerar a **versão PROFESSOR** do cap. 01-02 (atenção ao resíduo do §9-bis: o box
  de gabarito sobe a altura da verificação e pode interagir com as imagens 140mm).
- Consertar na ORIGEM o truncamento do XML do cap. 01-02 (o reparo desta sessão é
  rede de segurança, não correção definitiva do pipeline).

## 16. SESSÃO 2026-06-22 (noite) — UNIDADE 2 (2ª série): caps. 01-01 e 01-02 ALUNO, dois PDFs separados

**Tarefa:** diagramar em PDF a versão ALUNO dos caps. **01-01** ("Revoltas, poder
e disputas no Brasil Imperial") e **01-02** ("Escravidão, resistência e
transformações sociais") da apostila `apostila-historia-unidade2-2serie` —
**ATENÇÃO: é a UNIDADE 2**, não a unidade 1 das sessões §13–§15. Um PDF separado
por capítulo. Imagens reais em `output/apostila-historia-unidade2-2serie/imagens`,
verificações externas em `output/apostila-historia-unidade2-2serie/verificacao`.
Motor: `xml_to_pdf.py` (WeasyPrint), **sem alteração nenhuma** — os fixes do §13
(lista-subtipos/classificacao) e §14 (quebra por bloco, `bloco-keep`, imagens
140mm) já cobrem estes capítulos. `py_compile` limpo; 636 linhas.

**BLOQUEIO ENCONTRADO E RESOLVIDO ANTES DE RODAR:** no início, a pasta
`verificacao/` só tinha os 6 JSON do cap. 01-02 (`verif-01-02-s1…s5` +
`aplicar-01-02`); **faltavam todos os 6 do cap. 01-01**. Como as verificações do
01-01 são `status="externo"` no XML, na versão ALUNO (`incluir_gabarito=False`)
o `render_sb_externo`→`_sb_pendente` retorna `""` **silenciosamente** — o PDF
sairia sem nenhuma das 5 verificações nem o "Aplicar agora", sem erro visível.
Sinalizei ao usuário em vez de gerar incompleto; ele forneceu os 6 JSON
(`verif-01-01-s1…s5` + `aplicar-01-01`). Revalidados: `json.load` OK nos 6.
**Lição para a próxima sessão:** SEMPRE conferir, ANTES de rodar, que existe um
JSON na pasta de verificações para cada `ref` `status="externo"` do XML (grep
`ref=` no XML × `ls verificacao/`); ref ausente vira buraco mudo no aluno.

**Comandos finais usados:**
```bash
BASE=output/apostila-historia-unidade2-2serie
XMLDIR=$BASE/formatado/unidade-2-conflitos-e-transformacoes-no-brasil-do-seculo-xix
# cap 01-01
python3 xml_to_pdf.py "$XMLDIR/01-01-capitulo-1-revoltas-poder-e-disputas-no-brasil-imperial.xml" \
  --versao-aluno --imagens $BASE/imagens --verificacoes $BASE/verificacao \
  --output apostilas/01-01-capitulo-1-revoltas-poder-e-disputas-no-brasil-imperial-aluno.pdf
# cap 01-02
python3 xml_to_pdf.py "$XMLDIR/01-02-capitulo-2-escravidao-resistencia-e-transformacoes-sociais.xml" \
  --versao-aluno --imagens $BASE/imagens --verificacoes $BASE/verificacao \
  --output apostilas/01-02-capitulo-2-escravidao-resistencia-e-transformacoes-sociais-aluno.pdf
```
(Os XMLs dos dois capítulos fizeram `ET.parse` OK — **não** houve o truncamento
do §15 nesta unidade.)

**Verificação (ambos, versão aluno):**
- **Conformidade de conteúdo (via `--html-only` + grep):** cada capítulo tem
  exatamente **5** "Verificacao de aprendizagem" + **1** "Aplicar agora";
  **20** `class="alternativa"` (5×4); **0** `verif-pendente`; **0** classe
  distinta para a correta; legenda de imagem oculta (**0** `imagem-legenda`).
  Contagem de `<img>`: 01-01 = **4** (`fig-01-01-01…04`), 01-02 = **3**
  (`fig-01-02-01…03`) — bate com os refs dos XMLs.
- **Regras invioláveis (via `pdftotext` no PDF):** **0** ocorrências de
  gabarito/justificativa/"resposta comentada"/"resposta modelo"/"uso do
  professor" em ambos. Nenhuma marcação visual da alternativa correta.
- **Identificação (capa):** nomes vindos do briefing OK — "CAPITULO 1 / Como a
  disputa entre centralização política e poder regional…" e "CAPITULO 2 / Como a
  resistência dos escravizados…"; habilidade H15 nas duas. Sem "AVISO:
  briefing.json invalido".
- **Render PNG 150dpi de TODAS as páginas + 1ª linha de texto por página:**
  - 01-01 = **18 páginas**. Headers de bloco abrindo no topo seguidos de
    conteúdo: DEFINIR p2 · SEQUENCIAR p4 · COMPARAR p8 · MAPEAR CAUSALIDADE p12 ·
    APLICAR p15. **ZERO cabeçalho de bloco órfão** (o §9 NÃO se manifestou; o
    `bloco-keep` do §14 segura). **ZERO página totalmente em branco.**
  - 01-02 = **13 páginas**. DEFINIR p2 · CLASSIFICAR p4 · COMPARAR p6 · MAPEAR p9.
    Mesmo resultado: zero header órfão, zero página em branco. Fix §13
    (lista-subtipos) ativo no bloco CLASSIFICAR — texto completo nas 2 colunas.
  - Imagens grandes e legíveis, **sem legenda**; `nota_fonte` (citação) aparece
    abaixo das figuras.
- **Branco de rodapé por página (PIL, exclui faixa ~20mm do `@bottom-center`):**
  - 01-01: p1 53,7(capa)·p2 0,4·p3 31,4·p4 0,4·p5 14,7·p6 43,7·p7 48,1·p8 0,4·
    p9 38,4·p10 37,9·p11 46,5·p12 0,4·p13 5,3·p14 52,6·p15 0,4·p16 41,4·p17 41,3·
    p18 55,0. **Média 28,4%.**
  - 01-02: p1 51,7(capa)·p2 3,8·p3 51,5·p4 4,2·p5 12,8·p6 0,4·p7 4,6·p8 49,6·
    p9 0,4·p10 4,0·p11 0,4·p12 21,0·p13 7,0. **Média 16,3%.**

**Por que o 01-01 ficou maior (18 pgs, branco médio 28,4%):** ele tem **4
imagens + 5 verificações** (uma imagem a mais que o 01-02 e que os capítulos da
unidade 1). É o **resíduo conhecido e aceito do §14**: imagem grande (140mm,
full-width, `break-inside: avoid`) + verificação full-width não cabem juntas e
cada uma orfana com branco abaixo (p6/p7, p10/p11, p14, p16/p17). **NÃO é
regressão nem o bug do §9** — é o custo de ampliar as imagens. Se incomodar:
reduzir `max-height` (110–120mm) reequilibra imagem × branco (mesma receita do §14).

**Artefatos finais (em `C:\Users\Roberto\Desktop\IPPI\apostilas`):**
- `01-01-capitulo-1-revoltas-poder-e-disputas-no-brasil-imperial-aluno.pdf`
  (18 páginas, ~1,18 MB)
- `01-02-capitulo-2-escravidao-resistencia-e-transformacoes-sociais-aluno.pdf`
  (13 páginas, ~0,60 MB)

**Pendências herdadas / a fazer quando pedirem:**
- Gerar a **versão PROFESSOR** dos dois capítulos da unidade 2 (atenção ao
  resíduo do §9-bis: o box de gabarito sobe a altura da verificação e pode
  interagir com as imagens 140mm — mais relevante no 01-01, que já tem branco alto).
- Na ORIGEM do pipeline: garantir que os 6 JSON de verificação de cada capítulo
  sejam gerados/salvos junto, para não reincidir o bloqueio do início desta sessão.

## 17. SESSÃO 2026-06-23 — 1ª série, UNIDADE 1 de História: caps. 01-01 e 01-02 ALUNO

**Tarefa:** diagramar em PDF a versão **ALUNO** dos caps. **01-01**
("Fontes Históricas e Construção do Conhecimento Histórico") e **01-02**
("Narrativas Históricas e Linguagens") de
`output/1serie-apostila-historia-unidade1`. Dois PDFs separados, só ALUNO
(pedido explícito do usuário: "faça somente a versão do aluno"). Motor:
`xml_to_pdf.py` (WeasyPrint), **sem alteração nenhuma** — `python3 -m
py_compile xml_to_pdf.py` limpo, 636 linhas, igual ao §16. Imagens reais em
`output/1serie-apostila-historia-unidade1/imagens`, verificações externas em
`output/1serie-apostila-historia-unidade1/verificacoes` (nome da pasta no
plural nesta unidade — atenção ao copiar comandos de sessões anteriores).

**Achado ANTES de rodar — `briefing.json` não é auto-detectado em modo
XML único:** `carregar_briefing()` só dispara automaticamente quando se passa
`--unidade <pasta>`; passando o caminho de um XML específico (como pedido
aqui, um capítulo por vez), o briefing não é carregado e a capa sai sem o
"eyebrow" de Unidade. **Fix aplicado:** passar
`--briefing input/1serie-apostila-historia-unidade1/briefing.json`
explicitamente nos dois comandos. Confirmado via `pdftotext` que a capa
passou a trazer "UNIDADE 1 — A CONSTRUÇÃO DO CONHECIMENTO HISTÓRICO" +
"CAPÍTULO 1/2" + nome do capítulo + habilidade + "PERGUNTA NORTEADORA".
**Lição:** em modo de capítulo único, sempre passar `--briefing` manualmente.

**BLOQUEIO DE DADOS ENCONTRADO (não é bug de engine) — `aplicar-01-02.json`
ausente:** a pasta `verificacoes/` tem `aplicar-01-01.json` +
`verif-01-01-s1..s4.json` + `verif-01-02-s1..s4.json`, mas **falta
`aplicar-01-02.json`**. Como o rodapé do XML 01-02 referencia
`<sidebar tipo="aplicar-agora" ref="aplicar-01-02" status="externo">`, e na
versão ALUNO (`incluir_gabarito=False`) o `_sb_pendente()` retorna `""`
silenciosamente (mesmo "buraco mudo" documentado no §16), **o PDF do cap.
01-02 saiu sem a atividade "Aplicar agora" final, sem nenhum erro ou aviso
visível** — confirmado via `--html-only`: `class="aplicar-agora"` = 0
ocorrências (contra 1 no cap. 01-01) e `verif-pendente` = 0 também (porque o
retorno vazio não deixa nem placeholder). Gerei os dois PDFs mesmo assim,
porque o usuário pediu para diagramar os dois capítulos agora e o restante do
conteúdo de 01-02 está completo e correto — mas **este gap precisa ser
comunicado ao usuário e resolvido** (fornecer o JSON faltante e regerar
apenas o cap. 01-02) antes de considerar este capítulo como entregue de
verdade. Cap. 01-01 não tem esse problema — os 6 JSON dele existem todos.

**Comandos finais usados:**
```bash
BASE=output/1serie-apostila-historia-unidade1
XMLDIR=$BASE/formatado/unidade-1-a-construcao-do-conhecimento-historico
BRIEF=input/1serie-apostila-historia-unidade1/briefing.json
# cap 01-01
python3 xml_to_pdf.py "$XMLDIR/01-01-capitulo-1-fontes-historicas-e-construcao-do-conhecimento-historico.xml" \
  --versao-aluno --imagens $BASE/imagens --verificacoes $BASE/verificacoes --briefing $BRIEF \
  --output apostilas/01-01-capitulo-1-fontes-historicas-e-construcao-do-conhecimento-historico-aluno.pdf
# cap 01-02
python3 xml_to_pdf.py "$XMLDIR/01-02-capitulo-2-narrativas-historicas-e-linguagens.xml" \
  --versao-aluno --imagens $BASE/imagens --verificacoes $BASE/verificacoes --briefing $BRIEF \
  --output apostilas/01-02-capitulo-2-narrativas-historicas-e-linguagens-aluno.pdf
```
(Os dois XMLs fizeram `ET.parse` OK — sem truncamento do §15.)

**Nota de metodologia desta sessão:** ao inspecionar visualmente os PNGs
renderizados (`pdftoppm -png -r 150`), produzi descrições incorretas da
página em pelo menos duas ocasiões (confundi o conteúdo da p.5 com o da p.3,
e descrevi a p.8 como contendo uma tabela HTML quando na verdade é texto
corrido + a imagem `fig-01-01-02` embutida). Confirmei o engano comparando
com `pdftotext -layout -f N -l N` (texto real de cada página) e
`pdfimages -list` (página real de cada imagem) — ambos se mostraram corretos
e estáveis em re-checagens, ao contrário da minha leitura visual direta dos
PNGs. **Lição para a próxima sessão:** não confiar em descrição visual
freeform de PNG como evidência principal de validação, especialmente em
lotes de páginas com aparência repetitiva (cabeçalho colorido + 2 colunas).
Usar como evidência objetiva, nesta ordem: `pdftotext` por página, `pdfimages
-list`, contagem estrutural via `--html-only` + grep, e o script de
"branco de rodapé" via PIL. Visualizar PNG fica reservado para checagem
pontual final, não para descrever página por página.

**Verificação (ambos, versão aluno):**
- **Conformidade de conteúdo (via `--html-only` + grep):** 01-01 tem **4**
  sidebars de verificação (`verif-01-01-s1..s4`) + **1** "Aplicar agora";
  **16** `class="alternativa"` (4×4); **3** `<img>` (`fig-01-01-01..03`);
  **5** `subtipo-item` no bloco CLASSIFICAR (Fonte escrita oficial / não
  oficial / visual / oral / material). 01-02 tem **4** sidebars de
  verificação (`verif-01-02-s1..s4`) + **0** "Aplicar agora" (gap acima);
  **16** `class="alternativa"`; **2** `<img>` (`fig-01-02-01..02`); **5**
  `subtipo-item` (Livro didático / Pintura histórica / Filme histórico /
  Canção popular / Postagem em rede social). `verif-pendente` = 0 e
  `imagem-legenda` = 0 nos dois.
- **Regras invioláveis:** `correta="sim"` nunca aparece no HTML renderizado
  (0 ocorrências); todas as alternativas usam a mesma classe CSS; **0**
  ocorrências de gabarito/resposta-modelo/"uso do professor" como texto
  visível nos dois HTMLs e nos dois PDFs (via `pdftotext`).
- **Identificação (capa, após fix do `--briefing`):** "UNIDADE 1 — A
  CONSTRUÇÃO DO CONHECIMENTO HISTÓRICO" / "CAPÍTULO 1" e "CAPÍTULO 2" / nomes
  corretos / "PERGUNTA NORTEADORA" presente nos dois.
- **Render PNG 150dpi de todas as páginas + 1ª linha de texto por página
  (`pdftotext -layout -f N -l N`):**
  - 01-01 = **13 páginas**. DEFINIR p2 · CLASSIFICAR p4 · RECONHECER
    PERSPECTIVA p7 · COMPARAR p10 · APLICAR AGORA p13. Sidebars de
    verificação isolados em p3/p6/p9/p12 (conteúdo completo, não em branco —
    confirmado por `pdftotext`). **ZERO cabeçalho de bloco órfão** (§9 não se
    manifestou; `bloco-keep` do §14 segura). **ZERO página totalmente em
    branco.**
  - 01-02 = **11 páginas**. DEFINIR p2 · CLASSIFICAR p4 · RECONHECER
    PERSPECTIVA p7 · COMPARAR p9. Sidebar de verificação isolado em p3.
    Mesmo resultado: zero header órfão, zero página em branco. Termina na
    p11 com a última verificação + citações — **sem página de "Aplicar
    agora"** por causa do JSON ausente (gap já registrado acima).
  - As 5 imagens (3 no 01-01: p5/p8/p11; 2 no 01-02: p6/p10 — confirmado via
    `pdfimages -list`) caem todas em páginas de branco baixo (1,8%–13,1%),
    ou seja, compactas e packed com texto/sidebar ao redor, sem legenda
    (`imagem-legenda` = 0 nos dois).
- **Branco de rodapé por página (PIL, exclui faixa ~20mm do
  `@bottom-center`):**
  - 01-01: p1 46,8(capa)·p2 15,6·p3 55,0·p4 1,8·p5 9,5·p6 44,9·p7 2,4·
    p8 13,1·p9 48,2·p10 2,4·p11 3,2·p12 41,4·p13 53,1. **Média 25,9%.**
  - 01-02: p1 47,7(capa)·p2 30,0·p3 46,5·p4 1,0·p5 38,4·p6 3,1·p7 0,9·
    p8 2,9·p9 2,4·p10 5,9·p11 35,3. **Média 19,5%.**
  - Os percentuais altos (p3/p6/p9/p12 do 01-01; p3 do 01-02) são sidebars de
    verificação isolados no topo da página com branco abaixo — o mesmo
    resíduo já aceito no §14/§16 (quebra forçada por bloco não garante que a
    verificação encha a página). Nenhum chega ao nível grave "quase
    inteiramente em branco" do §13: todos têm texto real substancial
    confirmado por `pdftotext`.

**Artefatos finais (em `C:\Users\Roberto\Desktop\IPPI\apostilas`):**
- `01-01-capitulo-1-fontes-historicas-e-construcao-do-conhecimento-historico-aluno.pdf`
  (13 páginas, ~2,31 MB) — **completo**, sem gaps.
- `01-02-capitulo-2-narrativas-historicas-e-linguagens-aluno.pdf`
  (11 páginas, ~1,52 MB) — **incompleto**: falta a seção "Aplicar agora"
  final por causa do `aplicar-01-02.json` ausente.

**Pendências herdadas / a fazer quando pedirem:**
- Obter ou escrever `aplicar-01-02.json` (mesmo formato de
  `aplicar-01-01.json`: tipo, ref, enunciado, resposta_comentada) e regerar
  **só** o PDF do cap. 01-02 com o mesmo comando acima — sem precisar tocar
  no cap. 01-01.
- Gerar a versão PROFESSOR dos dois capítulos quando solicitado.
- Na ORIGEM do pipeline: ao gerar uma nova unidade/capítulo, conferir
  `grep -o 'ref="[^"]*"' <xml>` × `ls verificacoes/` ANTES de rodar, para
  pegar refs ausentes antes da diagramação (lição repetida do §16 — vale
  reforçar como checklist fixo, não só lição pontual).
