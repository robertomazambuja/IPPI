#!/usr/bin/env python3
"""
formatador.py -- Conversor Markdown+HTML -> XML (substitui Agente 5)

Le texto.md com marcacao HTML normalizada e produz o XML para InDesign.
Implementa a spec completa de agente5-skill.md de forma deterministica.
"""

import re
import logging
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from xml.sax.saxutils import escape as xe

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Regexes
# ---------------------------------------------------------------------------
_RE_H2   = re.compile(r"^##\s+(.+)$")
_RE_H3   = re.compile(r"^###\s+(.+)$")
_RE_H4   = re.compile(r"^####\s+(.+)$")
_RE_OPEN = re.compile(r"^<!--\s*\[([A-Z][A-Z0-9_]*)(?::([^\]]*))?\]\s*-->$")
_RE_CLOSE= re.compile(r"^<!--\s*\[/([A-Z][A-Z0-9_]*)\]\s*-->$")
_RE_AVISO= re.compile(r"^<!--\s*AVISO_AGENTE5:")
_RE_BOLD = re.compile(r"^\*\*(.+?):\*\*\s*(.+)$")
_RE_HR   = re.compile(r"^-{3,}$")
_RE_ID   = re.compile(r"^(\d{2}-\d{2})")

# Mapeamento tipo HTML -> tipo XML
TIPO_MAP: Dict[str, str] = {
    "DEFINICAO": "definicao",
    "APRESENTACAO": "definicao",
    "CLASSIFICACAO": "classificacao",
    "PERSPECTIVA": "perspectiva",
    "PERSPECTIVA_A": "perspectiva",
    "PERSPECTIVA_B": "perspectiva",
    "PERSPECTIVA_C": "perspectiva",
    "CAUSA": "causa",
    "CONSEQUENCIA": "consequencia",
    "RELACAO_CAUSAL": "relacao-causal",
    "SEQUENCIA": "sequencia",
    "ASPECTO": "aspecto",
    "INTRODUCAO_COMPARACAO": "introducao-comparacao",
    "COMPARACAO": "comparacao",
    "APLICACAO": "aplicacao",
    "CONCLUSAO_PARCIAL": "conclusao-parcial",
    "RESULTADO": "resultado",
    "SINTESE": "sintese",
    "ENCADEAMENTO": "encadeamento",
}

PRIMARY_TYPES = set(TIPO_MAP.keys())
RODAPE_TYPES  = {"SINTESE", "ENCADEAMENTO"}

# ---------------------------------------------------------------------------
# Token
# ---------------------------------------------------------------------------
class Token:
    __slots__ = ("kind", "text", "body")
    def __init__(self, kind: str, text: str, body: str = ""):
        self.kind = kind   # H2 H3 H4 OPEN CLOSE AVISO HR TEXT BLANK
        self.text = text
        self.body = body   # content after ':' for OPEN

def tokenize(src: str) -> List[Token]:
    out: List[Token] = []
    for line in src.split("\n"):
        s = line.strip()
        if not s:
            out.append(Token("BLANK", line)); continue
        m = _RE_H4.match(s)
        if m: out.append(Token("H4", m.group(1).strip())); continue
        m = _RE_H3.match(s)
        if m: out.append(Token("H3", m.group(1).strip())); continue
        m = _RE_H2.match(s)
        if m: out.append(Token("H2", m.group(1).strip())); continue
        m = _RE_CLOSE.match(s)
        if m: out.append(Token("CLOSE", m.group(1))); continue
        m = _RE_OPEN.match(s)
        if m: out.append(Token("OPEN", m.group(1), (m.group(2) or "").strip())); continue
        if _RE_AVISO.match(s): out.append(Token("AVISO", s)); continue
        if _RE_HR.match(s): out.append(Token("HR", s)); continue
        out.append(Token("TEXT", line))
    return out

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def count_words(lines: List[str]) -> int:
    total = 0
    for line in lines:
        s = line.strip()
        if not s: continue
        if _RE_OPEN.match(s) or _RE_CLOSE.match(s) or _RE_AVISO.match(s): continue
        if _RE_H2.match(s) or _RE_H3.match(s) or _RE_H4.match(s): continue
        if _RE_HR.match(s): continue
        clean = re.sub(r"\*+", "", s)
        clean = re.sub(r"<!--.*?-->", "", clean)
        total += len(clean.split())
    return total

def tokens_to_lines(toks: List[Token]) -> List[str]:
    return [t.text for t in toks if t.kind in ("TEXT", "BLANK")]

def indent(s: str, n: int) -> str:
    pad = "  " * n
    return "\n".join(pad + l if l.strip() else l for l in s.split("\n"))

def para_xml(lines: List[str], lvl: int) -> str:
    """Convert text lines to <paragrafo> XML elements."""
    out = []
    buf: List[str] = []
    def flush():
        if buf:
            text = " ".join(b.strip() for b in buf if b.strip())
            if text:
                out.append("  " * lvl + f"<paragrafo>{xe(text)}</paragrafo>")
            buf.clear()
    for line in lines:
        s = line.strip()
        if not s:
            flush()
        else:
            buf.append(s)
    flush()
    return "\n".join(out)

def parse_autor_tag(body: str) -> Dict[str, str]:
    """
    Parse AUTOR tag body: "Nome (datas) Pais | ref=tipo"
    Returns {nome, pais, ref}
    """
    ref = ""
    if "|" in body:
        parts = body.split("|", 1)
        body = parts[0].strip()
        extra = parts[1].strip()
        if extra.startswith("ref="):
            ref = extra[4:].strip()
    m = re.match(r"^(.+?)\s*\(([^)]+)\)\s*(.*)$", body)
    if m:
        nome = m.group(1).strip() + " (" + m.group(2).strip() + ")"
        pais = m.group(3).strip()
    else:
        nome = body
        pais = ""
    return {"nome": nome, "pais": pais, "ref": ref}

# ---------------------------------------------------------------------------
# Block collector
# ---------------------------------------------------------------------------

def collect_block(tokens: List[Token], start: int) -> Tuple[str, str, List[Token], int]:
    """
    tokens[start] must be OPEN. Collects until matching CLOSE.
    Returns (type, body, inner_tokens, idx_after_close).
    TIPO_OPERACAO has no close: returns immediately with empty inner.
    """
    t = tokens[start]
    btype = t.text
    body  = t.body

    if btype == "TIPO_OPERACAO":
        return btype, body, [], start + 1

    inner: List[Token] = []
    depth = 1
    i = start + 1
    while i < len(tokens):
        tok = tokens[i]
        if tok.kind == "OPEN" and tok.text == btype:
            depth += 1; inner.append(tok)
        elif tok.kind == "CLOSE" and tok.text == btype:
            depth -= 1
            if depth == 0:
                return btype, body, inner, i + 1
            inner.append(tok)
        else:
            inner.append(tok)
        i += 1
    return btype, body, inner, i

def collect_until_boundary(tokens: List[Token], start: int) -> Tuple[List[Token], int]:
    """
    Collect tokens until H2, H3, or EOF. Does not consume the boundary token.
    """
    out = []
    i = start
    while i < len(tokens):
        if tokens[i].kind in ("H2", "H3"):
            break
        out.append(tokens[i])
        i += 1
    return out, i

# ---------------------------------------------------------------------------
# Intermediate representation
# ---------------------------------------------------------------------------

class AutorNode:
    def __init__(self, nome, pais, ref, descricao):
        self.nome = nome; self.pais = pais
        self.ref = ref; self.descricao = descricao

class FonteNode:
    def __init__(self, texto, tipo=""):
        self.texto = texto; self.tipo = tipo

class SubtipoNode:
    def __init__(self, nome, lines):
        self.nome = nome; self.lines = lines

class SecaoNode:
    def __init__(self, tipo_xml, nome="", h4="", lines=None,
                 intro_lines=None, subtipos=None, autores=None, aviso=""):
        self.tipo_xml   = tipo_xml
        self.nome       = nome
        self.h4         = h4
        self.lines      = lines or []
        self.intro_lines= intro_lines or []
        self.subtipos   = subtipos or []
        self.autores    = autores or []
        self.aviso      = aviso

class BlocoNode:
    def __init__(self, idx, titulo, operacao):
        self.idx      = idx
        self.titulo   = titulo
        self.operacao = operacao
        self.secoes: List[SecaoNode] = []
        self.fontes:  List[FonteNode] = []
        self.palavras = 0

class RodapeNode:
    def __init__(self):
        self.sintese = ""
        self.encadeamento = ""
        self.extras: List[SecaoNode] = []

# ---------------------------------------------------------------------------
# Parse a section group (tokens between two ### headings)
# ---------------------------------------------------------------------------

def parse_section_group(titulo: str, toks: List[Token], bloco_idx: int) -> BlocoNode:
    bloco = BlocoNode(bloco_idx, titulo, "")

    # All text lines for word count (includes all content)
    all_text = [t.text for t in toks]

    pending_secoes: List[SecaoNode] = []
    pending_autores: List[AutorNode] = []
    free_text_buf: List[str] = []  # text lines between primary blocks

    i = 0
    while i < len(toks):
        t = toks[i]

        if t.kind in ("TEXT", "BLANK"):
            free_text_buf.append(t.text)
            i += 1
            continue

        if t.kind not in ("OPEN",):
            i += 1
            continue

        btype, body, inner, i = collect_block(toks, i)

        if btype == "TIPO_OPERACAO":
            if not bloco.operacao:
                bloco.operacao = body
            continue

        if btype == "AUTOR":
            info = parse_autor_tag(body)
            desc = " ".join(x.text.strip() for x in inner if x.kind == "TEXT" and x.text.strip())
            pending_autores.append(AutorNode(info["nome"], info["pais"], info["ref"], desc))
            continue

        if btype in ("FONTE", "FONTE_PRIMARIA"):
            lines = [x.text.strip() for x in inner if x.kind == "TEXT" and x.text.strip()]
            tipo = "primaria" if btype == "FONTE_PRIMARIA" else ""
            bloco.fontes.append(FonteNode(" ".join(lines), tipo))
            free_text_buf.clear()
            continue

        if btype == "SUBTIPO":
            sub_lines = tokens_to_lines(inner)
            last_clas = next((s for s in reversed(pending_secoes)
                              if s.tipo_xml == "classificacao"), None)
            if last_clas is not None:
                last_clas.subtipos.append(SubtipoNode(body, sub_lines))
            else:
                pending_secoes.append(SecaoNode("subtipo", nome=body, lines=sub_lines))
            free_text_buf.clear()
            continue

        # --- Primary block ---
        tipo_xml = TIPO_MAP.get(btype)
        if tipo_xml is None:
            tipo_xml = "generico"
            aviso = f"tipo {btype} nao mapeado"
        else:
            aviso = ""

        # Parse inner tokens with explicit index to properly skip nested block content
        h4 = ""
        inner_lines: List[str] = []
        j = 0
        while j < len(inner):
            x = inner[j]
            if x.kind == "H4":
                h4 = x.text
                j += 1
            elif x.kind == "OPEN":
                nb, nbody, ninner, j = collect_block(inner, j)
                if nb == "AUTOR":
                    info = parse_autor_tag(nbody)
                    desc = " ".join(xi.text.strip() for xi in ninner
                                    if xi.kind == "TEXT" and xi.text.strip())
                    if not info["ref"]:
                        info["ref"] = tipo_xml
                    pending_autores.append(AutorNode(info["nome"], info["pais"], info["ref"], desc))
                # All other nested blocks (FONTE inside primary, etc.) are skipped from inner_lines
            elif x.kind in ("TEXT", "BLANK"):
                inner_lines.append(x.text)
                j += 1
            else:
                j += 1  # AVISO, CLOSE, HR, etc.

        # Prepend free-standing text to the first secao of the bloco
        if free_text_buf and not pending_secoes:
            inner_lines = free_text_buf + inner_lines
        free_text_buf.clear()

        secao = SecaoNode(tipo_xml, nome=body, h4=h4, lines=inner_lines, aviso=aviso)
        pending_secoes.append(secao)

    # Flush remaining free text into the last secao
    if free_text_buf and pending_secoes:
        pending_secoes[-1].lines.extend(free_text_buf)

    # Set H3 titulo as secao titulo when no H4 is present (single primary secao)
    if len(pending_secoes) == 1 and not pending_secoes[0].h4:
        pending_secoes[0].h4 = titulo

    # Assign pending AUTORs to secoes by ref=
    for aut in pending_autores:
        ref = aut.ref
        matched = False
        if ref:
            for sec in pending_secoes:
                if sec.tipo_xml == ref or ref == sec.tipo_xml.replace("-", "_"):
                    sec.autores.append(aut)
                    matched = True
                    break
                if sec.tipo_xml == "classificacao" and ref == "subtipo":
                    sec.autores.append(aut)
                    matched = True
                    break
        if not matched and pending_secoes:
            pending_secoes[-1].autores.append(aut)

    bloco.secoes = pending_secoes
    bloco.palavras = count_words(all_text)
    return bloco


# ---------------------------------------------------------------------------
# Parse rodapé tokens
# ---------------------------------------------------------------------------

def parse_rodape_tokens(toks: List[Token]) -> RodapeNode:
    rod = RodapeNode()
    i = 0
    while i < len(toks):
        t = toks[i]
        if t.kind == "OPEN":
            btype, body, inner, i = collect_block(toks, i)
            lines = [x.text.strip() for x in inner if x.kind == "TEXT" and x.text.strip()]
            text = " ".join(lines)
            if btype == "SINTESE":
                rod.sintese = text
            elif btype == "ENCADEAMENTO":
                rod.encadeamento = text
            else:
                tipo_xml = TIPO_MAP.get(btype, "generico")
                aviso = "" if btype in TIPO_MAP else f"tipo {btype} nao mapeado"
                rod.extras.append(SecaoNode(tipo_xml, lines=lines, aviso=aviso))
        else:
            i += 1
    return rod

# ---------------------------------------------------------------------------
# Parse full document
# ---------------------------------------------------------------------------

def parse_document(filepath: Path):
    src = filepath.read_text(encoding="utf-8")
    tokens = tokenize(src)
    n = len(tokens)

    titulo = ""
    cap_id = ""
    contexto = {}
    blocos: List[BlocoNode] = []
    rodape: Optional[RodapeNode] = None

    # Derive cap_id from filename
    m = _RE_ID.match(filepath.stem)
    if m:
        cap_id = m.group(1)

    i = 0
    # Step 1: find H2 title
    while i < n:
        if tokens[i].kind == "H2":
            titulo = tokens[i].text
            i += 1
            break
        i += 1

    # Step 2: find CONTEXTO_OPERACAO
    while i < n:
        t = tokens[i]
        if t.kind == "OPEN" and t.text == "CONTEXTO_OPERACAO":
            _, _, inner, i = collect_block(tokens, i)
            for x in inner:
                if x.kind == "TEXT":
                    bm = _RE_BOLD.match(x.text.strip())
                    if bm:
                        contexto[bm.group(1).strip()] = bm.group(2).strip()
        elif t.kind == "H3":
            break
        else:
            i += 1

    # Step 3: parse section groups
    bloco_idx = 0
    while i < n:
        t = tokens[i]
        if t.kind == "H2":
            # Rodapé area starts
            i += 1
            break
        elif t.kind == "H3":
            sec_titulo = t.text
            i += 1
            sec_toks, i = collect_until_boundary(tokens, i)
            bloco_idx += 1
            bloco = parse_section_group(sec_titulo, sec_toks, bloco_idx)
            blocos.append(bloco)
        else:
            i += 1

    # Step 4: parse rodapé
    rod_toks = tokens[i:]
    rodape = parse_rodape_tokens(rod_toks)

    return titulo, cap_id, contexto, blocos, rodape

# ---------------------------------------------------------------------------
# XML Renderer
# ---------------------------------------------------------------------------

def render_sidebar_autor(aut: AutorNode, lvl: int) -> str:
    pad = "  " * lvl
    lines = [f'{pad}<sidebar tipo="autor">']
    lines.append(f'{pad}  <nome>{xe(aut.nome)}</nome>')
    if aut.pais:
        lines.append(f'{pad}  <pais>{xe(aut.pais)}</pais>')
    if aut.descricao:
        lines.append(f'{pad}  <descricao>{xe(aut.descricao)}</descricao>')
    lines.append(f'{pad}</sidebar>')
    return "\n".join(lines)

def render_secao(sec: SecaoNode, sec_id: str, lvl: int) -> str:
    pad = "  " * lvl
    attrs = f'id="{sec_id}" tipo="{sec.tipo_xml}"'
    if sec.nome:
        attrs += f' nome="{xe(sec.nome)}"'
    if sec.aviso:
        attrs += f' aviso="{xe(sec.aviso)}"'

    lines = [f'{pad}<secao {attrs}>']

    if sec.h4:
        lines.append(f'{pad}  <titulo>{xe(sec.h4)}</titulo>')

    if sec.tipo_xml == "classificacao":
        if sec.intro_lines or sec.lines:
            intro_text = para_xml(sec.lines, lvl + 1)
            if intro_text:
                lines.append(f'{pad}  <introducao>')
                lines.append(intro_text)
                lines.append(f'{pad}  </introducao>')
        if sec.subtipos:
            lines.append(f'{pad}  <lista-subtipos>')
            for st in sec.subtipos:
                lines.append(f'{pad}    <item tipo="subtipo" nome="{xe(st.nome)}">')
                body = para_xml(st.lines, lvl + 3)
                if body:
                    lines.append(f'{pad}      <conteudo>')
                    lines.append(body)
                    lines.append(f'{pad}      </conteudo>')
                lines.append(f'{pad}    </item>')
            lines.append(f'{pad}  </lista-subtipos>')
    else:
        body = para_xml(sec.lines, lvl + 1)
        if body:
            lines.append(f'{pad}  <conteudo>')
            lines.append(body)
            lines.append(f'{pad}  </conteudo>')

    for aut in sec.autores:
        lines.append(render_sidebar_autor(aut, lvl + 1))

    lines.append(f'{pad}</secao>')
    return "\n".join(lines)

def render_bloco(bloco: BlocoNode, lvl: int,
                 verificacoes: Optional[Dict[int, str]] = None) -> str:
    pad = "  " * lvl
    op = xe(bloco.operacao) if bloco.operacao else ""
    lines = [f'{pad}<bloco id="bloco-{bloco.idx}" palavras="{bloco.palavras}" operacao="{op}">']

    sec_counter = [0]
    def next_sec_id():
        sec_counter[0] += 1
        return f"sec-{sec_counter[0]}"

    for sec in bloco.secoes:
        lines.append(render_secao(sec, next_sec_id(), lvl + 1))

    for fonte in bloco.fontes:
        if fonte.tipo:
            lines.append(f'{pad}  <nota_fonte tipo="{fonte.tipo}">{xe(fonte.texto)}</nota_fonte>')
        else:
            lines.append(f'{pad}  <nota_fonte>{xe(fonte.texto)}</nota_fonte>')

    # Sidebar de verificação para este bloco (se houver)
    if verificacoes and bloco.idx in verificacoes:
        verif_xml = verificacoes[bloco.idx]
        # Indenta o sidebar para ficar alinhado com o bloco
        indented = indent(verif_xml, lvl + 1)
        lines.append(indented)

    lines.append(f'{pad}</bloco>')
    return "\n".join(lines)

def render_xml(titulo: str, cap_id: str, contexto: dict,
               blocos: List[BlocoNode], rodape: RodapeNode,
               verificacoes: Optional[Dict[int, str]] = None,
               aplicar_agora: Optional[str] = None) -> str:
    total_words = sum(b.palavras for b in blocos)

    parts = ['<?xml version="1.0" encoding="UTF-8"?>']
    parts.append(f'<capitulo id="{cap_id}" titulo="{xe(titulo)}" palavras_total="{total_words}">')

    # Cabecalho
    parts.append("  <cabecalho>")
    field_map = {
        "Habilidade": "habilidade",
        "Operação principal": "operacao_principal",
        "Pergunta do capítulo": "pergunta_capitulo",
        "Por que importa": "por_que_importa",
    }
    for label, tag in field_map.items():
        val = contexto.get(label, "")
        if val and val != "[AUSENTE]":
            parts.append(f"    <{tag}>{xe(val)}</{tag}>")
        else:
            parts.append(f"    <!-- WARNING: campo '{label}' ausente -->")
    parts.append("  </cabecalho>")
    parts.append("")

    # Mapa de progressão — sequência de operações cognitivas do capítulo
    ops = [(b.idx, b.operacao) for b in blocos if b.operacao]
    if ops:
        parts.append("  <mapa-progressao>")
        for idx, op in ops:
            parts.append(f'    <passo ordem="{idx}" bloco="bloco-{idx}">{xe(op)}</passo>')
        parts.append("  </mapa-progressao>")
        parts.append("")

    # Corpo com quebras de pagina
    parts.append("  <corpo>")
    parts.append("")
    acum = 0
    LIMIAR = 1300
    for bloco in blocos:
        will_cross = acum + bloco.palavras > LIMIAR
        if will_cross and acum > 0:
            diff = (acum + bloco.palavras) - LIMIAR
            sugestao = "fraca" if diff < 150 else "forte"
            parts.append(f'    <quebra tipo="pagina" sugestao="{sugestao}"/>')
            parts.append("")
            acum = 0
        parts.append(render_bloco(bloco, 2, verificacoes=verificacoes))
        parts.append("")
        acum += bloco.palavras

    parts.append("  </corpo>")
    parts.append("")

    # Rodape
    parts.append("  <rodape>")
    if rodape:
        for extra in rodape.extras:
            body = para_xml(extra.lines, 2)
            attrs = f'tipo="{extra.tipo_xml}"'
            if extra.aviso:
                attrs += f' aviso="{xe(extra.aviso)}"'
            parts.append(f"    <secao {attrs}>")
            if body:
                parts.append("      <conteudo>")
                parts.append(body)
                parts.append("      </conteudo>")
            parts.append("    </secao>")
        if rodape.sintese:
            parts.append(f"    <sintese>{xe(rodape.sintese)}</sintese>")
        if rodape.encadeamento:
            parts.append(f"    <encadeamento>{xe(rodape.encadeamento)}</encadeamento>")
        if aplicar_agora:
            parts.append(indent(aplicar_agora, 2))
    parts.append("  </rodape>")
    parts.append("")
    parts.append("</capitulo>")

    return "\n".join(parts)

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def formatar_capitulo(
    texto_path: Path,
    output_dir: Path,
    verificacoes: Optional[Dict[int, str]] = None,
    aplicar_agora: Optional[str] = None,
) -> Optional[Path]:
    """
    Converte texto_path (markdown normalizado) em XML.
    Salva em output_dir/<stem>.xml.
    Retorna o Path do XML gerado, ou None em caso de erro.

    verificacoes: dict {idx_secao: xml_sidebar} gerado por verificador.gerar_verificacoes()
    aplicar_agora: xml_sidebar do exercício final, ou None
    """
    try:
        titulo, cap_id, contexto, blocos, rodape = parse_document(texto_path)
        xml_str = render_xml(titulo, cap_id, contexto, blocos, rodape,
                             verificacoes=verificacoes, aplicar_agora=aplicar_agora)

        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = output_dir / (texto_path.stem + ".xml")
        out_path.write_text(xml_str, encoding="utf-8")
        logger.info("[Formatador] Salvo: %s (%d blocos, %d palavras)",
                    out_path.name, len(blocos), sum(b.palavras for b in blocos))
        return out_path
    except Exception as e:
        logger.exception("[Formatador] Falha ao processar %s", texto_path)
        return None
