#!/usr/bin/env python3
"""
Pipeline de geração de apostilas didáticas — VERSÃO 5 (FUNCIONAL + NORMALIZAÇÃO + ESTILO + FORMATO)

Combina:
- Loop agêntico com tools (read_file, write_file)
- Cache ephemeral para reduzir custo de tokens
- Streaming para respostas longas
- Retry com backoff exponencial para erros transitórios
- 6 agentes: Decompositor → Arquiteto → Redator Funcional → Normalizador → Redator de Estilo → Formatador
- Validação rigorosa de CSV
- Logging estruturado com arquivo

Ordem de execução padrão (modo manual):  1 → 2 → 3 → 4 → 5
Modo briefing (com Agente 0):            0 → 1 → 2 → 3 → 4 → 5

Uso:
    # Modo briefing: Agente 0 gera o CSV, depois roda 1-5
    python pipeline.py --briefing input/apostila-sociologia/briefing.json --apostila apostila-sociologia

    # Modo briefing: só gera o CSV (Agente 0)
    python pipeline.py --briefing input/apostila-sociologia/briefing.json --apostila apostila-sociologia --agentes 0

    # Modo manual: professor já tem o CSV
    python pipeline.py input/apostila-historia-midia/instrucoes.csv
    python pipeline.py input/apostila-historia-midia/instrucoes.csv --agentes 1,2
    python pipeline.py input/apostila-historia-midia/instrucoes.csv --force
    python pipeline.py input/apostila-historia-midia/instrucoes.csv --cap 1
"""

import anthropic
import argparse
import csv
import httpx
import logging
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from normalizador import normalizar_texto
from formatador import formatar_capitulo
from verificador import coletar_pontos_verificacao

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

BASE_DIR = Path(__file__).parent
MAX_TOKENS = int(os.environ.get("IPPI_MAX_TOKENS", "32000"))
AGENTE_MAX_ITERATIONS = int(os.environ.get("IPPI_MAX_ITERATIONS", "30"))

# Modelos por agente — sobrescrevíveis via env var (ex: IPPI_MODEL_A1=claude-opus-4-6)
_DEFAULT_MODELS = {
    0: "claude-sonnet-4-6",   # Decompositor: tarefa estruturada, Sonnet suficiente
    1: "claude-opus-4-6",     # Arquiteto: decisões pedagógicas — Opus paga seu preço
    2: "claude-opus-4-6",     # Redator: qualidade da prosa é o produto
    3: None,                  # Normalizador: código Python, sem LLM
    4: "claude-sonnet-4-6",   # Polidor: reescrita local, sem criação de conteúdo
    5: None,                  # Formatador: código Python, sem LLM
}
AGENT_MODELS: dict = {
    agente: os.environ.get(f"IPPI_MODEL_A{agente}", modelo)
    for agente, modelo in _DEFAULT_MODELS.items()
}
# Fallback global para agentes não mapeados
_FALLBACK_MODEL = os.environ.get("IPPI_MODEL", "claude-sonnet-4-6")

# Diretórios
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Logging
_RUN_TS = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_FILE = LOG_DIR / f"pipeline_{_RUN_TS}.log"
USAGE_CSV = LOG_DIR / f"usage_{_RUN_TS}.csv"
_USAGE_CSV_LOCK = threading.Lock()   # protege escrita concorrente no CSV de usage
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load .env
load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY não configurada em .env")

# ============================================================================
# UTILIDADES
# ============================================================================

def slugify(text: str) -> str:
    """Converte texto em slug para nomes de arquivo (com acentos)."""
    replacements = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
        'é': 'e', 'ê': 'e', 'ë': 'e', 'í': 'i', 'î': 'i',
        'ó': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o', 'ú': 'u',
        'û': 'u', 'ü': 'u', 'ç': 'c', 'ñ': 'n',
    }
    text = text.lower().strip()
    for char, rep in replacements.items():
        text = text.replace(char, rep)
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def capitulo_filename(unidade_idx: int, capitulo_idx: int, capitulo: str) -> str:
    """Gera nome de arquivo: 01-02-nome-do-capitulo.md"""
    return f"{unidade_idx:02d}-{capitulo_idx:02d}-{slugify(capitulo)}.md"

def read_file_safe(path: Path) -> str:
    """Lê um arquivo ou retorna mensagem de erro clara."""
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"ERRO: Arquivo não encontrado: {path}"
    except Exception as e:
        return f"ERRO ao ler {path}: {e}"

def log_print(msg: str, indent: int = 0):
    """Imprime com indentação opcional."""
    prefix = "  " * indent
    logger.info(f"{prefix}{msg}")

def extract_habilidade(matrix_path: Path, codigo: str) -> str:
    """Extrai a entrada de uma habilidade de uma matriz JSON e retorna como string JSON.
    Retorna mensagem de erro clara se a chave não for encontrada."""
    try:
        with open(matrix_path, encoding="utf-8") as f:
            import json as _json
            data = _json.load(f)
        habilidades = data.get("habilidades", {})
        entry = habilidades.get(codigo)
        if entry is None:
            return f"ERRO: habilidade '{codigo}' não encontrada em {matrix_path.name}"
        return _json.dumps(entry, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"ERRO ao ler {matrix_path.name}: {e}"

def extract_core_summary(core_path: Path, cap_idx: int, cap_name: str) -> str:
    """Extrai SINTESE_FINAL, ENCADEAMENTO e autores de um core.md (sem LLM).

    Retorna bloco compacto para injetar no user_message do A1, substituindo
    a leitura do core completo via read_file (E9).
    Nunca levanta exceção — fallback legível em caso de erro.
    """
    try:
        content = core_path.read_text(encoding="utf-8")
    except Exception as e:
        return f"--- Cap. {cap_idx}: {cap_name} ---\n[SUMÁRIO INDISPONÍVEL — erro ao ler: {e}]\n"

    m = re.search(r'SINTESE_FINAL:\s*"(.*?)"', content, re.DOTALL)
    if not m:
        m = re.search(r'SINTESE_FINAL:\s*([^\n]+)', content)
    sintese = m.group(1).strip() if m else "(não encontrado)"

    m = re.search(r'ENCADEAMENTO:\s*"(.*?)"', content, re.DOTALL)
    if not m:
        m = re.search(r'ENCADEAMENTO:\s*([^\n]+)', content)
    encadeamento = m.group(1).strip() if m else "(não encontrado)"

    autores: list = []
    for m in re.finditer(r'^AUTOR(?:_SECUNDARIO)?:\s*"?([^"\n]+)"?\s*$', content, re.MULTILINE):
        valor = m.group(1).strip()
        if valor.lower() == "vazio":
            continue
        nome = valor.split("(")[0].strip()
        if nome and nome not in autores:
            autores.append(nome)

    autores_str = ", ".join(autores) if autores else "(nenhum)"
    return (
        f"--- Cap. {cap_idx}: {cap_name} ---\n"
        f"SÍNTESE: {sintese}\n"
        f"ENCADEAMENTO: {encadeamento}\n"
        f"AUTORES USADOS: {autores_str}\n"
    )


def _with_cache(messages: list) -> list:
    """Retorna cópia de messages com cache_control:ephemeral no último bloco user (E6).

    Marca o último item 'user' para prompt caching sem modificar o objeto original.
    Trata string simples (user_message) e lista de blocos (tool_results).
    A API exige ~1.024 tokens mínimos; blocos menores são ignorados sem erro.
    """
    import copy as _copy
    result = _copy.deepcopy(messages)
    last_user_idx = None
    for i in range(len(result) - 1, -1, -1):
        if result[i].get("role") == "user":
            last_user_idx = i
            break
    if last_user_idx is None:
        return result
    msg = result[last_user_idx]
    content = msg["content"]
    if isinstance(content, str):
        msg["content"] = [
            {"type": "text", "text": content, "cache_control": {"type": "ephemeral"}}
        ]
    elif isinstance(content, list) and content:
        content[-1] = {**content[-1], "cache_control": {"type": "ephemeral"}}
    return result


def _write_usage_csv(row: dict):
    """Grava uma linha no CSV de usage (thread-safe)."""
    import csv as _csv
    with _USAGE_CSV_LOCK:
        file_exists = USAGE_CSV.exists()
        with open(USAGE_CSV, "a", encoding="utf-8", newline="") as f:
            writer = _csv.DictWriter(f, fieldnames=[
                "timestamp", "apostila", "agente", "capitulo",
                "iteracoes", "input_tokens", "output_tokens",
                "cache_creation_tokens", "cache_read_tokens",
            ])
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

# ============================================================================
# FERRAMENTAS DOS AGENTES
# ============================================================================

TOOLS = [
    {
        "name": "read_file",
        "description": "Lê o conteúdo de um arquivo do projeto.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Caminho do arquivo relativo à raiz do projeto."
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": (
            "Salva conteúdo em um arquivo, criando os diretórios necessários. "
            "Use para salvar o output final da sua tarefa."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Caminho do arquivo relativo à raiz do projeto."
                },
                "content": {
                    "type": "string",
                    "description": "Conteúdo completo a salvar."
                }
            },
            "required": ["path", "content"]
        }
    }
]

def _validate_path(path: Path) -> Optional[str]:
    """Retorna mensagem de erro se o path escapar do BASE_DIR, None se seguro."""
    try:
        resolved = path.resolve()
        if not str(resolved).startswith(str(BASE_DIR.resolve())):
            return f"ERRO: acesso negado — caminho fora do projeto: {path}"
    except Exception as e:
        return f"ERRO: caminho inválido: {e}"
    return None


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Executa uma ferramenta e retorna o resultado como string."""

    if tool_name == "read_file":
        path = BASE_DIR / tool_input["path"]
        err = _validate_path(path)
        if err:
            log_print(f"⚠  {err}", indent=2)
            return err
        result = read_file_safe(path)
        if result.startswith("ERRO:"):
            log_print(f"⚠  {result}", indent=2)
        return result

    if tool_name == "write_file":
        path = BASE_DIR / tool_input["path"]
        err = _validate_path(path)
        if err:
            log_print(f"⚠  {err}", indent=2)
            return err
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(tool_input["content"], encoding="utf-8")
            log_print(f"✓  Salvo: {tool_input['path']}", indent=2)
            return f"Arquivo salvo: {tool_input['path']}"
        except OSError as e:
            msg = f"ERRO ao salvar {tool_input['path']}: {e}"
            log_print(f"⚠  {msg}", indent=2)
            return msg

    return f"Ferramenta desconhecida: {tool_name}"

# ============================================================================
# LOOP AGÊNTICO
# ============================================================================

def run_agent(
    client: anthropic.Anthropic,
    system_prompt: str,
    user_message: str,
    agent_name: str,
    max_iterations: int = AGENTE_MAX_ITERATIONS,
    chapter_label: str = "",
    apostila_label: str = "",
    model: str = _FALLBACK_MODEL,
) -> Optional[str]:
    """
    Executa um agente em loop até end_turn ou limite de iterações.
    Retorna o texto final da resposta (pode ser vazio se o agente salvou tudo via write_file).
    """
    messages = [{"role": "user", "content": user_message}]
    iteration = 0
    usage_total = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_creation_tokens": 0,
        "cache_read_tokens": 0,
    }

    while iteration < max_iterations:
        iteration += 1

        # Retry com backoff exponencial apenas em erros transitórios
        for attempt in range(4):
            try:
                with client.messages.stream(
                    model=model,
                    max_tokens=MAX_TOKENS,
                    system=[
                        {
                            "type": "text",
                            "text": system_prompt,
                            "cache_control": {"type": "ephemeral"},
                        }
                    ],
                    tools=TOOLS,
                    messages=_with_cache(messages),
                ) as stream:
                    response = stream.get_final_message()
                break
            except (
                anthropic.InternalServerError,
                anthropic.APITimeoutError,
                anthropic.APIConnectionError,
                anthropic.RateLimitError,
                httpx.ReadError,
                httpx.RemoteProtocolError,
            ) as e:
                if attempt == 3:
                    raise
                wait = 10 * (attempt + 1)
                log_print(f"⚠  Erro transitório — aguardando {wait}s antes de tentar novamente...", indent=2)
                time.sleep(wait)

        # Acumula usage desta iteração
        if response.usage:
            usage_total["input_tokens"]        += getattr(response.usage, "input_tokens", 0)
            usage_total["output_tokens"]       += getattr(response.usage, "output_tokens", 0)
            usage_total["cache_creation_tokens"] += getattr(response.usage, "cache_creation_input_tokens", 0)
            usage_total["cache_read_tokens"]   += getattr(response.usage, "cache_read_input_tokens", 0)

        # Registra resposta no histórico
        messages.append({"role": "assistant", "content": response.content})

        # Coleta texto da resposta
        text_blocks = [b.text for b in response.content if hasattr(b, "text")]
        final_text = "\n".join(text_blocks).strip()

        # Agente terminou
        if response.stop_reason == "end_turn":
            log_print(
                f"✓  {agent_name} concluiu ({iteration} iteração(ões)) | "
                f"in={usage_total['input_tokens']} out={usage_total['output_tokens']} "
                f"cache_create={usage_total['cache_creation_tokens']} cache_read={usage_total['cache_read_tokens']}",
                indent=1,
            )
            _write_usage_csv({
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "apostila": apostila_label,
                "agente": agent_name,
                "capitulo": chapter_label,
                "iteracoes": iteration,
                **{k: usage_total[k] for k in ("input_tokens", "output_tokens", "cache_creation_tokens", "cache_read_tokens")},
            })
            return final_text

        # Uso de ferramentas — executa e continua o loop
        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    preview = block.input.get("path", "")
                    if not preview:
                        content_preview = block.input.get("content", "")[:50]
                        preview = f"(conteúdo) {content_preview}..."
                    log_print(f"→  {block.name}: {preview}", indent=2)
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})
            continue

        # Parada inesperada
        log_print(f"⚠  {agent_name} parou: {response.stop_reason}", indent=1)
        _write_usage_csv({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "apostila": apostila_label,
            "agente": agent_name,
            "capitulo": chapter_label,
            "iteracoes": iteration,
            **{k: usage_total[k] for k in ("input_tokens", "output_tokens", "cache_creation_tokens", "cache_read_tokens")},
        })
        return final_text

    log_print(f"⚠  {agent_name} atingiu limite de iterações ({max_iterations})", indent=1)
    _write_usage_csv({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "apostila": apostila_label,
        "agente": agent_name,
        "capitulo": chapter_label,
        "iteracoes": iteration,
        **{k: usage_total[k] for k in ("input_tokens", "output_tokens", "cache_creation_tokens", "cache_read_tokens")},
    })
    return None

# ============================================================================
# BUILDER DE SYSTEM PROMPT
# ============================================================================

def build_system_prompt(orientation_file: str, skill_file: str) -> str:
    """Combina orientação e skill num único system prompt."""
    orientation = read_file_safe(BASE_DIR / "orientacoes" / orientation_file)
    skill = read_file_safe(BASE_DIR / "skills" / skill_file)
    return f"{orientation}\n\n---\n\n{skill}"

# ============================================================================
# AGENTES INDIVIDUAIS
# ============================================================================

# Cabeçalho canônico do instrucoes.csv (19 colunas) — fonte única da ordem.
CSV_HEADER = [
    'disciplina', 'unidade', 'pergunta_unidade', 'capitulo', 'habilidade',
    'micro_hab_1', 'operacao_secao_1',
    'micro_hab_2', 'operacao_secao_2',
    'micro_hab_3', 'operacao_secao_3',
    'micro_hab_4', 'operacao_secao_4',
    'micro_hab_5', 'operacao_secao_5',
    'micro_hab_6', 'operacao_secao_6',
    'autores', 'conteudos_nucleares',
]

_OPERACOES_VALIDAS = {
    'Definir', 'Classificar', 'Comparar', 'Sequenciar',
    'Mapear causalidade', 'Reconhecer perspectiva', 'Aplicar',
}


def serialize_instrucoes(
    instrucoes_json: dict,
    briefing_data: dict,
    habilidade_entry: str,
    codigo_hab: str,
    csv_path: Path,
) -> None:
    """Serializa o JSON do Decompositor em instrucoes.csv de forma determinística.

    O agente fornece apenas a parte gerativa (capítulo + seções com micro_hab/operacao).
    Os campos de contexto (disciplina, unidade, pergunta, enunciado da habilidade,
    autores, conteudos) vêm do briefing e da matriz — fonte de verdade — e nunca do
    agente. csv.writer com QUOTE_MINIMAL garante quoting correto de qualquer vírgula.
    """
    import json as _json

    # Enunciado vem da matriz (não do agente) — blinda contra divergência/alucinação.
    enunciado = ""
    try:
        entry = _json.loads(habilidade_entry)
        enunciado = (entry.get("enunciado") or "").strip()
    except Exception:
        enunciado = ""
    habilidade_str = f"{codigo_hab} — {enunciado}" if enunciado else codigo_hab

    disciplina = (briefing_data.get("disciplina") or "").strip()
    unidade = (briefing_data.get("unidade") or "").strip()
    pergunta = (briefing_data.get("pergunta_unidade") or "").strip()
    capitulos = briefing_data.get("capitulos") or []
    autores_map = briefing_data.get("autores_por_capitulo") or {}
    conteudos_map = briefing_data.get("conteudos_por_capitulo") or {}

    # Indexa as entradas do agente por nome de capítulo (com fallback posicional).
    raw_caps = instrucoes_json.get("capitulos") if isinstance(instrucoes_json, dict) else instrucoes_json
    if not isinstance(raw_caps, list) or not raw_caps:
        raise ValueError("instrucoes.json não contém uma lista 'capitulos' não-vazia.")
    by_name = {}
    for c in raw_caps:
        nome = (c.get("capitulo") or "").strip()
        if nome:
            by_name[nome] = c

    rows = []
    for idx, cap_nome in enumerate(capitulos):
        cap_nome = cap_nome.strip()
        cap = by_name.get(cap_nome)
        if cap is None:
            # fallback posicional, caso o agente tenha variado a grafia
            cap = raw_caps[idx] if idx < len(raw_caps) else None
        if cap is None:
            raise ValueError(f"Decompositor não gerou seções para o capítulo: {cap_nome!r}")

        secoes = cap.get("secoes") or []
        if not (4 <= len(secoes) <= 6):
            raise ValueError(
                f"Capítulo {cap_nome!r}: esperado 4–6 seções, recebido {len(secoes)}."
            )

        micro_ops = []
        for s in secoes:
            mh = (s.get("micro_hab") or "").strip()
            op = (s.get("operacao") or "").strip()
            if not mh:
                raise ValueError(f"Capítulo {cap_nome!r}: micro_hab vazia.")
            if op not in _OPERACOES_VALIDAS:
                raise ValueError(
                    f"Capítulo {cap_nome!r}: operação inválida {op!r}. "
                    f"Válidas: {', '.join(sorted(_OPERACOES_VALIDAS))}."
                )
            micro_ops.append((mh, op))

        # Preenche os 6 pares de slots (vazios quando não usados).
        slots = []
        for i in range(6):
            if i < len(micro_ops):
                slots.extend(micro_ops[i])
            else:
                slots.extend(["", ""])

        autores_str = "; ".join(autores_map.get(cap_nome, []))
        conteudos_str = "; ".join(conteudos_map.get(cap_nome, []))

        row = [disciplina, unidade, pergunta, cap_nome, habilidade_str] + slots + [autores_str, conteudos_str]
        rows.append(row)

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(CSV_HEADER)
        writer.writerows(rows)


def run_agente0(
    client: anthropic.Anthropic,
    briefing_path: Path,
    apostila_name: str,
) -> Optional[Path]:
    """Agente 0 — Decompositor. Produz instrucoes.json e serializa instrucoes.csv."""
    import json as _json

    output_json_rel = f"input/{apostila_name}/instrucoes.json"
    output_csv_rel = f"input/{apostila_name}/instrucoes.csv"

    system = build_system_prompt("decompositor-orientacao.md", "decompositor-skill.md")

    # Extrair habilidade do briefing e fatiar a matriz — injeta só a entrada relevante
    habilidade_entry = ""
    briefing_data = {}
    codigo_hab = ""
    try:
        with open(briefing_path, encoding="utf-8") as _f:
            briefing_data = _json.load(_f)
        codigo_hab = briefing_data.get("habilidade_bncc", "")
        if codigo_hab:
            habilidade_entry = extract_habilidade(BASE_DIR / "contexto" / "matriz-bncc.json", codigo_hab)
    except Exception as _e:
        habilidade_entry = f"ERRO ao pré-extrair habilidade do briefing: {_e}"

    # Lê o briefing para injetar o conteúdo diretamente
    briefing_content = read_file_safe(briefing_path)

    user_message = f"""Sua tarefa: transformar o briefing do professor em instrucoes.json válido.

CONTEÚDO DO BRIEFING:
{briefing_content}

ENTRADA DA HABILIDADE (de matriz-bncc.json — extraia sequencia_pedagogica, operacao_predominante e foco_cognitivo daqui):
{habilidade_entry}

ONDE SALVAR O OUTPUT:
{output_json_rel}

Siga os passos da sua skill:
1. Use o briefing e a entrada da habilidade acima (não é necessário ler os arquivos — o conteúdo já está aqui)
2. Para cada capítulo: use a sequencia_pedagogica como template de operações e escreva micro-habilidades no formato (operação + objeto conceitual do capítulo) — sem nomear autores ou fontes específicas
3. Monte o JSON no formato da skill (apenas capitulo + secoes[].micro_hab/operacao) — NÃO escreva CSV, NÃO copie enunciado, autores ou conteúdos (o pipeline preenche isso a partir do briefing e da matriz)
4. Valide (checklist da skill) e salve o JSON em {output_json_rel}
"""

    log_print(f"\n[Agente 0] Decompositor — gerando {output_json_rel}")
    run_agent(client, system, user_message, "Agente 0",
              chapter_label="briefing", apostila_label=apostila_name,
              model=AGENT_MODELS.get(0, _FALLBACK_MODEL))

    json_path = BASE_DIR / output_json_rel
    csv_path = BASE_DIR / output_csv_rel

    if not json_path.exists():
        log_print(f"✗  Decompositor não salvou {output_json_rel}.", indent=1)
        return None

    try:
        with open(json_path, encoding="utf-8") as _f:
            instrucoes_json = _json.load(_f)
        serialize_instrucoes(instrucoes_json, briefing_data, habilidade_entry, codigo_hab, csv_path)
        log_print(f"✓  CSV serializado a partir do JSON: {output_csv_rel}", indent=1)
    except (ValueError, _json.JSONDecodeError) as e:
        log_print(f"✗  Falha ao serializar CSV a partir do JSON do Decompositor: {e}", indent=1)
        return None

    return csv_path if csv_path.exists() else None

def run_agente1(
    client: anthropic.Anthropic,
    row: dict,
    unidade_idx: int,
    capitulo_idx: int,
    capitulos_da_unidade: list,
    todas_unidades: list,
    apostila_name: str,
) -> Optional[Path]:
    """Agente 1 — Arquiteto Curricular. Produz core.md."""

    disciplina = row["disciplina"].strip()
    disciplina_slug = slugify(disciplina)
    unidade = row["unidade"].strip()
    unidade_slug = slugify(unidade)
    pergunta_unidade = row["pergunta_unidade"].strip()
    capitulo = row["capitulo"].strip()

    filename = capitulo_filename(unidade_idx, capitulo_idx, capitulo)
    output_rel = f"output/{apostila_name}/core/{unidade_slug}/{filename}"

    system = build_system_prompt("agente1-orientacao.md", "agente1-skill.md")

    # Lista de capítulos desta unidade
    caps_list = "\n".join(
        f"  {i + 1}. {c}" for i, c in enumerate(capitulos_da_unidade)
    )

    # Resumo de todas as unidades
    unidades_list = "\n".join(
        f"  Unidade {u['unidade_idx']}: {u['unidade']} — {u['pergunta_unidade']}"
        for u in todas_unidades
    )

    # Extrair entrada da habilidade de matriz-conteudosbncc.json e injetar
    codigo_hab = row["habilidade"].split("—")[0].strip().split()[0].strip()
    matriz_conteudos_entry = extract_habilidade(
        BASE_DIR / "contexto" / "matriz-conteudosbncc.json", codigo_hab
    )

    # Injetar princípios pedagógicos e contexto disciplinar diretamente
    principios_content = read_file_safe(BASE_DIR / "contexto" / "principios-pedagogicos-agente1.md")
    disciplina_content = read_file_safe(BASE_DIR / "contexto" / "disciplinas" / f"{disciplina_slug}.md")

    # Cores anteriores — sumário compacto extraído em Python (E9)
    # Substitui read_file dos cores completos (~1.000-1.600 tokens cada)
    # por ~250-300 tokens por capítulo com SINTESE_FINAL, ENCADEAMENTO e autores.
    # Nota: a skill do A1 diz "Leia-os" para cores anteriores — o user_message
    # abaixo sobrescreve com "não leia os cores completos".
    cores_anteriores_section = ""

    if capitulo_idx > 1:
        summaries = []
        for prev_c_idx in range(1, capitulo_idx):
            prev_cap_name = capitulos_da_unidade[prev_c_idx - 1]
            prev_filename = capitulo_filename(unidade_idx, prev_c_idx, prev_cap_name)
            prev_core_path = BASE_DIR / f"output/{apostila_name}/core/{unidade_slug}/{prev_filename}"
            if prev_core_path.exists():
                summaries.append(extract_core_summary(prev_core_path, prev_c_idx, prev_cap_name))

        if summaries:
            cores_anteriores_section = "\nSUMÁRIOS DOS CAPÍTULOS ANTERIORES DESTA UNIDADE:\n"
            cores_anteriores_section += "\n".join(summaries) + "\n"

    # Monta andaime de seções
    andaime_secoes = []
    for sec in range(1, 7):
        micro_hab = row.get(f'micro_hab_{sec}', '').strip()
        operacao = row.get(f'operacao_secao_{sec}', '').strip()
        if micro_hab:
            andaime_secoes.append(f"  Seção {sec}: [{operacao}] {micro_hab}")
    andaime_str = "\n".join(andaime_secoes) if andaime_secoes else "(Não informado)"

    conteudos_str = row.get('conteudos_nucleares', '').strip() or "(Nenhum)"

    user_message = f"""Sua tarefa: arquitetar o capítulo abaixo a partir do andaime prescrito pelo professor.

PRINCÍPIOS PEDAGÓGICOS (contexto/principios-pedagogicos-agente1.md):
{principios_content}

CONTEXTO DISCIPLINAR (contexto/disciplinas/{disciplina_slug}.md):
{disciplina_content}

ENTRADA DA HABILIDADE (de matriz-conteudosbncc.json — use conteudos_prioritarios e conteudos_por_disciplina daqui):
{matriz_conteudos_entry}

CONTEXTO DA UNIDADE:
- Unidade {unidade_idx}: {unidade}
- Pergunta central da unidade: {pergunta_unidade}
- Capítulos desta unidade:
{caps_list}
- Capítulo atual: {capitulo_idx} de {len(capitulos_da_unidade)} desta unidade
{cores_anteriores_section}
TODAS AS UNIDADES DA APOSTILA (para referência de encadeamento macro):
{unidades_list}

DADOS DO CAPÍTULO ATUAL:
- Disciplina: {disciplina}
- Capítulo: {capitulo}
- Habilidade principal: {row['habilidade']}

MICRO-HABILIDADES PRESCRITAS (operação + objeto conceitual — você materializa com conteúdo específico):
{andaime_str}

CONTEÚDOS OBRIGATÓRIOS DO PROFESSOR (todos devem aparecer em pelo menos uma seção):
{conteudos_str}

AUTORES DISPONÍVEIS PARA ESTE CAPÍTULO (distribua entre as seções por afinidade com o objeto conceitual):
{row['autores']}

IMPORTANTE:
- O andaime acima já prescreve as operações e a progressão de micro-habilidades
- Você NÃO precisa inventar a estrutura — ela já está definida
- Seu trabalho é CONCRETIZAR: escolher exemplos âncora, pesos das seções, fontes primárias, verificações
- Os princípios pedagógicos e o contexto disciplinar já estão acima — não é necessário ler esses arquivos
- Os sumários dos capítulos anteriores já estão acima — não leia os cores completos
- Garanta que cada micro-habilidade seja alcançável e progressiva em relação à anterior

ONDE SALVAR O OUTPUT:
{output_rel}
"""

    log_print(f"\n[Agente 1] Unidade {unidade_idx} | Capítulo {capitulo_idx}: {capitulo}")
    run_agent(client, system, user_message, "Agente 1",
              chapter_label=f"{unidade_idx}.{capitulo_idx} {capitulo}", apostila_label=apostila_name,
              model=AGENT_MODELS.get(1, _FALLBACK_MODEL))

    full_path = BASE_DIR / output_rel
    return full_path if full_path.exists() else None

def run_agente2(
    client: anthropic.Anthropic,
    core_path: Path,
    unidade_idx: int,
    capitulo_idx: int,
    unidade_slug: str,
    capitulo: str,
    disciplina: str,
    apostila_name: str,
) -> Optional[Path]:
    """Agente 2 — Redator Funcional. Produz texto.md com rótulos explícitos."""

    filename = capitulo_filename(unidade_idx, capitulo_idx, capitulo)
    output_rel = f"output/{apostila_name}/texto/{unidade_slug}/{filename}"
    core_rel = str(core_path.relative_to(BASE_DIR))

    system = build_system_prompt("agente2-orientacao.md", "agente2-skill.md")

    core_content = read_file_safe(core_path)
    disciplina_content_a2 = read_file_safe(BASE_DIR / "contexto" / "disciplinas" / f"{slugify(disciplina)}.md")

    user_message = f"""Sua tarefa: escrever o texto funcional do capítulo a partir do core abaixo.

CORE DO CAPÍTULO ({core_rel}):
{core_content}

CONTEXTO DISCIPLINAR (contexto/disciplinas/{slugify(disciplina)}.md):
{disciplina_content_a2}

ONDE SALVAR O OUTPUT:
{output_rel}
"""

    log_print(f"\n[Agente 2] Unidade {unidade_idx} | Capítulo {capitulo_idx}: {capitulo}")
    run_agent(client, system, user_message, "Agente 2",
              chapter_label=f"{unidade_idx}.{capitulo_idx} {capitulo}", apostila_label=apostila_name,
              model=AGENT_MODELS.get(2, _FALLBACK_MODEL))

    full_path = BASE_DIR / output_rel
    return full_path if full_path.exists() else None

def run_agente3(
    client: anthropic.Anthropic,
    texto_path: Path,
    unidade_idx: int,
    capitulo_idx: int,
    unidade_slug: str,
    capitulo: str,
    apostila_name: str,
) -> Optional[Path]:
    """Agente 3 — Normalizador de Marcação (determinístico, sem LLM).

    Substitui a chamada ao LLM por normalizar_texto() do normalizador.py,
    eliminando latência e custo de tokens para esta etapa mecânica.
    """
    log_print(f"\n[Agente 3] Unidade {unidade_idx} | Capítulo {capitulo_idx}: {capitulo}")

    try:
        modificado, avisos = normalizar_texto(texto_path)
        if modificado:
            log_print(f"  ✓ Normalizações aplicadas ({len(avisos)} alteração(ões))", indent=1)
            for aviso in avisos:
                log_print(f"    · {aviso}", indent=2)
        else:
            log_print("  ✓ Sem alterações necessárias", indent=1)
        return texto_path
    except Exception as e:
        log_print(f"  ✗ Erro no normalizador: {e}", indent=1)
        logger.exception("[Agente 3] Falha ao normalizar %s", texto_path)
        return None

def _apply_diffs(texto_path: Path, json_response: str) -> Tuple[int, List[str]]:
    """
    Recebe o JSON devolvido pelo Agente 4 e aplica as substituições no arquivo.
    Retorna (n_aplicadas, avisos).
    """
    import json as _json

    # Extrai o bloco JSON da resposta (pode haver texto residual antes/depois)
    raw = json_response.strip()
    # Tenta encontrar o array JSON na resposta
    start = raw.find("[")
    end   = raw.rfind("]") + 1
    if start == -1 or end == 0:
        return 0, ["Agente 4 não devolveu JSON válido — arquivo não alterado"]

    try:
        trocas = _json.loads(raw[start:end])
    except _json.JSONDecodeError as e:
        return 0, [f"JSON inválido do Agente 4: {e} — arquivo não alterado"]

    if not trocas:
        return 0, []

    texto = texto_path.read_text(encoding="utf-8")
    avisos: List[str] = []
    aplicadas = 0

    for item in trocas:
        original = item.get("original", "")
        novo     = item.get("novo", "")
        if not original:
            avisos.append("Troca sem campo 'original' — ignorada")
            continue
        if original not in texto:
            avisos.append(f"Trecho não encontrado no arquivo (ignorado): {original[:60]}…")
            continue
        texto = texto.replace(original, novo, 1)
        aplicadas += 1

    if aplicadas:
        texto_path.write_text(texto, encoding="utf-8")

    return aplicadas, avisos


def run_agente4(
    client: anthropic.Anthropic,
    texto_path: Path,
    unidade_idx: int,
    capitulo_idx: int,
    unidade_slug: str,
    capitulo: str,
    apostila_name: str,
) -> Optional[Path]:
    """Agente 4 — Polidor de prosa. Devolve JSON de diffs; pipeline aplica."""

    texto_rel = str(texto_path.relative_to(BASE_DIR))
    system = build_system_prompt("agente4-orientacao.md", "agente4-skill.md")
    texto_content_a4 = read_file_safe(texto_path)

    user_message = f"""Sua tarefa: polir a prosa do capítulo para leitura fluida por alunos do Ensino Médio.

CONTEÚDO DO ARQUIVO ({texto_rel}):
{texto_content_a4}

Os HTML comments já estão normalizados — não os toque e não os inclua no JSON.
Siga o procedimento da sua skill (já está no seu system prompt).
Devolva apenas o array JSON de trocas — sem nenhum texto antes ou depois.
"""

    log_print(f"\n[Agente 4] Unidade {unidade_idx} | Capítulo {capitulo_idx}: {capitulo}")
    resposta = run_agent(client, system, user_message, "Agente 4",
                         chapter_label=f"{unidade_idx}.{capitulo_idx} {capitulo}",
                         apostila_label=apostila_name,
                         model=AGENT_MODELS.get(4, _FALLBACK_MODEL))

    if resposta:
        n, avisos = _apply_diffs(texto_path, resposta)
        log_print(f"  ✓ {n} troca(s) aplicada(s) pelo Agente 4", indent=1)
        for av in avisos:
            log_print(f"  ⚠  {av}", indent=2)
    else:
        log_print("  ⚠  Agente 4 não devolveu resposta — arquivo não alterado", indent=1)

    return texto_path if texto_path.exists() else None

def run_agente5(
    client: anthropic.Anthropic,
    texto_path: Path,
    unidade_idx: int,
    capitulo_idx: int,
    unidade_slug: str,
    capitulo: str,
    apostila_name: str,
    core_path: Optional[Path] = None,
    micro_habs: Optional[Dict[int, str]] = None,
) -> Optional[Path]:
    """Agente 5 — Formatador XML (determinístico, sem LLM).

    Se core_path for fornecido, identifica (sem chamada à API) quais seções
    precisam de verificação externa — ver PLANO-VERIFICACAO-EXTERNA.md.
    A produção da verificação em si passou a ser um insumo externo, anexado
    só na hora de montar o PDF (xml_to_pdf.py --verificacoes <pasta>).
    """
    output_dir = BASE_DIR / f"output/{apostila_name}/formatado/{unidade_slug}"
    log_print(f"\n[Agente 5] Unidade {unidade_idx} | Capítulo {capitulo_idx}: {capitulo}")

    # Identifica pontos de verificação no core (sem custo de token).
    # A produção da verificação é externa; aqui só marcamos onde ela entra.
    pontos_verif = None
    aplicar_ctx = None
    if core_path and core_path.exists():
        try:
            pontos_verif, aplicar_ctx = coletar_pontos_verificacao(core_path)
            log_print(
                f"  ✓ Pontos de verificação identificados: {len(pontos_verif or {})} seção(ões) | "
                f"aplicar_agora={'sim' if aplicar_ctx else 'não'}",
                indent=1,
            )
        except Exception as e:
            log_print(f"  ⚠  Verificador falhou ({e}) — XML sem marcadores de verificação", indent=1)

    try:
        out_path = formatar_capitulo(texto_path, output_dir,
                                     pontos_verif=pontos_verif,
                                     aplicar_ctx=aplicar_ctx,
                                     micro_habs=micro_habs)
        if out_path:
            log_print(f"  ✓ XML gerado: {out_path.name}", indent=1)
            return out_path
        else:
            log_print("  ✗ Erro no formatador.", indent=1)
            return None
    except Exception as e:
        log_print(f"  ✗ Erro no formatador: {e}", indent=1)
        logger.exception("[Agente 5] Falha ao formatar %s", texto_path)
        return None

# ============================================================================
# PIPELINE PRINCIPAL
# ============================================================================

def fix_csv_alignment(csv_path: Path) -> bool:
    """
    Corrige o bug consistente do Decompositor: sempre escreve exatamente 3 campos
    vazios de trailing, independente de quantas seções foram usadas.

    O header tem 19 colunas. Se uma linha de dados tiver != 19 campos, calcula
    a diferença e insere/remove campos vazios imediatamente antes de 'autores'.

    Retorna True se alguma linha foi corrigida.
    """
    with open(csv_path, encoding='utf-8', newline='') as f:
        raw = list(csv.reader(f))

    if len(raw) < 2:
        return False

    header = raw[0]
    expected = len(header)

    if 'autores' not in header:
        return False

    autores_pos = header.index('autores')
    changed = False
    new_rows = [header]

    for row in raw[1:]:
        if len(row) == expected:
            new_rows.append(row)
            continue

        diff = expected - len(row)  # positivo = curto demais; negativo = longo demais

        if abs(diff) > 4:
            new_rows.append(row)  # discrepância grande demais — não toca
            continue

        current_autores_pos = autores_pos - diff

        if not (0 <= current_autores_pos < len(row)):
            new_rows.append(row)
            continue

        if diff > 0:
            fixed = row[:current_autores_pos] + [''] * diff + row[current_autores_pos:]
        else:
            remove_from = current_autores_pos - abs(diff)
            fixed = row[:remove_from] + row[current_autores_pos:]

        if len(fixed) == expected:
            new_rows.append(fixed)
            changed = True
            log_print(f"⚠  Alinhamento corrigido: linha tinha {len(row)} campos (esperado {expected}).", indent=2)
        else:
            new_rows.append(row)

    if changed:
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(new_rows)

    return changed


def parse_csv(csv_path: Path) -> List[Dict]:
    """Lê e valida CSV com formato de andaime."""
    COLUNAS_OBRIGATORIAS = [
        'disciplina', 'unidade', 'pergunta_unidade', 'capitulo', 'habilidade',
        'micro_hab_1', 'operacao_secao_1',
        'micro_hab_2', 'operacao_secao_2',
        'micro_hab_3', 'operacao_secao_3',
        'micro_hab_4', 'operacao_secao_4',
        'autores',
    ]

    OPERACOES_VALIDAS = {
        'Definir', 'Classificar', 'Comparar', 'Sequenciar',
        'Mapear causalidade', 'Reconhecer perspectiva', 'Aplicar'
    }

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV não encontrado: {csv_path}")

    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV vazio ou sem cabeçalho")

        # Validar colunas obrigatórias
        faltando = set(COLUNAS_OBRIGATORIAS) - set(reader.fieldnames or [])
        if faltando:
            raise ValueError(f"Colunas obrigatórias faltando: {faltando}")

        for idx, row in enumerate(reader, start=2):
            # Validar células obrigatórias não vazias
            for col in COLUNAS_OBRIGATORIAS:
                if not row[col].strip():
                    raise ValueError(f"Célula vazia na linha {idx}, coluna '{col}'")

            # Validar operações (apenas as preenchidas)
            for sec in range(1, 7):
                op_col = f'operacao_secao_{sec}'
                if op_col in reader.fieldnames:
                    op_value = row[op_col].strip()
                    if op_value and op_value not in OPERACOES_VALIDAS:
                        dica = ""
                        if any(c in op_value for c in [';', ' e ', 'Marx', 'Weber']):
                            dica = " PROVÁVEL CAUSA: desalinhamento de colunas — o Decompositor escreveu 3 vírgulas vazias em vez de 4 para os slots opcionais (micro_hab_5/6, operacao_secao_5/6)."
                        raise ValueError(
                            f"Operação inválida na linha {idx}, coluna '{op_col}': '{op_value}'. "
                            f"Deve ser um de: {', '.join(sorted(OPERACOES_VALIDAS))}.{dica}"
                        )

            rows.append(row)

    logger.info(f"CSV carregado: {len(rows)} capítulos (formato com andaime)")
    return rows

def _run_cap_stages_2_5(
    cap_info: dict,
    agentes: List[int],
    force: bool,
    apostila_name: str,
) -> None:
    """
    Executa os estágios 2→5 para um único capítulo.
    Cada chamada usa seu próprio cliente Anthropic (thread-safe).
    """
    client = anthropic.Anthropic(api_key=API_KEY)
    core_path   = cap_info["core_path"]
    u_idx       = cap_info["u_idx"]
    c_idx       = cap_info["c_idx"]
    cap_global  = cap_info["cap_global"]
    total_caps  = cap_info["total_caps"]
    unidade_slug= cap_info["unidade_slug"]
    capitulo    = cap_info["capitulo"]
    disciplina  = cap_info["disciplina"]
    filename    = cap_info["filename"]

    log_print(f"\n{'─' * 70}")
    log_print(f"Cap. {cap_global}/{total_caps}  [{u_idx}.{c_idx}] {capitulo}  [estágios 2–5]")
    log_print(f"{'─' * 70}")

    texto_path = None

    # ─ Agente 2 ─
    if 2 in agentes:
        if not core_path:
            log_print("✗  Core não disponível. Pulando Agente 2.", indent=1)
            return
        expected = BASE_DIR / f"output/{apostila_name}/texto/{unidade_slug}/{filename}"
        if expected.exists() and not force:
            log_print("[Agente 2] Texto já existe — pulando.", indent=1)
            texto_path = expected
        else:
            texto_path = run_agente2(
                client, core_path, u_idx, c_idx,
                unidade_slug, capitulo, disciplina, apostila_name,
            )
            if not texto_path:
                log_print("✗  Agente 2 não produziu output. Pulando agentes posteriores.", indent=1)
                return
    else:
        expected = BASE_DIR / f"output/{apostila_name}/texto/{unidade_slug}/{filename}"
        if expected.exists():
            texto_path = expected

    # ─ Agente 3 ─
    if 3 in agentes:
        if not texto_path:
            log_print("✗  Texto não disponível. Pulando Agente 3.", indent=1)
        else:
            texto_path = run_agente3(
                client, texto_path, u_idx, c_idx,
                unidade_slug, capitulo, apostila_name,
            ) or texto_path

    # ─ Agente 4 ─
    if 4 in agentes:
        if not texto_path:
            log_print("✗  Texto não disponível. Pulando Agente 4.", indent=1)
        else:
            resultado4 = run_agente4(
                client, texto_path, u_idx, c_idx,
                unidade_slug, capitulo, apostila_name,
            )
            if not resultado4:
                log_print("✗  Agente 4 não produziu output. Pulando Agente 5.", indent=1)
                return
            texto_path = resultado4

    # ─ Agente 5 ─
    if 5 in agentes:
        if not texto_path:
            log_print("✗  Texto não disponível. Pulando Agente 5.", indent=1)
        else:
            if not run_agente5(
                client, texto_path, u_idx, c_idx,
                unidade_slug, capitulo, apostila_name,
                core_path=core_path,
                micro_habs=cap_info.get("micro_habs"),
            ):
                log_print("✗  Agente 5 não produziu output.", indent=1)


def run_pipeline(
    csv_path: Path,
    agentes: List[int],
    force: bool = False,
    cap_filter: Optional[int] = None,
    client: Optional[anthropic.Anthropic] = None,
    workers: int = 1,
):
    """
    Executa o pipeline completo para uma apostila.

    Quando workers > 1:
      - Fase 1 (sequencial): Agente 1 para todos os capítulos (dependência de cores anteriores)
      - Fase 2 (paralela):   Agentes 2→5 para cada capítulo em ThreadPoolExecutor
    """
    if client is None:
        client = anthropic.Anthropic(api_key=API_KEY)

    apostila_name = csv_path.parent.name
    workers = max(1, workers)

    log_print(f"\n{'═' * 70}")
    log_print(f"Apostila : {apostila_name}")
    log_print(f"Agentes  : {', '.join(str(a) for a in sorted(agentes))}")
    log_print(f"Workers  : {workers}")
    log_print(f"Forçar   : {'sim' if force else 'não'}")
    if cap_filter is not None:
        log_print(f"Capítulo : {cap_filter} (somente)")
    log_print(f"{'═' * 70}")

    rows = parse_csv(csv_path)

    # Agrupa capítulos por unidade
    unidades_ordenadas: List[str] = []
    unidades_map: Dict[str, List[Dict]] = {}
    for row in rows:
        unidade = row["unidade"].strip()
        if unidade not in unidades_map:
            unidades_ordenadas.append(unidade)
            unidades_map[unidade] = []
        unidades_map[unidade].append(row)

    todas_unidades = [
        {
            "unidade_idx": u_idx + 1,
            "unidade": u_nome,
            "pergunta_unidade": unidades_map[u_nome][0]["pergunta_unidade"].strip(),
        }
        for u_idx, u_nome in enumerate(unidades_ordenadas)
    ]

    total_caps = len(rows)
    log_print(f"Unidades : {len(unidades_ordenadas)}")
    log_print(f"Capítulos: {total_caps}")

    # ── FASE 1: Agente 1 — sempre sequencial ────────────────────────────────
    caps_prontos: List[dict] = []   # capítulos com core_path definido
    cap_global = 0

    for u_idx, unidade_nome in enumerate(unidades_ordenadas, start=1):
        unidade_slug = slugify(unidade_nome)
        caps = unidades_map[unidade_nome]
        capitulos_da_unidade = [r["capitulo"].strip() for r in caps]

        log_print(f"\n{'═' * 70}")
        log_print(f"Unidade {u_idx}: {unidade_nome}")
        log_print(f"{'═' * 70}")

        for c_idx, row in enumerate(caps, start=1):
            cap_global += 1

            if cap_filter is not None and cap_global != cap_filter:
                continue

            capitulo  = row["capitulo"].strip()
            disciplina= row["disciplina"].strip()
            filename  = capitulo_filename(u_idx, c_idx, capitulo)
            core_path = None

            if 1 in agentes:
                log_print(f"\n{'─' * 70}")
                log_print(f"Cap. {cap_global}/{total_caps}  [{u_idx}.{c_idx}] {capitulo}  [Agente 1]")
                log_print(f"{'─' * 70}")
                expected = BASE_DIR / f"output/{apostila_name}/core/{unidade_slug}/{filename}"
                if expected.exists() and not force:
                    log_print("[Agente 1] Core já existe — pulando.", indent=1)
                    core_path = expected
                else:
                    core_path = run_agente1(
                        client, row, u_idx, c_idx,
                        capitulos_da_unidade, todas_unidades, apostila_name,
                    )
                    if not core_path:
                        log_print("✗  Agente 1 não produziu output. Capítulo descartado.", indent=1)
                        continue
            else:
                expected = BASE_DIR / f"output/{apostila_name}/core/{unidade_slug}/{filename}"
                if expected.exists():
                    core_path = expected

            # Só enfileira estágios 2-5 se há algo para fazer
            if any(a in agentes for a in [2, 3, 4, 5]):
                micro_habs = {
                    sec: row.get(f"micro_hab_{sec}", "").strip()
                    for sec in range(1, 7)
                    if row.get(f"micro_hab_{sec}", "").strip()
                }
                caps_prontos.append({
                    "core_path":    core_path,
                    "u_idx":        u_idx,
                    "c_idx":        c_idx,
                    "cap_global":   cap_global,
                    "total_caps":   total_caps,
                    "unidade_slug": unidade_slug,
                    "capitulo":     capitulo,
                    "disciplina":   disciplina,
                    "filename":     filename,
                    "micro_habs":   micro_habs,
                })

    # ── FASE 2: Agentes 2→5 — paralelo quando workers > 1 ──────────────────
    if caps_prontos:
        if workers == 1:
            for cap_info in caps_prontos:
                _run_cap_stages_2_5(cap_info, agentes, force, apostila_name)
        else:
            log_print(f"\n[Fase 2] Processando {len(caps_prontos)} capítulo(s) em paralelo ({workers} workers)…")
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = {
                    executor.submit(_run_cap_stages_2_5, cap_info, agentes, force, apostila_name): cap_info
                    for cap_info in caps_prontos
                }
                for future in as_completed(futures):
                    cap_info = futures[future]
                    try:
                        future.result()
                    except Exception as exc:
                        log_print(
                            f"✗  Capítulo [{cap_info['u_idx']}.{cap_info['c_idx']}] "
                            f"{cap_info['capitulo']} gerou exceção: {exc}",
                            indent=1,
                        )

    # ── Totais de usage ──────────────────────────────────────────────────────
    if USAGE_CSV.exists():
        import csv as _csv
        totals: dict = {}
        with open(USAGE_CSV, encoding="utf-8") as f:
            for row_u in _csv.DictReader(f):
                if row_u.get("apostila") != apostila_name:
                    continue
                for key in ("input_tokens", "output_tokens", "cache_creation_tokens", "cache_read_tokens"):
                    totals[key] = totals.get(key, 0) + int(row_u.get(key) or 0)
        if totals:
            log_print(
                f"USAGE TOTAL [{apostila_name}] — "
                f"in={totals.get('input_tokens',0)} "
                f"out={totals.get('output_tokens',0)} "
                f"cache_create={totals.get('cache_creation_tokens',0)} "
                f"cache_read={totals.get('cache_read_tokens',0)}"
            )

    log_print(f"\n{'═' * 70}")
    log_print(f"Pipeline concluído.")
    log_print(f"Outputs em: output/{apostila_name}/")
    log_print(f"Logs em: {LOG_FILE}")
    log_print(f"CSV de usage: {USAGE_CSV}")
    log_print(f"{'═' * 70}\n")

    # Gera listas de insumos externos para o professor (se agente 5 rodou)
    if 5 in agentes:
        gerar_lista_imagens(OUTPUT_DIR / apostila_name)
        gerar_lista_verificacoes(OUTPUT_DIR / apostila_name)


# ============================================================================
# GERAÇÃO DA LISTA DE IMAGENS PARA O PROFESSOR
# ============================================================================

def gerar_lista_imagens(apostila_dir: Path) -> None:
    """
    Lê todos os XMLs em output/{apostila}/formatado/**/*.xml,
    extrai elementos <imagem>, e escreve IMAGENS-NECESSARIAS.txt
    em linguagem clara para o professor.
    """
    import xml.etree.ElementTree as ET

    xml_files = sorted(apostila_dir.glob("formatado/**/*.xml"))
    if not xml_files:
        log_print("[Imagens] Nenhum XML encontrado — lista de imagens não gerada.")
        return

    # Coleta imagens por capítulo
    capitulos: List[Dict] = []
    for xml_path in xml_files:
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except ET.ParseError as e:
            log_print(f"[Imagens] AVISO: erro ao parsear {xml_path.name}: {e}")
            continue

        cap_el = root.find(".//capitulo") if root.tag != "capitulo" else root
        if cap_el is None:
            cap_el = root

        cap_id     = cap_el.get("id", xml_path.stem)
        cap_titulo = cap_el.get("titulo", xml_path.stem)

        imagens: List[Dict] = []
        for img_el in cap_el.iter("imagem"):
            ref       = img_el.get("ref", "")
            desc_el   = img_el.find("descricao")
            descricao = desc_el.text.strip() if desc_el is not None and desc_el.text else "(sem descrição)"
            imagens.append({"ref": ref, "descricao": descricao})

        if imagens:
            capitulos.append({"id": cap_id, "titulo": cap_titulo, "imagens": imagens})

    saida_path = apostila_dir / "IMAGENS-NECESSARIAS.txt"
    apostila_nome = apostila_dir.name
    data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")

    linhas: List[str] = []
    sep = "=" * 65

    linhas.append(f"IMAGENS NECESSÁRIAS — Apostila: {apostila_nome}")
    linhas.append(f"Gerado em: {data_hoje}")
    linhas.append("")
    linhas.append(sep)
    linhas.append("INSTRUÇÕES")
    linhas.append(sep)
    linhas.append("1. Para cada imagem listada abaixo, encontre ou crie o visual descrito.")
    linhas.append("2. Nomeie o arquivo EXATAMENTE como indicado (use .jpg, .png ou .pdf).")
    linhas.append('3. Coloque todos os arquivos em uma pasta chamada "imagens".')
    linhas.append('4. Envie a pasta "imagens" para o responsável técnico.')
    linhas.append(sep)

    if not capitulos:
        linhas.append("")
        linhas.append("(Nenhuma imagem necessária nesta apostila.)")
    else:
        total = 0
        for cap in capitulos:
            linhas.append("")
            linhas.append(f"CAPÍTULO {cap['id']} — {cap['titulo']}")
            linhas.append("-" * 65)
            for img in cap["imagens"]:
                total += 1
                linhas.append(f"  NOME DO ARQUIVO : {img['ref']}.jpg")
                linhas.append(f"  O QUE MOSTRAR   : {img['descricao']}")
                linhas.append("")

        linhas.append(sep)
        linhas.append(f"TOTAL: {total} imagem(ns) necessária(s)")
        linhas.append(sep)

    saida_path.write_text("\n".join(linhas), encoding="utf-8")
    log_print(f"[Imagens] Lista de imagens salva em: {saida_path}")
    if capitulos:
        total_imgs = sum(len(c["imagens"]) for c in capitulos)
        log_print(f"[Imagens] {total_imgs} imagem(ns) em {len(capitulos)} capítulo(s).")
    else:
        log_print("[Imagens] Nenhuma imagem referenciada nos XMLs.")


# ============================================================================
# GERAÇÃO DA LISTA DE VERIFICAÇÕES PARA OS AGENTES EXTERNOS
# ============================================================================

def gerar_lista_verificacoes(apostila_dir: Path) -> None:
    """
    Lê todos os XMLs em output/{apostila}/formatado/**/*.xml, extrai os
    marcadores <sidebar status="externo"> e escreve VERIFICACOES-NECESSARIAS.txt
    — o briefing para os agentes externos produzirem a pasta verificacoes/.
    Espelha gerar_lista_imagens (ver PLANO-VERIFICACAO-EXTERNA.md, seção 5).
    """
    import xml.etree.ElementTree as ET

    xml_files = sorted(apostila_dir.glob("formatado/**/*.xml"))
    if not xml_files:
        log_print("[Verificações] Nenhum XML encontrado — lista de verificações não gerada.")
        return

    # Coleta marcadores por capítulo
    capitulos: List[Dict] = []
    for xml_path in xml_files:
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except ET.ParseError as e:
            log_print(f"[Verificações] AVISO: erro ao parsear {xml_path.name}: {e}")
            continue

        cap_el = root.find(".//capitulo") if root.tag != "capitulo" else root
        if cap_el is None:
            cap_el = root

        cap_id     = cap_el.get("id", xml_path.stem)
        cap_titulo = cap_el.get("titulo", xml_path.stem)

        marcadores: List[Dict] = []
        for sb in cap_el.iter("sidebar"):
            if sb.get("status") != "externo":
                continue
            tipo = sb.get("tipo", "")
            ref  = sb.get("ref", "")
            oqv_el = sb.find("o-que-verificar")
            oqv = oqv_el.text.strip() if oqv_el is not None and oqv_el.text else "(sem descrição)"
            marcadores.append({"tipo": tipo, "ref": ref, "o_que_verificar": oqv})

        if marcadores:
            capitulos.append({"id": cap_id, "titulo": cap_titulo, "marcadores": marcadores})

    saida_path = apostila_dir / "VERIFICACOES-NECESSARIAS.txt"
    apostila_nome = apostila_dir.name
    data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")

    linhas: List[str] = []
    sep = "=" * 65

    linhas.append(f"VERIFICAÇÕES NECESSÁRIAS — Apostila: {apostila_nome}")
    linhas.append(f"Gerado em: {data_hoje}")
    linhas.append("")
    linhas.append(sep)
    linhas.append("INSTRUÇÕES")
    linhas.append(sep)
    linhas.append("1. Para cada item abaixo, produza a verificação descrita.")
    linhas.append("2. Salve um arquivo JSON nomeado EXATAMENTE como o REF indicado")
    linhas.append("   (ex.: verif-01-01-s3.json, aplicar-01-01.json).")
    linhas.append('3. Coloque todos os arquivos numa pasta chamada "verificacoes".')
    linhas.append("4. Use o schema de exemplo (ver PLANO-VERIFICACAO-EXTERNA.md, seção 4):")
    linhas.append('   - tipo "verificacao": {tipo, ref, pergunta, alternativas{A,B,C,D}, correta, justificativa}')
    linhas.append('   - tipo "aplicar-agora": {tipo, ref, enunciado, resposta_comentada}')
    linhas.append("5. Envie a pasta \"verificacoes\" para o responsável técnico.")
    linhas.append(sep)

    if not capitulos:
        linhas.append("")
        linhas.append("(Nenhuma verificação necessária nesta apostila.)")
    else:
        total = 0
        for cap in capitulos:
            linhas.append("")
            linhas.append(f"CAPÍTULO {cap['id']} — {cap['titulo']}")
            linhas.append("-" * 65)
            for m in cap["marcadores"]:
                total += 1
                linhas.append(f"  REF             : {m['ref']}   (tipo: {m['tipo']})")
                linhas.append(f"  O QUE VERIFICAR : {m['o_que_verificar']}")
                linhas.append("")

        linhas.append(sep)
        linhas.append(f"TOTAL: {total} verificação(ões) necessária(s)")
        linhas.append(sep)

    saida_path.write_text("\n".join(linhas), encoding="utf-8")
    log_print(f"[Verificações] Lista salva em: {saida_path}")
    if capitulos:
        total_v = sum(len(c["marcadores"]) for c in capitulos)
        log_print(f"[Verificações] {total_v} marcador(es) em {len(capitulos)} capítulo(s).")
    else:
        log_print("[Verificações] Nenhum marcador de verificação nos XMLs.")


# ============================================================================
# VALIDAÇÃO DOS INSUMOS DE VERIFICAÇÃO (antes de montar o PDF)
# ============================================================================

_ALTS_ESPERADAS = {"A", "B", "C", "D"}

def _validar_schema_verificacao(ref: str, tipo: str, data: dict) -> Tuple[List[str], List[str]]:
    """Valida um JSON de verificação. Retorna (erros, avisos)."""
    erros: List[str] = []
    avisos: List[str] = []
    if tipo == "verificacao":
        if not str(data.get("pergunta", "")).strip():
            erros.append(f"{ref}: falta 'pergunta'")
        alts = data.get("alternativas") or {}
        if set(alts.keys()) != _ALTS_ESPERADAS:
            erros.append(f"{ref}: 'alternativas' devem ser exatamente A,B,C,D "
                         f"(achei {sorted(alts.keys())})")
        elif any(not str(v).strip() for v in alts.values()):
            erros.append(f"{ref}: alguma alternativa está vazia")
        if data.get("correta") not in _ALTS_ESPERADAS:
            erros.append(f"{ref}: 'correta' deve ser A, B, C ou D (achei {data.get('correta')!r})")
        if not str(data.get("justificativa", "")).strip():
            avisos.append(f"{ref}: sem 'justificativa' (gabarito do professor)")
    elif tipo == "aplicar-agora":
        if not str(data.get("enunciado", "")).strip():
            erros.append(f"{ref}: falta 'enunciado'")
        if not str(data.get("resposta_comentada", "")).strip():
            avisos.append(f"{ref}: sem 'resposta_comentada' (resposta modelo do professor)")
    else:
        avisos.append(f"{ref}: tipo desconhecido '{tipo}'")
    return erros, avisos


def validar_verificacoes(apostila_dir: Path, verifdir: Optional[Path] = None) -> bool:
    """
    Cruza os marcadores <sidebar status="externo"> dos XMLs com os JSON da
    pasta verificacoes/ e relata pendências (arquivos ausentes, JSON inválido,
    schema fora do esperado). Retorna True se não houver ERROS bloqueantes.
    Ver PLANO-VERIFICACAO-EXTERNA.md, Fase 5.
    """
    import json
    import xml.etree.ElementTree as ET

    verifdir = Path(verifdir) if verifdir else (apostila_dir / "verificacoes")
    xml_files = sorted(apostila_dir.glob("formatado/**/*.xml"))
    if not xml_files:
        log_print("[Validação] Nenhum XML encontrado — nada a validar.")
        return True

    refs: List[Tuple[str, str]] = []
    for xml_path in xml_files:
        try:
            root = ET.parse(xml_path).getroot()
        except ET.ParseError as e:
            log_print(f"[Validação] AVISO: erro ao parsear {xml_path.name}: {e}")
            continue
        for sb in root.iter("sidebar"):
            if sb.get("status") == "externo":
                refs.append((sb.get("ref", ""), sb.get("tipo", "")))

    erros: List[str] = []
    avisos: List[str] = []
    ausentes = 0
    for ref, tipo in refs:
        p = verifdir / f"{ref}.json"
        if not p.exists():
            erros.append(f"{ref}: arquivo ausente ({verifdir.name}/{ref}.json)")
            ausentes += 1
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            erros.append(f"{ref}: JSON inválido ({e})")
            continue
        e, a = _validar_schema_verificacao(ref, tipo, data)
        erros.extend(e)
        avisos.extend(a)

    sep = "=" * 65
    log_print(f"\n{sep}")
    log_print(f"[Validação] Verificações em: {verifdir}")
    log_print(f"[Validação] {len(refs)} marcador(es) | {ausentes} ausente(s) | "
              f"{len(erros)} erro(s) | {len(avisos)} aviso(s)")
    log_print(sep)
    for e in erros:
        log_print(f"  ✗ ERRO  : {e}")
    for a in avisos:
        log_print(f"  ⚠ aviso : {a}")
    if not erros and not avisos:
        log_print("  ✓ Tudo certo: todos os refs têm JSON válido no schema esperado.")
    log_print(sep + "\n")
    return len(erros) == 0


# ============================================================================
# CLI
# ============================================================================

def parse_agentes(value: str) -> List[int]:
    try:
        return [int(a.strip()) for a in value.split(",")]
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Formato inválido: '{value}'. Use ex: 1,2 ou 1,2,3"
        )

def main():
    parser = argparse.ArgumentParser(
        description="Pipeline de geração de apostilas didáticas (V5).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Agentes:
  0 = Decompositor (briefing.json → instrucoes.csv) — requer --briefing e --apostila
  1 = Arquiteto Curricular (instrucoes.csv → core.md)
  2 = Redator Funcional (core.md → texto.md com rótulos)
  3 = Normalizador de Marcação (normaliza HTML comments no texto.md)
  4 = Redator de Estilo (qualifica prosa, preserva rótulos em comments)
  5 = Formatador (extrai estrutura → XML para InDesign)

Ordem padrão (modo manual): 1,2,3,4,5
Ordem padrão (modo briefing): 0,1,2,3,4,5

Exemplos:
  # Modo briefing: gera CSV e roda pipeline completo
  python pipeline.py --briefing input/apostila-sociologia/briefing.json --apostila apostila-sociologia

  # Modo briefing: só gera o CSV
  python pipeline.py --briefing input/apostila-sociologia/briefing.json --apostila apostila-sociologia --agentes 0

  # Modo manual: professor já tem o CSV
  python pipeline.py input/apostila-historia-midia/instrucoes.csv
  python pipeline.py input/apostila-historia-midia/instrucoes.csv --agentes 1,2
  python pipeline.py input/apostila-historia-midia/instrucoes.csv --force
  python pipeline.py input/apostila-historia-midia/instrucoes.csv --cap 1
        """,
    )
    parser.add_argument(
        "csv",
        nargs="?",
        type=Path,
        default=None,
        help="Caminho para o CSV (modo manual). Omitir quando usar --briefing.",
    )
    parser.add_argument(
        "--briefing",
        type=Path,
        default=None,
        metavar="BRIEFING_JSON",
        help="Caminho para o briefing.json. Ativa o modo briefing (Agente 0).",
    )
    parser.add_argument(
        "--apostila",
        type=str,
        default=None,
        metavar="NOME",
        help="Nome da apostila (ex: apostila-sociologia). Obrigatório no modo briefing.",
    )
    parser.add_argument(
        "--agentes",
        type=parse_agentes,
        default=None,
        help="Agentes a executar. Padrão: 1,2,3,4,5 (manual) ou 0,1,2,3,4,5 (briefing).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenera outputs mesmo que já existam",
    )
    parser.add_argument(
        "--cap",
        type=int,
        default=None,
        metavar="N",
        help="Processa apenas o capítulo N (número global)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        metavar="N",
        help="Nº de capítulos processados em paralelo nos estágios 2–5 (padrão: 1). "
             "Use 2–3; valores altos podem atingir rate limits.",
    )
    parser.add_argument(
        "--validar-verif",
        type=str,
        default=None,
        metavar="APOSTILA_DIR",
        help="Só valida os insumos de verificação de output/<apostila>/ contra a "
             "pasta verificacoes/ e sai (não roda o pipeline).",
    )
    parser.add_argument(
        "--verif-dir",
        type=str,
        default=None,
        metavar="PASTA",
        help="Pasta dos JSON de verificação (padrão: <apostila_dir>/verificacoes).",
    )

    args = parser.parse_args()

    # ── Modo validação avulsa ────────────────────────────────────────────────────
    if args.validar_verif:
        apostila_dir = Path(args.validar_verif)
        if not apostila_dir.is_absolute():
            apostila_dir = OUTPUT_DIR / args.validar_verif if not apostila_dir.exists() else apostila_dir
        verifdir = Path(args.verif_dir) if args.verif_dir else None
        ok = validar_verificacoes(apostila_dir, verifdir)
        sys.exit(0 if ok else 1)

    # ── Modo briefing ──────────────────────────────────────────────────────────
    if args.briefing:
        if not args.apostila:
            log_print("ERRO: --apostila é obrigatório no modo briefing.")
            sys.exit(1)

        briefing_path = args.briefing if args.briefing.is_absolute() else BASE_DIR / args.briefing
        if not briefing_path.exists():
            log_print(f"ERRO: briefing não encontrado: {briefing_path}")
            sys.exit(1)

        agentes = args.agentes if args.agentes is not None else [0, 1, 2, 3, 4, 5]
        apostila_name = args.apostila
        csv_path = BASE_DIR / f"input/{apostila_name}/instrucoes.csv"

        client = anthropic.Anthropic(api_key=API_KEY)

        if 0 in agentes:
            csv_path = run_agente0(client, briefing_path, apostila_name)
            if not csv_path:
                log_print("✗  Agente 0 não produziu o CSV. Abortando.")
                sys.exit(1)
            if fix_csv_alignment(csv_path):
                log_print("⚠  CSV corrigido automaticamente (desalinhamento de colunas).", indent=1)
            try:
                parse_csv(csv_path)
                log_print("✓  Schema do CSV validado.")
            except (ValueError, FileNotFoundError) as e:
                log_print(f"✗  CSV gerado com schema inválido: {e}. Abortando.")
                sys.exit(1)

        agentes_pipeline = [a for a in agentes if a != 0]
        if agentes_pipeline:
            if not csv_path.exists():
                log_print(f"ERRO: CSV não encontrado: {csv_path}")
                sys.exit(1)
            run_pipeline(csv_path, agentes_pipeline, args.force, args.cap, client, workers=args.workers)

    # ── Modo manual ────────────────────────────────────────────────────────────
    else:
        if not args.csv:
            log_print("ERRO: informe o CSV ou use --briefing para modo automatico.")
            parser.print_help()
            sys.exit(1)

        agentes = args.agentes if args.agentes is not None else [1, 2, 3, 4, 5]
        csv_path = args.csv if args.csv.is_absolute() else BASE_DIR / args.csv

        if not csv_path.exists():
            log_print(f"ERRO: CSV nao encontrado: {csv_path}")
            sys.exit(1)

        client = anthropic.Anthropic(api_key=API_KEY)
        run_pipeline(csv_path, agentes, args.force, args.cap, client, workers=args.workers)

if __name__ == "__main__":
    main()
