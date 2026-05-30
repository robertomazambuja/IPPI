# SETUP E USO DO PIPELINE

## 1. Preparação do ambiente

### 1.1 Instalar dependências

```bash
pip install -r requirements.txt
```

### 1.2 Configurar chave de API

Crie arquivo `.env` na raiz do projeto:

```env
ANTHROPIC_API_KEY=sk-ant-api03-...
```

Obtenha a chave em: https://console.anthropic.com

## 2. Executar o pipeline

### 2.1 Rodar pipeline completo (Agentes 1, 2, 3, 5)

```bash
python pipeline.py input/apostila-teste-sociologia/instrucoes.csv
```

Isso produzirá:
- `output/apostila-teste-sociologia/core/` — arquitetura dos capítulos
- `output/apostila-teste-sociologia/texto/` — capítulos em texto funcional

### 2.2 Rodar apenas Agentes 1 e 2 (core + texto)

```bash
python pipeline.py input/apostila-teste-sociologia/instrucoes.csv --agentes 1,2
```

### 2.3 Rodar apenas um capítulo (para teste rápido)

```bash
python pipeline.py input/apostila-teste-sociologia/instrucoes.csv --cap 1
```

Processa apenas o capítulo 1 (ordem no CSV, começando em 1).

### 2.4 Forçar regeneração (ignora cache)

```bash
python pipeline.py input/apostila-teste-sociologia/instrucoes.csv --force
```

### 2.5 Simular execução sem chamar API (dry-run)

```bash
python pipeline.py input/apostila-teste-sociologia/instrucoes.csv --dry-run
```

Útil para validar CSV e estrutura antes de custo real.

## 3. Estrutura de saída

```
output/apostila-teste-sociologia/
├── core/
│   └── unidade-1-fundamentos-da-sociologia/
│       ├── 1-1-imaginacao-sociologica.md
│       ├── 2-2-acao-e-estrutura.md
│       └── ...
├── texto/
│   └── unidade-1-fundamentos-da-sociologia/
│       ├── 1-1-imaginacao-sociologica.md
│       ├── 2-2-acao-e-estrutura.md
│       └── ...
└── logs/
    └── pipeline_20260530_123456.log
```

## 4. Criando novo CSV de input

A estrutura esperada é:

| disciplina | unidade | pergunta_unidade | capitulo | habilidade | conteudos_nucleares | autores | elementos_obrigatorios |
|---|---|---|---|---|---|---|---|
| Sociologia | Unidade 1 — ... | O que...? | Capítulo 1: ... | EM13CHS... | Conteúdo 1; Conteúdo 2 | Autor 1 (datas); Autor 2 | Elemento 1; Elemento 2 |

**Colunas obrigatórias:**
- `disciplina` — Sociologia, História, Filosofia ou Geografia
- `unidade` — Nome da unidade (ex: "Unidade 1 — Fundamentos")
- `pergunta_unidade` — Pergunta central da unidade
- `capitulo` — Nome do capítulo (ex: "Capítulo 1: A imaginação sociológica")
- `habilidade` — Código + texto da habilidade BNCC (ex: "EM13CHS101 - Analisar...")
- `conteudos_nucleares` — Lista separada por ponto-e-vírgula (ex: "Conceito 1; Conceito 2")
- `autores` — Lista com nome, datas e filiação (ex: "C. Wright Mills (1916–1962)")
- `elementos_obrigatorios` — Elementos que DEVEM aparecer no capítulo (ex: "Definição de X; Exemplos")

## 5. Estrutura de disciplinas suportadas

### Sociologia ✓
Contexto completo: `contexto/disciplinas/sociologia.md`

### História ✓
Contexto completo: `contexto/disciplinas/historia.md`

### Filosofia ⚠️ (em desenvolvimento)
Contexto incompleto: `contexto/disciplinas/filosofia.md`

### Geografia ⚠️ (em desenvolvimento)
Contexto incompleto: `contexto/disciplinas/geografia.md`

## 6. Monitoramento e logs

Logs detalhados são salvos em:
```
logs/pipeline_YYYYMMDD_HHMMSS.log
```

Também aparece no stdout em tempo real.

## 7. Fluxo de execução típico

### Passo 1: Teste rápido (dry-run)
```bash
python pipeline.py input/apostila-teste-sociologia/instrucoes.csv --dry-run --cap 1
```

### Passo 2: Executar um capítulo completo
```bash
python pipeline.py input/apostila-teste-sociologia/instrucoes.csv --cap 1
```

### Passo 3: Toda a apostila
```bash
python pipeline.py input/apostila-teste-sociologia/instrucoes.csv
```

## 8. Próximos passos

- [ ] **Agente 3** (Validador Técnico) — skill + integração
- [ ] **Agente 5** (Diagramador XML) — skill + integração
- [ ] **teste_cache.py** — validar redução de custo
- [ ] **Contextos Filosofia + Geografia** — disciplinas completas
- [ ] **Interface web** — alternativa ao CSV manual

## 9. Troubleshooting

### "ANTHROPIC_API_KEY não configurada"
→ Crie arquivo `.env` com sua chave. Veja seção 1.2.

### "Contexto disciplinar não encontrado"
→ Disciplina no CSV não tem contexto. Verifique `contexto/disciplinas/`.

### "Rate limit"
→ Pipeline faz retry automático com backoff exponencial. Aguarde.

### Arquivo de log muito grande?
→ Logs antigos estão em `logs/`. Pipeline cria novo arquivo a cada execução.

