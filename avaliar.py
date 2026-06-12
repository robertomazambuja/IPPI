#!/usr/bin/env python3
"""
avaliar.py — Rubrica de qualidade didática (LLM-judge)

Avalia capítulos gerados pelo pipeline IPPI com base em 6 critérios objetivos.
Grava os resultados em logs/qualidade_YYYYMMDD.csv para série histórica.

Uso:
    # Avaliar um capítulo específico (texto.md + core.md deduzido automaticamente)
    python avaliar.py output/apostila-historia-em1/texto/unidade-1.../01-01-cap.md

    # Fornecer core explicitamente
    python avaliar.py output/.../texto/.../01-01-cap.md --core output/.../core/.../01-01-cap.md

    # Avaliar todos os capítulos de uma apostila
    python avaliar.py --apostila apostila-teste-historia-em1

    # Usar modelo diferente
    python avaliar.py --apostila apostila-X --modelo claude-sonnet-4-6
"""

import anthropic
import argparse
import csv
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).parent
LOG_DIR  = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY não configurada em .env")

DEFAULT_MODEL = os.environ.get("IPPI_AVALIADOR_MODEL", "claude-haiku-4-5-20251001")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rubrica — 6 critérios
# ---------------------------------------------------------------------------

CRITERIOS = [
    {
        "id": "operacao_executada",
        "nome": "Operação cognitiva executada",
        "descricao": (
            "A operação prescrita (Definir, Classificar, Comparar, etc.) é de fato "
            "EXECUTADA no texto — não apenas nomeada ou descrita. O aluno vê a operação "
            "acontecer sobre o objeto conceitual."
        ),
    },
    {
        "id": "exemplo_ancora_especifico",
        "nome": "Exemplo âncora específico",
        "descricao": (
            "Cada seção principal contém um exemplo âncora com pelo menos dois elementos "
            "concretos: dado quantitativo, nome próprio, data, local ou evento específico. "
            "Exemplos genéricos ('um país europeu', 'certa época') reprovam."
        ),
    },
    {
        "id": "sintese_responde_pergunta",
        "nome": "Síntese responde à pergunta",
        "descricao": (
            "A SÍNTESE FINAL responde literalmente à PERGUNTA DO CAPÍTULO definida no core. "
            "Deve haver correspondência direta de vocabulário e argumento — não só de tema."
        ),
    },
    {
        "id": "proibicoes_estilo",
        "nome": "Proibições de estilo respeitadas",
        "descricao": (
            "Nenhuma das seguintes proibições foi violada no texto corrido: "
            "(1) travessão (—) no meio de frase, "
            "(2) exclamações (!), "
            "(3) 'nós', 'a gente', 'nosso', "
            "(4) conectores vazios ('além disso', 'é importante ressaltar', 'cabe destacar'), "
            "(5) adjetivos avaliativos ('o maior', 'brilhante', 'fascinante')."
        ),
    },
    {
        "id": "marcacao_preservada",
        "nome": "Marcação estrutural preservada",
        "descricao": (
            "Os HTML comments (<!-- [TIPO: ...] --> e <!-- [/TIPO] -->) estão presentes, "
            "bem formados e não têm conteúdo de prosa dentro deles. "
            "Nenhum rótulo visível do tipo [DEFINIÇÃO] ou [EXEMPLO] aparece no texto corrido."
        ),
    },
    {
        "id": "fluidez_prosa",
        "nome": "Fluidez da prosa",
        "descricao": (
            "A transição entre blocos é natural — sem saltos abruptos nem frases-template "
            "('O primeiro aspecto é...', 'Em relação ao segundo ponto...'). "
            "Os parágrafos do mesmo bloco se encadeiam com clareza."
        ),
    },
]

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

_SYSTEM = """Você é um avaliador especialista em materiais didáticos para o Ensino Médio brasileiro.
Sua tarefa é avaliar um capítulo de apostila segundo critérios objetivos.
Devolva APENAS um objeto JSON — sem texto antes ou depois."""


def _build_prompt(texto: str, pergunta_capitulo: str, operacao_principal: str,
                  sintese_core: str) -> str:
    criterios_json = [
        {"id": c["id"], "nome": c["nome"], "descricao": c["descricao"]}
        for c in CRITERIOS
    ]

    return json.dumps({
        "instrucao": (
            "Avalie o capítulo abaixo segundo os 6 critérios. "
            "Para cada critério devolva: nota (0-10), aprovado (true/false, limiar=6), "
            "evidencia (trecho do texto que justifica a nota — máx 80 chars), "
            "comentario (uma frase explicativa)."
        ),
        "metadados_do_capitulo": {
            "pergunta_do_capitulo": pergunta_capitulo,
            "operacao_principal": operacao_principal,
            "sintese_final_do_core": sintese_core[:300],
        },
        "criterios": criterios_json,
        "formato_resposta": {
            "capitulo": "<nome do arquivo avaliado>",
            "nota_geral": "<média das notas, 0-10>",
            "aprovado_geral": "<true se todos os critérios aprovados>",
            "criterios": [
                {
                    "id": "<id do critério>",
                    "nota": "<0-10>",
                    "aprovado": "<true/false>",
                    "evidencia": "<trecho do texto>",
                    "comentario": "<uma frase>"
                }
            ]
        },
        "texto_do_capitulo": texto[:6000],  # limita para caber no contexto
    }, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Parser do core (extrai metadados para o prompt)
# ---------------------------------------------------------------------------

def _extrair_meta_core(core_path: Optional[Path]) -> dict:
    if not core_path or not core_path.exists():
        return {"pergunta": "", "operacao": "", "sintese": ""}
    src = core_path.read_text(encoding="utf-8")
    def _val(key):
        m = re.search(rf'^{re.escape(key)}:\s*"?([^"\n]+)"?', src, re.MULTILINE)
        return m.group(1).strip().strip('"') if m else ""
    sint_m = re.search(r'SINTESE_FINAL:\s*"([^"]+)"', src)
    return {
        "pergunta":  _val("PERGUNTA_DO_CAPITULO"),
        "operacao":  _val("OPERACAO_PRINCIPAL"),
        "sintese":   sint_m.group(1).strip() if sint_m else "",
    }


# ---------------------------------------------------------------------------
# Avaliação de um capítulo
# ---------------------------------------------------------------------------

def avaliar_capitulo(
    texto_path: Path,
    core_path: Optional[Path],
    client: anthropic.Anthropic,
    model: str = DEFAULT_MODEL,
) -> Optional[dict]:
    """
    Avalia um capítulo e retorna o dict de resultados.
    Retorna None em caso de erro.
    """
    if not texto_path.exists():
        logger.error("Arquivo não encontrado: %s", texto_path)
        return None

    texto = texto_path.read_text(encoding="utf-8")
    meta  = _extrair_meta_core(core_path)
    prompt = _build_prompt(texto, meta["pergunta"], meta["operacao"], meta["sintese"])

    try:
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            system=_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
    except Exception as e:
        logger.error("Erro na API: %s", e)
        return None

    start = raw.find("{")
    end   = raw.rfind("}") + 1
    if start == -1 or end == 0:
        logger.warning("Resposta sem JSON válido para %s", texto_path.name)
        return None

    try:
        data = json.loads(raw[start:end])
    except json.JSONDecodeError as e:
        logger.warning("JSON inválido: %s", e)
        return None

    data["_arquivo"]  = texto_path.name
    data["_apostila"] = texto_path.parts[-4] if len(texto_path.parts) >= 4 else ""
    data["_modelo"]   = model
    data["_timestamp"] = datetime.now().isoformat(timespec="seconds")
    return data


# ---------------------------------------------------------------------------
# Gravação no CSV histórico
# ---------------------------------------------------------------------------

def _gravar_csv(resultado: dict, csv_path: Path):
    """Grava uma linha de resultado no CSV histórico."""
    file_exists = csv_path.exists()
    fieldnames = [
        "timestamp", "apostila", "capitulo", "modelo",
        "nota_geral", "aprovado_geral",
    ] + [f"{c['id']}_nota" for c in CRITERIOS] + [f"{c['id']}_ok" for c in CRITERIOS]

    row = {
        "timestamp":      resultado.get("_timestamp", ""),
        "apostila":       resultado.get("_apostila", ""),
        "capitulo":       resultado.get("_arquivo", ""),
        "modelo":         resultado.get("_modelo", ""),
        "nota_geral":     resultado.get("nota_geral", ""),
        "aprovado_geral": resultado.get("aprovado_geral", ""),
    }
    for item in resultado.get("criterios", []):
        cid = item.get("id", "")
        row[f"{cid}_nota"] = item.get("nota", "")
        row[f"{cid}_ok"]   = item.get("aprovado", "")

    with open(csv_path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def _imprimir_resultado(resultado: dict):
    """Exibe o resultado de forma legível no terminal."""
    nome = resultado.get("_arquivo", "?")
    nota = resultado.get("nota_geral", "?")
    aprovado = resultado.get("aprovado_geral", False)
    status = "✓ APROVADO" if aprovado else "✗ REPROVADO"
    print(f"\n{'─' * 60}")
    print(f"{nome}")
    print(f"Nota geral: {nota}/10  {status}")
    print(f"{'─' * 60}")
    for item in resultado.get("criterios", []):
        icon = "✓" if item.get("aprovado") else "✗"
        cid = item.get("id", "")
        nome_c = next((c["nome"] for c in CRITERIOS if c["id"] == cid), cid)
        nota_c = item.get("nota", "?")
        coment = item.get("comentario", "")
        print(f"  {icon} [{nota_c:>2}/10] {nome_c}")
        if coment:
            print(f"           {coment}")


# ---------------------------------------------------------------------------
# Deduzir core_path a partir de texto_path
# ---------------------------------------------------------------------------

def _deduzir_core(texto_path: Path) -> Optional[Path]:
    """
    texto: output/apostila-X/texto/unidade-Y/arquivo.md
    core:  output/apostila-X/core/unidade-Y/arquivo.md
    """
    try:
        partes = list(texto_path.parts)
        idx_texto = next(i for i, p in enumerate(partes) if p == "texto")
        partes[idx_texto] = "core"
        return Path(*partes)
    except (StopIteration, Exception):
        return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Avalia capítulos do pipeline IPPI com rubrica de 6 critérios.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "texto",
        nargs="?",
        type=Path,
        default=None,
        help="Caminho para o texto.md a avaliar.",
    )
    parser.add_argument(
        "--core",
        type=Path,
        default=None,
        help="Caminho para o core.md correspondente (deduzido automaticamente se omitido).",
    )
    parser.add_argument(
        "--apostila",
        type=str,
        default=None,
        help="Avaliar todos os capítulos de uma apostila (ex: apostila-teste-historia-em1).",
    )
    parser.add_argument(
        "--modelo",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Modelo LLM a usar (padrão: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--saida",
        type=Path,
        default=None,
        help="Caminho do CSV de saída (padrão: logs/qualidade_YYYYMMDD.csv).",
    )

    args = parser.parse_args()

    if not args.texto and not args.apostila:
        parser.print_help()
        sys.exit(1)

    client  = anthropic.Anthropic(api_key=API_KEY)
    csv_out = args.saida or (LOG_DIR / f"qualidade_{datetime.now().strftime('%Y%m%d')}.csv")

    # Coleta arquivos a avaliar
    textos: list[tuple[Path, Optional[Path]]] = []

    if args.apostila:
        pasta_texto = BASE_DIR / "output" / args.apostila / "texto"
        if not pasta_texto.exists():
            logger.error("Pasta não encontrada: %s", pasta_texto)
            sys.exit(1)
        for md in sorted(pasta_texto.rglob("*.md")):
            core = _deduzir_core(md)
            textos.append((md, core))
    else:
        texto_path = args.texto if args.texto.is_absolute() else BASE_DIR / args.texto
        core_path  = args.core
        if core_path is None:
            core_path = _deduzir_core(texto_path)
        textos.append((texto_path, core_path))

    logger.info("Avaliando %d capítulo(s) com modelo %s", len(textos), args.modelo)

    reprovados = 0
    for texto_path, core_path in textos:
        resultado = avaliar_capitulo(texto_path, core_path, client, args.modelo)
        if resultado is None:
            logger.warning("Avaliação falhou para %s", texto_path.name)
            continue
        _gravar_csv(resultado, csv_out)
        _imprimir_resultado(resultado)
        if not resultado.get("aprovado_geral"):
            reprovados += 1

    print(f"\n{'═' * 60}")
    print(f"Avaliados : {len(textos)} capítulo(s)")
    print(f"Reprovados: {reprovados}")
    print(f"CSV gravado em: {csv_out}")
    print(f"{'═' * 60}\n")


if __name__ == "__main__":
    main()
