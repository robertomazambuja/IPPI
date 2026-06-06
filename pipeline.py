#!/usr/bin/env python3
"""
Pipeline de geração de apostilas didáticas — VERSÃO 5 (FUNCIONAL)

Combina:
- Loop agêntico com tools (read_file, write_file)
- Cache ephemeral para reduzir custo de tokens
- Streaming para respostas longas
- Retry com backoff exponencial para erros transitórios
- 6 agentes: Decompositor → Arquiteto → Redator Funcional → Validador → Diagramador
- Validação rigorosa de CSV
- Logging estruturado com arquivo

Ordem de execução padrão (modo manual): 1 → 2 → 3 → 5
Modo briefing (com Agente 0):           0 → 1 → 2 → 3 → 5

Agente 4 (Redator de Estilo) disponível via --agentes mas fora do fluxo padrão.

Uso:
    # Modo briefing: Agente 0 gera o CSV, depois roda 1–5
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
import logging
import os
import re
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

BASE_DIR = Path(__file__).parent
MODEL = "claude-opus-4-6"
MAX_TOKENS = 32000
AGENTE_MAX_ITERATIONS = 30

# Diretórios
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Logging
LOG_FILE = LOG_DIR / f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
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

def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Executa uma ferramenta e retorna o resultado como string."""

    if tool_name == "read_file":
        path = BASE_DIR / tool_input["path"]
        result = read_file_safe(path)
        if result.startswith("ERRO:"):
            log_print(f"⚠  {result}", indent=2)
        return result

    if tool_name == "write_file":
        path = BASE_DIR / tool_input["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(tool_input["content"], encoding="utf-8")
        log_print(f"✓  Salvo: {tool_input['path']}", indent=2)
        return f"Arquivo salvo: {tool_input['path']}"

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
) -> Optional[str]:
    """
    Executa um agente em loop até end_turn ou limite de iterações.
    Retorna o texto final da resposta (pode ser vazio se o agente salvou tudo via write_file).
    """
    messages = [{"role": "user", "content": user_message}]
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Retry com backoff exponencial apenas em erros transitórios
        for attempt in range(4):
            try:
                with client.messages.stream(
                    model=MODEL,
                    max_tokens=MAX_TOKENS,
                    system=[
                        {
                            "type": "text",
                            "text": system_prompt,
                            "cache_control": {"type": "ephemeral"},
                        }
                    ],
                    tools=TOOLS,
                    messages=messages,
                ) as stream:
                    response = stream.get_final_message()
                break
            except (
                anthropic.InternalServerError,
                anthropic.APITimeoutError,
                anthropic.APIConnectionError,
            ) as e:
                if attempt == 3:
                    raise
                wait = 10 * (attempt + 1)
                log_print(f"⚠  Erro transitório — aguardando {wait}s antes de tentar novamente...", indent=2)
                time.sleep(wait)

        # Registra resposta no histórico
        messages.append({"role": "assistant", "content": response.content})

        # Coleta texto da resposta
        text_blocks = [b.text for b in response.content if hasattr(b, "text")]
        final_text = "\n".join(text_blocks).strip()

        # Agente terminou
        if response.stop_reason == "end_turn":
            log_print(f"✓  {agent_name} concluiu ({iteration} iteração(ões))", indent=1)
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
        return final_text

    log_print(f"⚠  {agent_name} atingiu limite de iterações ({max_iterations})", indent=1)
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

def run_agente0(
    client: anthropic.Anthropic,
    briefing_path: Path,
    apostila_name: str,
) -> Optional[Path]:
    """Agente 0 — Decompositor. Produz instrucoes.csv a partir de um briefing JSON."""

    output_rel = f"input/{apostila_name}/instrucoes.csv"
    briefing_rel = str(briefing_path.relative_to(BASE_DIR))

    system = build_system_prompt("decompositor-orientacao.md", "decompositor-skill.md")

    user_message = f"""Sua tarefa: transformar o briefing do professor em instrucoes.csv válido.

ARQUIVO DE BRIEFING:
{briefing_rel}

ONDE SALVAR O OUTPUT:
{output_rel}

Siga os passos da sua skill (skills/decompositor-skill.md):
1. Leia o briefing ({briefing_rel})
2. Consulte contexto/matriz-enem.json para a habilidade identificada — extraia sequencia_pedagogica, enunciado e foco_cognitivo
3. Para cada capítulo: use a sequencia_pedagogica como template de operações e escreva micro-habilidades no formato (operação + objeto conceitual do capítulo) — sem nomear autores ou fontes específicas
4. Para cada capítulo: mapeie autores_por_capitulo[capitulo] → coluna autores; mapeie conteudos_por_capitulo[capitulo] → coluna conteudos_nucleares
5. Monte o CSV, valide (checklist da skill) e salve em {output_rel}
"""

    log_print(f"\n[Agente 0] Decompositor — gerando {output_rel}")
    run_agent(client, system, user_message, "Agente 0")

    full_path = BASE_DIR / output_rel
    return full_path if full_path.exists() else None


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

    # Cores anteriores
    cores_anteriores_section = ""
    arquivos_a_ler = f"1. contexto/principios-pedagogicos-agente1.md\n2. contexto/disciplinas/{disciplina_slug}.md\n"

    if capitulo_idx > 1:
        cores_anteriores = []
        for prev_c_idx in range(1, capitulo_idx):
            prev_cap_name = capitulos_da_unidade[prev_c_idx - 1]
            prev_filename = capitulo_filename(unidade_idx, prev_c_idx, prev_cap_name)
            prev_core_rel = f"output/{apostila_name}/core/{unidade_slug}/{prev_filename}"
            prev_core_path = BASE_DIR / prev_core_rel
            if prev_core_path.exists():
                cores_anteriores.append((prev_c_idx, prev_cap_name, prev_core_rel))

        if cores_anteriores:
            cores_anteriores_section = "\nCAPÍTULOS ANTERIORES DESTA UNIDADE:\n"
            for idx, cap_name, rel_path in cores_anteriores:
                cores_anteriores_section += f"  - Capítulo {idx}: {cap_name}\n    {rel_path}\n"
            cores_anteriores_section += "\n"
            arquivos_a_ler += "3. Os cores dos capítulos anteriores (listados acima)\n"

    # Monta andaime de seções
    andaime_secoes = []
    for sec in range(1, 7):
        micro_hab_col = f'micro_hab_{sec}'
        op_col = f'operacao_secao_{sec}'

        micro_hab = row.get(micro_hab_col, '').strip()
        operacao = row.get(op_col, '').strip()

        if micro_hab:  # Apenas adiciona se preenchida
            andaime_secoes.append(f"  Seção {sec}: [{operacao}] {micro_hab}")

    andaime_str = "\n".join(andaime_secoes) if andaime_secoes else "(Não informado)"

    conteudos_nucleares = row.get('conteudos_nucleares', '').strip()
    conteudos_str = conteudos_nucleares if conteudos_nucleares else "(Nenhum)"

    user_message = f"""Sua tarefa: arquitetar o capítulo abaixo a partir do andaime prescrito pelo professor.

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
- Habilidade principal: {row['habilidade_principal']}

MICRO-HABILIDADES PRESCRITAS (operação + objeto conceitual — você materializa com conteúdo específico):
{andaime_str}

CONTEÚDOS OBRIGATÓRIOS DO PROFESSOR (todos devem aparecer em pelo menos uma seção):
{conteudos_str}

AUTORES DISPONÍVEIS PARA ESTE CAPÍTULO (distribua entre as seções por afinidade com o objeto conceitual):
{row['autores']}

ARQUIVOS QUE VOCÊ DEVE LER ANTES DE INICIAR (nesta ordem):
{arquivos_a_ler}

IMPORTANTE:
- O andaime acima já prescreve as operações e a progressão de micro-habilidades
- Você NÃO precisa inventar a estrutura — ela já está definida
- Seu trabalho é CONCRETIZAR: escolher exemplos âncora, pesos das seções, fontes primárias, verificações
- Garanta que cada micro-habilidade seja alcançável e progressiva em relação à anterior

ONDE SALVAR O OUTPUT:
{output_rel}
"""

    log_print(f"\n[Agente 1] Unidade {unidade_idx} | Capítulo {capitulo_idx}: {capitulo}")
    run_agent(client, system, user_message, "Agente 1")

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

    user_message = f"""Sua tarefa: escrever o texto funcional do capítulo a partir do core abaixo.

ARQUIVOS QUE VOCÊ DEVE LER ANTES DE INICIAR (nesta ordem):
1. {core_rel}
2. contexto/disciplinas/{slugify(disciplina)}.md

ONDE SALVAR O OUTPUT:
{output_rel}
"""

    log_print(f"\n[Agente 2] Unidade {unidade_idx} | Capítulo {capitulo_idx}: {capitulo}")
    run_agent(client, system, user_message, "Agente 2")

    full_path = BASE_DIR / output_rel
    return full_path if full_path.exists() else None

def run_agente3(
    client: anthropic.Anthropic,
    core_path: Path,
    texto_path: Path,
    unidade_idx: int,
    capitulo_idx: int,
    unidade_slug: str,
    capitulo: str,
    apostila_name: str,
) -> Optional[Path]:
    """Agente 3 — Validador Técnico. Produz validacao.md."""

    filename = capitulo_filename(unidade_idx, capitulo_idx, capitulo)
    output_rel = f"output/{apostila_name}/validacao/{unidade_slug}/{filename}"
    core_rel = str(core_path.relative_to(BASE_DIR))
    texto_rel = str(texto_path.relative_to(BASE_DIR))

    system = build_system_prompt("agente3-orientacao.md", "agente3-skill.md")

    user_message = f"""Sua tarefa: validar o texto funcional do capítulo.

ARQUIVOS QUE VOCÊ DEVE LER ANTES DE INICIAR:
1. {core_rel}
2. {texto_rel}
3. contexto/principios-pedagogicos-agente1.md

ONDE SALVAR O OUTPUT:
{output_rel}
"""

    log_print(f"\n[Agente 3] Unidade {unidade_idx} | Capítulo {capitulo_idx}: {capitulo}")
    run_agent(client, system, user_message, "Agente 3")

    full_path = BASE_DIR / output_rel
    return full_path if full_path.exists() else None

def run_agente4(
    client: anthropic.Anthropic,
    texto_path: Path,
    unidade_idx: int,
    capitulo_idx: int,
    unidade_slug: str,
    capitulo: str,
    apostila_name: str,
) -> Optional[Path]:
    """Agente 4 — Redator de Estilo. Qualifica prosa, torna invisível rótulos."""

    filename = capitulo_filename(unidade_idx, capitulo_idx, capitulo)
    texto_rel = str(texto_path.relative_to(BASE_DIR))

    system = build_system_prompt("agente4-orientacao.md", "agente4-skill.md")

    user_message = f"""Sua tarefa: qualificar o texto funcional, tornando invisível a engenharia estrutural.

ARQUIVO QUE VOCÊ DEVE EDITAR:
{texto_rel}

Leia o arquivo, reescreva para prosa natural (rótulos desaparecem),
e salve de volta no mesmo caminho.
"""

    log_print(f"\n[Agente 4] Unidade {unidade_idx} | Capítulo {capitulo_idx}: {capitulo}")
    run_agent(client, system, user_message, "Agente 4")

    full_path = BASE_DIR / f"output/{apostila_name}/texto/{unidade_slug}/{filename}"
    return full_path if full_path.exists() else None

def run_agente5(
    client: anthropic.Anthropic,
    texto_path: Path,
    unidade_idx: int,
    capitulo_idx: int,
    unidade_slug: str,
    capitulo: str,
    apostila_name: str,
) -> Optional[Path]:
    """Agente 5 — Formatador XML. Extrai estrutura + produz XML para InDesign."""

    filename = capitulo_filename(unidade_idx, capitulo_idx, capitulo)
    output_rel = f"output/{apostila_name}/formatado/{unidade_slug}/{filename.replace('.md', '.xml')}"
    texto_rel = str(texto_path.relative_to(BASE_DIR))

    system = build_system_prompt("agente5-orientacao.md", "agente5-skill.md")

    user_message = f"""Sua tarefa: formatar o texto qualificado em XML estruturado.

ARQUIVO QUE VOCÊ DEVE LER:
{texto_rel}

ARQUIVO QUE VOCÊ DEVE SALVAR:
{output_rel}

Leia o arquivo markdown (com comentários ocultos), extraia estrutura,
e salve em XML com cabeçalho (pergunta+habilidade), corpo (seções),
sidebars (verificações com resposta oculta) e rodapé (encadeamento).
"""

    log_print(f"\n[Agente 5] Unidade {unidade_idx} | Capítulo {capitulo_idx}: {capitulo}")
    run_agent(client, system, user_message, "Agente 5")

    full_path = BASE_DIR / output_rel
    return full_path if full_path.exists() else None

# ============================================================================
# PIPELINE PRINCIPAL
# ============================================================================

def parse_csv(csv_path: Path) -> List[Dict]:
    """Lê e valida CSV com novo formato de andaime."""
    COLUNAS_OBRIGATORIAS = [
        'disciplina', 'unidade', 'pergunta_unidade', 'capitulo', 'habilidade_principal',
        'micro_hab_1', 'operacao_secao_1',
        'micro_hab_2', 'operacao_secao_2',
        'micro_hab_3', 'operacao_secao_3',
        'micro_hab_4', 'operacao_secao_4',
        'autores'
    ]

    OPERACOES_VALIDAS = {
        'Definir', 'Classificar', 'Comparar', 'Sequenciar',
        'Mapear causalidade', 'Reconhecer perspectiva', 'Aplicar'
    }

    COLUNAS_OPCIONAIS = [
        'micro_hab_5', 'operacao_secao_5',
        'micro_hab_6', 'operacao_secao_6',
        'conteudos_nucleares',
    ]

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
                        raise ValueError(
                            f"Operação inválida na linha {idx}, coluna '{op_col}': '{op_value}'. "
                            f"Deve ser um de: {', '.join(sorted(OPERACOES_VALIDAS))}"
                        )

            rows.append(row)

    logger.info(f"CSV carregado: {len(rows)} capítulos (novo formato com andaime)")
    return rows

def run_pipeline(
    csv_path: Path,
    agentes: List[int],
    force: bool = False,
    cap_filter: Optional[int] = None,
    briefing_path: Optional[Path] = None,
):
    """Executa o pipeline completo para uma apostila."""

    client = anthropic.Anthropic(api_key=API_KEY)

    apostila_name = csv_path.parent.name

    # ─ Agente 0 (Decompositor) — só roda em modo briefing ─
    if 0 in agentes:
        if briefing_path is None:
            log_print("ERRO: --briefing obrigatório para rodar o Agente 0.")
            sys.exit(1)
        if not briefing_path.exists():
            log_print(f"ERRO: Briefing não encontrado: {briefing_path}")
            sys.exit(1)
        log_print(f"\n{'═' * 70}")
        log_print(f"Agente 0 — Decompositor")
        log_print(f"Briefing : {briefing_path}")
        log_print(f"Output   : input/{apostila_name}/instrucoes.csv")
        log_print(f"{'═' * 70}")
        result = run_agente0(client, briefing_path, apostila_name)
        if not result:
            log_print("✗  Agente 0 não produziu CSV. Pipeline interrompido.")
            sys.exit(1)
        log_print(f"✓  CSV gerado: {result}")
        # Se só pediu o Agente 0, encerra aqui
        if agentes == [0]:
            log_print(f"\nAgente 0 concluído. Para continuar: python pipeline.py {csv_path}")
            return

    log_print(f"\n{'═' * 70}")
    log_print(f"Apostila : {apostila_name}")
    log_print(f"Agentes  : {', '.join(str(a) for a in sorted(agentes))}")
    log_print(f"Forçar   : {'sim' if force else 'não'}")
    if cap_filter is not None:
        log_print(f"Capítulo : {cap_filter} (somente)")
    log_print(f"{'═' * 70}")

    # Parse CSV com validação
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

    # Sumário de todas as unidades
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

    cap_global = 0

    # Processa unidade por unidade
    for u_idx, unidade_nome in enumerate(unidades_ordenadas, start=1):
        unidade_slug = slugify(unidade_nome)
        caps = unidades_map[unidade_nome]
        capitulos_da_unidade = [r["capitulo"].strip() for r in caps]

        log_print(f"\n{'═' * 70}")
        log_print(f"Unidade {u_idx}: {unidade_nome}")
        log_print(f"{'═' * 70}")

        for c_idx, row in enumerate(caps, start=1):
            cap_global += 1

            # Filtro por capítulo específico
            if cap_filter is not None and cap_global != cap_filter:
                continue

            capitulo = row["capitulo"].strip()
            disciplina = row["disciplina"].strip()
            filename = capitulo_filename(u_idx, c_idx, capitulo)

            log_print(f"\n{'─' * 70}")
            log_print(f"Cap. {cap_global}/{total_caps}  [{u_idx}.{c_idx}] {capitulo}")
            log_print(f"{'─' * 70}")

            core_path = None
            texto_path = None

            # ─ Agente 1 ─
            if 1 in agentes:
                expected = BASE_DIR / f"output/{apostila_name}/core/{unidade_slug}/{filename}"
                if expected.exists() and not force:
                    log_print("[Agente 1] Core já existe — pulando. (--force para regenerar)", indent=1)
                    core_path = expected
                else:
                    core_path = run_agente1(
                        client, row, u_idx, c_idx,
                        capitulos_da_unidade, todas_unidades, apostila_name,
                    )
                    if not core_path:
                        log_print("✗  Agente 1 não produziu output. Pulando agentes posteriores.", indent=1)
                        continue
            else:
                expected = BASE_DIR / f"output/{apostila_name}/core/{unidade_slug}/{filename}"
                if expected.exists():
                    core_path = expected

            # ─ Agente 2 ─
            if 2 in agentes:
                if not core_path:
                    log_print("✗  Core não disponível. Pulando Agente 2.", indent=1)
                else:
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
                            continue
            else:
                expected = BASE_DIR / f"output/{apostila_name}/texto/{unidade_slug}/{filename}"
                if expected.exists():
                    texto_path = expected

            # ─ Agente 3 (opcional) ─
            # Agente 3 removido do fluxo automático (muito custoso)
            # Use --agentes 1,2,3,4 se quiser validação explícita
            if 3 in agentes:
                if not core_path or not texto_path:
                    log_print("✗  Core ou texto não disponível. Pulando Agente 3.", indent=1)
                else:
                    expected = BASE_DIR / f"output/{apostila_name}/validacao/{unidade_slug}/{filename}"
                    if expected.exists() and not force:
                        log_print("[Agente 3] Validação já existe — pulando.", indent=1)
                    else:
                        run_agente3(
                            client, core_path, texto_path, u_idx, c_idx,
                            unidade_slug, capitulo, apostila_name,
                        )

            # ─ Agente 4 ─
            if 4 in agentes:
                if not texto_path:
                    log_print("✗  Texto não disponível. Pulando Agente 4.", indent=1)
                else:
                    run_agente4(
                        client, texto_path, u_idx, c_idx,
                        unidade_slug, capitulo, apostila_name,
                    )

            # ─ Agente 5 ─
            if 5 in agentes:
                if not texto_path:
                    log_print("✗  Texto não disponível. Pulando Agente 5.", indent=1)
                else:
                    run_agente5(
                        client, texto_path, u_idx, c_idx,
                        unidade_slug, capitulo, apostila_name,
                    )

    log_print(f"\n{'═' * 70}")
    log_print(f"Pipeline concluído.")
    log_print(f"Logs em: {LOG_FILE}")
    log_print(f"{'=' * 70}\n")

# ============================================================================
# CLI
# ============================================================================

def parse_agentes(value: str) -> List[int]:
    try:
        return [int(a.strip()) for a in value.split(",")]
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Formato invalido: '{value}'. Use ex: 1,2 ou 1,2,3"
        )

def main():
    parser = argparse.ArgumentParser(
        description="Pipeline de geracao de apostilas didaticas (funcional).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Agentes:
  0 = Decompositor (briefing.json -> instrucoes.csv) -- requer --briefing e --apostila
  1 = Arquiteto Curricular (core.md)
  2 = Redator Funcional (texto.md com rotulos)
  3 = Validador Tecnico (validacao.md)
  4 = Redator de Estilo -- fora do fluxo padrao
  5 = Diagramador (XML para InDesign)

Ordem padrao (modo manual): 1,2,3,5
Ordem padrao (modo briefing): 0,1,2,3,5

Exemplos:
  python pipeline.py --briefing input/apostila-sociologia/briefing.json --apostila apostila-sociologia
  python pipeline.py --briefing input/apostila-sociologia/briefing.json --apostila apostila-sociologia --agentes 0
  python pipeline.py input/apostila-historia-midia/instrucoes.csv
  python pipeline.py input/apostila-historia-midia/instrucoes.csv --agentes 1,2
  python pipeline.py input/apostila-historia-midia/instrucoes.csv --force
  python pipeline.py input/apostila-historia-midia/instrucoes.csv --cap 1
        """,
    )
    parser.add_argument(
        "csv", type=Path, nargs="?",
        help="Caminho para o CSV. Omitir quando usar --briefing.",
    )
    parser.add_argument(
        "--briefing", type=Path, default=None, metavar="ARQUIVO",
        help="Briefing JSON para o Agente 0 (ex: input/apostila/briefing.json)",
    )
    parser.add_argument(
        "--apostila", type=str, default=None, metavar="NOME",
        help="Nome da pasta da apostila. Obrigatorio com --briefing.",
    )
    parser.add_argument(
        "--agentes", type=parse_agentes, default=None,
        help="Agentes a executar. Padrao: 1,2,3,5 (manual) ou 0,1,2,3,5 (briefing).",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Regenera outputs mesmo que ja existam",
    )
    parser.add_argument(
        "--cap", type=int, default=None, metavar="N",
        help="Processa apenas o capitulo N (numero global)",
    )

    args = parser.parse_args()

    # Modo briefing
    if args.briefing is not None:
        if not args.apostila:
            log_print("ERRO: --apostila e obrigatorio quando usando --briefing.")
            sys.exit(1)
        briefing_path = args.briefing if args.briefing.is_absolute() else BASE_DIR / args.briefing
        csv_path = BASE_DIR / f"input/{args.apostila}/instrucoes.csv"
        agentes = args.agentes if args.agentes is not None else [0, 1, 2, 3, 5]
        run_pipeline(csv_path, agentes, args.force, args.cap, briefing_path=briefing_path)
        return

    # Modo manual
    if args.csv is None:
        log_print("ERRO: informe o CSV ou use --briefing para modo automatico.")
        parser.print_help()
        sys.exit(1)

    csv_path = args.csv if args.csv.is_absolute() else BASE_DIR / args.csv
    if not csv_path.exists():
        log_print(f"ERRO: CSV nao encontrado: {csv_path}")
        sys.exit(1)

    agentes = args.agentes if args.agentes is not None else [1, 2, 3, 5]
    run_pipeline(csv_path, agentes, args.force, args.cap)

if __name__ == "__main__":
    main()
