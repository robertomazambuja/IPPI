#!/usr/bin/env python3
"""
verificador.py — Geração de verificações fechadas e "Aplicar agora"

Lê o core.md de um capítulo e produz:
  - verificacoes: dict {idx_secao (1-based): texto_pergunta_com_resposta}
    para cada seção com VERIFICACAO: Sim
  - aplicar_agora: str com o mini-caso + resposta comentada oculta
    baseado na OPERACAO_PRINCIPAL e no EXEMPLO_ANCOLA da última seção principal

Usa uma única chamada à API (Haiku) por capítulo — sem tools, sem loop agêntico.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Optional, Tuple

import anthropic

logger = logging.getLogger(__name__)

# Modelo padrão para geração de verificações (barato e suficiente)
VERIFICADOR_MODEL = "claude-haiku-4-5-20251001"

# ---------------------------------------------------------------------------
# Parser do core.md
# ---------------------------------------------------------------------------

def _extract_yaml_value(block: str, key: str) -> str:
    """Extrai o valor de uma chave YAML simples de um bloco de texto."""
    m = re.search(rf'^{re.escape(key)}:\s*"?([^"\n]+)"?', block, re.MULTILINE)
    return m.group(1).strip().strip('"') if m else ""


def parse_core(core_path: Path) -> dict:
    """
    Extrai do core.md:
      - operacao_principal
      - pergunta_do_capitulo
      - sintese_final
      - secoes: lista de dicts com {idx, tipo_operacao, cabecalho, exemplo_ancola, verificacao}
    """
    src = core_path.read_text(encoding="utf-8")

    # Metadados globais
    meta_m = re.search(r"```yaml\n(.*?)```", src, re.DOTALL)
    meta_block = meta_m.group(1) if meta_m else ""
    operacao_principal = _extract_yaml_value(meta_block, "OPERACAO_PRINCIPAL")
    pergunta = _extract_yaml_value(meta_block, "PERGUNTA_DO_CAPITULO")

    # Síntese final
    sint_m = re.search(r'SINTESE_FINAL:\s*"([^"]+)"', src)
    sintese = sint_m.group(1).strip() if sint_m else ""

    # Seções (blocos ## SEÇÃO N)
    sec_blocks = re.split(r"^## SEÇÃO \d+", src, flags=re.MULTILINE)

    secoes = []
    for i, bloco in enumerate(sec_blocks[1:], start=1):
        yaml_m = re.search(r"```yaml\n(.*?)```", bloco, re.DOTALL)
        if not yaml_m:
            continue
        y = yaml_m.group(1)

        tipo = _extract_yaml_value(y, "TIPO_OPERACAO")
        cabecalho = _extract_yaml_value(y, "CABECALHO")
        exemplo = _extract_yaml_value(y, "EXEMPLO_ANCOLA")
        verificacao = _extract_yaml_value(y, "VERIFICACAO").lower() == "sim"

        # Para "Aplicar agora", também pega campos específicos da operação
        conceito = _extract_yaml_value(y, "CONCEITO_CENTRAL")
        relacao = _extract_yaml_value(y, "RELACAO")
        caso_novo = _extract_yaml_value(y, "CASO_NOVO")

        secoes.append({
            "idx": i,
            "tipo_operacao": tipo,
            "cabecalho": cabecalho,
            "exemplo_ancola": exemplo,
            "verificacao": verificacao,
            "conceito_central": conceito,
            "relacao": relacao,
            "caso_novo": caso_novo,
        })

    return {
        "operacao_principal": operacao_principal,
        "pergunta_do_capitulo": pergunta,
        "sintese_final": sintese,
        "secoes": secoes,
    }


# ---------------------------------------------------------------------------
# Prompt de geração
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """Você é um especialista em elaboração de exercícios para apostilas de Ensino Médio.
Sua tarefa é gerar:
1. Uma pergunta de verificação fechada (múltipla escolha com 3 alternativas) para cada seção indicada.
2. Um mini-exercício "Aplicar agora" para o fechamento do capítulo.

Regras:
- Perguntas de verificação: 1 correta + 2 distratores plausíveis. Breves, diretas.
- "Aplicar agora": apresente um caso concreto novo (diferente dos exemplos do capítulo), peça ao aluno para aplicar a operação cognitiva principal, e forneça a resposta comentada entre tags <resposta> e </resposta> para que o professor possa ocultar no InDesign.
- Linguagem acessível para alunos do Ensino Médio.
- Devolva APENAS o JSON pedido, sem texto antes ou depois.
"""

def _build_prompt(core_data: dict) -> str:
    secoes_elegiveis = [s for s in core_data["secoes"] if s["verificacao"]]

    secoes_json = []
    for s in secoes_elegiveis:
        secoes_json.append({
            "idx": s["idx"],
            "tipo_operacao": s["tipo_operacao"],
            "cabecalho": s["cabecalho"],
            "exemplo_ancola": s["exemplo_ancola"][:300] if s["exemplo_ancola"] else "",
        })

    # Para "Aplicar agora": usa a última seção com a operação principal
    sec_principal = next(
        (s for s in reversed(core_data["secoes"])
         if s["tipo_operacao"] == core_data["operacao_principal"]),
        core_data["secoes"][-1] if core_data["secoes"] else None,
    )
    aplicar_ctx = {}
    if sec_principal:
        aplicar_ctx = {
            "operacao": core_data["operacao_principal"],
            "cabecalho_secao": sec_principal["cabecalho"],
            "exemplo_ancola": sec_principal["exemplo_ancola"][:400] if sec_principal["exemplo_ancola"] else "",
            "relacao": sec_principal.get("relacao", ""),
        }

    return json.dumps({
        "instrucao": (
            "Gere verificações para as seções abaixo e o exercício 'Aplicar agora'. "
            "Retorne APENAS JSON no formato especificado."
        ),
        "formato_resposta": {
            "verificacoes": [
                {
                    "idx_secao": "<igual ao idx recebido>",
                    "pergunta": "<pergunta de múltipla escolha>",
                    "alternativas": {
                        "A": "<alternativa A>",
                        "B": "<alternativa B>",
                        "C": "<alternativa C>"
                    },
                    "correta": "<A, B ou C>",
                    "justificativa": "<uma frase explicando por que é correta>"
                }
            ],
            "aplicar_agora": {
                "enunciado": "<apresentação do caso novo + pergunta ao aluno>",
                "resposta_comentada": "<resposta modelo com explicação — será oculta no InDesign>"
            }
        },
        "secoes": secoes_json,
        "aplicar_agora_contexto": aplicar_ctx,
        "operacao_principal": core_data["operacao_principal"],
        "sintese_final": core_data["sintese_final"][:300] if core_data["sintese_final"] else "",
    }, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Formatação do XML de sidebar
# ---------------------------------------------------------------------------

def _render_verificacao_xml(v: dict) -> str:
    """Converte um dict de verificação em XML de sidebar."""
    from xml.sax.saxutils import escape as xe
    alts = v.get("alternativas", {})
    correta = v.get("correta", "")
    just = v.get("justificativa", "")
    lines = ['<sidebar tipo="verificacao">']
    lines.append(f'  <pergunta>{xe(v.get("pergunta", ""))}</pergunta>')
    lines.append('  <alternativas>')
    for letra in ("A", "B", "C"):
        texto = alts.get(letra, "")
        correto_attr = ' correta="sim"' if letra == correta else ""
        lines.append(f'    <alternativa letra="{letra}"{correto_attr}>{xe(texto)}</alternativa>')
    lines.append('  </alternativas>')
    if just:
        lines.append(f'  <justificativa>{xe(just)}</justificativa>')
    lines.append('</sidebar>')
    return "\n".join(lines)


def _render_aplicar_agora_xml(aa: dict) -> str:
    """Converte o dict 'aplicar_agora' em XML de sidebar."""
    from xml.sax.saxutils import escape as xe
    enunciado = aa.get("enunciado", "")
    resposta = aa.get("resposta_comentada", "")
    lines = ['<sidebar tipo="aplicar-agora">']
    lines.append(f'  <enunciado>{xe(enunciado)}</enunciado>')
    if resposta:
        lines.append(f'  <resposta>{xe(resposta)}</resposta>')
    lines.append('</sidebar>')
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Coleta determinística (sem API) — usada pelo Agente 5 no fluxo de
# verificação externa (ver PLANO-VERIFICACAO-EXTERNA.md)
# ---------------------------------------------------------------------------

def coletar_pontos_verificacao(core_path: Path) -> Tuple[Dict[int, dict], Optional[dict]]:
    """
    Versão determinística (zero chamadas à API) do que `gerar_verificacoes()` fazia.

    Lê o core.md e devolve só os dados mínimos para o Agente 5 marcar, no XML,
    onde a verificação externa deve entrar — sem produzir a verificação em si.

    Retorna:
      - pontos: dict {idx_secao: {"tipo_operacao", "cabecalho",
        "conceito_central", "exemplo_ancola"}} para cada seção com
        VERIFICACAO: Sim. Contexto completo para guiar os agentes externos
        (ver decisão "granularidade" do PLANO-VERIFICACAO-EXTERNA.md).
      - aplicar_agora_ctx: dict {"operacao_principal", "pergunta_do_capitulo",
        "sintese_final", "exemplo_ancola_principal"}, ou None se não houver
        nenhuma seção elegível no capítulo (mesmo critério que
        `gerar_verificacoes()` já usava).
    """
    try:
        core_data = parse_core(core_path)
    except Exception as e:
        logger.error("[Verificador] Falha ao parsear core %s: %s", core_path, e)
        return {}, None

    pontos: Dict[int, dict] = {
        s["idx"]: {
            "tipo_operacao": s["tipo_operacao"],
            "cabecalho": s["cabecalho"],
            "conceito_central": s["conceito_central"],
            "exemplo_ancola": s["exemplo_ancola"],
        }
        for s in core_data["secoes"] if s["verificacao"]
    }
    if not pontos:
        logger.info("[Verificador] Nenhuma seção elegível em %s", core_path.name)
        return {}, None

    # Seção principal (para o "Aplicar agora"): mesma heurística do _build_prompt —
    # última seção cuja operação == operação principal do capítulo; fallback: última.
    sec_principal = next(
        (s for s in reversed(core_data["secoes"])
         if s["tipo_operacao"] == core_data["operacao_principal"]),
        core_data["secoes"][-1] if core_data["secoes"] else None,
    )
    aplicar_agora_ctx = {
        "operacao_principal": core_data["operacao_principal"],
        "pergunta_do_capitulo": core_data["pergunta_do_capitulo"],
        "sintese_final": core_data["sintese_final"],
        "exemplo_ancola_principal": sec_principal["exemplo_ancola"] if sec_principal else "",
    }
    return pontos, aplicar_agora_ctx


# ---------------------------------------------------------------------------
# API pública (gerador via Haiku — mantido por ora; ver Fase 5 do plano)
# ---------------------------------------------------------------------------

def gerar_verificacoes(
    core_path: Path,
    client: anthropic.Anthropic,
    model: str = VERIFICADOR_MODEL,
) -> Tuple[Dict[int, str], Optional[str]]:
    """
    Gera verificações fechadas e "Aplicar agora" para um capítulo.

    Retorna:
      - verificacoes: dict {idx_secao: xml_sidebar_verificacao}
      - aplicar_agora: xml_sidebar ou None
    """
    try:
        core_data = parse_core(core_path)
    except Exception as e:
        logger.error("[Verificador] Falha ao parsear core %s: %s", core_path, e)
        return {}, None

    secoes_elegiveis = [s for s in core_data["secoes"] if s["verificacao"]]
    if not secoes_elegiveis:
        logger.info("[Verificador] Nenhuma seção elegível em %s", core_path.name)
        return {}, None

    prompt = _build_prompt(core_data)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
    except Exception as e:
        logger.error("[Verificador] Erro na API: %s", e)
        return {}, None

    # Extrai JSON da resposta
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start == -1 or end == 0:
        logger.warning("[Verificador] Resposta sem JSON válido")
        return {}, None

    try:
        data = json.loads(raw[start:end])
    except json.JSONDecodeError as e:
        logger.warning("[Verificador] JSON inválido: %s", e)
        return {}, None

    # Monta verificacoes por idx de seção
    verificacoes: Dict[int, str] = {}
    for v in data.get("verificacoes", []):
        idx = v.get("idx_secao")
        if idx is not None:
            verificacoes[int(idx)] = _render_verificacao_xml(v)

    # Monta aplicar_agora
    aplicar_agora: Optional[str] = None
    aa = data.get("aplicar_agora")
    if aa and aa.get("enunciado"):
        aplicar_agora = _render_aplicar_agora_xml(aa)

    logger.info(
        "[Verificador] %d verificação(ões) gerada(s), aplicar_agora=%s",
        len(verificacoes), "sim" if aplicar_agora else "não",
    )
    return verificacoes, aplicar_agora
