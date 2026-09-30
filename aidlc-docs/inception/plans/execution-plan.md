# Execution Plan — Histórias #15 e #18 (Histórico de Doações e Distribuições)

## Detailed Analysis Summary

### Transformation Scope (Brownfield)
- **Transformation Type**: Single component change (app `core`), duas telas estruturalmente idênticas tratadas no mesmo ciclo
- **Primary Changes**: Views `doacao_list`/`distribuicao_list`, rotas `doacoes/`/`distribuicoes/`, templates `doacao_list.html`/`distribuicao_list.html`, links recíprocos de navegação, testes
- **Related Components**: Nenhum além de `core` — `Doacao`/`Distribuicao`/`Doador`/`Familia`/`Item` já existentes e migrados

### Change Impact Assessment
- **User-facing changes**: Sim — duas novas telas de consulta/histórico
- **Structural changes**: Não
- **Data model changes**: Não
- **API changes**: Sim, menor — duas rotas novas (`doacoes/`, `distribuicoes/`), seguindo o padrão já existente
- **NFR impact**: Menor — mesmas regras de Security Baseline já mapeadas para as listagens existentes (`item_list`, `doador_list`)

### Component Relationships
- **Primary Component**: `core`
- **Shared Components**: `Doacao`, `Distribuicao`, `Doador`, `Familia`, `Item` (sem alteração)
- **Dependent Components**: `templates/core/doacao_form.html`, `templates/core/distribuicao_form.html` (ganham link de navegação)

### Risk Assessment
- **Risk Level**: Low — leitura/listagem pura, sem escrita de dados além do já existente
- **Rollback Complexity**: Easy
- **Testing Complexity**: Simple — mesmo padrão de `TestCase` com `Client`, casos já especificados em CT25/CT27

## Phases to Execute

### INCEPTION PHASE
- [x] Workspace Detection (COMPLETED — reaproveitado)
- [x] Reverse Engineering (SKIPPED — artefatos já existentes)
- [x] Requirements Analysis (COMPLETED, referenciando CT25/CT27)
- [x] User Stories (SKIPPED — backlog #15/#18 já são histórias completas com critérios de aceite, reforçados pelos casos de teste do professor)
- [x] Execution Plan (IN PROGRESS)
- [ ] Application Design — **SKIP**
  - **Rationale**: Nenhum componente novo; duas views de listagem dentro do app `core` já existente, mesmo padrão de `item_list`/`doador_list`.
- [ ] Units Generation — **SKIP**
  - **Rationale**: Duas telas estruturalmente idênticas, implementação direta, um único pacote (`core`) — não justifica decomposição em unidades separadas.

### CONSTRUCTION PHASE
- [ ] Functional Design — **SKIP**
  - **Rationale**: Sem lógica de negócio complexa nova — filtro por FK e por intervalo de data são operações de ORM diretas (`.filter(doador=..., data__gte=..., data__lte=...)`), mesmo padrão de `doador_list`/`item_list` com busca por `icontains`.
- [ ] NFR Requirements — **SKIP**
  - **Rationale**: Regras de Security Baseline aplicáveis já mapeadas em requirements.md; nenhuma tecnologia nova.
- [ ] NFR Design — **SKIP**
  - **Rationale**: Consequência do skip de NFR Requirements.
- [ ] Infrastructure Design — **SKIP**
  - **Rationale**: Nenhuma mudança de infraestrutura.
- [ ] Code Generation — **EXECUTE (ALWAYS)**
  - **Rationale**: Implementação das duas views, templates, rotas, navegação e testes.
- [ ] Build and Test — **EXECUTE (ALWAYS)**
  - **Rationale**: `ruff`, `manage.py test` cobrindo os cenários de CT25/CT27, `makemigrations --check`.

### OPERATIONS PHASE
- [ ] Operations — PLACEHOLDER

## Estimated Timeline
- **Total Phases Executed**: 2 (Code Generation, Build and Test) + Requirements já concluída
- **Estimated Duration**: Sessão única (2 histórias pequenas, 3 pontos cada, mesmo padrão)

## Success Criteria
- **Primary Goal**: Voluntário/Administrador consegue consultar o histórico de doações (por doador/período) e de distribuições (por família/período), com paginação, exatamente como especificado nos critérios de aceite do backlog e nos casos CT25/CT27 do plano de testes.
- **Key Deliverables**: `doacao_list`, `distribuicao_list`, templates correspondentes, navegação recíproca, testes cobrindo filtros isolados/combinados, paginação e exclusão de canceladas.
- **Quality Gates**: `ruff check` sem erros; `python manage.py test` passando; `makemigrations --check` sem pendências; nenhum teste existente quebrado (critério de bloqueio de merge do plano de testes, item "a").
