# Code Generation Summary — Unit: distribuicao-saldo-formulario

## Backlog Story
- **#17**: Como Voluntário, quero ver o saldo disponível do item ao preencher o formulário de distribuição, para que eu saiba antes de submeter se a quantidade é viável.

## Referência de Design
Figma — frame "distribuicao" (node `2603:641`), card "Nova Distribuição" (node `2603:701`).

## Files Modified
- `core/forms.py` — novo `_ItemComSaldoChoiceField` (subclasse de `ModelChoiceField` com `label_from_instance` mostrando saldo inline); `DistribuicaoForm.item` declarado explicitamente usando esse field.
- `core/views.py` — `distribuicao_create` agora monta e passa `itens_saldo` (saldo + unidade por item) ao contexto do template.
- `templates/core/distribuicao_form.html` — adicionado `{{ itens_saldo|json_script }}`, Info-Box (`#distribuicao-form-saldo-info`) entre o campo "Item" e a linha Qtd/Data, e um `<script>` vanilla JS que atualiza o Info-Box ao trocar o item.
- `core/tests.py` — 2 novos testes em `DistribuicaoTestCase`.

## Files Created
- Nenhum.

## Acceptance Criteria Coverage
| Critério (backlog #17) | Onde é atendido |
|---|---|
| Saldo atual do item selecionado é exibido ao selecionar o item | Opção do dropdown mostra `"{nome} saldo: {saldo}"` (`_ItemComSaldoChoiceField`) + Info-Box atualizado via JS no evento `change` |
| Saldo reflete sempre o valor mais atualizado | `itens_saldo` é calculado a partir de `Item.saldo_atual` no momento da renderização (GET/POST), sem cache/hardcode |

## No Migration / No New Route
Nenhuma alteração de model ou rota — mesma `GET/POST /distribuicoes/nova/` da história #16.
