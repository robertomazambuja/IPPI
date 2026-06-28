#!/usr/bin/env python3
"""
xml_to_pdf.py — Converte XMLs do pipeline IPPI em PDFs de apostila.

Uso:
    python xml_to_pdf.py <arquivo.xml> [--imagens <pasta>] [--output <arquivo.pdf>]
    python xml_to_pdf.py --unidade <pasta_xml> [--briefing <briefing.json>] [--output apostila.pdf]
    python xml_to_pdf.py --unidade <pasta_xml> --versao-aluno      # processo do ALUNO  (sem gabarito/resposta)
    python xml_to_pdf.py --unidade <pasta_xml> --versao-professor  # processo do PROFESSOR (com gabarito/resposta)

IMPORTANTE: aluno e professor sao DOIS processos separados. Rode um de cada vez.
Se nenhuma versao for indicada, o script ERRA para evitar gerar a versao errada.
"""

import argparse, os, sys, re, json, html as html_mod
from pathlib import Path
from xml.etree import ElementTree as ET
import weasyprint

# --- Guarda de contrato: nao deixa o renderizador descartar tag em silencio. ---
# Toda vez que o formatador emite uma tag que nenhum ramo deste arquivo consome,
# avisamos em stderr (com de-dup). Foi a ausencia disso que deixou o bug de
# <introducao>/<lista-subtipos> (classificacao) e <sintese>/<encadeamento>
# (rodape) passarem despercebidos: o conteudo sumia sem erro algum.
_TAGS_DESCONHECIDAS = set()
def avisar_tag_desconhecida(contexto, tag):
    chave = (contexto, tag)
    if chave not in _TAGS_DESCONHECIDAS:
        _TAGS_DESCONHECIDAS.add(chave)
        sys.stderr.write(
            f"[xml_to_pdf] AVISO: tag <{tag}> dentro de <{contexto}> nao e "
            f"renderizada — conteudo descartado. O formatador emitiu algo que o "
            f"renderizador nao conhece; atualize render_* ou o contrato.\n")

# A4 em mm e inset da moldura (frame com tamanho EXPLICITO)
PAGE_W_MM, PAGE_H_MM = 210, 297
FRAME_INSET_MM = 10
FRAME_W_MM = PAGE_W_MM - 2 * FRAME_INSET_MM   # 190
FRAME_H_MM = PAGE_H_MM - 2 * FRAME_INSET_MM   # 277

OPERACAO_CORES = {
    "Definir":                {"fundo": "#E3F2FD", "destaque": "#1565C0"},  # Nivel 1
    "Classificar":            {"fundo": "#E0F7FA", "destaque": "#00838F"},  # Nivel 1
    "Sequenciar":             {"fundo": "#E8F5E9", "destaque": "#2E7D32"},  # Nivel 1
    "Comparar":               {"fundo": "#F3E5F5", "destaque": "#6A1B9A"},  # Nivel 2
    "Mapear causalidade":     {"fundo": "#FFF3E0", "destaque": "#E65100"},  # Nivel 2
    "Reconhecer perspectiva": {"fundo": "#FCE4EC", "destaque": "#AD1457"},  # Nivel 3
    "Aplicar":                {"fundo": "#EFEBE9", "destaque": "#4E342E"},  # Nivel 3
}
COR_PADRAO = {"fundo": "#F5F5F5", "destaque": "#424242"}


def build_css(versao_label=""):
    rotulo = ('@bottom-right { content: "' + versao_label + '"; font-family: Arial; '
              'font-size: 7pt; color: #B0B0B0; }') if versao_label else ""
    css = r"""
@page {
    size: A4;
    margin: 18mm 16mm 20mm 16mm;
    @bottom-center { content: counter(page); font-family: Arial; font-size: 10pt; color: #888; }
    __ROTULO__
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Georgia, serif; font-size: 10.5pt; line-height: 1.65; color: #1a1a1a;
       hyphens: auto; orphans: 2; widows: 2; }


/* CAPA DO CAPITULO */
.capa-capitulo { break-before: page; padding: 6pt 0 18pt; border-bottom: 3pt solid #1565C0; margin-bottom: 20pt; }
.capitulo-eyebrow { font-family: Arial; font-size: 8pt; font-weight: 700; letter-spacing: .10em;
    text-transform: uppercase; color: #5B7AA8; margin-bottom: 10pt; }
.capitulo-numero { font-family: Arial; font-size: 11pt; font-weight: 700; letter-spacing: .14em;
    text-transform: uppercase; color: #1565C0; margin-bottom: 4pt; }
.capitulo-nome { font-family: Arial; font-size: 18pt; font-weight: 700; color: #0d2b6e;
    line-height: 1.25; margin-bottom: 14pt; }
.habilidade-badge { display: inline-block; background: #1565C0; color: #fff; font-family: Arial;
    font-size: 8.5pt; font-weight: 700; padding: 4pt 10pt; border-radius: 12pt; margin-bottom: 12pt; }
.pergunta-norteadora { font-family: Arial; font-size: 10pt; font-weight: 700; color: #243b66;
    line-height: 1.35; margin-bottom: 10pt; }
.pergunta-norteadora .rotulo { font-weight: 700; color: #1565C0; text-transform: uppercase;
    font-size: 8pt; letter-spacing: .06em; display: block; margin-bottom: 2pt; }
.por-que-importa { background: #EEF4FF; border-left: 4pt solid #1565C0; padding: 10pt 14pt;
    font-size: 9.5pt; font-style: italic; color: #1a3566; border-radius: 0 6pt 6pt 0; margin-top: 10pt; }

/* CAPA DO INDICE — sumario da unidade (primeira pagina, gerada a partir de
   um XML <indice> dentro da pasta --unidade). O numero de pagina de cada
   capitulo e calculado automaticamente pelo PDF via CSS target-counter,
   apontando para a ancora id="capa-{ref}" emitida em capa-capitulo abaixo —
   nao precisa ser mantido manualmente quando o conteudo mudar de tamanho. */
.capa-indice { padding: 6pt 0 18pt; break-after: page; }
.indice-eyebrow { font-family: Arial; font-size: 8pt; font-weight: 700; letter-spacing: .10em;
    text-transform: uppercase; color: #5B7AA8; margin-bottom: 10pt; }
.indice-titulo-unidade { font-family: Arial; font-size: 20pt; font-weight: 700; color: #0d2b6e;
    line-height: 1.25; margin-bottom: 10pt; }
.indice-habilidade { display: inline-block; background: #1565C0; color: #fff; font-family: Arial;
    font-size: 8.5pt; font-weight: 700; padding: 4pt 10pt; border-radius: 12pt; margin-bottom: 20pt; }
.indice-sumario-label { font-family: Arial; font-size: 10pt; font-weight: 700; letter-spacing: .08em;
    text-transform: uppercase; color: #243b66; border-bottom: 2pt solid #1565C0; padding-bottom: 6pt;
    margin-bottom: 18pt; }
.indice-item { margin-bottom: 18pt; break-inside: avoid; }
.indice-item:last-child { margin-bottom: 0; }
.indice-link { display: flex; align-items: baseline; text-decoration: none; color: #1a1a1a; }
.indice-link::after { content: target-counter(attr(href), page); font-family: Arial; font-size: 11pt;
    font-weight: 700; color: #1565C0; margin-left: auto; padding-left: 10pt; }
.indice-numero { font-family: Arial; font-size: 9pt; font-weight: 700; letter-spacing: .06em;
    text-transform: uppercase; color: #1565C0; flex: 0 0 auto; margin-right: 12pt; white-space: nowrap; }
.indice-nome { font-family: Arial; font-size: 12.5pt; font-weight: 700; color: #243b66; }
.indice-pergunta { font-family: Georgia, serif; font-size: 9pt; font-style: italic; color: #666;
    margin: 4pt 0 0 0; line-height: 1.5; }

/* MAPA PROGRESSAO */
.mapa-progressao { display: flex; margin: 18pt 0 4pt; background: #F8F9FA; border: 1pt solid #DEE2E6;
    border-radius: 8pt; overflow: hidden; }
.mapa-passo { flex: 1; text-align: center; padding: 9pt 8pt; font-family: Arial; font-size: 8.5pt;
    font-weight: 700; border-right: 1pt solid #DEE2E6; }
.mapa-passo:last-child { border-right: none; }
.mapa-passo .num { display: block; font-size: 7pt; color: #999; margin-bottom: 3pt; font-weight: 400; }

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

/* BLOCO */
.bloco { margin-bottom: 22pt; }
/* Cada micro-habilidade (bloco) comeca em pagina nova; o primeiro nao recebe a classe. */
.bloco-quebra { break-before: page; }
/* Mantem o cabecalho do bloco colado a primeira fatia de conteudo,
   evitando a faixa de operacao orfa no topo de uma pagina (problema do
   multicol que ignora break-after:avoid no cabecalho). */
.bloco-keep { break-inside: avoid; }
.bloco-header { padding: 9pt 14pt; border-radius: 6pt 6pt 0 0; break-after: avoid; }
.bloco-header .operacao-nome { font-family: Arial; font-size: 9pt; font-weight: 700;
    text-transform: uppercase; letter-spacing: .08em; color: #fff; }
.bloco-header .micro-habilidade { font-family: Arial; font-size: 8.5pt; font-weight: 700;
    color: #fff; margin-top: 4pt; }

/* MULTICOL */
.bloco-multicol { column-count: 2; column-gap: 7mm; column-rule: 0.5pt solid #DDDDDD;
    border-top: 2pt solid #ccc; padding: 11pt 2pt 3pt; }
.bloco-multicol .secao { margin-bottom: 12pt; }
.bloco-multicol .secao:last-child { margin-bottom: 0; }

/* SECAO */
.secao-titulo { font-family: Arial; font-size: 10.5pt; font-weight: 700; margin-bottom: 8pt;
    padding-bottom: 4pt; border-bottom: 1pt solid #E0E0E0; break-after: avoid; }
.secao p { margin-bottom: 8pt; text-align: justify; }
.secao p:last-child { margin-bottom: 0; }

/* LISTA DE SUBTIPOS (operacao Classificar: introducao + itens nomeados) */
.lista-subtipos { margin-top: 2pt; }
.lista-subtipos .subtipo-item { margin-bottom: 8pt; }
.lista-subtipos .subtipo-item:last-child { margin-bottom: 0; }
.subtipo-nome { font-family: Arial; font-size: 9pt; font-weight: 700; color: #333; margin-bottom: 3pt; }

/* SIDEBAR AUTOR */
.sidebar-autor { width: 100%; margin: 4pt 0 10pt; background: #FFF8F0; border: 1.5pt solid #E8A838;
    border-left-width: 4pt; border-radius: 0 6pt 6pt 0; padding: 9pt 11pt; font-family: Arial; break-inside: avoid; }
.sidebar-autor .autor-nome { font-size: 9.5pt; font-weight: 700; color: #7B4A00; margin-bottom: 1pt; }
.sidebar-autor .autor-pais { font-size: 8pt; color: #A0714A; margin-bottom: 6pt; }
.sidebar-autor .autor-desc { font-size: 8.5pt; line-height: 1.5; color: #3a2000; }

/* VERIFICACAO */
.sidebar-verificacao { background: #EEF4FF; border: 1.5pt solid #90CAF9; border-left-width: 4pt;
    border-radius: 0 6pt 6pt 0; padding: 11pt 13pt; margin: 9pt 0 6pt; font-family: Arial;
    break-inside: avoid; }
.sidebar-verificacao .verif-header { font-size: 8pt; font-weight: 700; color: #1565C0;
    text-transform: uppercase; letter-spacing: .06em; margin-bottom: 6pt; }
.sidebar-verificacao .verif-pergunta { font-size: 9.5pt; font-weight: 600; margin-bottom: 8pt; line-height: 1.45; }
.alternativa { padding: 5pt 8pt; border-radius: 4pt; margin-bottom: 4pt; font-size: 9pt; line-height: 1.45;
    background: #fff; border: 1pt solid #BBDEFB; color: #444; }
.alt-letra { font-weight: 700; color: #1565C0; margin-right: 6pt; }
.verif-gabarito { margin-top: 8pt; font-size: 8.5pt; color: #555; background: #F7F7F7;
    border-left: 3pt solid #BBBBBB; padding: 7pt 10pt; border-radius: 0 4pt 4pt 0; }
.verif-gabarito .gab-tag { display: block; font-family: Arial; font-size: 7.5pt; font-weight: 700;
    text-transform: uppercase; letter-spacing: .05em; color: #888; margin-bottom: 3pt; }
.verif-gabarito .gab-texto { font-style: italic; }

/* NOTA FONTE */
.nota-fonte { font-family: Arial; font-size: 8pt; color: #666; margin: 6pt 0 2pt; padding-left: 10pt;
    border-left: 2pt solid #CCC; break-inside: avoid; }

/* RODAPE do capitulo: sintese final e encadeamento para o proximo capitulo */
.sintese-final { background: #F5F5F5; border-left: 4pt solid #555; padding: 10pt 14pt;
    margin-top: 14pt; break-inside: avoid; }
.sintese-final .rotulo { display: block; font-family: Arial; font-size: 8.5pt; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.5pt; color: #555; margin-bottom: 4pt; }
.encadeamento { font-family: Arial; font-style: italic; font-size: 9pt; color: #666;
    margin-top: 10pt; padding-left: 10pt; border-left: 2pt solid #CCC; break-inside: avoid; }

/* IMAGEM (apenas quando ha arquivo real). Compacta para empacotar com a
   verificacao na mesma pagina e nao orfanar. break-before:avoid puxa a imagem
   para junto do texto anterior. */
.imagem-container { margin: 9pt 0 8pt; text-align: center; break-inside: avoid; }
.imagem-container img { max-width: 100%; max-height: 140mm; width: auto; height: auto; }

/* VERIFICACAO — SECAO SEPARADA. Cada pagina reune ate 2 quadros de
   verificacao sozinhos; a primeira quebra antes (break-before:page) e o que
   vem depois (proximo bloco / aplicar-agora) tambem comeca em pagina nova,
   garantindo a "quebra antes e depois" da secao. */
.verif-page { break-before: page; }
.verif-secao-titulo { font-family: Arial; font-size: 9pt; font-weight: 700; color: #1565C0;
    text-transform: uppercase; letter-spacing: .08em; padding-bottom: 5pt; margin-bottom: 12pt;
    border-bottom: 2pt solid #90CAF9; }
.verif-page > .sidebar-verificacao { min-height: 112mm; margin: 0 0 14pt; }
.verif-page > .sidebar-verificacao:last-child { margin-bottom: 0; }

/* APLICAR AGORA — pagina propria: comando em cima + quadro de trabalho abaixo.
   Aluno: quadro grande em branco ocupando o resto da pagina.
   Professor: quadro menor + resposta comentada. */
.aplicar-page { break-before: page; break-inside: avoid; display: flex; flex-direction: column;
    height: 255mm; }
.aplicar-page-prof { break-before: page; display: flex; flex-direction: column; }
.aplicar-comando { background: #FFFDE7; border: 2pt solid #F9A825; border-radius: 8pt;
    padding: 14pt 18pt; flex: 0 0 auto; }
.aplicar-comando-header { font-family: Arial; font-size: 11pt; font-weight: 700; color: #F57F17;
    text-transform: uppercase; letter-spacing: .04em; margin-bottom: 8pt; }
.aplicar-comando-enunciado { font-size: 10pt; line-height: 1.55; white-space: pre-wrap; }
.aplicar-trabalho { flex: 1 1 auto; border: 1.5pt dashed #C9A227; border-radius: 8pt;
    margin-top: 12pt; padding: 9pt 12pt; min-height: 50mm; }
.aplicar-trabalho-menor { flex: 0 0 95mm; }
.aplicar-trabalho-label { font-family: Arial; font-size: 8pt; color: #B0982E;
    text-transform: uppercase; letter-spacing: .05em; }
.aplicar-agora-resposta { background: #FFF8E1; border: 1pt solid #FFE082; border-radius: 4pt;
    margin-top: 12pt; padding: 10pt 12pt; font-size: 8.5pt; line-height: 1.55; color: #3a2a00; }
.aplicar-agora-resposta-header { font-family: Arial; font-size: 8pt; font-weight: 700; color: #F57F17;
    text-transform: uppercase; margin-bottom: 6pt; }

/* QUEBRA */
.quebra-pagina { break-before: page; }

em { font-style: italic; }
strong { font-weight: 700; }
"""
    return (css.replace("__ROTULO__", rotulo).replace("__INSET__", str(FRAME_INSET_MM))
               .replace("__FW__", str(FRAME_W_MM)).replace("__FH__", str(FRAME_H_MM)))


def txt(el):
    return (el.text or "").strip() if el is not None else ""

def md(text):
    if not text:
        return ""
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    return text

def p_html(el):
    content = el.text or ""
    if len(list(el)) > 0:
        content = (el.text or "")
        for ch in el:
            content += ET.tostring(ch, encoding="unicode") + (ch.tail or "")
    return f'<p>{md(html_mod.escape(content.strip()))}</p>\n'

def conteudo_html(cel):
    if cel is None: return ""
    return "".join(p_html(p) for p in cel.findall("paragrafo"))

def lista_subtipos_html(el):
    """Renderiza <lista-subtipos><item nome="..."><conteudo>...</conteudo></item></lista-subtipos>
    (usado por secoes tipo="classificacao"). Sem isso, esse conteudo era descartado em
    silencio porque render_secao so lia <conteudo> direto da secao."""
    if el is None: return ""
    items = el.findall("item")
    if not items: return ""
    parts = ['<div class="lista-subtipos">']
    for it in items:
        nome = it.get("nome", "")
        nome_h = f'<div class="subtipo-nome">{html_mod.escape(nome)}</div>' if nome else ""
        parts.append(f'<div class="subtipo-item">{nome_h}{conteudo_html(it.find("conteudo"))}</div>')
    parts.append('</div>')
    return "".join(parts)


def render_imagem(ref, desc, imagens_dir):
    # So usamos arquivo real se existir em --imagens. Sem legenda visivel:
    # a <descricao> do XML e um briefing de producao, nao texto para o aluno.
    if imagens_dir:
        for ext in ("png", "jpg", "jpeg", "svg"):
            c = (Path(imagens_dir) / f"{ref}.{ext}").resolve()
            if c.exists():
                return (f'<figure class="imagem-container"><img src="{c.as_uri()}" '
                        f'alt="{html_mod.escape(desc)}" /></figure>')
    return ""


def sb_autor(el):
    nome, pais, desc = txt(el.find("nome")), txt(el.find("pais")), txt(el.find("descricao"))
    return (f'<div class="sidebar-autor"><div class="autor-nome">{html_mod.escape(nome)}</div>'
            f'<div class="autor-pais">{html_mod.escape(pais)}</div>'
            f'<div class="autor-desc">{md(html_mod.escape(desc))}</div></div>')

def sb_verif(el, incluir_gabarito=True):
    perg = txt(el.find("pergunta"))
    alts_el = el.find("alternativas")
    alts = ""
    if alts_el is not None:
        for a in alts_el.findall("alternativa"):
            letra = a.get("letra", "")
            texto = (a.text or "").strip()
            alts += (f'<div class="alternativa"><span class="alt-letra">{html_mod.escape(letra)}.</span>'
                     f'{md(html_mod.escape(texto))}</div>')
    just = txt(el.find("justificativa"))
    jh = ""
    if just and incluir_gabarito:
        jh = (f'<div class="verif-gabarito"><span class="gab-tag">Gabarito (uso do professor)</span>'
              f'<span class="gab-texto">{md(html_mod.escape(just))}</span></div>')
    return (f'<div class="sidebar-verificacao"><div class="verif-header">Verificacao de aprendizagem</div>'
            f'<div class="verif-pergunta">{md(html_mod.escape(perg))}</div>{alts}{jh}</div>')

def sb_aplicar(el, incluir_gabarito=True):
    enun = txt(el.find("enunciado"))
    resp = txt(el.find("resposta"))
    comando = (f'<div class="aplicar-comando">'
               f'<div class="aplicar-comando-header">Aplicar agora</div>'
               f'<div class="aplicar-comando-enunciado">{md(html_mod.escape(enun))}</div></div>')
    label = ('<div class="aplicar-trabalho-label">Espaço de trabalho — '
             'mapas mentais, gráficos, quadros comparativos</div>')
    if incluir_gabarito:
        # Versao PROFESSOR: comando + quadro menor de trabalho + resposta comentada.
        rh = ""
        if resp:
            rh = (f'<div class="aplicar-agora-resposta"><div class="aplicar-agora-resposta-header">'
                  f'Resposta modelo (uso do professor)</div>{md(html_mod.escape(resp))}</div>')
        return (f'<div class="aplicar-page-prof">{comando}'
                f'<div class="aplicar-trabalho aplicar-trabalho-menor">{label}</div>{rh}</div>')
    # Versao ALUNO: comando em cima + quadro grande em branco ocupando o resto da pagina.
    return (f'<div class="aplicar-page">{comando}'
            f'<div class="aplicar-trabalho">{label}</div></div>')

# ---------------------------------------------------------------------------
# Verificacao externa (status="externo") — conteudo vem da pasta --verificacoes
# (Fase 4 — ver PLANO-VERIFICACAO-EXTERNA.md). Convertendo o JSON para os
# MESMOS elementos que sb_verif/sb_aplicar ja consomem, preservamos
# integralmente a logica aluno/professor.
# ---------------------------------------------------------------------------

def _json_to_elem_verif(data):
    """Converte o JSON de verificacao no elemento que sb_verif espera."""
    el = ET.Element("sidebar", {"tipo": "verificacao"})
    ET.SubElement(el, "pergunta").text = data.get("pergunta", "")
    alts = ET.SubElement(el, "alternativas")
    correta = data.get("correta", "")
    for letra in sorted((data.get("alternativas") or {}).keys()):
        attrs = {"letra": letra}
        if letra == correta:
            attrs["correta"] = "sim"
        ET.SubElement(alts, "alternativa", attrs).text = (data["alternativas"].get(letra) or "")
    just = data.get("justificativa", "")
    if just:
        ET.SubElement(el, "justificativa").text = just
    return el


def _json_to_elem_aplicar(data):
    """Converte o JSON de aplicar-agora no elemento que sb_aplicar espera."""
    el = ET.Element("sidebar", {"tipo": "aplicar-agora"})
    ET.SubElement(el, "enunciado").text = data.get("enunciado", "")
    resp = data.get("resposta_comentada", "")
    if resp:
        ET.SubElement(el, "resposta").text = resp
    return el


def _sb_pendente(ref, incluir_gabarito):
    """Aviso de verificacao pendente — SO na versao professor; nada para o aluno."""
    if not incluir_gabarito:
        return ""
    return (f'<div class="sidebar-verificacao verif-pendente">'
            f'<div class="verif-header">Verificacao pendente</div>'
            f'<div class="verif-pergunta">Sem insumo para o marcador '
            f'<b>{html_mod.escape(ref)}</b> (arquivo {html_mod.escape(ref)}.json '
            f'ausente ou invalido na pasta de verificacoes).</div></div>')


def render_sb_externo(el, verifdir, incluir_gabarito=True):
    tipo = el.get("tipo", "")
    ref = el.get("ref", "")
    if not verifdir or not ref:
        return _sb_pendente(ref, incluir_gabarito)
    jpath = os.path.join(verifdir, ref + ".json")
    if not os.path.isfile(jpath):
        return _sb_pendente(ref, incluir_gabarito)
    try:
        with open(jpath, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError, ValueError):
        return _sb_pendente(ref, incluir_gabarito)
    if tipo == "verificacao":
        return sb_verif(_json_to_elem_verif(data), incluir_gabarito)
    if tipo == "aplicar-agora":
        return sb_aplicar(_json_to_elem_aplicar(data), incluir_gabarito)
    return _sb_pendente(ref, incluir_gabarito)


def render_sb(el, incluir_gabarito=True, verifdir=None):
    if el.get("status") == "externo":
        return render_sb_externo(el, verifdir, incluir_gabarito)
    t = el.get("tipo", "")
    if t == "autor": return sb_autor(el)
    if t == "verificacao": return sb_verif(el, incluir_gabarito)
    if t == "aplicar-agora": return sb_aplicar(el, incluir_gabarito)
    return ""


def render_secao(el, imdir, incluir_gabarito=True, verifdir=None):
    col_parts = []
    te = el.find("titulo")
    if te is not None and te.text:
        col_parts.append(f'<div class="secao-titulo">{html_mod.escape(te.text.strip())}</div>')
    col_parts.append(conteudo_html(el.find("conteudo")))
    # secoes tipo="classificacao" usam <introducao> + <lista-subtipos> em vez de <conteudo>
    col_parts.append(conteudo_html(el.find("introducao")))
    col_parts.append(lista_subtipos_html(el.find("lista-subtipos")))

    full_parts = []
    verif_parts = []
    for sb in el.findall("sidebar"):
        tipo = sb.get("tipo", "")
        if tipo == "autor":
            col_parts.append(sb_autor(sb))
        elif tipo == "verificacao":
            verif_parts.append(render_sb(sb, incluir_gabarito, verifdir))
        else:
            full_parts.append(render_sb(sb, incluir_gabarito, verifdir))
    for img in el.findall("imagem"):
        ref = img.get("ref", "")
        de = img.find("descricao")
        desc = txt(de) if de is not None else (img.text or "").strip()
        h = render_imagem(ref, desc, imdir)
        if h:
            full_parts.append(h)

    _CONHECIDAS_SECAO = {"titulo", "conteudo", "introducao", "lista-subtipos", "sidebar", "imagem"}
    for ch in el:
        if ch.tag not in _CONHECIDAS_SECAO:
            avisar_tag_desconhecida("secao", ch.tag)

    out = [('col', f'<div class="secao">{"".join(col_parts)}</div>')]
    out += [('full', h) for h in full_parts]
    out += [('verif', h) for h in verif_parts]
    return out

def render_bloco(el, imdir, incluir_gabarito=True, verifdir=None, quebrar_pagina=False):
    op = el.get("operacao", "")
    bid = el.get("id", "")
    c = OPERACAO_CORES.get(op, COR_PADRAO)
    micro = txt(el.find("micro-habilidade"))
    mh = f'<div class="micro-habilidade">{html_mod.escape(micro)}</div>' if micro else ""
    header = (f'<div class="bloco-header" style="background:{c["destaque"]}">'
              f'<span class="operacao-nome">{html_mod.escape(op)}</span>{mh}</div>')

    segments, buffer, verifs = [], [], []
    def flush():
        if buffer:
            segments.append(f'<div class="bloco-multicol" style="border-top-color:{c["destaque"]}">'
                            + "".join(buffer) + '</div>')
            buffer.clear()

    for ch in el:
        t = ch.tag
        if t == "secao":
            for kind, html in render_secao(ch, imdir, incluir_gabarito, verifdir):
                if kind == 'col':
                    buffer.append(html)
                elif kind == 'verif':
                    verifs.append(html)
                else:
                    flush(); segments.append(html)
        elif t == "sidebar":
            tipo = ch.get("tipo", "")
            if tipo == "autor":
                buffer.append(sb_autor(ch))
            elif tipo == "verificacao":
                verifs.append(render_sb(ch, incluir_gabarito, verifdir))
            else:
                flush(); segments.append(render_sb(ch, incluir_gabarito, verifdir))
        elif t == "imagem":
            ref = ch.get("ref", "")
            de = ch.find("descricao")
            desc = txt(de) if de is not None else (ch.text or "").strip()
            h = render_imagem(ref, desc, imdir)
            if h:
                flush(); segments.append(h)
        elif t == "nota_fonte":
            buffer.append(f'<div class="nota-fonte">{md(html_mod.escape(txt(ch)))}</div>')
        elif t in ("micro-habilidade", "resumo-aluno"):
            pass  # lidos via find() (cabecalho do bloco / quadro resumo); ignorar no loop
        else:
            avisar_tag_desconhecida("bloco", t)
    flush()
    cls = "bloco bloco-quebra" if quebrar_pagina else "bloco"
    if segments:
        corpo_bloco = (f'<div class="bloco-keep">{header}{segments[0]}</div>'
                       + "".join(segments[1:]))
    else:
        corpo_bloco = header

    # Secao separada de verificacao: paginas proprias com ATE 2 quadros cada,
    # quebra de pagina antes (e o que vem depois ja comeca em pagina nova).
    verif_html = ""
    for i in range(0, len(verifs), 2):
        par = verifs[i:i + 2]
        verif_html += '<div class="verif-page">' + "".join(par) + '</div>'

    return f'<div class="{cls}" id="{bid}">{corpo_bloco}{verif_html}</div>'


def split_nome_capitulo(nome_completo):
    if not nome_completo:
        return "", ""
    for sep in ("—", "–", " - "):
        if sep in nome_completo:
            a, b = nome_completo.split(sep, 1)
            return a.strip(), b.strip()
    return "", nome_completo.strip()

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

def render_indice(root):
    """Renderiza a pagina de sumario da unidade a partir de um XML <indice>.

    Formato esperado:
        <indice titulo_unidade="..." habilidade="...">
          <capitulo ref="01-01" numero="Capitulo 1" nome="...">
            <pergunta>...</pergunta>   (opcional)
          </capitulo>
          ...
        </indice>

    O "ref" de cada <capitulo> deve ser igual ao atributo id="" do XML do
    capitulo correspondente (ex.: id="01-01"), pois render_capitulo() emite
    a ancora id="capa-{id}" usada aqui. O numero de pagina exibido no PDF e
    calculado pelo proprio motor de paginacao (CSS target-counter), entao o
    sumario continua correto mesmo que o conteudo dos capitulos mude de
    tamanho — nao ha numero de pagina fixado a mao neste arquivo.
    """
    unidade = root.get("titulo_unidade", "") or root.get("titulo", "")
    habilidade = root.get("habilidade", "")
    eyebrow = '<div class="indice-eyebrow">Sumário da unidade</div>'
    titulo_h = f'<h1 class="indice-titulo-unidade">{html_mod.escape(unidade)}</h1>' if unidade else ""
    hab_h = f'<div class="indice-habilidade">{html_mod.escape(habilidade)}</div>' if habilidade else ""

    itens = []
    for cap in root.findall("capitulo"):
        ref = cap.get("ref", "")
        numero = cap.get("numero", "")
        nome = cap.get("nome", "")
        pergunta = txt(cap.find("pergunta"))
        num_h = f'<span class="indice-numero">{html_mod.escape(numero)}</span>' if numero else ""
        nome_h = f'<span class="indice-nome">{html_mod.escape(nome)}</span>'
        if ref:
            link = f'<a class="indice-link" href="#capa-{html_mod.escape(ref)}">{num_h}{nome_h}</a>'
        else:
            link = f'<div class="indice-link">{num_h}{nome_h}</div>'
        perg_h = f'<div class="indice-pergunta">{html_mod.escape(pergunta)}</div>' if pergunta else ""
        itens.append(f'<div class="indice-item">{link}{perg_h}</div>')

    return (f'<div class="capa-indice">{eyebrow}{titulo_h}{hab_h}'
            f'<div class="indice-sumario-label">Sumário</div>'
            f'<div class="indice-lista">{"".join(itens)}</div></div>')


def render_capitulo(xml_path, imdir, incluir_gabarito=True, meta=None, verifdir=None):
    meta = meta or {}
    root = ET.parse(xml_path).getroot()
    cab = root.find("cabecalho")
    hab = txt(cab.find("habilidade")) if cab is not None else ""
    perg = txt(cab.find("pergunta_capitulo")) if cab is not None else root.get("titulo", "")
    pq = txt(cab.find("por_que_importa")) if cab is not None else ""

    numero = meta.get("numero", "")
    nome = meta.get("nome", "")
    unidade = meta.get("unidade", "")

    eyebrow = f'<div class="capitulo-eyebrow">{html_mod.escape(unidade)}</div>' if unidade else ""
    numero_h = f'<div class="capitulo-numero">{html_mod.escape(numero)}</div>' if numero else ""
    nome_h = (f'<h1 class="capitulo-nome">{html_mod.escape(nome)}</h1>' if nome
              else f'<h1 class="capitulo-nome">{html_mod.escape(perg)}</h1>')
    hab_h = f'<div class="habilidade-badge">{html_mod.escape(hab)}</div>' if hab else ""
    perg_h = ""
    if nome and perg:
        perg_h = (f'<div class="pergunta-norteadora"><span class="rotulo">Pergunta norteadora</span>'
                  f'{html_mod.escape(perg)}</div>')

    mapa_el = root.find("mapa-progressao")
    mapa_html = ""
    if mapa_el is not None:
        items = ""
        for pp in mapa_el.findall("passo"):
            t = (pp.text or "").strip()
            cor = OPERACAO_CORES.get(t, COR_PADRAO)
            items += (f'<div class="mapa-passo" style="color:{cor["destaque"]}">'
                      f'<span class="num">Passo {pp.get("ordem","")}</span>{html_mod.escape(t)}</div>')
        mapa_html = f'<div class="mapa-progressao">{items}</div>'

    pqh = f'<div class="por-que-importa">Por que importa: {html_mod.escape(pq)}</div>' if pq else ""
    # Quadro resumo "o que voce vai aprender", logo apos o stepper (mapa-progressao).
    corpo_el = root.find("corpo")
    quadro_html = render_quadro_resumo(corpo_el)

    cap_id = root.get("id", "")
    capa_id_attr = f' id="capa-{html_mod.escape(cap_id)}"' if cap_id else ""
    capa = (f'<div class="capa-capitulo"{capa_id_attr}>{eyebrow}{numero_h}{nome_h}{hab_h}{perg_h}'
            f'{pqh}{mapa_html}{quadro_html}</div>')

    corpo = []
    if corpo_el is not None:
        children = list(corpo_el)
        primeiro_bloco = True
        for i, ch in enumerate(children):
            t = ch.tag
            if t == "bloco":
                # Quebra de pagina antes de cada bloco (cada micro-habilidade comeca
                # em pagina nova), exceto o primeiro, que segue logo apos a capa.
                corpo.append(render_bloco(ch, imdir, incluir_gabarito, verifdir,
                                          quebrar_pagina=not primeiro_bloco))
                primeiro_bloco = False
            elif t == "quebra":
                # Com a quebra automatica por bloco, uma <quebra> seguida de <bloco>
                # geraria pagina em branco dupla. So emite se o proximo nao for bloco.
                prox = children[i + 1] if i + 1 < len(children) else None
                if prox is None or prox.tag != "bloco":
                    corpo.append('<div class="quebra-pagina"></div>')
            elif t == "sidebar": corpo.append(render_sb(ch, incluir_gabarito, verifdir))
            elif t == "nota_fonte": corpo.append(f'<div class="nota-fonte">{md(html_mod.escape(txt(ch)))}</div>')
            else: avisar_tag_desconhecida("corpo", t)

    rodape = ""
    re_el = root.find("rodape")
    if re_el is not None:
        for ch in re_el:
            t = ch.tag
            if t == "sidebar":
                rodape += render_sb(ch, incluir_gabarito, verifdir)
            elif t == "sintese":
                rodape += (f'<div class="sintese-final"><span class="rotulo">Síntese</span>'
                           f'{md(html_mod.escape(txt(ch)))}</div>')
            elif t == "encadeamento":
                rodape += f'<div class="encadeamento">{md(html_mod.escape(txt(ch)))}</div>'
            else:
                avisar_tag_desconhecida("rodape", t)

    return capa + "".join(corpo) + rodape


def build_html(caps, versao_label=""):
    css = build_css(versao_label)
    return ('<!DOCTYPE html>\n<html lang="pt-BR">\n<head>\n<meta charset="UTF-8">\n<style>\n'
            + css + '\n</style>\n</head>\n<body>\n'
            + "\n".join(caps) + '\n</body>\n</html>')


def carregar_briefing(path):
    """numero_do_capitulo(int) -> {'numero','nome','unidade'}. Tolerante a JSON invalido."""
    meta_por_num = {}
    if not path or not Path(path).exists():
        return {}, ""
    raw = Path(path).read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {}
        mu = re.search(r'"unidade"\s*:\s*"((?:[^"\\]|\\.)*)"', raw)
        if mu:
            data["unidade"] = json.loads('"' + mu.group(1) + '"')
        mc = re.search(r'"capitulos"\s*:\s*\[(.*?)\]', raw, re.S)
        if mc:
            data["capitulos"] = [json.loads('"' + s + '"')
                                 for s in re.findall(r'"((?:[^"\\]|\\.)*)"', mc.group(1))]
        print("  AVISO: briefing.json invalido; usei extracao tolerante.")
    unidade = data.get("unidade", "")
    for i, nome_completo in enumerate(data.get("capitulos", []), start=1):
        numero, nome = split_nome_capitulo(nome_completo)
        if not numero:
            numero = f"Capitulo {i}"
        meta_por_num[i] = {"numero": numero, "nome": nome, "unidade": unidade}
    return meta_por_num, unidade

def numero_capitulo_do_xml(xml_path):
    try:
        root = ET.parse(xml_path).getroot()
        cid = root.get("id", "")
        m = re.match(r'\d+-(\d+)', cid)
        if m:
            return int(m.group(1))
    except Exception:
        pass
    m = re.search(r'(\d+)-(\d+)', Path(xml_path).name)
    return int(m.group(2)) if m else None


def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("xml", nargs="?")
    g.add_argument("--unidade")
    p.add_argument("--imagens")
    p.add_argument("--verificacoes",
                   help="Pasta com os JSON das verificacoes externas ({ref}.json).")
    p.add_argument("--briefing", help="JSON com nomes da unidade e dos capitulos (fora do XML).")
    p.add_argument("--output")
    p.add_argument("--html-only", action="store_true")
    vg = p.add_mutually_exclusive_group()
    vg.add_argument("--versao-aluno", action="store_true",
                    help="Processo do ALUNO: omite gabaritos e respostas modelo.")
    vg.add_argument("--versao-professor", action="store_true",
                    help="Processo do PROFESSOR: inclui gabaritos e respostas modelo.")
    args = p.parse_args()

    if not args.versao_aluno and not args.versao_professor:
        sys.exit("ERRO: escolha o processo. Use --versao-aluno OU --versao-professor (rode um de cada vez).")
    incluir_gabarito = args.versao_professor
    versao = "professor" if args.versao_professor else "aluno"
    versao_label = ("Versao do professor - contem gabaritos (uso interno)"
                    if incluir_gabarito else "Versao do aluno")

    if args.xml:
        xml_files = [Path(args.xml)]
        base = Path(args.xml).with_suffix("")
    else:
        xml_files = sorted(Path(args.unidade).glob("*.xml"))
        if not xml_files: sys.exit(f"Nenhum XML em {args.unidade}")
        base = Path(args.unidade) / "apostila"

    if args.output:
        out = Path(args.output)
    else:
        out = base.with_name(f"{base.name}-{versao}.pdf")
    if args.html_only: out = out.with_suffix(".html")

    brief_path = args.briefing
    if not brief_path and args.unidade:
        for cand in Path(args.unidade).resolve().parents:
            g2 = list(cand.glob("input/**/briefing.json"))
            if g2:
                brief_path = str(g2[0]); break
    meta_por_num, unidade = carregar_briefing(brief_path)
    if brief_path:
        print(f"  briefing: {brief_path}")

    imdir = str(Path(args.imagens).resolve()) if args.imagens else None
    verifdir = str(Path(args.verificacoes).resolve()) if args.verificacoes else None
    print(f"  >>> PROCESSO: VERSAO DO {versao.upper()} <<<")
    if verifdir:
        print(f"  verificacoes: {verifdir}")
    caps = []
    for xf in xml_files:
        root_el = ET.parse(xf).getroot()
        if root_el.tag == "indice":
            # Pagina de sumario da unidade (deve ordenar antes dos capitulos,
            # ex.: 01-00-indice.xml). Os numeros de pagina sao calculados
            # automaticamente no PDF; nao ha necessidade de meta/briefing aqui.
            print(f"  {xf.name}  -> indice (sumario da unidade)")
            caps.append(render_indice(root_el))
            continue
        num = numero_capitulo_do_xml(xf)
        meta = meta_por_num.get(num, {"numero": (f"Capitulo {num}" if num else ""),
                                      "nome": "", "unidade": unidade})
        print(f"  {xf.name}  -> {meta.get('numero','?')}")
        caps.append(render_capitulo(xf, imdir, incluir_gabarito, meta, verifdir))

    html = build_html(caps, versao_label)
    if args.html_only:
        out.write_text(html, encoding="utf-8")
        print(f"HTML: {out}")
    else:
        weasyprint.HTML(string=html).write_pdf(str(out))
        print(f"PDF ({versao}): {out}")


if __name__ == "__main__":
    main()
