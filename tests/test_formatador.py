"""
Testes para formatador.py (substitui Agente 5).
Usa o arquivo fixture real como fonte de verdade estrutural.
"""
import pytest
from pathlib import Path
from formatador import (
    tokenize, parse_document, formatar_capitulo,
    parse_section_group, Token,
)

FIXTURE = Path("output/apostila-teste-historia-em1/texto"
               "/unidade-1-justica-estado-e-poder-no-brasil-imperial"
               "/01-01-capitulo-1-formacao-do-estado-imperial-e-organizacao-da-justica.md")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_xml(tmp_path) -> str:
    result = formatar_capitulo(FIXTURE, tmp_path)
    assert result is not None and result.exists()
    return result.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Estrutura do documento
# ---------------------------------------------------------------------------

class TestEstruturaDocumento:

    def test_declaracao_xml(self, tmp_path):
        xml = get_xml(tmp_path)
        assert xml.startswith('<?xml version="1.0" encoding="UTF-8"?>')

    def test_elemento_raiz_capitulo(self, tmp_path):
        xml = get_xml(tmp_path)
        assert '<capitulo id="01-01"' in xml
        assert 'titulo="Formação do Estado Imperial e Organização da Justiça"' in xml

    def test_palavras_total_positivo(self, tmp_path):
        xml = get_xml(tmp_path)
        import re
        m = re.search(r'palavras_total="(\d+)"', xml)
        assert m and int(m.group(1)) > 1000

    def test_cabecalho_completo(self, tmp_path):
        xml = get_xml(tmp_path)
        assert "<habilidade>" in xml
        assert "<operacao_principal>Mapear causalidade</operacao_principal>" in xml
        assert "<pergunta_capitulo>" in xml
        assert "<por_que_importa>" in xml

    def test_corpo_presente(self, tmp_path):
        xml = get_xml(tmp_path)
        assert "<corpo>" in xml and "</corpo>" in xml

    def test_rodape_presente(self, tmp_path):
        xml = get_xml(tmp_path)
        assert "<rodape>" in xml and "</rodape>" in xml

    def test_encadeamento_no_rodape(self, tmp_path):
        xml = get_xml(tmp_path)
        rodape = xml.split("<rodape>")[1].split("</rodape>")[0]
        assert "<encadeamento>" in rodape

    def test_quatro_blocos(self, tmp_path):
        xml = get_xml(tmp_path)
        assert xml.count('<bloco id="bloco-') == 4

    def test_xml_bem_formado(self, tmp_path):
        import xml.etree.ElementTree as ET
        xml = get_xml(tmp_path)
        # Deve parsear sem excecao
        ET.fromstring(xml)


# ---------------------------------------------------------------------------
# Bloco 1 — DEFINICAO com 2 AUTORs aninhados
# ---------------------------------------------------------------------------

class TestBloco1Definicao:

    def test_operacao_definir(self, tmp_path):
        xml = get_xml(tmp_path)
        assert 'id="bloco-1"' in xml
        assert 'operacao="Definir"' in xml

    def test_secao_tipo_definicao(self, tmp_path):
        xml = get_xml(tmp_path)
        b1 = xml.split("bloco-1")[1].split("</bloco>")[0]
        assert 'tipo="definicao"' in b1

    def test_titulo_h3_na_secao(self, tmp_path):
        xml = get_xml(tmp_path)
        assert "<titulo>O Estado imperial brasileiro e sua estrutura jurídica</titulo>" in xml

    def test_dois_sidebars_autor(self, tmp_path):
        xml = get_xml(tmp_path)
        b1 = xml.split("bloco-1")[1].split("</bloco>")[0]
        assert b1.count('<sidebar tipo="autor">') == 2

    def test_autor_ilmar_presente(self, tmp_path):
        xml = get_xml(tmp_path)
        assert "Ilmar Rohloff de Mattos (1944–)" in xml

    def test_autor_lilia_presente(self, tmp_path):
        xml = get_xml(tmp_path)
        assert "Lilia Moritz Schwarcz (1957–)" in xml

    def test_bio_nao_duplicado_no_conteudo(self, tmp_path):
        xml = get_xml(tmp_path)
        # Texto que so existe no bio do autor (nao no texto principal)
        bio = "investigou os mecanismos pelos quais a elite imperial"
        assert xml.count(bio) == 1

    def test_duas_notas_fonte(self, tmp_path):
        xml = get_xml(tmp_path)
        b1 = xml.split("bloco-1")[1].split("</bloco>")[0]
        assert b1.count("<nota_fonte>") == 2


# ---------------------------------------------------------------------------
# Bloco 2 — CLASSIFICACAO com 5 SUBTIPOs
# ---------------------------------------------------------------------------

class TestBloco2Classificacao:

    def test_operacao_classificar(self, tmp_path):
        xml = get_xml(tmp_path)
        assert 'operacao="Classificar"' in xml

    def test_secao_tipo_classificacao(self, tmp_path):
        xml = get_xml(tmp_path)
        b2 = xml.split("bloco-2")[1].split("</bloco>")[0]
        assert 'tipo="classificacao"' in b2

    def test_lista_subtipos_presente(self, tmp_path):
        xml = get_xml(tmp_path)
        b2 = xml.split("bloco-2")[1].split("</bloco>")[0]
        assert "<lista-subtipos>" in b2

    def test_cinco_itens_subtipo(self, tmp_path):
        xml = get_xml(tmp_path)
        b2 = xml.split("bloco-2")[1].split("</bloco>")[0]
        assert b2.count('tipo="subtipo"') == 5

    def test_introducao_presente(self, tmp_path):
        xml = get_xml(tmp_path)
        b2 = xml.split("bloco-2")[1].split("</bloco>")[0]
        assert "<introducao>" in b2

    def test_autor_jose_murilo(self, tmp_path):
        xml = get_xml(tmp_path)
        b2 = xml.split("bloco-2")[1].split("</bloco>")[0]
        assert "José Murilo de Carvalho (1939–)" in b2


# ---------------------------------------------------------------------------
# Bloco 3 — PERSPECTIVA (2x) + CONCLUSAO_PARCIAL
# ---------------------------------------------------------------------------

class TestBloco3Perspectivas:

    def test_operacao_comparar(self, tmp_path):
        xml = get_xml(tmp_path)
        assert 'operacao="Comparar"' in xml

    def test_duas_secoes_perspectiva(self, tmp_path):
        xml = get_xml(tmp_path)
        b3 = xml.split("bloco-3")[1].split("</bloco>")[0]
        assert b3.count('tipo="perspectiva"') == 2

    def test_secao_conclusao_parcial(self, tmp_path):
        xml = get_xml(tmp_path)
        b3 = xml.split("bloco-3")[1].split("</bloco>")[0]
        assert 'tipo="conclusao-parcial"' in b3

    def test_titulo_h4_perspectiva(self, tmp_path):
        xml = get_xml(tmp_path)
        assert "Período regencial: a experiência de descentralização" in xml

    def test_intro_livre_presente(self, tmp_path):
        xml = get_xml(tmp_path)
        b3 = xml.split("bloco-3")[1].split("</bloco>")[0]
        assert "A organização do Estado imperial não permaneceu estável" in b3

    def test_autor_boris_fausto_em_conclusao(self, tmp_path):
        xml = get_xml(tmp_path)
        b3 = xml.split("bloco-3")[1].split("</bloco>")[0]
        conclusao = b3.split('tipo="conclusao-parcial"')[1].split("</secao>")[0]
        assert "Boris Fausto (1930–2019)" in conclusao


# ---------------------------------------------------------------------------
# Bloco 4 — CAUSA + RELACAO_CAUSAL + CONSEQUENCIA
# ---------------------------------------------------------------------------

class TestBloco4Causalidade:

    def test_operacao_mapear_causalidade(self, tmp_path):
        xml = get_xml(tmp_path)
        assert 'operacao="Mapear causalidade"' in xml

    def test_secao_causa(self, tmp_path):
        xml = get_xml(tmp_path)
        b4 = xml.split("bloco-4")[1].split("</bloco>")[0]
        assert 'tipo="causa"' in b4

    def test_secao_relacao_causal(self, tmp_path):
        xml = get_xml(tmp_path)
        b4 = xml.split("bloco-4")[1].split("</bloco>")[0]
        assert 'tipo="relacao-causal"' in b4

    def test_secao_consequencia(self, tmp_path):
        xml = get_xml(tmp_path)
        b4 = xml.split("bloco-4")[1].split("</bloco>")[0]
        assert 'tipo="consequencia"' in b4

    def test_autor_viotti_em_consequencia(self, tmp_path):
        xml = get_xml(tmp_path)
        b4 = xml.split("bloco-4")[1].split("</bloco>")[0]
        consequencia = b4.split('tipo="consequencia"')[1].split("</secao>")[0]
        assert "Emília Viotti da Costa (1928–2017)" in consequencia


# ---------------------------------------------------------------------------
# Quebra de página
# ---------------------------------------------------------------------------

class TestQuebrasPagina:

    def test_quebra_presente(self, tmp_path):
        xml = get_xml(tmp_path)
        assert '<quebra tipo="pagina"' in xml

    def test_quebra_entre_blocos(self, tmp_path):
        xml = get_xml(tmp_path)
        # Quebra deve estar no corpo, entre blocos
        corpo = xml.split("<corpo>")[1].split("</corpo>")[0]
        assert '<quebra tipo="pagina"' in corpo


# ---------------------------------------------------------------------------
# Rodapé
# ---------------------------------------------------------------------------

class TestRodape:

    def test_sintese_final_vira_generico(self, tmp_path):
        xml = get_xml(tmp_path)
        rodape = xml.split("<rodape>")[1].split("</rodape>")[0]
        assert 'tipo="generico"' in rodape
        assert 'aviso=' in rodape

    def test_encadeamento_presente(self, tmp_path):
        xml = get_xml(tmp_path)
        assert "<encadeamento>" in xml
        assert "próximo capítulo" in xml


# ---------------------------------------------------------------------------
# Idempotência
# ---------------------------------------------------------------------------

class TestIdempotencia:

    def test_segunda_rodada_identica(self, tmp_path):
        xml1 = get_xml(tmp_path)
        # Rodar de novo: resultado deve ser identico
        result2 = formatar_capitulo(FIXTURE, tmp_path)
        xml2 = result2.read_text(encoding="utf-8")
        assert xml1 == xml2

