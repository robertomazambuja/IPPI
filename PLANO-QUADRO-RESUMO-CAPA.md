# PLANO DE AÇÃO — Quadro resumo de micro-habilidades na capa do capítulo

**Status:** proposta para aprovação. Nada foi alterado no código ainda.
**Arquivo-alvo principal:** `xml_to_pdf.py`
**Data:** 24/06/2026

---

## 1. Objetivo

Preencher o espaço em branco da primeira página de cada capítulo com um **quadro
resumo** que lista cada micro-habilidade do capítulo acompanhada de uma frase curta
("o que você vai aprender"), com a cor da operação cognitiva correspondente.

O quadro é, na prática, o `mapa-progressao` (stepper) **expandido**: além do nome do
passo, ganha uma linha de texto por micro-habilidade.

---

## 2. Decisões já tomadas (com o Beto)

1. **Fonte do texto:** um campo novo `<resumo-aluno>` por bloco, escrito pelo
   **agente escritor** (modelo de 2 agentes). O renderizador apenas lê e diagrama.
2. **Cores:** completar `OPERACAO_CORES` com as **7 operações reais**, cada uma com
   cor própria.

---

## 3. Por que existe o espaço em branco (diagnóstico)

- A capa (`.capa-capitulo`) tem `break-before: page`.
- Cada micro-habilidade (`.bloco`) tem `.bloco-keep { break-inside: avoid }` e a
  **primeira** não recebe quebra de página (`primeiro_bloco` em `render_capitulo`).
- Como o primeiro bloco não cabe inteiro embaixo da capa, ele é empurrado para a
  página 2, deixando a folga no fim da página 1.

**Consequência boa:** o quadro resumo entra *dentro* da capa, ocupa essa folga e
não desloca mais nada — o primeiro bloco já ia para a página 2 de qualquer forma.

**Espaço medido (A4, margens do `@page` = 18/16/20/16 mm):**
- Largura útil: **~178 mm**
- Altura livre abaixo da linha azul: **~138 mm**
- Quadro proposto: **~45 mm** de altura (deixa folga), até 6 linhas.

---

## 4. Bug colateral encontrado: `OPERACAO_CORES` desalinhado

O dicionário atual (linhas 41-49) **não corresponde** ao vocabulário do projeto.

| Atual (errado) | Vocabulário real (matriz-enem + decompositor) |
|---|---|
| Definir ✓ | Definir |
| Sequenciar ✓ | Classificar ← **faltando** |
| Mapear causalidade ✓ | Sequenciar |
| Comparar ✓ | Comparar |
| Analisar ← **não existe** | Mapear causalidade |
| Avaliar ← **não existe** | Reconhecer perspectiva ← **faltando** |
| | Aplicar ← **faltando** |

Por isso `Classificar` e `Reconhecer perspectiva` caíam no cinza padrão (`COR_PADRAO`),
inclusive no stepper da capa. Corrigir o dicionário conserta o stepper **e** alimenta
o quadro resumo de uma vez.

### Paleta proposta (ajustável)

| Operação | Nível | destaque | fundo |
|---|---|---|---|
| Definir | 1 | `#1565C0` | `#E3F2FD` |
| Classificar | 1 | `#00838F` | `#E0F7FA` |
| Sequenciar | 1 | `#2E7D32` | `#E8F5E9` |
| Comparar | 2 | `#6A1B9A` | `#F3E5F5` |
| Mapear causalidade | 2 | `#E65100` | `#FFF3E0` |
| Reconhecer perspectiva | 3 | `#AD1457` | `#FCE4EC` |
| Aplicar | 3 | `#4E342E` | `#EFEBE9` |

(7 cores distintas. `COR_PADRAO` cinza permanece só como rede de segurança.)

---

## 5. Os dois agentes e a interface entre eles

### Agente 1 — Escritor (LLM)
- **Entrada:** a `<micro-habilidade>` de cada bloco + tema/conteúdos do capítulo.
- **Saída:** uma frase por micro-habilidade, **25–35 palavras**, linguagem voltada ao
  aluno ("Você vai aprender a…"), sem nomear autores/dados (mesma regra de abstração
  do decompositor).
- **Formato de entrega:** estruturado, **não** prosa solta nem imagem. Grava um campo
  `<resumo-aluno>` dentro de cada `<bloco>` no XML.

### Agente 2 — Renderizador = o próprio `xml_to_pdf.py`
- Lê `operacao`, `<micro-habilidade>` e `<resumo-aluno>` de cada bloco.
- Monta o quadro na capa, aplicando a cor da operação.
- **Não** decide texto nem cor de conteúdo — só diagrama.

> Decisão de arquitetura confirmada: **não criar um terceiro agente** que "cola texto e
> faz o gráfico". O renderizador já é o dono do layout (medidas, cores, fontes);
> duplicar esse conhecimento criaria duas fontes de verdade.

---

## 6. Mudança de schema (XML)

Adicionar um filho opcional em cada `<bloco>`:

```xml
<bloco operacao="Definir" id="...">
  <micro-habilidade>Definir fonte histórica como vestígio...</micro-habilidade>
  <resumo-aluno>Você vai entender o que conta como fonte histórica e por que
  ela é a base de tudo o que sabemos sobre o passado.</resumo-aluno>
  <secao>...</secao>
</bloco>
```

- Campo **opcional**: se ausente, o renderizador usa a `<micro-habilidade>` como
  fallback (o quadro nunca quebra por falta de texto).
- `<resumo-aluno>` precisa entrar na lista `_CONHECIDAS_*` para não disparar o
  `avisar_tag_desconhecida` (a guarda de contrato das linhas 26-33).

---

## 7. Mudanças no renderizador (`xml_to_pdf.py`)

Três pontos, todos cirúrgicos:

1. **`OPERACAO_CORES` (linhas 41-49):** substituir pelas 7 operações da seção 4.

2. **`build_css()`:** adicionar um bloco de CSS `.quadro-resumo` —
   - container largura plena, borda `#D0D6DC`, cantos 6pt;
   - faixa-título "O QUE VOCÊ VAI APRENDER NESTE CAPÍTULO" (Arial, 8.5pt, caixa-alta);
   - linhas com barra vertical de 4pt na cor `destaque` da operação, nome do passo em
     negrito na mesma cor + texto neutro `#3a4654` (~10pt);
   - `break-inside: avoid` para o quadro não fatiar entre páginas.

3. **`render_capitulo()`:** depois de montar o `mapa_html`, varrer os `<bloco>` de
   `<corpo>`, coletar `(operacao, micro-habilidade, resumo-aluno)` e gerar o HTML do
   quadro, anexando-o à `capa` (logo abaixo do `mapa-progressao`). Função nova
   sugerida: `render_quadro_resumo(corpo_el)`.

Nenhuma alteração em `render_bloco`, `render_secao`, no pipeline de verificações ou na
lógica aluno/professor.

---

## 8. Orçamento de texto (para o prompt do Agente 1)

- Largura útil de linha: ~178 mm → ~15 palavras por linha visual.
- Alvo por micro-habilidade: **25–35 palavras** (2 linhas), confortável.
- Quadro inteiro (4-6 itens + título): ~120-210 palavras, ainda deixa folga na página.

---

## 9. Ordem de execução proposta

1. Corrigir `OPERACAO_CORES` (conserta o stepper imediatamente — ganho isolado).
2. Adicionar CSS `.quadro-resumo` + `render_quadro_resumo()` usando **fallback para
   `<micro-habilidade>`** → já dá para ver o quadro renderizado sem depender do escritor.
3. Definir o campo `<resumo-aluno>` no schema e na lista de tags conhecidas.
4. Escrever o prompt do Agente 1 (regras + faixa de 25-35 palavras).
5. Rodar Agente 1 fora do pipeline (como o Beto pediu), colar os `<resumo-aluno>` no XML.
6. Regerar o PDF e validar o encaixe na página 1.

---

## 10. Pontos em aberto para decidir

- Posição do quadro: **logo após o stepper** (recomendado) ou substituindo o stepper?
- Título do quadro: "O QUE VOCÊ VAI APRENDER NESTE CAPÍTULO" — confirmar redação.
- Cor de `Aplicar` (`#4E342E`, marrom) — confirmar ou trocar.
- Numerar as linhas (1, 2, 3…) ou só nome da operação?
