"""
tests/test_normalizador.py — Testes do normalizador.py

Fixtures reais: os dois capítulos de apostila-teste-historia-em1 já existem
no repositório e servem de base para os testes de idempotência.

Testes unitários cobrem cada uma das 4 normalizações com entradas sintéticas.
"""

import pytest
from pathlib import Path
from normalizador import _normalizar, normalizar_texto, TIPOS_CONHECIDOS

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BASE = Path(__file__).parent.parent


def texto_fixture(capitulo: str) -> str:
    return (
        BASE
        / "output"
        / "apostila-teste-historia-em1"
        / "texto"
        / "unidade-1-justica-estado-e-poder-no-brasil-imperial"
        / capitulo
    ).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Idempotência nos fixtures reais
# ---------------------------------------------------------------------------

class TestIdempotencia:
    """
    Roda o normalizador nos arquivos reais e verifica que o resultado
    é idêntico ao original EXCETO pela remoção dos AVISOs incorretos
    de TIPO_OPERACAO (que estavam nos arquivos antes de TIPO_OPERACAO
    ser adicionado à lista de tipos conhecidos).
    """

    @pytest.mark.parametrize("cap", [
        "01-01-capitulo-1-formacao-do-estado-imperial-e-organizacao-da-justica.md",
        "01-02-capitulo-2-escravidao-direitos-e-crise-do-imperio.md",
    ])
    def test_segunda_rodada_sem_alteracoes(self, cap, tmp_path):
        """
        Depois de uma primeira rodada (que remove os AVISOs incorretos),
        a segunda rodada não deve produzir mais nenhuma alteração.
        """
        original = texto_fixture(cap)
        # Primeira rodada
        resultado1, avisos1 = _normalizar(original)
        # Segunda rodada — deve ser idempotente
        resultado2, avisos2 = _normalizar(resultado1)
        assert resultado1 == resultado2, (
            "Normalizador não é idempotente. "
            f"Avisos segunda rodada: {avisos2}"
        )

    @pytest.mark.parametrize("cap", [
        "01-01-capitulo-1-formacao-do-estado-imperial-e-organizacao-da-justica.md",
        "01-02-capitulo-2-escravidao-direitos-e-crise-do-imperio.md",
    ])
    def test_remove_avisos_incorretos_tipo_operacao(self, cap):
        """
        Os arquivos existentes têm AVISOs para TIPO_OPERACAO (que era
        'desconhecido' antes da correção da Fase 1). O normalizador deve
        removê-los, pois TIPO_OPERACAO está na lista de tipos conhecidos.
        """
        original = texto_fixture(cap)
        assert "AVISO_AGENTE5: tipo TIPO_OPERACAO" in original, (
            "Fixture não contém o AVISO incorreto esperado — "
            "verifique se o arquivo está no estado pré-normalização."
        )
        resultado, avisos = _normalizar(original)
        assert "AVISO_AGENTE5: tipo TIPO_OPERACAO" not in resultado
        assert any("TIPO_OPERACAO" in a for a in avisos)

    @pytest.mark.parametrize("cap", [
        "01-01-capitulo-1-formacao-do-estado-imperial-e-organizacao-da-justica.md",
        "01-02-capitulo-2-escravidao-direitos-e-crise-do-imperio.md",
    ])
    def test_preserva_prosa(self, cap):
        """
        Texto visível (fora de HTML comments) não deve ser alterado.
        """
        original = texto_fixture(cap)
        resultado, _ = _normalizar(original)
        # Remove todas as linhas de HTML comment antes de comparar prosa
        def prose(t):
            return "\n".join(
                l for l in t.split("\n")
                if not l.strip().startswith("<!--")
            )
        assert prose(original) == prose(resultado)

    @pytest.mark.parametrize("cap", [
        "01-01-capitulo-1-formacao-do-estado-imperial-e-organizacao-da-justica.md",
        "01-02-capitulo-2-escravidao-direitos-e-crise-do-imperio.md",
    ])
    def test_mantém_aviso_sintese_final(self, cap):
        """
        SINTESE_FINAL é um tipo desconhecido — seu AVISO deve ser mantido.
        """
        original = texto_fixture(cap)
        resultado, _ = _normalizar(original)
        assert "SINTESE_FINAL" in resultado
        assert "AVISO_AGENTE5: tipo SINTESE_FINAL" in resultado


# ---------------------------------------------------------------------------
# N1 — CONTEXTO_OPERACAO
# ---------------------------------------------------------------------------

class TestN1ContextoOperacao:

    def test_formato_html_comment_convertido(self):
        texto = (
            "<!-- [CONTEXTO_OPERACAO] -->\n"
            "<!-- Habilidade: H12 — Texto da habilidade. -->\n"
            "<!-- Operação principal: Definir -->\n"
            "<!-- Pergunta do capítulo: Qual é a pergunta? -->\n"
            "<!-- Por que importa: Porque sim. -->\n"
            "<!-- [/CONTEXTO_OPERACAO] -->"
        )
        resultado, avisos = _normalizar(texto)
        assert "**Habilidade:** H12 — Texto da habilidade." in resultado
        assert "**Operação principal:** Definir" in resultado
        assert "**Pergunta do capítulo:** Qual é a pergunta?" in resultado
        assert "**Por que importa:** Porque sim." in resultado
        # Tags originais em comment não devem aparecer
        assert "<!-- Habilidade:" not in resultado

    def test_formato_bold_ja_correto_nao_alterado(self):
        texto = (
            "<!-- [CONTEXTO_OPERACAO] -->\n"
            "**Habilidade:** H12 — Texto.\n"
            "**Operação principal:** Definir\n"
            "**Pergunta do capítulo:** Qual?\n"
            "**Por que importa:** Porque.\n"
            "<!-- [/CONTEXTO_OPERACAO] -->"
        )
        resultado, avisos = _normalizar(texto)
        assert resultado == texto
        assert avisos == []

    def test_campo_ausente_recebe_marcador(self):
        texto = (
            "<!-- [CONTEXTO_OPERACAO] -->\n"
            "**Habilidade:** H12 — Texto.\n"
            "**Operação principal:** Definir\n"
            "<!-- [/CONTEXTO_OPERACAO] -->"
        )
        resultado, _ = _normalizar(texto)
        assert "**Pergunta do capítulo:** [AUSENTE]" in resultado
        assert "**Por que importa:** [AUSENTE]" in resultado

    def test_idempotente_com_ausente(self):
        texto = (
            "<!-- [CONTEXTO_OPERACAO] -->\n"
            "**Habilidade:** H12 — Texto.\n"
            "**Operação principal:** Definir\n"
            "<!-- [/CONTEXTO_OPERACAO] -->"
        )
        r1, _ = _normalizar(texto)
        r2, avisos2 = _normalizar(r1)
        assert r1 == r2
        assert avisos2 == []


# ---------------------------------------------------------------------------
# N2 — FONTE
# ---------------------------------------------------------------------------

class TestN2Fonte:

    def test_formato_a_convertido_para_c(self):
        """Conteúdo embutido na tag de abertura → Formato C."""
        texto = (
            "<!-- [FONTE: MATTOS, Ilmar. *O Tempo Saquarema*. 1987.] -->\n"
            "<!-- [/FONTE] -->"
        )
        resultado, avisos = _normalizar(texto)
        assert "<!-- [FONTE] -->" in resultado
        assert "MATTOS, Ilmar. *O Tempo Saquarema*. 1987." in resultado
        assert "<!-- [/FONTE] -->" in resultado
        # Tag de abertura com conteúdo não deve aparecer
        assert "<!-- [FONTE: MATTOS" not in resultado
        assert any("FONTE" in a or resultado != texto for a in avisos) or resultado != texto

    def test_formato_c_ja_correto_nao_alterado(self):
        texto = (
            "<!-- [FONTE] -->\n"
            "MATTOS, Ilmar. *O Tempo Saquarema*. 1987.\n"
            "<!-- [/FONTE] -->"
        )
        resultado, avisos = _normalizar(texto)
        assert resultado == texto
        assert avisos == []

    def test_multiplas_aberturas_mescladas(self):
        """Múltiplas tags de abertura antes de um único fechamento → um bloco."""
        texto = (
            "<!-- [FONTE: FAUSTO, Boris. *História do Brasil*. 1994.] -->\n"
            "<!-- [FONTE: SCHWARCZ, Lilia. *As Barbas*. 1998.] -->\n"
            "<!-- [/FONTE] -->"
        )
        resultado, _ = _normalizar(texto)
        linhas = resultado.split("\n")
        # Deve haver apenas um <!-- [FONTE] --> e um <!-- [/FONTE] -->
        assert linhas.count("<!-- [FONTE] -->") == 1
        assert linhas.count("<!-- [/FONTE] -->") == 1
        assert "FAUSTO, Boris. *História do Brasil*. 1994." in resultado
        assert "SCHWARCZ, Lilia. *As Barbas*. 1998." in resultado

    def test_formato_b_linha_duplicada_descartada(self):
        """Conteúdo duplicado via **Fonte:** deve ser descartado."""
        texto = (
            "<!-- [FONTE: CHALHOUB, Visões da liberdade, 1990] -->\n"
            "**Fonte:** CHALHOUB, Sidney. *Visões da liberdade*. 1990.\n"
            "<!-- [/FONTE] -->"
        )
        resultado, avisos = _normalizar(texto)
        assert "**Fonte:**" not in resultado
        assert "CHALHOUB, Visões da liberdade, 1990" in resultado
        assert any("Formato B" in a for a in avisos)

    def test_fonte_dentro_de_bloco_pai(self):
        """FONTE dentro de DEFINICAO deve ser normalizado corretamente."""
        texto = (
            "<!-- [DEFINICAO] -->\n"
            "Texto da definição.\n"
            "<!-- [FONTE: MATTOS, Ilmar. *O Tempo*. 1987.] -->\n"
            "<!-- [/FONTE] -->\n"
            "<!-- [/DEFINICAO] -->"
        )
        resultado, _ = _normalizar(texto)
        assert "<!-- [FONTE] -->" in resultado
        assert "MATTOS, Ilmar. *O Tempo*. 1987." in resultado
        assert "<!-- [FONTE: MATTOS" not in resultado


# ---------------------------------------------------------------------------
# N3 — AUTOR
# ---------------------------------------------------------------------------

class TestN3Autor:

    def test_autor_solto_recebe_ref(self):
        """AUTOR fora de qualquer bloco sem ref= deve receber ref= do último bloco fechado."""
        texto = (
            "<!-- [CONCLUSAO_PARCIAL] -->\n"
            "Texto da conclusão.\n"
            "<!-- [/CONCLUSAO_PARCIAL] -->\n"
            "\n"
            "<!-- [AUTOR: Boris Fausto (1930–2019) Brasil] -->\n"
            "Bio do autor.\n"
            "<!-- [/AUTOR] -->"
        )
        resultado, avisos = _normalizar(texto)
        assert "ref=conclusao-parcial" in resultado
        assert any("ref=conclusao-parcial" in a for a in avisos)

    def test_autor_dentro_de_bloco_nao_alterado(self):
        """AUTOR dentro de um bloco pai não deve receber ref=."""
        texto = (
            "<!-- [DEFINICAO] -->\n"
            "Texto.\n"
            "<!-- [AUTOR: Ilmar Mattos (1944–) Brasil] -->\n"
            "Bio.\n"
            "<!-- [/AUTOR] -->\n"
            "<!-- [/DEFINICAO] -->"
        )
        resultado, avisos = _normalizar(texto)
        assert "ref=" not in resultado
        assert not any("ref=" in a for a in avisos)

    def test_autor_com_ref_existente_nao_alterado(self):
        """AUTOR já com ref= não deve ser modificado."""
        texto = (
            "<!-- [/RELACAO_CAUSAL] -->\n"
            "<!-- [AUTOR: Emília Viotti (1928–2017) Brasil | ref=relacao-causal] -->\n"
            "Bio.\n"
            "<!-- [/AUTOR] -->"
        )
        resultado, avisos = _normalizar(texto)
        assert "ref=relacao-causal" in resultado
        # Não deve duplicar o ref=
        assert resultado.count("ref=relacao-causal") == 1
        assert not any("Adicionado ref=" in a for a in avisos)

    def test_dois_autores_consecutivos_mesmo_pai(self):
        """Dois AUTOREs soltos após o mesmo bloco recebem o mesmo ref=."""
        texto = (
            "<!-- [RELACAO_CAUSAL] -->\n"
            "Texto.\n"
            "<!-- [/RELACAO_CAUSAL] -->\n"
            "<!-- [AUTOR: Boris Fausto (1930–2019) Brasil] -->\n"
            "Bio1.\n"
            "<!-- [/AUTOR] -->\n"
            "<!-- [AUTOR: Lilia Schwarcz (1957–) Brasil] -->\n"
            "Bio2.\n"
            "<!-- [/AUTOR] -->"
        )
        resultado, _ = _normalizar(texto)
        # Ambos devem ter ref=relacao-causal
        assert resultado.count("ref=relacao-causal") == 2


# ---------------------------------------------------------------------------
# N4 — Tipos desconhecidos
# ---------------------------------------------------------------------------

class TestN4TiposDesconhecidos:

    def test_tipo_desconhecido_recebe_aviso(self):
        texto = (
            "<!-- [TIPO_NOVO] -->\n"
            "Conteúdo.\n"
            "<!-- [/TIPO_NOVO] -->"
        )
        resultado, avisos = _normalizar(texto)
        assert 'AVISO_AGENTE5: tipo TIPO_NOVO não mapeado' in resultado
        assert any("TIPO_NOVO" in a for a in avisos)

    def test_aviso_nao_duplicado_se_ja_presente(self):
        """Se o AVISO já está na linha seguinte, não adicionar outro."""
        texto = (
            "<!-- [TIPO_NOVO] -->\n"
            '<!-- AVISO_AGENTE5: tipo TIPO_NOVO não mapeado — gerar secao tipo="generico" -->\n'
            "Conteúdo.\n"
            "<!-- [/TIPO_NOVO] -->"
        )
        resultado, _ = _normalizar(texto)
        assert resultado.count("AVISO_AGENTE5: tipo TIPO_NOVO") == 1

    def test_aviso_incorreto_tipo_conhecido_removido(self):
        """AVISO para tipo CONHECIDO deve ser removido."""
        texto = (
            "<!-- [TIPO_OPERACAO: Definir] -->\n"
            '<!-- AVISO_AGENTE5: tipo TIPO_OPERACAO não mapeado — gerar secao tipo="generico" -->\n'
            "Conteúdo.\n"
        )
        resultado, avisos = _normalizar(texto)
        assert "AVISO_AGENTE5: tipo TIPO_OPERACAO" not in resultado
        assert any("TIPO_OPERACAO" in a and "Removido" in a for a in avisos)

    def test_todos_tipos_conhecidos_sem_aviso(self):
        """Nenhum tipo da lista conhecida deve gerar AVISO."""
        for tipo in sorted(TIPOS_CONHECIDOS):
            # Tipos com conteúdo obrigatório na tag (AUTOR, SUBTIPO, etc.)
            # usam um placeholder
            texto = f"<!-- [{tipo}: placeholder] -->\nTexto.\n<!-- [/{tipo}] -->"
            resultado, avisos = _normalizar(texto)
            aviso_inesperado = [
                a for a in avisos
                if "Adicionado AVISO" in a and tipo in a
            ]
            assert not aviso_inesperado, (
                f"AVISO gerado indevidamente para tipo conhecido: {tipo}"
            )

    def test_sintese_final_desconhecido_mantem_aviso(self):
        """SINTESE_FINAL é desconhecido e deve manter o AVISO."""
        texto = (
            "<!-- [SINTESE_FINAL] -->\n"
            '<!-- AVISO_AGENTE5: tipo SINTESE_FINAL não mapeado — gerar secao tipo="generico" -->\n'
            "Texto da síntese.\n"
            "<!-- [/SINTESE_FINAL] -->"
        )
        resultado, _ = _normalizar(texto)
        assert "AVISO_AGENTE5: tipo SINTESE_FINAL" in resultado
        assert "Texto da síntese." in resultado

    def test_conteudo_tipo_desconhecido_preservado(self):
        """Conteúdo de tipo desconhecido nunca é descartado."""
        texto = (
            "<!-- [TIPO_RARO] -->\n"
            "Conteúdo importante que não pode ser perdido.\n"
            "<!-- [/TIPO_RARO] -->"
        )
        resultado, _ = _normalizar(texto)
        assert "Conteúdo importante que não pode ser perdido." in resultado


# ---------------------------------------------------------------------------
# Casos mistos e regressão
# ---------------------------------------------------------------------------

class TestCasosMistos:

    def test_multiplas_normalizacoes_em_sequencia(self):
        """N1 + N2 + N4 no mesmo texto."""
        texto = (
            "<!-- [CONTEXTO_OPERACAO] -->\n"
            "<!-- Habilidade: H12 -->\n"
            "<!-- Operação principal: Definir -->\n"
            "<!-- Pergunta do capítulo: Qual? -->\n"
            "<!-- Por que importa: Porque. -->\n"
            "<!-- [/CONTEXTO_OPERACAO] -->\n"
            "\n"
            "<!-- [TIPO_OPERACAO: Definir] -->\n"
            '<!-- AVISO_AGENTE5: tipo TIPO_OPERACAO não mapeado — gerar secao tipo="generico" -->\n'
            "\n"
            "<!-- [DEFINICAO] -->\n"
            "Texto.\n"
            "<!-- [FONTE: AUTOR, Título. 2000.] -->\n"
            "<!-- [/FONTE] -->\n"
            "<!-- [/DEFINICAO] -->"
        )
        resultado, avisos = _normalizar(texto)
        # N1
        assert "**Habilidade:** H12" in resultado
        assert "<!-- Habilidade:" not in resultado
        # N2
        assert "<!-- [FONTE] -->" in resultado
        assert "AUTOR, Título. 2000." in resultado
        assert "<!-- [FONTE: AUTOR" not in resultado
        # N4 remoção de AVISO incorreto
        assert "AVISO_AGENTE5: tipo TIPO_OPERACAO" not in resultado

    def test_texto_sem_comentarios_nao_alterado(self):
        """Texto sem nenhum HTML comment não deve ser modificado."""
        texto = "## Título\n\nParágrafo de texto simples.\n\n### Seção\n\nMais texto."
        resultado, avisos = _normalizar(texto)
        assert resultado == texto
        assert avisos == []

    def test_normalizar_texto_arquivo_real(self, tmp_path):
        """normalizar_texto() funciona com arquivo real do repositório."""
        cap = "01-01-capitulo-1-formacao-do-estado-imperial-e-organizacao-da-justica.md"
        original_path = (
            BASE
            / "output"
            / "apostila-teste-historia-em1"
            / "texto"
            / "unidade-1-justica-estado-e-poder-no-brasil-imperial"
            / cap
        )
        # Copia para tmp_path para não modificar o fixture
        tmp_file = tmp_path / cap
        tmp_file.write_text(original_path.read_text(encoding="utf-8"), encoding="utf-8")

        from normalizador import normalizar_texto
        modified, avisos = normalizar_texto(tmp_file)

        # O arquivo tem AVISOs incorretos de TIPO_OPERACAO → deve ser modificado
        assert modified is True
        resultado = tmp_file.read_text(encoding="utf-8")
        assert "AVISO_AGENTE5: tipo TIPO_OPERACAO" not in resultado

        # Segunda rodada — sem mais alterações
        modified2, avisos2 = normalizar_texto(tmp_file)
        assert modified2 is False
        assert avisos2 == []
