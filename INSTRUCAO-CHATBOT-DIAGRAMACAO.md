# Instrução para o chatbot — Diagramar a apostila em PDF

Você vai diagramar (layout/PDF) uma apostila de Sociologia já escrita. O foco **não é o conteúdo**, é a **diagramação**: legibilidade, duas colunas, hierarquia visual, sem páginas em branco e sem cabeçalhos órfãos. O conteúdo já existe como **XML estruturado** e é convertido em PDF pelo motor `xml_to_pdf.py` (WeasyPrint, HTML/CSS).

## 1. Leia ANTES de tocar em qualquer coisa (nesta ordem)

1. **`HANDOVER-DIAGRAMACAO-PDF.md`** — memória acumulada do projeto. Contém as regras invioláveis, os bugs já resolvidos e os problemas em aberto. É a fonte mais importante; leia inteiro.
2. **`xml_to_pdf.py`** — o motor. É a **fonte da verdade** do layout. Toda mudança de diagramação acontece aqui. Não use `apostila_pdf.py` (motor ReportLab, **aposentado**).
3. **`PLANO-LAYOUT-IMAGENS-PDF.md`** e **`PLANO-VERIFICACAO-EXTERNA.md`** — decisões de design sobre imagens e sobre as verificações externas (os JSON).

## 2. Arquivos de entrada para diagramar (a apostila)

Apostila de trabalho: `output/apostila-sociologia-trabalho/`

- **Capítulos (XML):** `output/apostila-sociologia-trabalho/formatado/unidade-4-o-trabalho-na-perspectiva-sociologica/*.xml`
  Cada `*.xml` é um `<capitulo>`. Hoje só o **01-01** está em `formatado/` — confirme quais capítulos existem antes de rodar.
- **Imagens reais:** `output/apostila-sociologia-trabalho/imagens/` (`fig-01-01-01.jpg` etc.). Passe esta pasta em `--imagens`. Sem ela, nenhuma imagem é gerada (MVP).
- **Verificações externas (JSON):** `output/apostila-sociologia-trabalho/verificacoes/` (`verif-01-01-sN.json`, `aplicar-01-01.json`). Passe em `--verificacoes`.
- **Nomes de capítulo/unidade (briefing):** o motor procura um `briefing.json` para o nome "bonito" do capítulo na capa. **Atenção: não há `briefing.json` neste projeto ainda** — só `input/apostila-sociologia-trabalho/instrucoes.csv`. Se faltar, o loader é tolerante mas a capa fica sem o nome correto. Verifique e, se necessário, peça/aponte o `briefing.json` ou passe `--briefing`.

## 3. Antes de rodar — checagem obrigatória

- **Cada `ref` `status="externo"` do XML precisa ter um JSON correspondente em `verificacoes/`.** Faça `grep ref= no XML` × `ls verificacoes/`. Se faltar um JSON, na versão ALUNO a verificação some **silenciosamente** (sem erro) e o PDF sai incompleto. Sinalize ao usuário em vez de gerar incompleto.
- Confirme que o XML faz `ET.parse` sem erro (já houve XML **truncado** na cauda do `<rodape>` em outro capítulo — ver §15 do handover).

## 4. Como rodar

Dependência: `pip install weasyprint --break-system-packages` (no Linux do sandbox; a `.venv` do repo é Windows).

Aluno e professor são **dois processos separados**; a flag é **obrigatória** (o script erra sem ela). Rode um de cada vez.

```bash
# ALUNO (sem gabarito nem resposta-modelo)
python3 xml_to_pdf.py <caminho-do.xml> \
  --versao-aluno \
  --imagens output/apostila-sociologia-trabalho/imagens \
  --verificacoes output/apostila-sociologia-trabalho/verificacoes \
  --output apostila-aluno.pdf

# PROFESSOR (com gabarito e resposta-modelo) — troque só a flag e o --output
python3 xml_to_pdf.py <caminho-do.xml> --versao-professor ... --output apostila-professor.pdf

# só HTML para inspecionar
python3 xml_to_pdf.py <caminho-do.xml> --versao-aluno --html-only --output saida.html
```

## 5. Regras invioláveis (nunca quebrar)

- **Nunca marque visualmente a alternativa correta** no PDF. O `correta="sim"` existe no XML, mas todas as alternativas usam a mesma classe neutra.
- **Versão ALUNO não pode vazar gabarito** nem resposta-modelo. Confirme com `pdftotext` + grep por "gabarito"/"justificativa"/"resposta modelo" → deve dar **0**.
- **Não volte ao motor ReportLab** (`apostila_pdf.py`).
- Priorize legibilidade do aluno: hifenização pt-BR, coluna ~50–60 caracteres, contraste alto, hierarquia (barra de operação > seção > corpo).

## 6. Verificação ao final (sempre)

- `python3 -m py_compile xml_to_pdf.py` limpo após qualquer edição no motor.
- Render visual de **todas** as páginas (`pdftoppm -png -r 150 saida.pdf prefixo`) e confira: zero cabeçalho de bloco órfão, zero página totalmente em branco, imagens legíveis.
- Medição de branco de rodapé por página (PIL) se for avaliar densidade.
- Conformidade das regras invioláveis (grep no HTML/pdftotext).

## 7. Edição segura do `xml_to_pdf.py`

A ferramenta de edição **já truncou** este arquivo mais de uma vez. Para mudanças grandes, reescreva via shell (`cat > arquivo <<'EOF' ... EOF`) ou patch por script Python com `assert count==1`; **sempre** confira depois com `wc -l` e `py_compile`. Não confie no "sucesso" reportado em arquivos grandes.
