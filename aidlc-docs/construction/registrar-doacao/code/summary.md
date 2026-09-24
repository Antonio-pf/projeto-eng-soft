# Code Generation Summary — registrar-doacao (História #14)

## Arquivos modificados (brownfield)
- `core/forms.py` — adicionado `DoacaoForm` (ModelForm sobre `Doacao`), com `clean_quantidade` (>0, aceita frações) e `clean_data` (≤ hoje); import de `Doacao` e `django.utils.timezone`.
- `core/views.py` — adicionada seção "Doações" com a view `doacao_create` (`@login_obrigatorio`, sem restrição de admin); import de `DoacaoForm`.
- `core/urls.py` — adicionada rota `doacoes/nova/` → `doacao_create`.
- `core/tests.py` — adicionado `DoacaoTestCase` com 6 testes; imports de `Doacao`, `Decimal`, `timedelta`, `timezone`.
- `templates/partials/_sidebar.html` — item "Movimentações" trocado de `<span>` inerte para `<a>` apontando para `doacao_create`, com destaque de rota ativa.
- `templates/core/item_list.html` — adicionado botão "+ Doação" ao lado de "+ Item".

## Arquivos criados
- `templates/core/doacao_form.html` — formulário de registro de doação, seguindo o layout de `doador_form.html`/`item_form.html`.

## Sem alteração de model/migração
- `Doacao` já existia e já estava migrado (`core/migrations/0001_initial.py`); nenhuma nova migração foi gerada.
- `Item.saldo_atual` (property já existente) resolve o critério de aceite "saldo aumenta exatamente pela quantidade informada" sem lógica adicional.

## Cobertura dos critérios de aceite da história #14
| Critério de aceite | Como é atendido |
|---|---|
| Formulário solicita doador, item, quantidade (>0) e data (padrão hoje) | `DoacaoForm` + `doacao_create` view (data inicial preenchida no `__init__` do form) |
| Saldo do item aumenta exatamente pela quantidade | `Item.saldo_atual` (pré-existente) agrega `Doacao` não canceladas |
| Doação aparece no histórico do doador e do item | FKs `Doacao.doador` / `Doacao.item` (pré-existentes); consulta ORM padrão. Tela de histórico dedicada é a história #15 (fora de escopo) |

## Decisões de requirements.md aplicadas
- Acesso: Voluntário e Administrador (sem `@admin_obrigatorio`)
- Quantidade: Decimal, aceita frações, deve ser > 0
- Data: não pode ser futura
- Pós-salvar: redireciona para o próprio formulário limpo
- Navegação: sidebar "Movimentações" ativo + botão "+ Doação" em Itens
