# NOVO FORMATO CSV — ANDAIME DE HABILIDADES

## Visão Geral

O novo formato CSV enriquecido permite que o professor **prescreva o andaime didático completo** de cada capítulo. Isso reduz ambiguidade, facilita validação e mantém a **agência do Agente 1** em decisões de concretização (exemplos, pesos, fontes).

---

## Estrutura do CSV

### Colunas Obrigatórias

| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `disciplina` | texto | Nome da disciplina | Sociologia |
| `unidade` | texto | Nome da unidade | Unidade 1 — Estrutura social e desigualdade |
| `pergunta_unidade` | texto | Pergunta central que governa toda a unidade | Como as estruturas sociais produzem desigualdade? |
| `capitulo` | texto | Nome do capítulo | Capítulo 1: Estrutura social e estratificação |
| `habilidade_principal` | BNCC | Habilidade BNCC do capítulo (código + texto) | EM13CHS402 - Analisar e comparar indicadores de emprego... |
| `micro_hab_1` | texto | Micro-habilidade da seção 1 | Diferenciar indivíduo de classe social |
| `operacao_secao_1` | enum | Operação elementar da seção 1 | Definir |
| `micro_hab_2` | texto | Micro-habilidade da seção 2 | Definir estratificação social |
| `operacao_secao_2` | enum | Operação elementar da seção 2 | Classificar |
| `micro_hab_3` | texto | Micro-habilidade da seção 3 | Comparar modelos de estratificação |
| `operacao_secao_3` | enum | Operação elementar da seção 3 | Comparar |
| `micro_hab_4` | texto | Micro-habilidade da seção 4 | Analisar estratificação no Brasil |
| `operacao_secao_4` | enum | Operação elementar da seção 4 | Aplicar |
| `micro_hab_5` | texto | (Opcional) Micro-habilidade da seção 5 | — |
| `operacao_secao_5` | enum | (Opcional) Operação elementar da seção 5 | — |
| `micro_hab_6` | texto | (Opcional) Micro-habilidade da seção 6 | — |
| `operacao_secao_6` | enum | (Opcional) Operação elementar da seção 6 | — |
| `conteudos_nucleares` | lista (;) | Conteúdos que serão abordados no capítulo | Estrutura social; estratificação; classe; capital |
| `autores` | lista (;) | Autores que podem ser usados | Karl Marx; Max Weber; Pierre Bourdieu |
| `elementos_desejáveis` | texto livre | (Opcional) Direcionamentos didáticos específicos | Usar exemplos Brasil; dados IBGE; focar em Bourdieu |

---

## Enumeração de Operações

As colunas `operacao_secao_X` devem conter **exatamente um** destes termos:

- `Definir`
- `Classificar`
- `Comparar`
- `Sequenciar`
- `Mapear causalidade`
- `Reconhecer perspectiva`
- `Aplicar`

---

## Exemplo Completo (Sociologia, Cap 1)

```csv
disciplina,unidade,pergunta_unidade,capitulo,habilidade_principal,micro_hab_1,operacao_secao_1,micro_hab_2,operacao_secao_2,micro_hab_3,operacao_secao_3,micro_hab_4,operacao_secao_4,micro_hab_5,operacao_secao_5,micro_hab_6,operacao_secao_6,conteudos_nucleares,autores,elementos_desejáveis
Sociologia,Unidade 1 — Estrutura social e desigualdade,Como as estruturas sociais produzem desigualdade?,Capítulo 1: Estrutura social e estratificação,"EM13CHS402 - Analisar e comparar indicadores de emprego, trabalho e renda em diferentes espaços, escalas e tempos, associando-os a processos de estratificação e desigualdade socioeconômica.",Diferenciar indivíduo de classe social,Definir,Definir estratificação social,Classificar,Comparar modelos de estratificação,Comparar,Analisar estratificação no Brasil,Aplicar,,,,,Estrutura social; estratificação; classe; capital; desigualdade socioeconômica,Karl Marx; Max Weber; Pierre Bourdieu,"Usar exemplos do Brasil; dados IBGE/PNAD; enfatizar diferença classe/status"
```

---

## Como o Agente 1 usa este andaime

1. **Recebe o CSV** com a estrutura prescrita (micro-habilidades + operações)
2. **NÃO precisa inventar** a progressão de operações
3. **DECIDE ainda:**
   - Qual EXEMPLO_ANCOLA (situação concreta singular)
   - Qual PESO da seção (Principal/Secundário/Passagem)
   - Qual BOX_BIOGRAFICO (qual autor merece box biográfico)
   - Qual FONTE_PRIMARIA (qual citação, qual obra)
   - Se há VERIFICACAO (sim/não) e qual tipo
   - ERROS_COMUNS (confusões conceituais comuns)
   - Coerência da progressão (faz sentido pedagogicamente?)

**Resultado:** Agente 1 continua sendo **arquiteto**, não "preenchedor de template".

---

## Validação no Pipeline

O arquivo `pipeline.py` foi atualizado para:

1. Validar que todas as colunas `micro_hab_X` e `operacao_secao_X` existem
2. Validar que `operacao_secao_X` contém um dos 7 valores permitidos
3. Validar que `micro_hab_1` até `micro_hab_4` são preenchidas (mínimo 4 seções)
4. Permitir `micro_hab_5`, `micro_hab_6` opcionais (máximo 6 seções)
5. Passar o andaime para o Agente 1 no prompt

---

## Notas

- **Micro-habilidades 5-6 são opcionais:** Se um capítulo tem 4 seções, deixe-as vazias
- **Elementos_desejáveis é opcional:** Se professor não tiver direcionamento específico, deixe em branco
- **Autores é lista genérica:** O Agente 1 decide em qual seção usar cada um
- **Conteúdos_nucleares:** Todos devem aparecer em pelo menos uma seção do capítulo
