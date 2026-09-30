# Code Generation Plan — Unit: historico-doacoes-distribuicoes

## Unit Context
- **Stories implemented**: Backlog #15 (histórico de doações, filtro por doador/período) e #18 (histórico de distribuições, filtro por família/período)
- **Dependencies on other units/services**: histórias #14/#16 (`Doacao`, `Distribuicao`, `doacao_create`, `distribuicao_create`) já implementadas
- **Expected interfaces/contracts**: Rotas `GET /doacoes/` (`doacao_list`) e `GET /distribuicoes/` (`distribuicao_list`)
- **Database entities owned**: Nenhuma nova — somente leitura de `Doacao`/`Distribuicao`/`Doador`/`Familia`/`Item`
- **Service boundaries**: Tudo dentro do app `core`

**Referência de critérios**: `docs/backlog.md` #15/#18 + `docs/plano-de-testes.md` CT25/CT27.

---

## Steps

### Step 1: Business Logic — Filtros de doacao_list
- [x] Modificar `core/views.py`: adicionar `doacao_list(request)` com `@login_obrigatorio`:
  - Query base: `Doacao.objects.filter(cancelado=False).select_related("doador", "item", "registrado_por").order_by("-data")`.
  - Filtro `id_doador` (GET, nome de parâmetro/variável no padrão `id_<atributo>` já usado no projeto — ex.: `id_usuario` na rota de status — em vez do sufixo `_id` do Django): `.filter(doador_id=id_doador)` se presente (o `doador_id=` do lado esquerdo é o nome interno que o Django gera para o lookup por FK a partir do campo `doador` do model; não é escolha nossa de nomenclatura).
  - Filtros `data_inicio`/`data_fim` (GET, formato `YYYY-MM-DD`): parseados com `django.utils.dateparse.parse_date` (retorna `None` para formato inválido, evitando erro 500 — SECURITY-05); aplicados via `.filter(data__gte=...)`/`.filter(data__lte=...)` somente quando parseados com sucesso.
  - `Paginator` (20 por página), mesmo padrão de `item_list`.
  - Contexto: `page_obj`, `doadores` (`Doador.objects.order_by("nome")`, para popular o `<select>` do filtro), `id_doador`, `data_inicio`, `data_fim` (valores brutos da querystring, para re-preencher o formulário).

### Step 2: Business Logic — Filtros de distribuicao_list
- [x] Modificar `core/views.py`: adicionar `distribuicao_list(request)`, espelhando `doacao_list` com `Distribuicao`/`Familia` no lugar de `Doacao`/`Doador` (parâmetro `id_familia`, mesmo padrão `id_<atributo>`).

### Step 3: Business Logic Unit Testing
- [x] Adicionar `DoacaoListTestCase` em `core/tests.py`: setUp com 2 doadores, 1 item, 3 doações em datas/doadores distintos (uma delas `cancelado=True`, criada diretamente via `Doacao.objects.create(..., cancelado=True)` ou `.update()`), usuário logado.
  - `test_lista_todas_as_doacoes_sem_filtro`: sem filtro, exibe as doações não canceladas, não exibe a cancelada.
  - `test_filtro_por_doador_isolado`.
  - `test_filtro_por_periodo_isolado` (intervalo cobrindo só uma das datas).
  - `test_filtro_por_doador_e_periodo_combinados`.
  - `test_filtro_com_data_invalida_e_ignorado_sem_erro_500`.
  - `test_paginacao_lista_doacoes` (mais de 20 registros).
  - `test_lista_doacoes_acesso_anonimo_redireciona_para_login`.
- [ ] Adicionar `DistribuicaoListTestCase`, espelhando os mesmos casos para `distribuicao_list`/`Familia`.

### Step 4: Business Logic Summary
- [x] Nenhuma alteração de model/migração — somente leitura.

### Step 5: API Layer — Rotas
- [x] Modificar `core/urls.py`: adicionar `path("doacoes/", views.doacao_list, name="doacao_list")` e `path("distribuicoes/", views.distribuicao_list, name="distribuicao_list")`, próximas às rotas de criação correspondentes.

### Step 6: API Layer Unit Testing
- [x] Coberto no Step 3 (mesmo padrão do projeto).

### Step 7: API Layer Summary
- [x] Duas rotas novas, somente leitura, seguindo exatamente o padrão de `item_list`/`doador_list`.

### Step 8: Frontend — Templates de listagem
- [x] Criar `templates/core/doacao_list.html`, espelhando `templates/core/item_list.html` (tabela + filtros + paginação):
  - Formulário `GET` com `<select name="id_doador">` (opções = `doadores` do contexto, `selected` se `doador.pk|stringformat:"s" == id_doador`), `<input type="date" name="data_inicio">`, `<input type="date" name="data_fim">`, botão "Filtrar" e link "Limpar" (se algum filtro ativo).
  - Tabela: colunas Data, Doador, Item, Quantidade, Usuário (`registrado_por.nome`).
  - Paginação preservando os 3 filtros na querystring (mesmo padrão de `item_list.html`, estendido).
  - Botão "+ Nova Doação" no topo, apontando para `doacao_create` (mesmo padrão de `item_list.html`).
  - `data-testid`: `doacao-list-*` (form, select, inputs, table, row).
- [x] Criar `templates/core/distribuicao_list.html`, espelhando o mesmo padrão com Família em vez de Doador.

### Step 9: Frontend — Navegação
- [x] Modificar `templates/core/doacao_form.html`: adicionar link "Ver histórico de doações" (`data-testid="doacao-form-ver-historico-link"`) apontando para `doacao_list`, próximo ao botão "Cancelar".
- [x] Modificar `templates/core/distribuicao_form.html`: adicionar link "Ver histórico de distribuições" (`data-testid="distribuicao-form-ver-historico-link"`) apontando para `distribuicao_list`, próximo ao botão "Cancelar".
- [x] Sidebar (`_sidebar.html`) **não é alterada** nesta história (decisão registrada em requirements.md).

### Step 10: Frontend Unit Testing
- [x] N/A — coberto pelos testes de view (Step 3) via `assertContains`.

### Step 11: Frontend Summary
- [x] Dois templates novos, 100% reaproveitando layout/classes de `item_list.html`; dois links novos nos formulários de criação existentes.

### Step 12: Database Migration Scripts
- [x] N/A — nenhuma alteração de model.

### Step 13: Documentation Generation
- [x] Criar `aidlc-docs/construction/historico-doacoes-distribuicoes/code/summary.md`.

### Step 14: Deployment Artifacts Generation
- [x] N/A.

---

## Story Traceability
- Backlog #15 / CT25: coberto pelos Steps 1, 3, 8.
- Backlog #18 / CT27: coberto pelos Steps 2, 3, 8.
- Critério de bloqueio de merge (plano de testes §2.b — regra de negócio nova sem teste): exclusão de canceladas coberta por teste dedicado em cada `TestCase`.

This plan is the single source of truth for Code Generation desta unidade.
