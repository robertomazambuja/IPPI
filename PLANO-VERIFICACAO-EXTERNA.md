# Plano — Externalizar a Verificação (modelo "imagens")

**Data:** 2026-06-18
**Objetivo:** retirar a geração de verificações de dentro do pipeline e transformá-la em um insumo externo, produzido por agentes qualificados e inserido só na hora de montar o PDF — exatamente como já acontece com as imagens.

---

## 1. Como funciona hoje (e o que muda)

Hoje a verificação é **gerada dentro do pipeline**, no Agente 5. Ao formatar cada capítulo, o `run_agente5` chama `gerar_verificacoes()` (verificador.py, uma chamada Haiku por capítulo), que lê o `core.md`, escreve as perguntas de múltipla escolha e o "Aplicar agora", e injeta tudo como `<sidebar tipo="verificacao">` e `<sidebar tipo="aplicar-agora">` direto no XML. O `xml_to_pdf.py` depois só renderiza essas sidebars (com ou sem gabarito, conforme `--versao-aluno`/`--versao-professor`).

O problema: o conteúdo da verificação fica **preso ao momento da formatação** e à qualidade do Haiku. Você quer que ele seja produzido **fora**, por agentes especializados, e só entre na montagem final.

O fluxo de **imagens** já resolve esse exato padrão e é o nosso molde:

| Etapa | Imagens (já existe) | Verificações (a criar) |
|---|---|---|
| Marcador no XML | `<imagem ref="..."><descricao>o que mostrar</descricao></imagem>` | `<sidebar tipo="verificacao" ref="..." status="externo"><o-que-verificar>...</o-que-verificar></sidebar>` |
| Lista para o produtor | `gerar_lista_imagens()` → `IMAGENS-NECESSARIAS.txt` | `gerar_lista_verificacoes()` → `VERIFICACOES-NECESSARIAS.txt` |
| Pasta de insumos | `imagens/` (`{ref}.jpg`) | `verificacoes/` (`{ref}.json`) |
| Inserção no PDF | `xml_to_pdf.py --imagens <pasta>` | `xml_to_pdf.py --verificacoes <pasta>` |

A grande vantagem: **a renderização no PDF não muda**. As funções `sb_verif()` e `sb_aplicar()` do `xml_to_pdf.py` continuam idênticas, com toda a lógica de versão aluno/professor. Só muda a **fonte** do conteúdo: em vez de vir embutido no XML, vem da pasta `verificacoes/`.

---

## 2. Arquitetura-alvo

```
PIPELINE (sem verificação — mais rápido e barato)
  A0 → A1 → A2 → A3 → A4 → A5
                              │
                              ├─► capitulo.xml  (com MARCADORES de verificação, sem conteúdo)
                              │       <sidebar tipo="verificacao" ref="01-01-s3" status="externo">
                              │         <o-que-verificar>...</o-que-verificar>
                              │       </sidebar>
                              │
                              └─► gerar_lista_verificacoes()
                                      │
                                      ▼
                              VERIFICACOES-NECESSARIAS.txt   (briefing para os agentes externos)

  ───────────────────  FORA DO PROJETO  ───────────────────
  Agentes qualificados leem o .txt e produzem um arquivo por marcador:
        verificacoes/01-01-s3.json
        verificacoes/01-01-aa.json
  e devolvem a pasta "verificacoes".

MONTAGEM DO PDF (junta tudo)
  xml_to_pdf.py --unidade <xml> --imagens imagens/ --verificacoes verificacoes/ --versao-professor
        │
        ├─ para cada <imagem ref> → pega imagens/{ref}.jpg
        └─ para cada <sidebar ... ref status="externo"> → pega verificacoes/{ref}.json e renderiza
```

Ponto-chave: o **Agente 5 deixa de chamar o Haiku**. Ele apenas marca, de forma determinística, onde a verificação entra e o que verificar — lendo os campos que já existem (operação da seção, micro-habilidade, `VERIFICACAO: Sim` do core). Zero custo de token na verificação.

---

## 3. Esquema do marcador (no XML)

Para cada seção com `VERIFICACAO: Sim`, o A5 emite, no lugar onde hoje insere a sidebar pronta:

```xml
<sidebar tipo="verificacao" ref="01-01-s3" status="externo">
  <o-que-verificar>
    Operação: Comparar.
    Micro-habilidade: "Comparar interpretações sobre estratificação e desigualdade".
    Conceito-âncora: estratificação social.
  </o-que-verificar>
</sidebar>
```

E uma vez por capítulo, no rodapé, o marcador do "Aplicar agora":

```xml
<sidebar tipo="aplicar-agora" ref="01-01-aa" status="externo">
  <o-que-verificar>
    Operação principal do capítulo: Comparar.
    Pergunta do capítulo: "Como raça e gênero se reproduzem no mercado de trabalho?"
    Pedir um caso novo (diferente dos exemplos) para o aluno aplicar a operação.
  </o-que-verificar>
</sidebar>
```

Convenção do `ref` (espelha o padrão dos nomes de arquivo): `{unidade}-{capitulo}-s{n}` para verificação de seção e `{unidade}-{capitulo}-aa` para o "Aplicar agora". Ex.: `01-01-s3`, `01-01-aa`. O atributo `status="externo"` é o que sinaliza ao `xml_to_pdf.py` que o conteúdo virá da pasta.

---

## 4. Esquema do arquivo de insumo (pasta `verificacoes/`)

Um arquivo JSON por `ref`, com o **mesmo schema que o verificador.py já produz** (para reaproveitar a renderização). Os agentes externos preenchem:

`verificacoes/01-01-s3.json`
```json
{
  "tipo": "verificacao",
  "ref": "01-01-s3",
  "pergunta": "Qual afirmação melhor compara solidariedade mecânica e orgânica?",
  "alternativas": {
    "A": "São sinônimos em Durkheim.",
    "B": "A mecânica vem da semelhança; a orgânica, da interdependência.",
    "C": "Ambas surgem só nas sociedades industriais.",
    "D": "A orgânica é típica de sociedades tradicionais; a mecânica, das modernas."
  },
  "correta": "B",
  "justificativa": "A distinção central em Durkheim é o tipo de coesão."
}
```

`verificacoes/01-01-aa.json`
```json
{
  "tipo": "aplicar-agora",
  "ref": "01-01-aa",
  "enunciado": "Um entregador de aplicativo... [caso novo]. Compare as duas situações.",
  "resposta_comentada": "Espera-se que o aluno identifique..."
}
```

Esse schema é idêntico ao que `verificador._render_verificacao_xml()` e `_render_aplicar_agora_xml()` já consomem — então o `xml_to_pdf.py` pode reutilizar essas funções para transformar o JSON em sidebar na hora do PDF.

---

## 5. O `VERIFICACOES-NECESSARIAS.txt` (briefing para os agentes)

Gerado por `gerar_lista_verificacoes()`, espelhando o `IMAGENS-NECESSARIAS.txt`:

```
VERIFICAÇÕES NECESSÁRIAS — Apostila: apostila-sociologia-trabalho
Gerado em: 18/06/2026 14:30

INSTRUÇÕES
1. Para cada item abaixo, produza a verificação descrita.
2. Salve um arquivo JSON nomeado EXATAMENTE como o REF indicado (ex.: 01-01-s3.json).
3. Coloque todos os arquivos numa pasta chamada "verificacoes".
4. Use o schema de exemplo (ver PLANO-VERIFICACAO-EXTERNA.md, seção 4).

CAPÍTULO 01-01 — O que é trabalho?
-----------------------------------------------------------------
  REF             : 01-01-s3   (tipo: verificacao)
  O QUE VERIFICAR : Operação Comparar | micro-hab "Comparar interpretações..."
  REF             : 01-01-aa   (tipo: aplicar-agora)
  O QUE VERIFICAR : Operação principal Comparar | pergunta do capítulo "..."

TOTAL: 2 verificação(ões) necessária(s)
```

---

## 6. Passo a passo de implementação

A implementação é incremental e segura: cada fase deixa o pipeline funcionando.

### Fase 0 — Preparação (sem alterar comportamento)
1. Criar uma branch (ex.: `verificacao-externa`).
2. Adicionar este plano ao repositório (já feito) e referenciá-lo no LEIAME.

### Fase 1 — Pipeline que ignora a verificação
3. Em `run_agente5` (pipeline.py), **remover a chamada a `gerar_verificacoes()`**. O A5 passa a chamar `formatar_capitulo()` sem `verificacoes`/`aplicar_agora` vindos do Haiku.
4. Adicionar uma função leve (sem LLM) que leia do `core.md` apenas **quais seções têm `VERIFICACAO: Sim`** e a operação/micro-habilidade de cada uma. Pode-se reaproveitar `verificador.parse_core()` (que já extrai isso) sem a parte de API.
5. Resultado desta fase: pipeline roda mais rápido, sem custo de token de verificação, e ainda não emite marcadores (validar que o XML continua válido).

### Fase 2 — Marcadores no XML (A5)
6. Em `formatador.py`, alterar a emissão das sidebars: quando a seção tem `VERIFICACAO: Sim`, emitir o **marcador** `<sidebar tipo="verificacao" ref="..." status="externo"><o-que-verificar>...</o-que-verificar></sidebar>` em vez da sidebar preenchida.
7. Emitir, no rodapé do capítulo, o marcador `<sidebar tipo="aplicar-agora" ref="{u}-{c}-aa" status="externo">`.
8. Definir a função de `ref` (`{unidade}-{capitulo}-s{n}` / `-aa`) de forma consistente com os nomes de arquivo já usados no projeto.
9. Validar: abrir um XML gerado e conferir que os marcadores aparecem com `ref` únicos e `o-que-verificar` preenchido.

### Fase 3 — Geração da lista (briefing externo)
10. Criar `gerar_lista_verificacoes(apostila_dir)` em pipeline.py, **copiando a estrutura de `gerar_lista_imagens()`**: varrer `formatado/**/*.xml`, extrair os `<sidebar status="externo">`, e escrever `VERIFICACOES-NECESSARIAS.txt`.
11. Chamar essa função no fim do `run_pipeline` (ao lado da chamada que já gera a lista de imagens).
12. Validar: rodar o pipeline e conferir o `.txt` gerado.

### Fase 4 — Inserção no PDF
13. Em `xml_to_pdf.py`, adicionar o argumento `--verificacoes <pasta>` (espelhando `--imagens`).
14. Em `render_sb()` (ou `sb_verif`/`sb_aplicar`), quando a sidebar tiver `status="externo"`:
    - se `--verificacoes` foi passado e existe `verificacoes/{ref}.json`, **carregar o JSON e renderizar** a sidebar (reutilizando `verificador._render_*` ou um pequeno conversor JSON→HTML);
    - se o arquivo não existir, renderizar um aviso discreto "verificação pendente" (ou nada), para não quebrar o PDF.
15. Manter intactas as flags `--versao-aluno` / `--versao-professor` (o gabarito/resposta continuam controlados na renderização, não na origem do conteúdo).
16. Validar: montar o PDF com uma pasta `verificacoes/` de teste e conferir aluno vs. professor.

### Fase 5 — Qualidade de vida e documentação
17. Adicionar um validador opcional `validar_verificacoes(apostila_dir)` que checa se todo `ref` marcado tem um JSON correspondente e se o schema está correto — relatório de pendências antes de gerar o PDF.
18. Atualizar LEIAME e `ARQUITETURA` para refletir: A5 não gera mais verificação; verificação é insumo externo na pasta `verificacoes/`.
19. (Opcional) Manter o `verificador.py` como **gerador de rascunho** acionável sob demanda (`--agentes ...` ou script avulso), caso queira um ponto de partida automático para os agentes humanos refinarem.

---

## 7. Decisões que dependem de você

1. **Formato do insumo:** JSON (recomendado — fácil de validar e de um agente produzir) ou o snippet XML pronto da sidebar (mais simples de inserir, menos validável). O plano assume JSON.
2. **Destino do verificador.py atual:** aposentar de vez, ou manter como gerador de rascunho opcional (item 19)?
3. **Comportamento quando falta a verificação no PDF:** omitir silenciosamente, ou imprimir um marcador visível "pendente" na versão professor para facilitar o controle?
4. **Granularidade do `o-que-verificar`:** o mínimo (operação + micro-habilidade) já basta, ou você quer incluir também o exemplo-âncora e a síntese para guiar melhor os agentes externos?

Definidos esses quatro pontos, a implementação segue as Fases 1→4 sem retrabalho.
