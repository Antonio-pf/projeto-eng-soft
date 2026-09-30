# Code Generation Summary — Unit: registrar-distribuicao

## Backlog Story
- **#16**: Como Voluntário, quero registrar uma distribuição vinculando uma família, um item e uma quantidade, para que o saldo diminua e o beneficiário fique registrado.

## Files Modified
- `core/forms.py` — adicionado `DistribuicaoForm` (ModelForm sobre `Distribuicao`), com `clean_quantidade`, `clean_data` e um `clean()` novo que bloqueia saldo insuficiente.
- `core/views.py` — adicionada view `distribuicao_create` (espelha `doacao_create`).
- `core/urls.py` — adicionada rota `distribuicoes/nova/` → `distribuicao_create`.
- `core/tests.py` — adicionada `DistribuicaoTestCase` com 7 testes.
- `templates/partials/_sidebar.html` — link "Movimentações" agora destaca também a rota `distribuicao_create`.
- `templates/core/item_list.html` — adicionado botão "+ Distribuição".

## Files Created
- `templates/core/distribuicao_form.html` — formulário de registro de distribuição (espelha `doacao_form.html`).

## Acceptance Criteria Coverage
| Critério (backlog #16) | Onde é atendido |
|---|---|
| Formulário solicita família, item, quantidade (inteiro/decimal > 0) e data (padrão hoje) | `DistribuicaoForm` + `distribuicao_create` (GET) |
| Se saldo atual < quantidade solicitada, bloqueia com "Saldo insuficiente: disponível X, solicitado Y" | `DistribuicaoForm.clean()` |
| Após salvar com sucesso, saldo diminui exatamente pela quantidade | `Item.saldo_atual` (já existente, subtrai distribuições não canceladas) — sem lógica nova |

## Out of Scope (ciclos AI-DLC próprios)
- #17 — saldo em tempo real no formulário via JS
- #18 — histórico/listagem de distribuições com filtro
- #19 — cancelamento de movimentação

## No Migration Needed
`Distribuicao` já existe e está migrada em `core/migrations/0001_initial.py`. `makemigrations --check` será executado em Build and Test para confirmar ausência de pendências.
