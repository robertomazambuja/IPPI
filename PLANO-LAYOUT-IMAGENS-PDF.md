# Plano — Reorganizar o layout do PDF após a entrada das imagens

> Documento de proposta (não executei mudanças no motor). Complementa o
> `HANDOVER-DIAGRAMACAO-PDF.md`. Foco: capítulo `01-01` da
> `apostila-sociologia-trabalho`, versão do aluno, com as 3 imagens reais
> já em `output/apostila-sociologia-trabalho/imagens/`.
> Data: 2026-06-16.

## 1. O que eu olhei

- `HANDOVER-DIAGRAMACAO-PDF.md` (estado anterior, ainda **sem** imagens).
- Motor `xml_to_pdf.py` (471 linhas): `render_imagem()`, `render_secao()`,
  `render_bloco()` (a segmentação multicol), e o CSS em `build_css()`.
- O XML `01-01-...xml`: estrutura de 4 blocos, com 3 `<imagem>` e 4
  `<sidebar tipo="verificacao">`, e 2 `<quebra tipo="pagina">`.
- As 3 imagens reais: paisagem larga — `fig-01-01-01` e `02` em 1408×768
  (proporção 1.83), `fig-01-01-03` em 1470×575 (proporção 2.56).
- O PDF atual já gerado (`01-01-...-aluno.pdf`, 12 páginas), renderizado
  página a página em PNG.

## 2. Diagnóstico — o que de fato "bagunçou"

O sintoma principal **não** é a imagem em si: as 3 imagens são infográficos
em paisagem que ficam legíveis em largura total. O problema é **espaço em
branco grande e irregular** que apareceu junto com elas. Exemplos do PDF atual:

- **p.4** — só a linha do tempo (`fig-01-01-01`) no topo, ~65% da página em branco abaixo.
- **p.5** — só a verificação do bloco 2 no topo, ~75% em branco abaixo.
- **p.8** — só a verificação do bloco 3 no topo, ~70% em branco abaixo.
- **p.11** — em contraste, a tabela comparativa (`fig-01-01-03`) **+** a
  verificação couberam juntas na mesma página: ficou bem diagramada.

Ou seja: o resultado é **inconsistente**. Às vezes empacota bem (p.11),
às vezes deixa páginas quase vazias (p.4, p.5, p.8).

### 2.1 Causa-raiz (arquitetural)

A "segmentação multicol" (seção 3 do handover) trata **imagem e verificação
como elementos full-width** que dão `flush()` nas colunas e são emitidos
soltos, cada um com `break-inside: avoid`. Dentro de um bloco a ordem típica é:

```
[texto em 2 colunas]  →  [IMAGEM full-width]  →  [VERIFICAÇÃO full-width]
```

Quando **imagem + verificação não cabem juntas** no que sobra da página, o
`break-inside: avoid` joga cada uma para uma página nova. Como o motor é
**linear e não tem "backfill"** (nada volta a preencher o vão deixado para
trás), sobra a página anterior com um buraco enorme. Quando, por sorte de
encadeamento, os dois cabem juntos (p.11), fica ótimo. É puro acaso de quanto
espaço sobrou — daí a inconsistência.

Antes das imagens isso quase não aparecia: havia menos elementos full-width
por página, então a verificação geralmente cabia. As imagens **dobraram** a
quantidade de blocos full-width que disputam o mesmo espaço, e o problema
latente virou visível.

### 2.2 Problemas secundários encontrados

1. **Bug de caminho relativo em `render_imagem()`.** A função faz
   `Path(...).as_uri()`, que **estoura** (`ValueError: relative path can't be
   expressed as a file URI`) se `--imagens` for passado como caminho relativo.
   Reproduzi rodando com caminho relativo. O PDF atual só existe porque foi
   gerado com caminho absoluto. Precisa de `.resolve()` antes do `as_uri()`.
2. **Legenda truncada em 100 caracteres** (`desc[:100]`) — corta a descrição
   no meio, às vezes deixando frase pela metade sob a imagem.
3. **Sem `max-height` na imagem.** Hoje a imagem ocupa 100% da largura útil
   (~178 mm). Uma imagem 2.56:1 vira ~70 mm de altura; uma 1.83:1 vira ~97 mm.
   Tudo bem para estas 3, mas uma imagem em retrato (futuros capítulos)
   ocuparia a página inteira sem teto de altura.
4. **A descrição no XML é um *briefing* de produção**, não uma legenda final
   (ex.: "Linha do tempo com 5 marcos: ... → ..."). Usar isso como legenda
   visível para o aluno fica estranho. Vale decidir o que mostrar.

## 3. Princípios para a solução

- Manter o motor WeasyPrint; **não** voltar ao ReportLab (handover §12).
- Não brigar com `column-span: all` (instável no WeasyPrint) — manter a
  segmentação por flush.
- Objetivo de diagramação: **menos buracos, ritmo visual previsível**, imagem
  perto do texto que ela ilustra, e a verificação fechando o bloco sem ficar
  sozinha numa página.
- Toda mudança grande no `xml_to_pdf.py`: reescrever via shell + `py_compile`
  + render visual em PNG (handover §10).

## 4. Propostas (em ordem de impacto / esforço)

### Correções rápidas (baixo risco, fazer de qualquer forma)

- **C1. Corrigir o bug do caminho** — `Path(imagens_dir).resolve()` (ou tornar
  `imdir` absoluto logo na leitura de `--imagens` em `main()`). Destrava rodar
  com caminho relativo.
- **C2. Legenda** — parar de truncar em 100 chars. Decidir entre:
  (a) não exibir legenda (a descrição é briefing de produção); ou
  (b) criar no XML um campo `<legenda>` curto e próprio para o aluno, separado
  da `<descricao>` técnica. Recomendo (b), mas (a) é o "MVP" imediato.
- **C3. `max-height` na imagem** — teto de ~110–130 mm em `.imagem-container img`
  (com `object-fit: contain`), para nenhuma imagem futura tomar a página inteira.

### Ataque ao espaço em branco (o ponto central)

O alvo é fazer imagem e verificação **pararem de orfanar**. Três caminhos,
do mais simples ao mais estrutural:

- **A. Tornar a imagem "flutuável" dentro da coluna quando ela for estreita,
  e full-width só quando for larga.**
  Imagens em paisagem larga (como estas 3) ficam full-width; mas o motor passa
  a **permitir que o texto seguinte volte a fluir em 2 colunas logo abaixo**,
  em vez de cada full-width forçar página nova. Reduz buraco, mas sozinho não
  resolve o par imagem+verificação que não cabe.

- **B. "Keep-together" imagem + legenda, e verificação tratada à parte, com
  preenchimento por reordenação local.**
  Em cada bloco, se sobra pouco espaço antes de um full-width, deixar o motor
  **adiantar** o próximo segmento de coluna para encher a página atual e só
  então emitir o full-width na página seguinte. Na prática é mudar a ordem de
  emissão dentro do `render_bloco()` para "empacotar gulosamente": acumular
  full-widths e segmentos de coluna e soltar na ordem que minimiza vão.
  Médio esforço, resolve a maioria dos casos (p.4/p.5/p.8).

- **C. Repensar o slot da verificação.** A verificação é sempre o **fecho do
  bloco**. Duas opções de design:
  (c1) deixá-la entrar como **caixa dentro de uma das 2 colunas** quando o
  texto da alternativa é curto (como já fazem as caixas de autor), em vez de
  full-width — assim ela preenche coluna em vez de virar uma faixa solitária;
  (c2) mantê-la full-width, mas com `break-before: avoid` amarrando-a ao
  último segmento de coluna do bloco, para nunca começar sozinha no topo de
  uma página.
  (c1) é a que mais elimina branco; (c2) é a mais conservadora.

> Recomendação: combinar **C1+C3** (rápidas) com **B** (empacotamento guloso)
> e **c2** (amarrar verificação ao conteúdo anterior). Isso ataca a causa-raiz
> sem reescrever a arquitetura de colunas. Se ainda sobrar branco em blocos
> curtos, avaliar **c1** (verificação na coluna).

### Item ainda herdado (do handover §9)

- **Cabeçalho de bloco órfão** (a faixa "SEQUENCIAR" sozinha no pé da página).
  Não foi resolvido e continua em aberto. A direção 1 do handover (emitir o
  `.bloco-header` **dentro** do primeiro `.bloco-multicol`, com a unidade
  header+1ª-fatia em `break-inside: avoid`) deve entrar junto, porque mexe no
  mesmo `render_bloco()` que vamos tocar para o empacotamento.

## 5. Plano de execução sugerido (em fases)

1. **Fase 0 — rede de segurança.** Backup do `xml_to_pdf.py`, fixar comando de
   render PNG de referência (as 12 páginas) para comparar antes/depois.
2. **Fase 1 — correções rápidas C1, C2(a), C3.** Destrava caminho relativo,
   tira truncamento, põe teto de altura. Render + conferir.
3. **Fase 2 — empacotamento (B) + amarrar verificação (c2) + header não-órfão.**
   Reescrever `render_bloco()` via shell (heredoc), `py_compile`, render visual
   das páginas-problema (4, 5, 7, 8) e das boas (6, 11) para não regredir.
4. **Fase 3 — avaliação de design (decisões suas):** legenda própria no XML
   (C2b), e se a verificação curta deve ir para dentro da coluna (c1).
5. **Fase 4 — validar nos 3 capítulos** (01-01, 01-02, 01-03) e na versão do
   professor (que tem gabarito e resposta-modelo e muda as alturas).

## 6. Decisões que preciso de vocês para fechar

1. **Legenda da imagem:** esconder por enquanto, ou criar um campo `<legenda>`
   curto no XML (separado da `<descricao>` técnica)?
2. **Verificação:** pode virar caixa **dentro de coluna** quando for curta
   (mais compacto), ou deve permanecer sempre em largura total?
3. **Escopo agora:** quer que eu já implemente as **Fases 1–2** (correções +
   empacotamento) e te traga o PDF revisado para comparar, ou prefere validar
   este plano primeiro?

## 7. Validação prevista

- `python3 -m py_compile xml_to_pdf.py` após cada edição grande.
- `pdftoppm -png -r 150` e leitura página a página, comparando contra o PNG de
  referência da Fase 0 (medir % de branco nas páginas 4/5/8).
- Rodar aluno **e** professor, e os 3 capítulos, antes de considerar pronto.
