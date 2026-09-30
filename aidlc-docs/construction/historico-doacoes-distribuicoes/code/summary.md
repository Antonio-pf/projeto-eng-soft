# Code Generation Summary — Unit: historico-doacoes-distribuicoes

## Backlog Stories
- **#15**: Como Voluntário, quero visualizar o histórico de doações com filtro por doador e por período, para que eu consulte o que cada doador contribuiu.
- **#18**: Como Voluntário, quero visualizar o histórico de distribuições com filtro por família e por período, para que eu consulte o que cada família recebeu.

## Referência de Critérios
`docs/backlog.md` #15/#18 e `docs/plano-de-testes.md` CT25/CT27 (casos de teste já definidos pelo professor).

## Files Modified
- `core/views.py` — `doacao_list` e `distribuicao_list` (filtro por `id_doador`/`id_familia` + `data_inicio`/`data_fim`, paginação, exclusão de canceladas).
- `core/urls.py` — rotas `doacoes/` (`doacao_list`) e `distribuicoes/` (`distribuicao_list`).
- `templates/core/doacao_form.html` / `distribuicao_form.html` — link "Ver histórico de ..." apontando para a listagem correspondente.
- `core/tests.py` — `DoacaoListTestCase` (7 testes) e `DistribuicaoListTestCase` (7 testes).

## Files Created
- `templates/core/doacao_list.html`
- `templates/core/distribuicao_list.html`

## Acceptance Criteria Coverage
| Critério | Onde é atendido |
|---|---|
| Lista exibe data, doador/família, item, quantidade e usuário que registrou (CT25/CT27) | Templates `doacao_list.html`/`distribuicao_list.html`, colunas da tabela |
| Filtros por doador/família e por período funcionam isolados e combinados (CT25/CT27) | `doacao_list`/`distribuicao_list` (views), testado em `test_filtro_*_isolado` e `test_filtro_*_combinados` |
| Lista é paginada | `Paginator` (20/página), testado em `test_paginacao_lista_*` |

## Nomenclatura
Parâmetros de filtro por entidade usam o padrão `id_<atributo>` já estabelecido no projeto (ex.: `id_usuario` na rota de status de usuário), em vez do sufixo `_id` — `id_doador`, `id_familia` (correção aplicada a pedido do usuário durante a geração de código).

## Critério de Bloqueio de Merge (plano de testes §2.b)
Regra de negócio nova (exclusão de movimentações canceladas da listagem) coberta por teste dedicado em cada `TestCase` (`test_lista_todas_as_*_sem_filtro`, que verifica que o registro cancelado não aparece).

## No Migration / No New Model
Nenhuma alteração de model ou migração — somente leitura de `Doacao`/`Distribuicao`/`Doador`/`Familia`/`Item` já existentes.
