# Code Generation Plan — Unit: distribuicao-saldo-formulario

## Unit Context
- **Stories implemented**: Backlog #17 — "Como Voluntário, quero ver o saldo disponível do item ao preencher o formulário de distribuição, para que eu saiba antes de submeter se a quantidade é viável."
- **Dependencies on other units/services**: história #16 (`distribuicao_create`, `DistribuicaoForm`, `distribuicao_form.html`) já implementada nesta mesma branch
- **Expected interfaces/contracts**: Nenhuma rota nova — mesma `GET/POST /distribuicoes/nova/`
- **Database entities owned**: Nenhuma (somente leitura de `Item.saldo_atual`)
- **Service boundaries**: Tudo dentro do app `core` existente

**Workspace root**: `/home/afelipe/projects/projeto-eng-soft`
**Application code location**: raiz do workspace, dentro do app `core/` já existente (brownfield — modificar arquivos existentes in-place)

**Referência de design**: Figma — frame "distribuicao" (node `2603:641`), card "Nova Distribuição" (node `2603:701`). Ver `aidlc-docs/inception/requirements/requirements.md` seção "Referência de Design (Figma)".

---

## Steps

### Step 1: Business Logic — Item com saldo inline no DistribuicaoForm
- [x] Modificar `core/forms.py`: declarar explicitamente o campo `item` em `DistribuicaoForm` como `forms.ModelChoiceField`, sobrepondo `label_from_instance` para retornar `f"{obj.nome} saldo: {obj.saldo_atual:.2f}"` — mantendo o mesmo `queryset` (`Item.objects.all()`), o mesmo widget (`_CARD_SELECT_CLASS`, `data-testid="distribuicao-form-item-select"`) e o mesmo `label` ("Item") já existentes.
- [x] Adicionar `select_related("unidade_medida")` ao queryset do campo `item` (já necessário para o Step 4, evita N+1 ao montar `itens_saldo` na view).

### Step 2: Business Logic Unit Testing
- [x] Adicionar teste em `DistribuicaoTestCase` (`core/tests.py`): `test_formulario_exibe_saldo_inline_na_opcao_do_item` — GET em `distribuicao_create`, verifica que a resposta contém a string `"saldo: 10.00"` (dado o item com saldo 10 do `setUp`) na opção do campo item.

### Step 3: Business Logic Summary
- [x] Nenhuma alteração de model/migração — apenas o rótulo de exibição do campo muda.

### Step 4: API Layer — Contexto da view com saldo por item
- [x] Modificar `core/views.py`: em `distribuicao_create`, construir `itens_saldo = {str(item.pk): {"saldo": f"{item.saldo_atual:.2f}", "unidade": item.unidade_medida.sigla} for item in Item.objects.select_related("unidade_medida").all()}` e incluir no contexto (`{"form": form, "itens_saldo": itens_saldo}`), tanto no branch GET quanto no branch de POST inválido (reexibição do formulário).

### Step 5: API Layer Unit Testing
- [x] Adicionar teste `test_contexto_da_view_contem_saldo_por_item`: GET em `distribuicao_create`, verifica `response.context["itens_saldo"]` contém a entrada do item de teste com o saldo correto (`"10.00"`).

### Step 6: API Layer Summary
- [x] View `distribuicao_create` (história #16) ganha uma chave extra de contexto (`itens_saldo`); nenhuma mudança de assinatura de rota/método.

### Step 7: Repository Layer
- [x] N/A — Django ORM direto, sem alteração.

### Step 8: Frontend Components — Info-Box + script (conforme Figma)
- [x] Modificar `templates/core/distribuicao_form.html`:
  - Adicionar `{{ itens_saldo|json_script:"distribuicao-itens-saldo" }}` dentro do `<form>` (ou logo antes dele).
  - Adicionar, entre o campo "Item" e a linha Qtd/Data (mesma posição do "Info-Box" no Figma), um elemento `<div id="distribuicao-form-saldo-info" data-testid="distribuicao-form-saldo-info" class="hidden rounded-lg bg-green-100 px-4 py-3 text-sm font-semibold text-primary"></div>` — reaproveitando as classes `bg-green-100`/`text-primary` já usadas em `item_list.html`/`usuarios.html` para indicadores positivos.
  - Adicionar um `<script>` inline (vanilla JS, sem framework/lib nova) que:
    - Lê o JSON de `#distribuicao-itens-saldo`.
    - Define `atualizarSaldoInfo()`: lê o `<select>` de item pelo `data-testid="distribuicao-form-item-select"`, busca a entrada correspondente no dicionário; se existir, define o texto `"Saldo disponível: {saldo} {unidade}"` no `#distribuicao-form-saldo-info` e remove a classe `hidden`; caso contrário, adiciona `hidden`.
    - Chama `atualizarSaldoInfo()` imediatamente (o script já está posicionado após os elementos no HTML, não precisa esperar `DOMContentLoaded`) e a registra também no evento `change` do select — cobre tanto o carregamento inicial quanto a reexibição do formulário após erro de validação.

### Step 9: Frontend Components — Navegação
- [x] N/A — nenhuma mudança de navegação/sidebar nesta história (já resolvida na #16).

### Step 10: Frontend Components Unit Testing
- [x] N/A — sem framework de teste de JS no projeto; comportamento do script validado manualmente em Build and Test (documentado em `integration-test-instructions.md`).

### Step 11: Frontend Components Summary
- [x] Template `distribuicao_form.html` ganha o Info-Box e o script, reaproveitando 100% dos tokens de cor e do `json_script` nativo do Django — layout final replica o card "Nova Distribuição" do Figma.

### Step 12: Database Migration Scripts
- [x] N/A — nenhuma alteração de model.

### Step 13: Documentation Generation
- [ ] Criar `aidlc-docs/construction/distribuicao-saldo-formulario/code/summary.md` com resumo dos arquivos modificados e como os critérios de aceite da #17 são atendidos.

### Step 14: Deployment Artifacts Generation
- [x] N/A — nenhuma mudança de deploy/infraestrutura.

---

## Story Traceability
- Backlog #17 (Deveria ter, 3 pontos, Sprint 2): coberto pelos Steps 1, 4, 8.
- Critério "saldo atual do item selecionado é exibido ao selecionar o item": coberto pelo Step 1 (opção com saldo inline) + Steps 4/8 (Info-Box dinâmico via JS).
- Critério "saldo reflete sempre o valor mais atualizado": satisfeito porque o saldo exibido é sempre calculado no momento da renderização da página (`Item.saldo_atual`), sem valor hardcoded ou cache.

This plan is the single source of truth for Code Generation desta unidade.
