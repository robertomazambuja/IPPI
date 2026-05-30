# RESUMO DAS MUDANÇAS — NOVO MODELO CSV COM ANDAIME

## Data
30 de maio de 2026

## O que foi alterado

### 1. ✅ Novo formato CSV com andaime de habilidades

**Arquivo:** `NOVO_FORMATO_CSV.md` (criado)

O CSV agora permite que o professor prescreva:
- **Habilidade principal** (código BNCC completo)
- **Andaime didático** — 4 a 6 seções, cada uma com:
  - Micro-habilidade específica
  - Operação elementar (Definir, Classificar, Comparar, etc.)
- **Conteúdos nucleares** (lista genérica)
- **Autores disponíveis** (lista genérica — Agente 1 distribui)
- **Elementos desejáveis** (opcional — direcionamentos didáticos)

### 2. ✅ Atualização do pipeline.py

**Mudanças:**
- Nova validação de CSV com as colunas expandidas
- Validação de operações (7 valores permitidos)
- Suporte a 4-6 seções por capítulo
- User message do Agente 1 agora **recebe o andaime completo** no prompt
- Agente 1 não precisa inventar a estrutura — apenas concretizá-la

### 3. ✅ Atualização do LEIAME.md

Documentação do novo CSV adicionada à seção "O CSV — input do professor"

### 4. ✅ CSV exemplo criado

**Arquivo:** `input/apostila-sociologia-em1/instrucoes.csv`

Exemplo funcional com seus 2 capítulos de Sociologia:
- **Capítulo 1:** Estrutura social e estratificação (EM13CHS402)
  - 4 seções: Definir → Classificar → Comparar → Aplicar
  - Autores: Marx, Weber, Bourdieu

- **Capítulo 2:** Desigualdade, raça e gênero no Brasil (EM13CHS502 + EM13CHS601)
  - 4 seções: Definir → Mapear causalidade → Reconhecer perspectiva → Aplicar
  - Autores: Lélia Gonzalez, Hasenbalg, Ianni, Flávia Rios, bell hooks

---

## Como testar

```bash
# Roda o pipeline com a nova apostila
python pipeline.py input/apostila-sociologia-em1/instrucoes.csv

# Roda apenas Agente 1 (arquitetura)
python pipeline.py input/apostila-sociologia-em1/instrucoes.csv --agentes 1

# Força regeneração
python pipeline.py input/apostila-sociologia-em1/instrucoes.csv --force
```

---

## Próximos passos (com o usuário)

1. ✅ Estrutura decidida
2. ✅ CSV criado
3. ⏳ **Testar o pipeline com a apostila de Sociologia**
4. ⏳ Ajustar Agente 1 skill se necessário
5. ⏳ Rodar Agente 2, 3, 4, 5 conforme necessário

---

## Notas

- **Compatibilidade:** O novo formato não quebra apostilas antigas (basta preencher as novas colunas)
- **Flexibilidade:** Micro-habilidades 5 e 6 são opcionais
- **Agência do Agente 1:** Mantém-se alta — ele ainda decide exemplos, pesos, fontes, verificações
- **Validação:** CSV é validado automaticamente antes do pipeline rodar
