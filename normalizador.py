#!/usr/bin/env python3
"""
normalizador.py -- Normalizacao de marcacao HTML (substitui Agente 3)

Aplica as 4 normalizacoes da agente3-skill.md em Python puro:
  N1. CONTEXTO_OPERACAO -- conteudo interno em markdown bold
  N2. FONTE -- Formato C (tag de abertura sem conteudo embutido)
  N3. AUTOR -- ancoragem com ref= quando solto fora de qualquer bloco
  N4. Tipos desconhecidos -- adicionar AVISO_AGENTE5; remover AVISOs incorretos
  N5. H2 de titulo -- injetar ## <Pergunta do capitulo> se ausente (contrato com A5)

Uso direto:
    from normalizador import normalizar_texto
    modificado, avisos = normalizar_texto(Path("output/.../texto.md"))
"""

import re
import logging
from pathlib import Path
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tipos conhecidos (agente3-skill.md, secao "Tipos desconhecidos")
# ---------------------------------------------------------------------------
TIPOS_CONHECIDOS: frozenset = frozenset({
    "CONTEXTO_OPERACAO", "TIPO_OPERACAO",
    "APRESENTACAO", "DEFINICAO", "CLASSIFICACAO", "SUBTIPO",
    "PERSPECTIVA", "PERSPECTIVA_A", "PERSPECTIVA_B", "PERSPECTIVA_C",
    "EXEMPLO", "CAUSA", "CONSEQUENCIA", "RELACAO_CAUSAL",
    "INTRODUCAO_COMPARACAO", "CONCLUSAO_PARCIAL", "COMPARACAO",
    "APLICACAO", "RESULTADO",
    "AUTOR", "FONTE", "FONTE_PRIMARIA", "VERIFICACAO",
    "SINTESE", "ENCADEAMENTO",
})

# Quatro campos obrigatorios do CONTEXTO_OPERACAO
_CAMPOS_CONTEXTO = [
    "Habilidade",
    "Operação principal",
    "Pergunta do capítulo",
    "Por que importa",
]

# Tipos que sao marcadores standalone (sem tag de fechamento correspondente).
# Nao sao empilhados no block_stack.
TIPOS_STANDALONE: frozenset = frozenset({"TIPO_OPERACAO"})

# ---------------------------------------------------------------------------
# Regexes
# ---------------------------------------------------------------------------

# Abre bloco: <!-- [TIPO] --> ou <!-- [TIPO: conteudo qualquer] -->
_RE_OPEN = re.compile(r"^<!--\s*\[([A-Z][A-Z0-9_]*)(?::([^\]]*))?\]\s*-->$")

# Fecha bloco: <!-- [/TIPO] -->
_RE_CLOSE = re.compile(r"^<!--\s*\[/([A-Z][A-Z0-9_]*)\]\s*-->$")

# AVISO existente: <!-- AVISO_AGENTE5: tipo NOME nao mapeado ... -->
_RE_AVISO = re.compile(r"^<!--\s*AVISO_AGENTE5:\s*tipo\s+(\w+)\s+n")

# Campo em HTML comment interno: <!-- Habilidade: texto -->
_RE_COMMENT_FIELD = re.compile(r"^<!--\s*(.+?):\s*(.*?)\s*-->$")

# Campo em markdown bold: **Campo:** valor  (o : fica dentro do bold, antes do **)
_RE_BOLD_FIELD = re.compile(r"^\*\*(.+?):\*\*\s*(.+)$")

# H2 de titulo (contrato com A5)
_RE_H2 = re.compile(r"^##\s+\S")

# Pergunta do capitulo dentro do CONTEXTO_OPERACAO
_RE_PERGUNTA = re.compile(r"^\*\*Pergunta do capítulo:\*\*\s*(.+)$")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _aviso_str(tipo: str) -> str:
    return '<!-- AVISO_AGENTE5: tipo ' + tipo + ' não mapeado — gerar secao tipo="generico" -->'


def _norm_contexto(lines: List[str]) -> List[str]:
    """
    Normaliza linhas internas de CONTEXTO_OPERACAO para markdown bold.

    - Detecta formato HTML comment (<!-- Campo: valor -->) e converte.
    - Verifica se os 4 campos obrigatorios estao presentes; adiciona [AUSENTE] se faltar.
    """
    has_comment_fields = any(
        _RE_COMMENT_FIELD.match(l.strip())
        for l in lines
        if l.strip() and not _RE_OPEN.match(l.strip()) and not _RE_CLOSE.match(l.strip())
    )

    if has_comment_fields:
        converted: List[str] = []
        for line in lines:
            s = line.strip()
            if not s:
                converted.append(line)
                continue
            m = _RE_COMMENT_FIELD.match(s)
            if m:
                converted.append("**" + m.group(1).strip() + ":** " + m.group(2).strip())
            else:
                converted.append(line)
        lines = converted

    # Verifica quais campos estao presentes
    present: set = set()
    for line in lines:
        m = _RE_BOLD_FIELD.match(line.strip())
        if m:
            present.add(m.group(1).strip())

    result = list(lines)
    for campo in _CAMPOS_CONTEXTO:
        if campo not in present:
            result.append("**" + campo + ":** [AUSENTE]")

    return result


# ---------------------------------------------------------------------------
# Normalizador principal
# ---------------------------------------------------------------------------

def _normalizar(texto: str) -> Tuple[str, List[str]]:
    """
    Aplica as normalizacoes N1-N5.
    Retorna (texto_normalizado, avisos).
    E idempotente: rodar duas vezes produz o mesmo resultado.
    """
    lines = texto.split("\n")
    out: List[str] = []
    avisos: List[str] = []

    block_stack: List[str] = []
    last_closed: Optional[str] = None
    last_parent: Optional[str] = None  # exclui AUTOR (para ref=)

    in_contexto = False
    contexto_buf: List[str] = []

    fonte_pending: List[str] = []

    n = len(lines)
    i = 0

    while i < n:
        line = lines[i]
        s = line.strip()

        # N4: AVISO existente
        m = _RE_AVISO.match(s)
        if m:
            # Extrair o nome do tipo do AVISO
            tipo_match = re.search(r"tipo\s+(\w+)", s)
            tipo_ref = tipo_match.group(1) if tipo_match else ""
            if tipo_ref in TIPOS_CONHECIDOS:
                avisos.append("Removido AVISO incorreto para tipo conhecido: " + tipo_ref)
                i += 1
                continue
            last_out_s = out[-1].strip() if out else ""
            if last_out_s != s:
                out.append(line)
            i += 1
            continue

        # TAG DE ABERTURA
        m = _RE_OPEN.match(s)
        if m:
            tag_type = m.group(1)
            tag_body = (m.group(2) or "").strip()

            # Standalone: emitir sem empilhar
            if tag_type in TIPOS_STANDALONE:
                out.append(line)
                i += 1
                continue

            # N2: FONTE com conteudo na tag de abertura (Formato A)
            if tag_type == "FONTE" and tag_body:
                fonte_pending.append(tag_body)
                i += 1
                continue

            # N3: AUTOR fora de qualquer bloco, sem ref=
            if (tag_type == "AUTOR"
                    and not block_stack
                    and "ref=" not in s
                    and last_parent is not None):
                ref_val = last_parent.lower().replace("_", "-")
                if tag_body:
                    new_tag = "<!-- [" + tag_type + ": " + tag_body + " | ref=" + ref_val + "] -->"
                else:
                    new_tag = "<!-- [" + tag_type + " | ref=" + ref_val + "] -->"
                out.append(new_tag)
                block_stack.append(tag_type)
                avisos.append("Adicionado ref=" + ref_val + " ao AUTOR solto apos " + last_parent)
                i += 1
                continue

            # N1: entrando em CONTEXTO_OPERACAO
            if tag_type == "CONTEXTO_OPERACAO":
                in_contexto = True
                contexto_buf = []
                out.append(line)
                block_stack.append(tag_type)
                i += 1
                continue

            out.append(line)
            block_stack.append(tag_type)

            # N4: tipo desconhecido
            if tag_type not in TIPOS_CONHECIDOS:
                aviso_line = _aviso_str(tag_type)
                next_s = lines[i + 1].strip() if i + 1 < n else ""
                if next_s != aviso_line:
                    out.append(aviso_line)
                    avisos.append("Adicionado AVISO para tipo desconhecido: " + tag_type)

            i += 1
            continue

        # TAG DE FECHAMENTO
        m = _RE_CLOSE.match(s)
        if m:
            tag_type = m.group(1)

            # N2: FONTE com conteudo pendente
            if tag_type == "FONTE" and fonte_pending:
                out.append("<!-- [FONTE] -->")
                for c in fonte_pending:
                    out.append(c)
                out.append("<!-- [/FONTE] -->")
                fonte_pending = []
                if block_stack and block_stack[-1] == "FONTE":
                    block_stack.pop()
                last_closed = "FONTE"
                last_parent = "FONTE"
                i += 1
                continue

            # N1: fechamento de CONTEXTO_OPERACAO
            if tag_type == "CONTEXTO_OPERACAO" and in_contexto:
                normalized_ctx = _norm_contexto(contexto_buf)
                out.extend(normalized_ctx)
                out.append(line)
                in_contexto = False
                contexto_buf = []
                if block_stack and block_stack[-1] == "CONTEXTO_OPERACAO":
                    block_stack.pop()
                last_closed = "CONTEXTO_OPERACAO"
                last_parent = "CONTEXTO_OPERACAO"
                i += 1
                continue

            out.append(line)
            if block_stack and block_stack[-1] == tag_type:
                block_stack.pop()
            last_closed = tag_type
            if tag_type != "AUTOR":
                last_parent = tag_type
            i += 1
            continue

        # LINHA REGULAR
        if in_contexto:
            contexto_buf.append(line)
        elif fonte_pending and s.startswith("**Fonte:**"):
            avisos.append("Descartada linha duplicada (Formato B FONTE): " + s[:80])
        else:
            out.append(line)

        i += 1

    # Verificacao final
    if block_stack:
        avisos.append(
            "AVISO: bloco(s) nao fechado(s) ao final do arquivo: " + str(block_stack) +
            ". Verifique a saida do Agente 2."
        )
        logger.warning("[Normalizador] Blocos nao fechados: %s", block_stack)

    if fonte_pending:
        avisos.append("AVISO: FONTE Formato A sem tag de fechamento -- emitido no final.")
        out.append("<!-- [FONTE] -->")
        for c in fonte_pending:
            out.append(c)
        out.append("<!-- [/FONTE] -->")

    # N5: garantir H2 de titulo para o A5 (formatador.py espera ## Titulo como primeira linha).
    # Idempotente: so injeta se nao houver nenhum H2 no output.
    if not any(_RE_H2.match(l) for l in out):
        titulo_h2 = ""
        for l in out:
            m = _RE_PERGUNTA.match(l.strip())
            if m:
                titulo_h2 = m.group(1).strip()
                break
        if titulo_h2:
            out.insert(0, "")
            out.insert(0, f"## {titulo_h2}")
            avisos.append("Injetado H2 de titulo a partir de 'Pergunta do capitulo': " + titulo_h2)

    return "\n".join(out), avisos


def normalizar_texto(path: Path) -> Tuple[bool, List[str]]:
    """
    Normaliza o arquivo de texto em `path`.
    Retorna (modificado: bool, avisos: List[str]).
    Se o conteudo normalizado for identico ao original, o arquivo nao e reescrito.
    """
    original = path.read_text(encoding="utf-8")
    normalizado, avisos = _normalizar(original)
    modified = normalizado != original

    if modified:
        path.write_text(normalizado, encoding="utf-8")
        logger.info("[Normalizador] Modificado: %s (%d alteracao(oes))", path.name, len(avisos))
    else:
        logger.info("[Normalizador] Sem alteracoes: %s", path.name)

    for a in avisos:
        logger.debug("[Normalizador] %s", a)

    return modified, avisos
