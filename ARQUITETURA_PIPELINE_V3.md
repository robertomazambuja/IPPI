# ARQUITETURA — Pipeline V3 (Funcional + Estilo)

## Ordem de Execução

### Padrão (Recomendado)
```
Agente 1 (Arquiteto)
   ↓
Agente 2 (Redator Funcional)
   ↓
Agente 4 (Redator de Estilo)
```

### Com Validação Opcional
```
Agente 1 (Arquiteto)
   ↓
Agente 2 (Redator Funcional)
   ↓
Agente 3 (Normalizador de Marcação) ← opcional, muito custoso
   ↓
Agente 4 (Redator de Estilo)
```

**Nota:** Agente 3 removido do fluxo automático. Use `--agentes 1,2,3,4` se quiser validação explícita.

---

## Os Quatro Agentes

### **Agente 1 — Arquiteto Curricular**
- **Input**: CSV (dados do professor)
- **Output**: `core.md` (estrutura funcional bruta)
- **Função**: Define seções, operações, exemplos, autores, verificações
- **Skill**: `skills/agente1-skill.md`
- **Orientação**: `orientacoes/agente1-orientacao.md`

---

### **Agente 2 — Redator Funcional**
- **Input**: `core.md` (estrutura)
- **Output**: `texto.md` (com **rótulos explícitos**)
- **Função**: Converte estrutura em prosa funcional
- **Rótulos visíveis**: `[PERSPECTIVA 1]`, `[VERIFICAÇÃO]`, "Argumento de apoio:", etc.
- **Skill**: `skills/agente2-skill.md`
- **Orientação**: `orientacoes/agente2-orientacao.md`
- **IMPORTANTE**: Esse é o output esperado — rótulos não são erro, são intermediate stage

---

### **Agente 3 — Normalizador de Marcação (OPCIONAL)**
- **Input**: `core.md` + `texto.md` (com rótulos ainda visíveis)
- **Output**: `validacao.md` (relatório)
- **Função**: Audita conformidade funcional (QA)
- **5 pontos de validação**:
  1. Conformidade com core (todas seções presentes?)
  2. Operação mapeada (definir/sequenciar/comparar/etc. está claro?)
  3. Estrutura funcional (moldura está clara?)
  4. Autores (datas + filiação presentes?)
  5. Encadeamento (próximo capítulo mencionado?)
- **NÃO reprova por**: rótulos visíveis (esperado neste ponto)
- **Status**: Removido do fluxo automático (muito custoso — 3-4min/cap, +4K tokens)
- **Uso**: Use `--agentes 1,2,3,4` se quiser validação explícita
- **Skill**: `skills/agente3-skill.md`
- **Orientação**: `orientacoes/agente3-orientacao.md`

---

### **Agente 4 — Redator de Estilo**
- **Input**: `texto.md` (com rótulos visíveis, já validado)
- **Output**: `texto.md` (sobrescrito, prosa natural)
- **Função**: Qualifica prosa, torna invisível rótulos
- **Transformações**:
  - `[PERSPECTIVA 1]` → desaparece, narrativa integrada
  - `"Argumento de apoio:"` → fluxo narrativo natural
  - `[VERIFICAÇÃO]` → pergunta no final da seção
  - Lista explícita → fluxo narrativo
  - Exemplos explícitos → casos integrados naturalmente
- **O que NÃO faz**: humanizar, dramatizar, usar padrões artificiais
- **Skill**: `skills/agente4-skill.md`
- **Orientação**: `orientacoes/agente4-orientacao.md`

---

## Outputs por Agente

```
output/[apostila]/
├── core/[unidade-slug]/
│   ├── 01-01-capitulo-um.md         (Agente 1)
│   ├── 01-02-capitulo-dois.md
│   └── ...
├── texto/[unidade-slug]/
│   ├── 01-01-capitulo-um.md         (Agente 2 → Agente 4)
│   ├── 01-02-capitulo-dois.md
│   └── ...
└── validacao/[unidade-slug]/
    ├── 01-01-capitulo-um.md         (Agente 3)
    ├── 01-02-capitulo-dois.md
    └── ...
```

---

## Fluxo de Dados

### Capítulo 1 (Padrão)

```
CSV → Agente 1 → core/01-01-...md
               ↓
             Agente 2 → texto/01-01-...md (com rótulos)
                      ↓
                    Agente 4 → texto/01-01-...md (prosa natural)
```

### Capítulo 1 (Com Validação Opcional)

```
CSV → Agente 1 → core/01-01-...md
               ↓
             Agente 2 → texto/01-01-...md (com rótulos)
                      ↓
                    Agente 3 → validacao/01-01-...md (relatório - opcional)
                             ↓
                           Agente 4 → texto/01-01-...md (prosa natural)
```

### Próximos capítulos

Mesmo fluxo, independente por capítulo (paralelizável em futuro).

---

## Como Rodar

### Apenas estrutura (Agente 1):
```bash
python pipeline.py input/apostila-historia-midia/instrucoes.csv --agentes 1
```

### Estrutura + redação (Agentes 1, 2):
```bash
python pipeline.py input/apostila-historia-midia/instrucoes.csv --agentes 1,2
```

### Completo (padrão: Agentes 1, 2, 4):
```bash
python pipeline.py input/apostila-historia-midia/instrucoes.csv
```

### Com qualificação de estilo (Agentes 1, 2, 4):
```bash
python pipeline.py input/apostila-historia-midia/instrucoes.csv --agentes 1,2,4
```

### Com validação explícita (Agentes 1, 2, 3, 4):
```bash
python pipeline.py input/apostila-historia-midia/instrucoes.csv --agentes 1,2,3,4
```

### Com regeneração (force):
```bash
python pipeline.py input/apostila-historia-midia/instrucoes.csv --force
```

### Apenas 1 capítulo:
```bash
python pipeline.py input/apostila-historia-midia/instrucoes.csv --cap 1
```

### Combinações:
```bash
python pipeline.py input/apostila-historia-midia/instrucoes.csv --agentes 1,2 --cap 1
python pipeline.py input/apostila-historia-midia/instrucoes.csv --agentes 1,2,3,4 --force
```

---

## Validação Entre Agentes

### Após Agente 2
Arquivos `.md` existem em `output/[apostila]/texto/[unidade-slug]/`.

**Status esperado**: Texto com rótulos visíveis como `[PERSPECTIVA 1]`, "Argumento de apoio:", `[VERIFICAÇÃO]`.

Isso é CORRETO. Não é erro.

### Após Agente 3
Arquivos `.md` existem em `output/[apostila]/validacao/[unidade-slug]/`.

**Status esperado**: Relatório de validação (APROVADO / COM RESSALVAS / REPROVADO).

Se REPROVADO, volta ao Agente 2 para correção.

### Após Agente 4
Arquivos `texto/*.md` são **sobrescritos** com prosa natural.

**Status esperado**: Rótulos desapareceram, fluxo é contínuo, estrutura é invisível mas sólida.

Pronto para leitura, diagramação, ou envio.

---

## Integração com Skills/Orientações

Cada agente carrega dois arquivos:
1. **Orientação** (`orientacoes/agente[N]-orientacao.md`) — contexto, identidade, papel
2. **Skill** (`skills/agente[N]-skill.md`) — procedimento detalhado

Ambos são combinados em um único system prompt (via `build_system_prompt()`).

---

## Próximas Etapas (Não Implementadas)

- **Agente 5** — Curador de Imagens (busca no Wikimedia, integra em sidebar)
- **Agente 6** — Diagramador (converte para XML, pronto para InDesign)

Quando criados, serão adicionados como:
```
Agente 4 (Redator de Estilo)
   ↓
Agente 5 (Curador de Imagens)
   ↓
Agente 6 (Diagramador)
```

---

## Checklist de Arquivos Necessários

### Scripts
- [ ] `pipeline.py` ✓

### Skills
- [ ] `skills/agente1-skill.md` ✓
- [ ] `skills/agente2-skill.md` ✓
- [ ] `skills/agente3-skill.md` ✓ (novo)
- [ ] `skills/agente4-skill.md` ✓ (novo)

### Orientações
- [ ] `orientacoes/agente1-orientacao.md` ✓
- [ ] `orientacoes/agente2-orientacao.md` ✓
- [ ] `orientacoes/agente3-orientacao.md` ✓ (novo)
- [ ] `orientacoes/agente4-orientacao.md` ✓ (novo)

### Contexto
- [ ] `contexto/principios-pedagogicos-agente1.md` ✓
- [ ] `contexto/disciplinas/[disciplina].md` ✓ (ex: historia.md)

### CSV
- [ ] `input/apostila-[nome]/instrucoes.csv` ✓

---

## Resumo da Mudança Arquitetural

| Aspecto | Antes | V2 | V3 (Agora) |
|---------|-------|-----|-----------|
| **Ordem** | 1→2→4→3→5→6 | 1→2→3→4 | 1→2→4 (padrão) |
| **Agente 3** | Validador (após estilo) | Validador (antes estilo) | Opcional (custoso) |
| **Agente 4** | Revisor (humanizar) | Redator (qualificar) | Redator (qualificar) |
| **Agentes 5,6** | Não implementado | Não implementado | Não implementado |
| **Decisão** | Validar depois humanizar | Validar antes qualificar | Skip validação automática |

**Benefício V3**: Remover Agente 3 do fluxo automático economiza 3-4min/cap e 4K tokens. Agente 2 é confiável. Agente 3 disponível sob demanda (`--agentes 1,2,3,4`).
