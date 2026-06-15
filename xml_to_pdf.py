#!/usr/bin/env python3
"""
xml_to_pdf.py — Converte XMLs do pipeline IPPI em PDFs de apostila.

Uso:
    python xml_to_pdf.py <arquivo.xml> [--imagens <pasta>] [--output <arquivo.pdf>]
    python xml_to_pdf.py --unidade <pasta_xml> [--imagens <pasta>] [--output apostila.pdf]
"""

import argparse, os, sys, re, html as html_mod
from pathlib import Path
from xml.etree import ElementTree as ET
import weasyprint

# ── Paleta por operação ─────────────────────────────────────────────────────
OPERACAO_CORES = {
    "Definir":            {"fundo": "#E3F2FD", "destaque": "#1565C0"},
    "Sequenciar":         {"fundo": "#E8F5E9", "destaque": "#2E7D32"},
    "Mapear causalidade": {"fundo": "#FFF3E0", "destaque": "#E65100"},
    "Comparar":           {"fundo": "#F3E5F5", "destaque": "#6A1B9A"},
    "Analisar":           {"fundo": "#FCE4EC", "destaque": "#AD1457"},
    "Avaliar":            {"fundo": "#FFFDE7", "destaque": "#F57F17"},
}
COR_PADRAO = {"fundo": "#F5F5F5", "destaque": "#424242"}

# ── CSS ─────────────────────────────────────────────────────────────────────
CSS = r"""
@page {
    size: A4;
    margin: 20mm 18mm 22mm 18mm;
    @bottom-center { content: counter(page); font-family: Arial; font-size: 10pt; color: #888; }
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Georgia, serif; font-size: 10.5pt; line-height: 1.65; color: #1a1a1a; }

/* CAPA */
.capa-capitulo { break-before: page; padding: 28pt 0 20pt; border-bottom: 3pt solid #1565C0; margin-bottom: 22pt; }
.habilidade-badge { display: inline-block; background: #1565C0; color: #fff; font-family: Arial; font-size: 8.5pt; font-weight: 700; padding: 4pt 10pt; border-radius: 12pt; margin-bottom: 12pt; }
.capa-capitulo h1 { font-family: Arial; font-size: 15pt; font-weight: 700; color: #0d2b6e; line-height: 1.3; margin-bottom: 14pt; }
.por-que-importa { background: #EEF4FF; border-left: 4pt solid #1565C0; padding: 10pt 14pt; font-size: 9.5pt; font-style: italic; color: #1a3566; border-radius: 0 6pt 6pt 0; margin-top: 10pt; }

/* MAPA PROGRESSAO */
.mapa-progressao { display: flex; margin: 18pt 0 24pt; background: #F8F9FA; border: 1pt solid #DEE2E6; border-radius: 8pt; overflow: hidden; }
.mapa-passo { flex: 1; text-align: center; padding: 9pt 8pt; font-family: Arial; font-size: 8.5pt; font-weight: 700; border-right: 1pt solid #DEE2E6; }
.mapa-passo:last-child { border-right: none; }
.mapa-passo .num { display: block; font-size: 7pt; color: #999; margin-bottom: 3pt; font-weight: 400; }

/* BLOCO */
.bloco { margin-bottom: 24pt; }
.bloco-header { padding: 10pt 14pt; border-radius: 6pt 6pt 0 0; }
.bloco-header .operacao-nome { font-family: Arial; font-size: 9pt; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: #fff; }
.bloco-header .micro-habilidade { font-family: Arial; font-size: 8.5pt; color: rgba(255,255,255,.88); margin-top: 4pt; }
.bloco-conteudo { border: 1.5pt solid #ccc; border-top: none; border-radius: 0 0 6pt 6pt; padding: 16pt 16pt 12pt; }

/* SECAO */
.secao { margin-bottom: 14pt; }
.secao:last-child { margin-bottom: 0; }
.secao-titulo { font-family: Arial; font-size: 10.5pt; font-weight: 700; margin-bottom: 8pt; padding-bottom: 4pt; border-bottom: 1pt solid #E0E0E0; }
.secao p { margin-bottom: 8pt; text-align: justify; }
.secao p:last-child { margin-bottom: 0; }

/* SIDEBAR AUTOR */
.sidebar-autor { float: right; clear: right; width: 36%; margin: 0 0 12pt 14pt; background: #FFF8F0; border-left: 4pt solid #E8A838; border: 1.5pt solid #E8A838; border-left-width: 4pt; border-radius: 0 6pt 6pt 0; padding: 10pt 12pt; font-family: Arial; }
.sidebar-autor .autor-nome { font-size: 9.5pt; font-weight: 700; color: #7B4A00; margin-bottom: 1pt; }
.sidebar-autor .autor-pais { font-size: 8pt; color: #A0714A; margin-bottom: 6pt; }
.sidebar-autor .autor-desc { font-size: 8.5pt; line-height: 1.5; color: #3a2000; }

/* SIDEBAR VERIFICACAO */
.sidebar-verificacao { background: #EEF4FF; border-left: 4pt solid #1565C0; border: 1.5pt solid #90CAF9; border-left-width: 4pt; border-radius: 0 6pt 6pt 0; padding: 12pt 14pt; margin: 14pt 0 6pt; font-family: Arial; }
.sidebar-verificacao .verif-header { font-size: 8pt; font-weight: 700; color: #1565C0; text-transform: uppercase; letter-spacing: .06em; margin-bottom: 6pt; }
.sidebar-verificacao .verif-pergunta { font-size: 9.5pt; font-weight: 600; margin-bottom: 8pt; line-height: 1.45; }
.alternativa { padding: 5pt 8pt; border-radius: 4pt; margin-bottom: 4pt; font-size: 9pt; line-height: 1.45; }
.alternativa.correta { background: #E8F5E9; border: 1.5pt solid #4CAF50; }
.alternativa:not(.correta) { background: #fff; border: 1pt solid #BBDEFB; color: #444; }
.alt-letra { font-weight: 700; color: #1565C0; margin-right: 6pt; }
.alternativa.correta .alt-letra { color: #2E7D32; }
.verif-justificativa { margin-top: 8pt; font-size: 8.5pt; font-style: italic; color: #444; border-top: 1pt solid #BBDEFB; padding-top: 6pt; }

/* NOTA FONTE */
.nota-fonte { font-family: Arial; font-size: 8pt; color: #666; margin: 6pt 0 2pt; padding-left: 10pt; border-left: 2pt solid #CCC; }

/* IMAGEM / QUADRO / TIMELINE */
.imagem-container { margin: 14pt 0; text-align: center; }
.imagem-container img { max-width: 100%; height: auto; }
.imagem-placeholder { background: #F8F9FA; border: 1.5pt dashed #BDBDBD; border-radius: 6pt; padding: 18pt 14pt; font-family: Arial; }
.imagem-placeholder .img-ref { font-size: 7.5pt; font-weight: 700; text-transform: uppercase; color: #BDBDBD; margin-bottom: 4pt; }
.imagem-placeholder .img-descricao { font-size: 8.5pt; line-height: 1.4; color: #9E9E9E; }
.quadro-comparativo { width: 100%; border-collapse: collapse; margin: 14pt 0; font-family: Arial; font-size: 8.5pt; }
.quadro-comparativo th { background: #263238; color: #fff; padding: 7pt 10pt; text-align: left; font-weight: 700; }
.quadro-comparativo td { padding: 7pt 10pt; border: 1pt solid #CFD8DC; vertical-align: top; line-height: 1.45; }
.quadro-comparativo tr:nth-child(even) td { background: #ECEFF1; }
.quadro-comparativo .row-header { background: #37474F; color: #fff; font-weight: 700; }
.quadro-label { font-family: Arial; font-size: 8pt; color: #888; margin-top: 4pt; font-style: italic; }
.timeline { margin: 14pt 0; }
.timeline-title { font-family: Arial; font-size: 8pt; color: #888; text-align: center; margin-bottom: 10pt; font-style: italic; }
.timeline-items { display: flex; align-items: flex-start; }
.timeline-item { flex: 1; text-align: center; padding: 0 4pt; }
.timeline-dot { width: 14pt; height: 14pt; border-radius: 50%; background: #1565C0; margin: 0 auto 6pt; }
.timeline-text { font-family: Arial; font-size: 7.5pt; line-height: 1.35; }
.timeline-periodo { font-weight: 700; color: #1565C0; font-size: 7pt; display: block; margin-bottom: 2pt; }

/* APLICAR AGORA */
.aplicar-agora { background: #FFFDE7; border: 2pt solid #F9A825; border-radius: 8pt; padding: 16pt 18pt; margin-top: 20pt; }
.aplicar-agora-header { font-family: Arial; font-size: 10pt; font-weight: 700; color: #F57F17; text-transform: uppercase; margin-bottom: 10pt; }
.aplicar-agora-enunciado { font-size: 9.5pt; line-height: 1.6; margin-bottom: 12pt; white-space: pre-wrap; }
.aplicar-agora-resposta { background: #FFF8E1; border: 1pt solid #FFE082; border-radius: 4pt; padding: 10pt 12pt; font-size: 8.5pt; line-height: 1.55; color: #3a2a00; }
.aplicar-agora-resposta-header { font-family: Arial; font-size: 8pt; font-weight: 700; color: #F57F17; text-transform: uppercase; margin-bottom: 6pt; }

/* QUEBRA */
.quebra-pagina { break-before: page; }

/* UTILITARIOS */
.clearfix::after { content: ''; display: table; clear: both; }
em { font-style: italic; }
strong { font-weight: 700; }
"""

# ── Utilidades ──────────────────────────────────────────────────────────────

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

# ── Imagens ──────────────────────────────────────────────────────────────────

def is_quadro(d): return any(k in d.lower() for k in ["quadro comparativo","tabela comparativa","quadro com"])
def is_timeline(d): return "linha do tempo" in d.lower()

def gen_quadro(ref, desc):
    cols, rows = [], []
    m = re.search(r'\(([^)]+)\)', desc)
    if m: cols = [c.strip() for c in re.split(r'[/,]', m.group(1))]
    m2 = re.search(r'linhas?\s*\(([^)]+)\)', desc, re.I)
    if m2: rows = [r.strip() for r in re.split(r'[/,]', m2.group(1))]
    if not cols and not rows: return gen_placeholder(ref, desc)
    h = ['<div class="imagem-container"><table class="quadro-comparativo">']
    if cols:
        h.append('<thead><tr><th></th>' + "".join(f'<th>{html_mod.escape(c)}</th>' for c in cols) + '</tr></thead>')
    if rows:
        nc = len(cols) if cols else 1
        h.append('<tbody>' + "".join(
            f'<tr><td class="row-header">{html_mod.escape(r)}</td>' + '<td>&nbsp;</td>'*nc + '</tr>'
            for r in rows
        ) + '</tbody>')
    h.append(f'</table><p class="quadro-label">Ref: {ref} — {html_mod.escape(desc[:80])}{"..." if len(desc)>80 else ""}</p></div>')
    return "\n".join(h)

def gen_timeline(ref, desc):
    marcos_raw = re.split(r'→|->|–>', desc)
    marcos = []
    for m in marcos_raw:
        m = re.sub(r'^[Ll]inha do tempo[^:]*:\s*', '', m.strip()).strip()
        if m: marcos.append(m)
    if len(marcos) < 2: return gen_placeholder(ref, desc)
    def parse(m):
        per = re.search(r'\(([^)]+)\)', m)
        return (per.group(1) if per else ""), re.sub(r'\([^)]+\)', '', m).strip()
    items = ""
    for m in marcos:
        per, tex = parse(m)
        items += ('<div class="timeline-item"><div class="timeline-dot"></div><div class="timeline-text">'
                  + (f'<span class="timeline-periodo">{html_mod.escape(per)}</span>' if per else "")
                  + html_mod.escape(tex[:100]) + '</div></div>')
    return (f'<div class="imagem-container"><p class="timeline-title">Linha do tempo — Ref: {ref}</p>'
            f'<div class="timeline"><div class="timeline-items">{items}</div></div></div>')

def gen_placeholder(ref, desc):
    return (f'<div class="imagem-container"><div class="imagem-placeholder">'
            f'<div class="img-ref">[Imagem: {html_mod.escape(ref)}]</div>'
            f'<div class="img-descricao">{html_mod.escape(desc)}</div></div></div>')

def render_imagem(ref, desc, imagens_dir):
    if imagens_dir:
        for ext in ("png","jpg","jpeg","svg"):
            c = Path(imagens_dir) / f"{ref}.{ext}"
            if c.exists():
                return (f'<div class="imagem-container"><img src="{c.as_uri()}" alt="{html_mod.escape(desc)}" />'
                        f'<p class="quadro-label">{html_mod.escape(desc[:100])}</p></div>')
    if is_quadro(desc): return gen_quadro(ref, desc)
    if is_timeline(desc): return gen_timeline(ref, desc)
    return gen_placeholder(ref, desc)

# ── Sidebars ──────────────────────────────────────────────────────────────────

def sb_autor(el):
    nome, pais, desc = txt(el.find("nome")), txt(el.find("pais")), txt(el.find("descricao"))
    return (f'<div class="sidebar-autor"><div class="autor-nome">{html_mod.escape(nome)}</div>'
            f'<div class="autor-pais">{html_mod.escape(pais)}</div>'
            f'<div class="autor-desc">{md(html_mod.escape(desc))}</div></div>')

def sb_verif(el):
    perg = txt(el.find("pergunta"))
    alts_el = el.find("alternativas")
    alts = ""
    if alts_el is not None:
        for a in alts_el.findall("alternativa"):
            letra = a.get("letra","")
            correta = a.get("correta","nao").lower() == "sim"
            texto = (a.text or "").strip()
            cls = "alternativa correta" if correta else "alternativa"
            alts += (f'<div class="{cls}"><span class="alt-letra">{html_mod.escape(letra)}.</span>'
                     f'{md(html_mod.escape(texto))}</div>')
    just = txt(el.find("justificativa"))
    jh = f'<div class="verif-justificativa">{md(html_mod.escape(just))}</div>' if just else ""
    return (f'<div class="sidebar-verificacao"><div class="verif-header">Verificacao de aprendizagem</div>'
            f'<div class="verif-pergunta">{md(html_mod.escape(perg))}</div>{alts}{jh}</div>')

def sb_aplicar(el):
    enun = txt(el.find("enunciado"))
    resp = txt(el.find("resposta"))
    rh = (f'<div class="aplicar-agora-resposta"><div class="aplicar-agora-resposta-header">'
          f'Resposta modelo (uso do professor)</div>{md(html_mod.escape(resp))}</div>') if resp else ""
    return (f'<div class="aplicar-agora"><div class="aplicar-agora-header">Aplicar agora</div>'
            f'<div class="aplicar-agora-enunciado">{md(html_mod.escape(enun))}</div>{rh}</div>')

def render_sb(el):
    t = el.get("tipo","")
    if t == "autor": return sb_autor(el)
    if t == "verificacao": return sb_verif(el)
    if t == "aplicar-agora": return sb_aplicar(el)
    return ""

# ── Renderização principal ────────────────────────────────────────────────────

def render_secao(el, imdir):
    parts = []
    te = el.find("titulo")
    if te is not None and te.text:
        parts.append(f'<div class="secao-titulo">{html_mod.escape(te.text.strip())}</div>')
    parts.append(conteudo_html(el.find("conteudo")))
    for sb in el.findall("sidebar"): parts.append(render_sb(sb))
    for img in el.findall("imagem"):
        ref = img.get("ref","")
        de = img.find("descricao")
        desc = txt(de) if de is not None else (img.text or "").strip()
        parts.append(render_imagem(ref, desc, imdir))
    return f'<div class="secao">{"".join(parts)}</div>'

def render_bloco(el, imdir):
    op = el.get("operacao","")
    bid = el.get("id","")
    c = OPERACAO_CORES.get(op, COR_PADRAO)
    micro = txt(el.find("micro-habilidade"))
    mh = f'<div class="micro-habilidade">{html_mod.escape(micro)}</div>' if micro else ""
    header = (f'<div class="bloco-header" style="background:{c["destaque"]}">'
              f'<span class="operacao-nome">{html_mod.escape(op)}</span>{mh}</div>')
    body = []
    for ch in el:
        t = ch.tag
        if t == "secao": body.append(render_secao(ch, imdir))
        elif t == "sidebar": body.append(render_sb(ch))
        elif t == "imagem":
            ref = ch.get("ref","")
            de = ch.find("descricao")
            desc = txt(de) if de is not None else (ch.text or "").strip()
            body.append(render_imagem(ref, desc, imdir))
        elif t == "nota_fonte": body.append(f'<div class="nota-fonte">{md(html_mod.escape(txt(ch)))}</div>')
    corpo = (f'<div class="bloco-conteudo clearfix" style="border-color:{c["destaque"]}55;background:{c["fundo"]}">'
             + "".join(body) + '</div>')
    return f'<div class="bloco" id="{bid}">{header}{corpo}</div>'

def render_capitulo(xml_path, imdir):
    root = ET.parse(xml_path).getroot()
    cab = root.find("cabecalho")
    hab = txt(cab.find("habilidade")) if cab else ""
    perg = txt(cab.find("pergunta_capitulo")) if cab else root.get("titulo","")
    pq = txt(cab.find("por_que_importa")) if cab else ""

    mapa_el = root.find("mapa-progressao")
    mapa_html = ""
    if mapa_el is not None:
        passos = mapa_el.findall("passo")
        items = ""
        for p in passos:
            t = (p.text or "").strip()
            cor = OPERACAO_CORES.get(t, COR_PADRAO)
            items += (f'<div class="mapa-passo" style="color:{cor["destaque"]}">'
                      f'<span class="num">Passo {p.get("ordem","")}</span>{html_mod.escape(t)}</div>')
        mapa_html = f'<div class="mapa-progressao">{items}</div>'

    pqh = f'<div class="por-que-importa">Por que importa: {html_mod.escape(pq)}</div>' if pq else ""
    capa = (f'<div class="capa-capitulo"><div class="habilidade-badge">{html_mod.escape(hab)}</div>'
            f'<h1>{html_mod.escape(perg)}</h1>{pqh}{mapa_html}</div>')

    corpo_el = root.find("corpo")
    corpo = []
    if corpo_el is not None:
        for ch in corpo_el:
            t = ch.tag
            if t == "bloco": corpo.append(render_bloco(ch, imdir))
            elif t == "quebra": corpo.append('<div class="quebra-pagina"></div>')
            elif t == "sidebar": corpo.append(render_sb(ch))
            elif t == "nota_fonte": corpo.append(f'<div class="nota-fonte">{md(html_mod.escape(txt(ch)))}</div>')

    rodape = ""
    re_el = root.find("rodape")
    if re_el is not None:
        for sb in re_el.findall("sidebar"): rodape += render_sb(sb)

    return capa + "".join(corpo) + rodape

def build_html(caps):
    return f'<!DOCTYPE html>\n<html lang="pt-BR">\n<head>\n<meta charset="UTF-8">\n<style>\n{CSS}\n</style>\n</head>\n<body>\n' + "\n".join(caps) + '\n</body>\n</html>'

def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("xml", nargs="?")
    g.add_argument("--unidade")
    p.add_argument("--imagens")
    p.add_argument("--output")
    p.add_argument("--html-only", action="store_true")
    args = p.parse_args()

    if args.xml:
        xml_files = [Path(args.xml)]
        default_out = Path(args.xml).with_suffix(".pdf")
    else:
        xml_files = sorted(Path(args.unidade).glob("*.xml"))
        if not xml_files: sys.exit(f"Nenhum XML em {args.unidade}")
        default_out = Path(args.unidade) / "apostila.pdf"

    out = Path(args.output) if args.output else default_out
    if args.html_only: out = out.with_suffix(".html")

    imdir = args.imagens
    caps = []
    for xf in xml_files:
        print(f"  {xf.name}")
        caps.append(render_capitulo(xf, imdir))

    html = build_html(caps)
    if args.html_only:
        out.write_text(html, encoding="utf-8")
        print(f"HTML: {out}")
    else:
        weasyprint.HTML(string=html).write_pdf(str(out))
        print(f"PDF: {out}")

if __name__ == "__main__":
    main()
