"""
Testes unitários para funções críticas do pipeline IPPI.
Executar: python -m pytest tests/ -v  (de dentro da pasta do projeto)
"""
import csv
import os
import sys
import shutil
import tempfile
from pathlib import Path

import pytest

# Adiciona a raiz do projeto ao path para importar pipeline
sys.path.insert(0, str(Path(__file__).parent.parent))
import pipeline


# ─── Fixture de diretório temporário fora do filesystem montado ──────────────

@pytest.fixture
def tmp(request):
    """Diretório temporário em /tmp — sem restrições de permissão."""
    d = tempfile.mkdtemp(prefix="ippi_test_")
    yield Path(d)
    shutil.rmtree(d, ignore_errors=True)


# ─── slugify ────────────────────────────────────────────────────────────────

class TestSlugify:
    def test_lowercase(self):
        assert pipeline.slugify("Filosofia") == "filosofia"

    def test_acento_agudo(self):
        assert pipeline.slugify("História") == "historia"

    def test_acento_til(self):
        assert pipeline.slugify("Educação") == "educacao"

    def test_cedilha(self):
        assert pipeline.slugify("Conceituação") == "conceituacao"

    def test_espacos_viram_hifen(self):
        assert pipeline.slugify("Meios de Comunicação") == "meios-de-comunicacao"

    def test_hifen_duplo_colapsa(self):
        assert pipeline.slugify("A--B") == "a-b"

    def test_caracteres_especiais_removidos(self):
        assert pipeline.slugify("A (1)") == "a-1"

    def test_string_vazia(self):
        assert pipeline.slugify("") == ""

    def test_sem_hifen_nas_bordas(self):
        result = pipeline.slugify("  espaço  ")
        assert not result.startswith("-")
        assert not result.endswith("-")


# ─── capitulo_filename ───────────────────────────────────────────────────────

class TestCapituloFilename:
    def test_formato_basico(self):
        result = pipeline.capitulo_filename(1, 1, "Conceitos fundamentais")
        assert result == "01-01-conceitos-fundamentais.md"

    def test_zero_padding(self):
        result = pipeline.capitulo_filename(2, 9, "Algo")
        assert result == "02-09-algo.md"

    def test_dois_digitos(self):
        result = pipeline.capitulo_filename(10, 12, "Fim")
        assert result == "10-12-fim.md"

    def test_com_acento(self):
        result = pipeline.capitulo_filename(1, 3, "Introdução")
        assert result == "01-03-introducao.md"

    def test_extensao_md(self):
        result = pipeline.capitulo_filename(1, 1, "Teste")
        assert result.endswith(".md")


# ─── parse_csv ───────────────────────────────────────────────────────────────

COLUNAS = [
    "disciplina", "unidade", "pergunta_unidade", "capitulo",
    "habilidade", "conteudos_nucleares", "autores", "elementos_obrigatorios",
]


def _make_csv(directory: Path, rows: list, fieldnames=None) -> Path:
    """Helper: escreve CSV temporário e retorna o path."""
    path = directory / "instrucoes.csv"
    fieldnames = fieldnames or COLUNAS
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


class TestParseCsv:
    def test_csv_valido(self, tmp):
        row = {col: f"valor_{col}" for col in COLUNAS}
        path = _make_csv(tmp, [row])
        result = pipeline.parse_csv(path)
        assert len(result) == 1
        assert result[0]["disciplina"] == "valor_disciplina"

    def test_multiplas_linhas(self, tmp):
        rows = [{col: f"v{i}_{col}" for col in COLUNAS} for i in range(3)]
        path = _make_csv(tmp, rows)
        result = pipeline.parse_csv(path)
        assert len(result) == 3

    def test_arquivo_inexistente(self, tmp):
        with pytest.raises(FileNotFoundError):
            pipeline.parse_csv(tmp / "nao_existe.csv")

    def test_coluna_faltando(self, tmp):
        colunas_incompletas = [c for c in COLUNAS if c != "habilidade"]
        row = {col: "x" for col in colunas_incompletas}
        path = _make_csv(tmp, [row], fieldnames=colunas_incompletas)
        with pytest.raises(ValueError, match="habilidade"):
            pipeline.parse_csv(path)

    def test_schema_antigo_habilidade_principal_rejeitado(self, tmp):
        """Garante que o schema antigo (habilidade_principal) é rejeitado."""
        colunas_antigas = [
            c if c != "habilidade" else "habilidade_principal" for c in COLUNAS
        ]
        row = {col: "x" for col in colunas_antigas}
        path = _make_csv(tmp, [row], fieldnames=colunas_antigas)
        with pytest.raises(ValueError):
            pipeline.parse_csv(path)

    def test_celula_vazia_obrigatoria(self, tmp):
        row = {col: "x" for col in COLUNAS}
        row["capitulo"] = "   "
        path = _make_csv(tmp, [row])
        with pytest.raises(ValueError, match="capitulo"):
            pipeline.parse_csv(path)

    def test_csv_vazio(self, tmp):
        path = tmp / "vazio.csv"
        path.write_text("")
        with pytest.raises((ValueError, Exception)):
            pipeline.parse_csv(path)


# ─── _validate_path ──────────────────────────────────────────────────────────

class TestValidatePath:
    def test_path_dentro_do_projeto(self):
        path = pipeline.BASE_DIR / "pipeline.py"
        assert pipeline._validate_path(path) is None

    def test_path_fora_do_projeto(self):
        path = pipeline.BASE_DIR / ".." / ".." / ".env"
        result = pipeline._validate_path(path)
        assert result is not None
        assert "ERRO" in result

    def test_path_exatamente_na_raiz(self):
        path = pipeline.BASE_DIR / "qualquer_arquivo.txt"
        assert pipeline._validate_path(path) is None

    def test_path_traversal_classico(self):
        result = pipeline._validate_path(pipeline.BASE_DIR / "../../etc/passwd")
        assert result is not None


# ─── execute_tool ────────────────────────────────────────────────────────────

class TestExecuteTool:
    def test_ferramenta_desconhecida(self):
        result = pipeline.execute_tool("ferramenta_invalida", {})
        assert "desconhecida" in result.lower() or "Ferramenta" in result

    def test_read_file_path_traversal_bloqueado(self):
        result = pipeline.execute_tool("read_file", {"path": "../../.env"})
        assert "ERRO" in result

    def test_write_file_path_traversal_bloqueado(self):
        result = pipeline.execute_tool("write_file", {
            "path": "../../malicious.txt",
            "content": "pwned",
        })
        assert "ERRO" in result

    def test_read_file_existente(self, tmp, monkeypatch):
        monkeypatch.setattr(pipeline, "BASE_DIR", tmp)
        test_file = tmp / "teste.md"
        test_file.write_text("conteúdo de teste", encoding="utf-8")
        result = pipeline.execute_tool("read_file", {"path": "teste.md"})
        assert "conteúdo de teste" in result

    def test_write_file_cria_arquivo(self, tmp, monkeypatch):
        monkeypatch.setattr(pipeline, "BASE_DIR", tmp)
        result = pipeline.execute_tool("write_file", {
            "path": "novo_arquivo.md",
            "content": "texto salvo",
        })
        assert "salvo" in result.lower() or "Arquivo" in result
        assert (tmp / "novo_arquivo.md").read_text(encoding="utf-8") == "texto salvo"
