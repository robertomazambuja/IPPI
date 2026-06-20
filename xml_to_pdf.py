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

# A4 em mm e inset da moldura (frame com tamanho EXPLICITO)
PAGE_W_MM, PAGE_H_MM = 210, 297
FRAME_INSET_MM = 10
FRAME_W_MM = PAGE_W_MM - 2 * FRAME_INSET_MM   # 190
FRAME_H_MM = PAGE_H_MM - 2 * FRAME_INSET_MM   # 277

OPERACAO_CORES = {
    "Definir":            {"fundo": "#E3F2FD", "destaque": "#1565C0"},
    "Sequenciar":         {"fundo": "#E8F5E9", "destaque": "#2E7D32"},
    "Mapear causalidade": {"fundo": "#FFF3E0", "destaque": "#E65100"},
    "Comparar":           {"fundo": "#F3E5F5", "destaque": "#6A1B9A"},
    "Analisar":           {"fundo": "#FCE4EC", "destaque": "#AD1457"},
    "Avaliar":            {"fundo": "#FFFDE7", "destaque": "#F57F17"},
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

/* MAPA PROGRESSAO */
.mapa-progressao { display: flex; margin: 18pt 0 4pt; background: #F8F9FA; border: 1pt solid #DEE2E6;
    border-radius: 8pt; overflow: hidden; }
.mapa-passo { flex: 1; text-align: center; padding: 9pt 8pt; font-family: Arial; font-size: 8.5pt;
    font-weight: 700; border-right: 1pt solid #DEE2E6; }
.mapa-passo:last-child { border-right: none; }
.mapa-passo .num { display: block; font-size: 7pt; color: #999; margin-bottom: 3pt; font-weight: 400; }

/* BLOCO */
.bloco { margin-bottom: 22pt; }
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
    break-inside: avoid; break-before: avoid; }
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

/* IMAGEM (apenas quando ha arquivo real). Compacta para empacotar com a
   verificacao na mesma pagina e nao orfanar. break-before:avoid puxa a imagem
   para junto do texto anterior. */
.imagem-container { margin: 7pt 0 6pt; text-align: center; break-inside: avoid; break-before: avoid; }
.imagem-container img { max-width: 100%; max-height: 74mm; width: auto; height: auto; }

/* APLICAR AGORA — nunca quebra entre paginas */
.aplicar-agora { background: #FFFDE7; border: 2pt solid #F9A825; border-radius: 8pt; padding: 16pt 18pt;
    margin-top: 20pt; break-inside: avoid; }
.aplicar-agora-header { font-family: Arial; font-size: 10pt; font-weight: 700; color: #F57F17;
    text-transform: uppercase; margin-bottom: 10pt; }
.aplicar-agora-enunciado { font-size: 9.5pt; line-height: 1.6; margin-bottom: 12pt; white-space: pre-wrap; }
.aplicar-agora-resposta { background: #FFF8E1; border: 1pt solid #FFE082; border-radius: 4pt;
    padding: 10pt 12pt; font-size: 8.5pt; line-height: 1.55; color: #3a2a00; }
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
    rh = ""
    if resp and incluir_gabarito:
        rh = (f'<div class="aplicar-agora-resposta"><div class="aplicar-agora-resposta-header">'
              f'Resposta modelo (uso do professor)</div>{md(html_mod.escape(resp))}</div>')
    return (f'<div class="aplicar-agora"><div class="aplicar-agora-header">Aplicar agora</div>'
            f'<div class="aplicar-agora-enunciado">{md(html_mod.escape(enun))}</div>{rh}</div>')

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
    for sb in el.findall("sidebar"):
        tipo = sb.get("tipo", "")
        if tipo == "autor":
            col_parts.append(sb_autor(sb))
        else:
            full_parts.append(render_sb(sb, incluir_gabarito, verifdir))
    for img in el.findall("imagem"):
        ref = img.get("ref", "")
        de = img.find("descricao")
        desc = txt(de) if de is not None else (img.text or "").strip()
        h = render_imagem(ref, desc, imdir)
        if h:
            full_parts.append(h)

    out = [('col', f'<div class="secao">{"".join(col_parts)}</div>')]
    out += [('full', h) for h in full_parts]
    return out

def render_bloco(el, imdir, incluir_gabarito=True, verifdir=None):
    op = el.get("operacao", "")
    bid = el.get("id", "")
    c = OPERACAO_CORES.get(op, COR_PADRAO)
    micro = txt(el.find("micro-habilidade"))
    mh = f'<div class="micro-habilidade">{html_mod.escape(micro)}</div>' if micro else ""
    header = (f'<div class="bloco-header" style="background:{c["destaque"]}">'
              f'<span class="operacao-nome">{html_mod.escape(op)}</span>{mh}</div>')

    segments, buffer = [], []
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
                else:
                    flush(); segments.append(html)
        elif t == "sidebar":
            tipo = ch.get("tipo", "")
            if tipo == "autor":
                buffer.append(sb_autor(ch))
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
    flush()
    return f'<div class="bloco" id="{bid}">{header}{"".join(segments)}</div>'


def split_nome_capitulo(nome_completo):
    if not nome_completo:
        return "", ""
    for sep in ("—", "–", " - "):
        if sep in nome_completo:
            a, b = nome_completo.split(sep, 1)
            return a.strip(), b.strip()
    return "", nome_completo.strip()

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
    capa = f'<div class="capa-capitulo">{eyebrow}{numero_h}{nome_h}{hab_h}{perg_h}{pqh}{mapa_html}</div>'

    corpo_el = root.find("corpo")
    corpo = []
    if corpo_el is not None:
        for ch in corpo_el:
            t = ch.tag
            if t == "bloco": corpo.append(render_bloco(ch, imdir, incluir_gabarito, verifdir))
            elif t == "quebra": corpo.append('<div class="quebra-pagina"></div>')
            elif t == "sidebar": corpo.append(render_sb(ch, incluir_gabarito, verifdir))
            elif t == "nota_fonte": corpo.append(f'<div class="nota-fonte">{md(html_mod.escape(txt(ch)))}</div>')

    rodape = ""
    re_el = root.find("rodape")
    if re_el is not None:
        for sb in re_el.findall("sidebar"): rodape += render_sb(sb, incluir_gabarito, verifdir)

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
