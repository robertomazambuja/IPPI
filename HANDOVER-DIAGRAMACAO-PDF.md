# Handover — Diagramação do PDF da apostila (projeto IPPI)

> Documento para o próximo assistente continuar a qualificação da diagramação
> do PDF. Lê isto antes de mexer em qualquer coisa.
> Última atualização: 2026-06-15 (após uma sessão de correções — ver seção 4).

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
