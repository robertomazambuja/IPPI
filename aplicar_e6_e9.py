#!/usr/bin/env python3
"""
Aplica E9 e E6 ao pipeline.py de forma atômica.
Executa: python aplicar_e6_e9.py
"""
import re
import sys
from pathlib import Path

SRC = Path(__file__).parent / "pipeline.py"

# ── lê o arquivo ──────────────────────────────────────────────────────────────
src = SRC.read_text(encoding="utf-8")
original_len = len(src)

changes = []

# ══════════════════════════════════════════════════════════════════════════════
# MUDANÇA 1 — inserir extract_core_summary() e _with_cache() antes de
#             _write_usage_csv()
# ══════════════════════════════════════════════════════════════════════════════

ANCHOR_1 = 'def _write_usage_csv(row: dict):\n    """Grava uma linha no CSV de usage (thread-safe)."""'

INSERT_1 = '''\
def extract_core_summary(core_path: Path, cap_idx: int, cap_name: str) -> str:
    """Extrai SINTESE_FINAL, ENCADEAMENTO e autores de um core.md (sem LLM).

    Retorna bloco compacto para injetar no user_message do A1, substituindo
    a leitura do core completo via read_file (E9).
    Nunca levanta exceção — fallback legível em caso de erro.
    """
    try:
        content = core_path.read_text(encoding="utf-8")
    except Exception as e:
        return f"--- Cap. {cap_idx}: {cap_name} ---\\n[SUMÁRIO INDISPONÍVEL — erro ao ler: {e}]\\n"

    m = re.search(r\'SINTESE_FINAL:\\s*"(.*?)"\', content, re.DOTALL)
    if not m:
        m = re.search(r\'SINTESE_FINAL:\\s*([^\\n]+)\', content)
    sintese = m.group(1).strip() if m else "(não encontrado)"

    m = re.search(r\'ENCADEAMENTO:\\s*"(.*?)"\', content, re.DOTALL)
    if not m:
        m = re.search(r\'ENCADEAMENTO:\\s*([^\\n]+)\', content)
    encadeamento = m.group(1).strip() if m else "(não encontrado)"

    autores: list = []
    for m in re.finditer(r\'^AUTOR(?:_SECUNDARIO)?:\\s*"?([^"\\n]+)"?\\s*$\', content, re.MULTILINE):
        valor = m.group(1).strip()
        if valor.lower() == "vazio":
            continue
        nome = valor.split("(")[0].strip()
        if nome and nome not in autores:
            autores.append(nome)

    autores_str = ", ".join(autores) if autores else "(nenhum)"
    return (
        f"--- Cap. {cap_idx}: {cap_name} ---\\n"
        f"SÍNTESE: {sintese}\\n"
        f"ENCADEAMENTO: {encadeamento}\\n"
        f"AUTORES USADOS: {autores_str}\\n"
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


''' + ANCHOR_1

assert ANCHOR_1 in src, "ANCHOR_1 não encontrado"
src = src.replace(ANCHOR_1, INSERT_1, 1)
changes.append("✓ extract_core_summary() e _with_cache() inseridos")

# ══════════════════════════════════════════════════════════════════════════════
# MUDANÇA 2 — substituir bloco de cores anteriores em run_agente1() (E9)
# ══════════════════════════════════════════════════════════════════════════════

OLD_CORES = (
    "    # Cores anteriores (mantidos como read_file — serão otimizados na Fase 2 com E9)\n"
    "    cores_anteriores_section = \"\"\n"
    "    arquivos_cores = \"\"\n"
    "\n"
    "    if capitulo_idx > 1:\n"
    "        cores_anteriores = []\n"
    "        for prev_c_idx in range(1, capitulo_idx):\n"
    "            prev_cap_name = capitulos_da_unidade[prev_c_idx - 1]\n"
    "            prev_filename = capitulo_filename(unidade_idx, prev_c_idx, prev_cap_name)\n"
    "            prev_core_rel = f\"output/{apostila_name}/core/{unidade_slug}/{prev_filename}\"\n"
    "            prev_core_path = BASE_DIR / prev_core_rel\n"
    "            if prev_core_path.exists():\n"
    "                cores_anteriores.append((prev_c_idx, prev_cap_name, prev_core_rel))\n"
    "\n"
    "        if cores_anteriores:\n"
    "            cores_anteriores_section = \"\\nCAPÍTULOS ANTERIORES DESTA UNIDADE:\\n\"\n"
    "            for idx, cap_name, rel_path in cores_anteriores:\n"
    "                cores_anteriores_section += f\"  - Capítulo {idx}: {cap_name}\\n    {rel_path}\\n\"\n"
    "            cores_anteriores_section += \"\\n\"\n"
    "            arquivos_cores = \"ARQUIVOS QUE VOCÊ DEVE LER (cores anteriores — use read_file):\\n\"\n"
    "            for idx, cap_name, rel_path in cores_anteriores:\n"
    "                arquivos_cores += f\"  - {rel_path}\\n\"\n"
    "            arquivos_cores += \"\\n\""
)

NEW_CORES = (
    "    # Cores anteriores — sumário compacto extraído em Python (E9)\n"
    "    # Substitui read_file dos cores completos (~1.000-1.600 tokens cada)\n"
    "    # por ~250-300 tokens por capítulo com SINTESE_FINAL, ENCADEAMENTO e autores.\n"
    "    # Nota: a skill do A1 diz \"Leia-os\" para cores anteriores — o user_message\n"
    "    # abaixo sobrescreve com \"não leia os cores completos\".\n"
    "    cores_anteriores_section = \"\"\n"
    "\n"
    "    if capitulo_idx > 1:\n"
    "        summaries = []\n"
    "        for prev_c_idx in range(1, capitulo_idx):\n"
    "            prev_cap_name = capitulos_da_unidade[prev_c_idx - 1]\n"
    "            prev_filename = capitulo_filename(unidade_idx, prev_c_idx, prev_cap_name)\n"
    "            prev_core_path = BASE_DIR / f\"output/{apostila_name}/core/{unidade_slug}/{prev_filename}\"\n"
    "            if prev_core_path.exists():\n"
    "                summaries.append(extract_core_summary(prev_core_path, prev_c_idx, prev_cap_name))\n"
    "\n"
    "        if summaries:\n"
    "            cores_anteriores_section = \"\\nSUMÁRIOS DOS CAPÍTULOS ANTERIORES DESTA UNIDADE:\\n\"\n"
    "            cores_anteriores_section += \"\\n\".join(summaries) + \"\\n\""
)

assert OLD_CORES in src, "ANCHOR_2 (cores anteriores) não encontrado"
src = src.replace(OLD_CORES, NEW_CORES, 1)
changes.append("✓ Bloco de cores anteriores substituído (E9)")

# ══════════════════════════════════════════════════════════════════════════════
# MUDANÇA 3 — user_message: remover {arquivos_cores}, adicionar instrução (E9)
# ══════════════════════════════════════════════════════════════════════════════

OLD_IMPORTANTE = (
    "{arquivos_cores}IMPORTANTE:\n"
    "- O andaime acima já prescreve as operações e a progressão de micro-habilidades\n"
    "- Você NÃO precisa inventar a estrutura — ela já está definida\n"
    "- Seu trabalho é CONCRETIZAR: escolher exemplos âncora, pesos das seções, fontes primárias, verificações\n"
    "- Os princípios pedagógicos e o contexto disciplinar já estão acima — não é necessário ler esses arquivos\n"
    "- Garanta que cada micro-habilidade seja alcançável e progressiva em relação à anterior"
)

NEW_IMPORTANTE = (
    "IMPORTANTE:\n"
    "- O andaime acima já prescreve as operações e a progressão de micro-habilidades\n"
    "- Você NÃO precisa inventar a estrutura — ela já está definida\n"
    "- Seu trabalho é CONCRETIZAR: escolher exemplos âncora, pesos das seções, fontes primárias, verificações\n"
    "- Os princípios pedagógicos e o contexto disciplinar já estão acima — não é necessário ler esses arquivos\n"
    "- Os sumários dos capítulos anteriores já estão acima — não leia os cores completos\n"
    "- Garanta que cada micro-habilidade seja alcançável e progressiva em relação à anterior"
)

assert OLD_IMPORTANTE in src, "ANCHOR_3 (IMPORTANTE) não encontrado"
src = src.replace(OLD_IMPORTANTE, NEW_IMPORTANTE, 1)
changes.append("✓ user_message atualizado: {arquivos_cores} removido, instrução de não leitura adicionada")

# ══════════════════════════════════════════════════════════════════════════════
# MUDANÇA 4 — messages=_with_cache(messages) em run_agent() (E6)
# ══════════════════════════════════════════════════════════════════════════════

OLD_MSG = "                    messages=messages,"
NEW_MSG = "                    messages=_with_cache(messages),"

assert OLD_MSG in src, "ANCHOR_4 (messages=messages) não encontrado"
src = src.replace(OLD_MSG, NEW_MSG, 1)
changes.append("✓ messages=_with_cache(messages) aplicado em run_agent()")

# ── valida sintaxe antes de gravar ────────────────────────────────────────────
import ast
try:
    ast.parse(src)
except SyntaxError as e:
    print(f"ERRO DE SINTAXE: {e}")
    sys.exit(1)

# ── grava ─────────────────────────────────────────────────────────────────────
SRC.write_text(src, encoding="utf-8")

print(f"pipeline.py atualizado ({original_len} → {len(src)} chars, {src.count(chr(10))} linhas)")
for c in changes:
    print(c)
print("\nVerificações:")
print(f"  arquivos_cores restantes : {src.count('arquivos_cores')}")
print(f"  extract_core_summary     : {src.count('extract_core_summary')}")
print(f"  _with_cache              : {src.count('_with_cache')}")
print(f"  não leia os cores        : {src.count('não leia os cores completos')}")
