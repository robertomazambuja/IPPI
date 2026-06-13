#!/usr/bin/env python3
"""
Script de teste para extract_core_summary().

Roda contra os cores reais em output/ e imprime:
  - O bloco compacto que seria injetado no user_message
  - Comparação de tamanho (tokens estimados) vs. core completo
  - Verificação de que os três campos foram encontrados

Uso:
    python teste_extract_core_summary.py
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent

# ─── Função candidata ────────────────────────────────────────────────────────

def extract_core_summary(core_path: Path, cap_idx: int, cap_name: str) -> str:
    """
    Lê um core.md e extrai SINTESE_FINAL, ENCADEAMENTO e autores usados.
    Retorna bloco compacto para injetar no user_message do A1.
    Nunca levanta exceção — fallback legível em caso de erro.
    """
    try:
        content = core_path.read_text(encoding="utf-8")
    except Exception as e:
        return f"--- Cap. {cap_idx}: {cap_name} ---\n[SUMÁRIO INDISPONÍVEL — erro ao ler arquivo: {e}]\n"

    # SINTESE_FINAL — tenta quoted primeiro, depois unquoted
    m = re.search(r'SINTESE_FINAL:\s*"(.*?)"', content, re.DOTALL)
    if not m:
        m = re.search(r'SINTESE_FINAL:\s*([^\n]+)', content)
    sintese = m.group(1).strip() if m else "(não encontrado)"

    # ENCADEAMENTO
    m = re.search(r'ENCADEAMENTO:\s*"(.*?)"', content, re.DOTALL)
    if not m:
        m = re.search(r'ENCADEAMENTO:\s*([^\n]+)', content)
    encadeamento = m.group(1).strip() if m else "(não encontrado)"

    # Autores — campos AUTOR: e AUTOR_SECUNDARIO: em qualquer seção
    autores = []
    for m in re.finditer(r'^AUTOR(?:_SECUNDARIO)?:\s*"?([^"\n]+)"?\s*$', content, re.MULTILINE):
        valor = m.group(1).strip()
        if valor.lower() == "vazio":
            continue
        nome = valor.split("(")[0].strip()  # só o nome, sem datas/filiação
        if nome and nome not in autores:
            autores.append(nome)

    autores_str = ", ".join(autores) if autores else "(nenhum)"

    return (
        f"--- Cap. {cap_idx}: {cap_name} ---\n"
        f"SÍNTESE: {sintese}\n"
        f"ENCADEAMENTO: {encadeamento}\n"
        f"AUTORES USADOS: {autores_str}\n"
    )


# ─── Estimativa de tokens (aproximação: 1 token ≈ 4 caracteres) ──────────────

def estimar_tokens(texto: str) -> int:
    return max(1, len(texto) // 4)


# ─── Runner ──────────────────────────────────────────────────────────────────

def main():
    cores_dir = BASE_DIR / "output"
    core_files = sorted(cores_dir.rglob("*.md"))
    core_files = [f for f in core_files if "/core/" in f.as_posix()]

    if not core_files:
        print("Nenhum core.md encontrado em output/. Verifique o caminho.")
        return

    print(f"{'='*70}")
    print(f"TESTE DE extract_core_summary() — {len(core_files)} core(s) encontrado(s)")
    print(f"{'='*70}\n")

    total_original_tokens = 0
    total_summary_tokens = 0

    for core_path in core_files:
        # Derive cap_idx e cap_name do nome do arquivo (ex: 01-02-nome.md)
        stem = core_path.stem  # ex: "01-02-capitulo-2-escravidao..."
        parts = stem.split("-", 2)
        try:
            cap_idx = int(parts[1])
            cap_name = parts[2].replace("-", " ").title() if len(parts) > 2 else stem
        except (ValueError, IndexError):
            cap_idx = 0
            cap_name = stem

        original_content = core_path.read_text(encoding="utf-8")
        summary = extract_core_summary(core_path, cap_idx, cap_name)

        orig_tokens = estimar_tokens(original_content)
        summ_tokens = estimar_tokens(summary)
        reducao = 100 * (1 - summ_tokens / orig_tokens)

        total_original_tokens += orig_tokens
        total_summary_tokens += summ_tokens

        print(f"Arquivo : {core_path.relative_to(BASE_DIR)}")
        print(f"Tamanho : {len(original_content):,} chars  (~{orig_tokens} tokens)  →  sumário: {len(summary):,} chars (~{summ_tokens} tokens)  [{reducao:.0f}% menor]")
        print()
        print("── SUMÁRIO GERADO ──────────────────────────────────────────────────")
        print(summary)

        # Diagnóstico: campos encontrados?
        issues = []
        if "não encontrado" in summary:
            issues.append("⚠️  Campo não encontrado — verifique o regex")
        if "(nenhum)" in summary:
            issues.append("⚠️  Nenhum autor extraído — verifique o padrão AUTOR:")
        if issues:
            for issue in issues:
                print(issue)
        else:
            print("✅ Todos os campos extraídos com sucesso")
        print(f"{'─'*70}\n")

    if len(core_files) > 1:
        reducao_total = 100 * (1 - total_summary_tokens / total_original_tokens)
        print(f"{'='*70}")
        print(f"TOTAL  — Original: ~{total_original_tokens} tokens  →  Sumários: ~{total_summary_tokens} tokens  [{reducao_total:.0f}% menor]")
        print(f"{'='*70}")

        print("\n── SIMULAÇÃO: bloco que seria injetado para o capítulo 2 (1 sumário anterior) ──")
        if len(core_files) >= 1:
            c = core_files[0]
            stem = c.stem
            parts = stem.split("-", 2)
            cap_idx = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
            cap_name = parts[2].replace("-", " ").title() if len(parts) > 2 else stem
            bloco = "\nSUMÁRIOS DOS CAPÍTULOS ANTERIORES DESTA UNIDADE:\n"
            bloco += extract_core_summary(c, cap_idx, cap_name)
            print(bloco)
            print(f"(~{estimar_tokens(bloco)} tokens injetados no user_message em vez de ~{estimar_tokens(c.read_text(encoding='utf-8'))} tokens de read_file)")


if __name__ == "__main__":
    main()
