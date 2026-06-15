#!/usr/bin/env python3
"""
apostila_pdf.py — Gera PDF de apostila a partir dos XMLs estruturados.
Motor: ReportLab (pip install reportlab)

Uso:
    python apostila_pdf.py --unidade <pasta_xml> [--output apostila.pdf]
    python apostila_pdf.py <arquivo.xml>          [--output capitulo.pdf]
"""
import argparse, re, sys
from pathlib import Path
from xml.etree import ElementTree as ET

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable,
)

# ── Dimensões ─────────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = A4
ML = MR = 18*mm;  MT = 22*mm;  MB = 24*mm
TW = PAGE_W - ML - MR          # ≈ 493 pt

# ── Paleta ────────────────────────────────────────────────────────────────────
CORES = {
    "Definir":            ("#E3F2FD", "#1565C0"),
    "Sequenciar":         ("#E8F5E9", "#2E7D32"),
    "Mapear causalidade": ("#FFF3E0", "#E65100"),
    "Comparar":           ("#F3E5F5", "#6A1B9A"),
    "Analisar":           ("#FCE4EC", "#AD1457"),
    "Avaliar":            ("#FFFDE7", "#F57F17"),
}
COR_DEF = ("#F5F5F5", "#424242")

def hx(h): return HexColor(int(h.lstrip("#"), 16))

# ── Utilidades ────────────────────────────────────────────────────────────────
def txt(el):   return (el.text or "").strip() if el is not None else ""
def nn(lst):   return [x for x in lst if x is not None]

def rl(text):
    if not text: return ""
    text = text.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text, flags=re.DOTALL)
    text = re.sub(r"\*(.+?)\*",     r"<i>\1</i>", text, flags=re.DOTALL)
    return text

def P(text, style):
    t = rl(str(text).strip()) if text else ""
    return Paragraph(t, style) if t else None

def para_lines(text, style):
    out = []
    for line in text.split("\n"):
        line = line.strip()
        if line:
            p = P(line, style)
            if p: out.append(p)
    return out

# ── Estilos ───────────────────────────────────────────────────────────────────
def make_styles():
    def ps(name, font="Helvetica", size=10, leading=None, color="#1a1a1a",
           bold=False, italic=False, align=TA_LEFT, before=0, after=4, il=0):
        fn = font
        if bold and italic: fn = {"Helvetica":"Helvetica-BoldOblique","Times-Roman":"Times-BoldItalic"}.get(font,font)
        elif bold:          fn = {"Helvetica":"Helvetica-Bold","Times-Roman":"Times-Bold"}.get(font,font)
        elif italic:        fn = {"Helvetica":"Helvetica-Oblique","Times-Roman":"Times-Italic"}.get(font,font)
        return ParagraphStyle(name, fontName=fn, fontSize=size,
            leading=leading or round(size*1.42,1), textColor=hx(color),
            alignment=align, spaceBefore=before, spaceAfter=after, leftIndent=il)
    S = {}
    S["body"]     = ps("body",    "Times-Roman",10.5,16.5,align=TA_JUSTIFY,after=6)
    S["h1"]       = ps("h1",      size=14,leading=19,color="#0d2b6e",bold=True,after=8)
    S["h2"]       = ps("h2",      size=10.5,leading=14,bold=True,before=2,after=4)
    S["badge"]    = ps("badge",   size=8,color="#ffffff",bold=True,after=0)
    S["por_que"]  = ps("por_que", size=9,leading=13,color="#1a3566",italic=True,after=0)
    S["mapa_num"] = ps("mapa_num",size=6.5,leading=9,color="#999999",align=TA_CENTER,after=1)
    S["mapa_op"]  = ps("mapa_op", size=8.5,leading=11,bold=True,align=TA_CENTER,after=0)
    S["op_label"] = ps("op_label",size=9,leading=12,color="#ffffff",bold=True,after=1)
    S["micro"]    = ps("micro",   size=8,leading=11,color="#dddddd",italic=True,after=0)
    S["aut_nome"] = ps("aut_nome",size=8.5,leading=12,color="#7B4A00",bold=True,after=1)
    S["aut_pais"] = ps("aut_pais",size=7,leading=9,color="#A0714A",after=2)
    S["aut_desc"] = ps("aut_desc",size=7.5,leading=11,color="#3a2000",align=TA_JUSTIFY,after=0)
    S["v_tag"]    = ps("v_tag",   size=7,leading=9,color="#1565C0",bold=True,after=3)
    S["v_q"]      = ps("v_q",     size=9,leading=13,bold=True,align=TA_JUSTIFY,after=5)
    S["v_alt"]    = ps("v_alt",   size=8.5,leading=12,color="#444444",align=TA_JUSTIFY,after=2)
    S["v_altok"]  = ps("v_altok", size=8.5,leading=12,color="#1a5e20",align=TA_JUSTIFY,after=2)
    S["v_just"]   = ps("v_just",  size=8,leading=11,color="#555555",italic=True,align=TA_JUSTIFY,before=3,after=0)
    S["nota"]     = ps("nota",    "Times-Roman",7.5,11,color="#666666",italic=True,before=1,after=1,il=6)
    S["apl_tag"]  = ps("apl_tag", size=9.5,leading=12,color="#E65100",bold=True,after=6)
    S["apl_txt"]  = ps("apl_txt", "Times-Roman",9,14,align=TA_JUSTIFY,after=4)
    S["apl_rtag"] = ps("apl_rtag",size=7.5,leading=10,color="#E65100",bold=True,after=3)
    S["apl_resp"] = ps("apl_resp",size=8,leading=11.5,color="#3a2a00",align=TA_JUSTIFY,after=2)
    S["img_ref"]  = ps("img_ref", size=7,leading=9,color="#BDBDBD",bold=True,align=TA_CENTER,after=2)
    S["img_desc"] = ps("img_desc",size=8,leading=11.5,color="#9E9E9E",italic=True,align=TA_CENTER,after=0)
    return S


# ── Boxes pequenos (sempre curtos → nunca estouram) ───────────────────────────
def box(items, w, bg, border=None, bw=1.5, lacc=None, aw=4, pv=8, ph=9):
    cleaned = nn(items)
    if not cleaned: return None
    t = Table([[cleaned]], colWidths=[w - 2*ph])
    st = [
        ("BACKGROUND",    (0,0),(-1,-1), hx(bg)),
        ("TOPPADDING",    (0,0),(-1,-1), pv),
        ("BOTTOMPADDING", (0,0),(-1,-1), pv),
        ("LEFTPADDING",   (0,0),(-1,-1), ph),
        ("RIGHTPADDING",  (0,0),(-1,-1), ph),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]
    if border: st.append(("BOX",       (0,0),(-1,-1), bw, hx(border)))
    if lacc:   st.append(("LINEBEFORE",(0,0),(0,-1),  aw, hx(lacc)))
    t.setStyle(TableStyle(st))
    return t

def build_autor(el, S, w):
    return box(nn([P(txt(el.find("nome")),S["aut_nome"]),
                   P(txt(el.find("pais")),S["aut_pais"]),
                   P(txt(el.find("descricao")),S["aut_desc"])]),
               w, "#FFF8F0", border="#E8A838", lacc="#E8A838", pv=8, ph=9)

def build_verif(el, S, w):
    perg = txt(el.find("pergunta"))
    alts = el.find("alternativas")
    just = txt(el.find("justificativa"))
    iw = w - 20
    items = nn([P("VERIFICAÇÃO DE APRENDIZAGEM", S["v_tag"]), P(perg, S["v_q"])])
    if alts is not None:
        for a in alts.findall("alternativa"):
            letra   = a.get("letra","")
            correta = a.get("correta","nao").lower() == "sim"
            texto   = (a.text or "").strip()
            st      = S["v_altok"] if correta else S["v_alt"]
            bg      = "#E8F5E9"    if correta else "#FFFFFF"
            bd      = "#4CAF50"    if correta else "#BBDEFB"
            p       = Paragraph(f"<b>{letra}.</b>  {rl(texto)}", st)
            at = Table([[p]], colWidths=[iw-2])
            at.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,-1),hx(bg)),("BOX",(0,0),(-1,-1),1,hx(bd)),
                ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
                ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
            ]))
            items += [at, Spacer(1,2)]
    if just:
        items += [HRFlowable(width=iw,thickness=0.5,color=hx("#BBDEFB"),
                             spaceBefore=3,spaceAfter=2),
                  P(just, S["v_just"])]
    return box(items, w, "#EEF4FF", border="#90CAF9", lacc="#1565C0", pv=10, ph=10)

def build_img(el, S, w):
    ref  = el.get("ref","")
    de   = el.find("descricao")
    desc = txt(de) if de is not None else txt(el)
    return box(nn([P(f"[ {ref} ]",S["img_ref"]), P(desc,S["img_desc"])]),
               w, "#F8F9FA", border="#BDBDBD", bw=1, pv=12, ph=10)

def build_aplicar(el, S, w):
    enun = txt(el.find("enunciado"))
    resp = txt(el.find("resposta"))
    iw   = w - 28
    items = [P("✦  APLICAR AGORA", S["apl_tag"])] + para_lines(enun, S["apl_txt"])
    if resp:
        items.append(Spacer(1,6))
        ri = [P("RESPOSTA MODELO (uso do professor)", S["apl_rtag"])] + para_lines(resp, S["apl_resp"])
        rt = Table([[nn(ri)]], colWidths=[iw-16])
        rt.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),hx("#FFF8E1")),("BOX",(0,0),(-1,-1),1,hx("#FFE082")),
            ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
            ("LEFTPADDING",(0,0),(-1,-1),9),("RIGHTPADDING",(0,0),(-1,-1),9),
            ("VALIGN",(0,0),(-1,-1),"TOP"),
        ]))
        items.append(rt)
    return box(nn(items), w, "#FFFDE7", border="#F9A825", bw=2, pv=12, ph=14)


# ── Bloco: Table multi-linha (uma linha por elemento) ─────────────────────────
# Garante que o Table pode quebrar entre páginas em qualquer linha.
def build_bloco(bloco_el, S):
    op = bloco_el.get("operacao","")
    fundo_hex, dest_hex = CORES.get(op, COR_DEF)
    dest  = hx(dest_hex)
    fundo = hx(fundo_hex)
    micro = txt(bloco_el.find("micro-habilidade"))
    PAD_H, PAD_V_HDR, PAD_V_ROW = 10, 9, 3

    # Coleta todas as linhas: [(conteúdo_da_célula, é_header)]
    # conteúdo = lista de flowables que cabe facilmente numa página
    rows_data = []

    # Linha 0 — header colorido
    rows_data.append((nn([P(op.upper(),S["op_label"]), P(micro,S["micro"]) if micro else None]), True))

    def add_row(items):
        c = nn(items)
        if c: rows_data.append((c, False))

    for ch in bloco_el:
        if ch.tag == "secao":
            # título
            te = ch.find("titulo")
            if te is not None and te.text:
                add_row([P(te.text.strip(), S["h2"])])

            # parágrafos — UM POR LINHA para permitir quebra de página
            conteudo_el = ch.find("conteudo")
            if conteudo_el is not None:
                for p_el in conteudo_el.findall("paragrafo"):
                    t = (p_el.text or "").strip()
                    if t:
                        add_row([P(t, S["body"])])

            # sidebar de autor (full-width, logo após o texto)
            for sb in ch.findall("sidebar"):
                if sb.get("tipo") == "autor":
                    s = build_autor(sb, S, TW - 2*PAD_H)
                    if s: add_row([Spacer(1,4), s, Spacer(1,4)])
                elif sb.get("tipo") == "verificacao":
                    v = build_verif(sb, S, TW - 2*PAD_H)
                    if v: add_row([Spacer(1,4), v, Spacer(1,4)])

            # imagens dentro da seção
            for img_el in ch.findall("imagem"):
                im = build_img(img_el, S, TW - 2*PAD_H)
                if im: add_row([Spacer(1,4), im, Spacer(1,4)])

        elif ch.tag == "sidebar":
            tipo = ch.get("tipo","")
            if tipo == "verificacao":
                v = build_verif(ch, S, TW - 2*PAD_H)
                if v: add_row([Spacer(1,4), v, Spacer(1,4)])
            elif tipo == "autor":
                s = build_autor(ch, S, TW - 2*PAD_H)
                if s: add_row([Spacer(1,4), s, Spacer(1,4)])

        elif ch.tag == "imagem":
            im = build_img(ch, S, TW - 2*PAD_H)
            if im: add_row([Spacer(1,5), im, Spacer(1,5)])

        elif ch.tag == "nota_fonte":
            p = P(txt(ch), S["nota"])
            if p: add_row([p])

    # Monta o Table
    table_data = [[row] for (row, _) in rows_data]
    is_hdrs    = [is_hdr for (_, is_hdr) in rows_data]
    n          = len(rows_data)

    style = [("VALIGN",(0,0),(-1,-1),"TOP"),
             ("BOX",  (0,0),(-1,-1),1.5,dest)]

    for i, is_hdr in enumerate(is_hdrs):
        if is_hdr:
            style += [
                ("BACKGROUND",    (0,i),(0,i), dest),
                ("TOPPADDING",    (0,i),(0,i), PAD_V_HDR),
                ("BOTTOMPADDING", (0,i),(0,i), PAD_V_HDR),
                ("LEFTPADDING",   (0,i),(0,i), PAD_H),
                ("RIGHTPADDING",  (0,i),(0,i), PAD_H),
            ]
        else:
            style += [
                ("BACKGROUND",    (0,i),(0,i), fundo),
                ("TOPPADDING",    (0,i),(0,i), PAD_V_ROW),
                ("BOTTOMPADDING", (0,i),(0,i), PAD_V_ROW),
                ("LEFTPADDING",   (0,i),(0,i), PAD_H),
                ("RIGHTPADDING",  (0,i),(0,i), PAD_H),
            ]

    t = Table(table_data, colWidths=[TW])
    t.setStyle(TableStyle(style))
    return [t, Spacer(1, 14)]


# ── Cabeçalho de capítulo ─────────────────────────────────────────────────────
def build_cap_header(root, S):
    cab  = root.find("cabecalho")
    hab  = txt(cab.find("habilidade"))        if cab else ""
    perg = txt(cab.find("pergunta_capitulo")) if cab else root.get("titulo","")
    pq   = txt(cab.find("por_que_importa"))   if cab else ""
    items = []

    if hab:
        bt = Table([[P(hab,S["badge"])]], colWidths=[TW])
        bt.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),hx("#1565C0")),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),
        ]))
        items += [bt, Spacer(1,9)]

    if perg:
        items.append(P(perg, S["h1"]))

    if pq:
        pqi = Table([[nn([P("Por que importa: "+pq, S["por_que"])])]], colWidths=[TW-24])
        pqi.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),hx("#EEF4FF")),
            ("LINEBEFORE",(0,0),(0,-1),4,hx("#1565C0")),
            ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
            ("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),10),
        ]))
        items += [pqi, Spacer(1,10)]

    mapa_el = root.find("mapa-progressao")
    if mapa_el is not None:
        passos = mapa_el.findall("passo")
        n = len(passos)
        if n > 0:
            cols = []
            w_each = TW / n
            for p in passos:
                op_name = (p.text or "").strip()
                _, d_hex = CORES.get(op_name, COR_DEF)
                cols.append(nn([
                    P(f"Passo {p.get('ordem','')}", S["mapa_num"]),
                    Paragraph(f'<font color="{d_hex}"><b>{rl(op_name)}</b></font>', S["mapa_op"]),
                ]))
            mapa = Table([cols], colWidths=[w_each]*n)
            ms = [
                ("BACKGROUND",(0,0),(-1,-1),hx("#F8F9FA")),
                ("BOX",(0,0),(-1,-1),1,hx("#DEE2E6")),
                ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
                ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
                ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("ALIGN",(0,0),(-1,-1),"CENTER"),
            ]
            for i in range(n-1):
                ms.append(("LINEAFTER",(i,0),(i,-1),1,hx("#DEE2E6")))
            mapa.setStyle(TableStyle(ms))
            items += [mapa, Spacer(1,12)]

    items.append(HRFlowable(width=TW,thickness=2.5,color=hx("#1565C0"),
                            spaceBefore=0,spaceAfter=14))
    return items


# ── Processamento de um XML ───────────────────────────────────────────────────
def process_capitulo(xml_path, S, is_first=True):
    root  = ET.parse(str(xml_path)).getroot()
    story = []
    if not is_first:
        story.append(PageBreak())
    story.extend(build_cap_header(root, S))

    corpo = root.find("corpo")
    if corpo is not None:
        for ch in corpo:
            if ch.tag == "bloco":
                story.extend(build_bloco(ch, S))
            elif ch.tag == "quebra":
                story.append(PageBreak())
            elif ch.tag == "nota_fonte":
                p = P(txt(ch), S["nota"])
                if p: story.append(p)
            elif ch.tag == "sidebar":
                tipo = ch.get("tipo","")
                if tipo == "verificacao":
                    v = build_verif(ch, S, TW)
                    if v: story.append(v)
                elif tipo == "aplicar-agora":
                    a = build_aplicar(ch, S, TW)
                    if a: story.append(a)

    rodape = root.find("rodape")
    if rodape is not None:
        story.append(Spacer(1,16))
        for sb in rodape.findall("sidebar"):
            if sb.get("tipo") == "aplicar-agora":
                a = build_aplicar(sb, S, TW)
                if a: story.append(a)
    return story


# ── Template de página ────────────────────────────────────────────────────────
def make_doc(output_path):
    doc = BaseDocTemplate(str(output_path), pagesize=A4,
                          leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB)
    frame = Frame(ML, MB, TW, PAGE_H-MT-MB, id="main")

    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica",8)
        canvas.setFillColor(hx("#888888"))
        canvas.drawCentredString(PAGE_W/2, 14*mm, str(doc.page))
        canvas.setStrokeColor(hx("#DEE2E6"))
        canvas.setLineWidth(0.5)
        canvas.line(ML, 18*mm, PAGE_W-MR, 18*mm)
        canvas.restoreState()

    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=on_page)])
    return doc


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    g  = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("xml", nargs="?")
    g.add_argument("--unidade", "-u")
    ap.add_argument("--output", "-o")
    args = ap.parse_args()

    if args.xml:
        xml_files   = [Path(args.xml)]
        default_out = Path(args.xml).with_suffix(".pdf")
    else:
        xml_files   = sorted(Path(args.unidade).glob("*.xml"))
        if not xml_files:
            sys.exit(f"Nenhum XML em: {args.unidade}")
        default_out = Path(args.unidade) / "apostila.pdf"

    out = Path(args.output) if args.output else default_out
    S   = make_styles()
    doc = make_doc(out)
    story = []
    for i, xf in enumerate(xml_files):
        print(f"  [{i+1}/{len(xml_files)}] {xf.name}")
        story.extend(process_capitulo(xf, S, is_first=(i==0)))
    print("  Gerando PDF...")
    doc.build(story)
    print(f"  PDF gerado: {out}")

if __name__ == "__main__":
    main()
