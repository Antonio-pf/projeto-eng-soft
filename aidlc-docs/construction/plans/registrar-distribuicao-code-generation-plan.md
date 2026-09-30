# Code Generation Plan — Unit: registrar-distribuicao

## Unit Context
- **Stories implemented**: Backlog #16 — "Como Voluntário, quero registrar uma distribuição vinculando uma família, um item e uma quantidade, para que o saldo diminua e o beneficiário fique registrado."
- **Dependencies on other units/services**: Nenhuma (models `Distribuicao`, `Item`, `Familia`, `Usuario` já existem e já estão migrados)
- **Expected interfaces/contracts**: Rota web `GET/POST /distribuicoes/nova/` → view `distribuicao_create`
- **Database entities owned**: `Distribuicao` (já existe, sem alteração de schema)
- **Service boundaries**: Tudo dentro do app `core` existente; nenhum novo app/serviço

**Workspace root**: `/home/afelipe/projects/projeto-eng-soft` (lido de `aidlc-docs/aidlc-state.md`)
**Application code location**: raiz do workspace, dentro do app `core/` já existente (brownfield — modificar arquivos existentes in-place; nenhum arquivo novo de config)

---

## Steps

### Step 1: Business Logic — DistribuicaoForm
- [x] Modificar `core/forms.py` (arquivo existe): adicionar `DistribuicaoForm(forms.ModelForm)` para o model `Distribuicao`, com campos `familia`, `item`, `quantidade`, `data` — espelhando `DoacaoForm` (`core/forms.py:281`).
  - `Meta.widgets`: `_CARD_SELECT_CLASS` para `familia`/`item` (Select), `_CARD_INPUT_CLASS` para `quantidade` (NumberInput, `step="0.01"`, `min="0.01"`) e `data` (DateInput `type="date"`).
  - `__init__`: mesmo padrão de `DoacaoForm.__init__` — se não vinculado e sem `initial["data"]`, define `timezone.localdate()`.
  - `clean_quantidade`: validar `> 0` (mesma mensagem de `DoacaoForm`: "A quantidade deve ser maior que zero.").
  - `clean_data`: validar `data <= timezone.localdate()` (mesma mensagem de `DoacaoForm`: "A data não pode ser no futuro.").
  - `clean()` (novo, específico desta história): após `super().clean()`, se `item` e `quantidade` presentes e válidos, comparar `item.saldo_atual` com `quantidade`; se `quantidade > saldo_atual`, `raise forms.ValidationError("Saldo insuficiente: disponível {saldo}, solicitado {quantidade}.".format(...))` com os dois valores formatados com 2 casas decimais. Quando saldo == quantidade, a operação é permitida (limite, não bloqueio).
  - `labels`: "Família", "Item", "Quantidade", "Data".
  - `data-testid` nos widgets: `distribuicao-form-familia-select`, `distribuicao-form-item-select`, `distribuicao-form-quantidade-input`, `distribuicao-form-data-input`.

### Step 2: Business Logic Unit Testing — DistribuicaoForm/View
- [x] Adicionar `DistribuicaoTestCase(TestCase)` em `core/tests.py`, seguindo o padrão de `DoacaoTestCase` (setUp cria usuário Voluntário e Administrador logáveis, família, categoria, unidade, item, e uma `Doacao` prévia para dar saldo ao item):
  - `test_registrar_distribuicao_com_sucesso`: POST válido cria `Distribuicao`, `registrado_por` = usuário logado, `Item.saldo_atual` diminui exatamente pela quantidade, mensagem de sucesso, redireciona para `distribuicao_create`.
  - `test_registrar_distribuicao_quantidade_zero_ou_negativa_invalida`: quantidade `0` e negativa rejeitadas, nenhuma `Distribuicao` criada.
  - `test_registrar_distribuicao_data_futura_invalida`: data futura rejeitada.
  - `test_registrar_distribuicao_saldo_insuficiente_bloqueada`: quantidade solicitada maior que `saldo_atual` é bloqueada, mensagem de erro contém "Saldo insuficiente" com os valores disponível/solicitado, nenhuma `Distribuicao` criada, saldo do item permanece inalterado.
  - `test_registrar_distribuicao_saldo_exatamente_igual_permitida`: quantidade igual ao saldo disponível é aceita (saldo final = 0).
  - `test_registrar_distribuicao_acesso_anonimo_redireciona_para_login`.
  - `test_administrador_tambem_pode_registrar_distribuicao`.

### Step 3: Business Logic Summary
- [x] Nenhuma alteração de model/migração necessária — `Distribuicao` já existe e já está migrado; `Item.saldo_atual` já subtrai distribuições não canceladas do total de doações.

### Step 4: API Layer — View e URL
- [x] Modificar `core/views.py` (arquivo existe): adicionar seção `# Distribuições` com view `distribuicao_create(request)`, logo após `doacao_create`:
  - `@login_obrigatorio` (sem `@admin_obrigatorio` — Voluntário e Administrador podem registrar).
  - GET: renderiza `DistribuicaoForm()` vazio, com `data` inicial = hoje.
  - POST: `DistribuicaoForm(request.POST)`; se válido (incluindo a checagem de saldo no `clean()`), `distribuicao = form.save(commit=False)`; `distribuicao.registrado_por = request.user`; `distribuicao.save()`; `messages.success(request, "Distribuição registrada com sucesso!")`; `redirect("distribuicao_create")`.
  - Se inválido (incluindo saldo insuficiente): renderiza `core/distribuicao_form.html` novamente com os erros do form (`form.non_field_errors` exibe a mensagem de saldo insuficiente).
- [x] Modificar `core/urls.py` (arquivo existe): adicionar `path("distribuicoes/nova/", views.distribuicao_create, name="distribuicao_create")` logo após a rota `doacoes/nova/`.

### Step 5: API Layer Unit Testing
- [x] Coberto no Step 2 (mesmo padrão do projeto — sem separação de testes de form vs. view para views simples).

### Step 6: API Layer Summary
- [x] Nova rota `distribuicoes/nova/` (`distribuicao_create`) segue o mesmo padrão de `doacao_create`, com a adição da checagem de saldo insuficiente delegada ao `clean()` do form (mantém a view enxuta e a regra de negócio testável isoladamente).

### Step 7: Repository Layer
- [x] N/A — projeto usa Django ORM diretamente nas views, conforme padrão existente. Nenhuma alteração necessária.

### Step 8: Frontend Components — Template
- [x] Criar `templates/core/distribuicao_form.html`, espelhando `templates/core/doacao_form.html`:
  - `{% extends "dashboard_base.html" %}`, `block title` = "Nova Distribuição | Conecta Social", `block page_title` = "Nova Distribuição", `block page_subtitle` = texto curto.
  - Card com `data-testid="distribuicao-form-card"`, `<form method="post" data-testid="distribuicao-form">`, `{% csrf_token %}`, exibindo `form.non_field_errors` (mostra a mensagem de saldo insuficiente).
  - Campos via `{% include "partials/_campo_formulario_dashboard.html" with field=form.<campo> %}` para `familia`, `item`, `quantidade`, `data` (layout em duas colunas `sm:flex-row`, como em `doacao_form.html`).
  - Botão "Registrar distribuição" (`data-testid="distribuicao-form-submit-button"`) + link "Cancelar" para `item_list`.

### Step 9: Frontend Components — Navegação
- [x] Modificar `templates/partials/_sidebar.html`: adicionar `distribuicao_create` à lista de rotas que destacam o link "Movimentações" (`sidebar-link-movimentacoes`), junto de `doacao_create` — `href` continua apontando para `doacao_create` (ponto de entrada padrão de "Movimentações"; sem submenu nesta história).
- [x] Modificar `templates/core/item_list.html`: adicionar `<a href="{% url 'distribuicao_create' %}" class="btn btn-secondary btn-sm rounded-md" data-testid="item-list-nova-distribuicao-link">+ Distribuição</a>` ao lado do botão "+ Doação" já existente.

### Step 10: Frontend Components Unit Testing
- [x] N/A — sem framework de teste de frontend no projeto; validação da UI ocorre via testes Django (Step 2).

### Step 11: Frontend Components Summary
- [x] Novo template `distribuicao_form.html` reaproveita 100% dos partials e classes CSS já existentes; sidebar e listagem de itens ganham ponto de entrada para a nova tela.

### Step 12: Database Migration Scripts
- [x] N/A — nenhuma alteração de model; `Distribuicao` já migrado em `0001_initial`. Build and Test irá rodar `makemigrations --check` para confirmar.

### Step 13: Documentation Generation
- [ ] Criar `aidlc-docs/construction/registrar-distribuicao/code/summary.md` com resumo em markdown dos arquivos modificados/criados e como os critérios de aceite da #16 são atendidos.

### Step 14: Deployment Artifacts Generation
- [x] N/A — nenhuma mudança de deploy/infraestrutura; projeto continua servido pelo mesmo processo já configurado.

---

## Story Traceability
- Backlog #16 (Deve ter, 5 pontos, Sprint 2): coberto pelos Steps 1, 4, 8, 9.
- Critério "se saldo atual < quantidade, operação bloqueada com mensagem exata": coberto pelo Step 1 (`clean()`) e verificado em `test_registrar_distribuicao_saldo_insuficiente_bloqueada` (Step 2).
- Critério "saldo diminui exatamente pela quantidade": coberto pelo Step 1 (validação) + Step 4 (persistência) + já implementado em `Item.saldo_atual`; verificado em `test_registrar_distribuicao_com_sucesso` (Step 2).
- Fora de escopo (histórias próprias, ciclos AI-DLC separados): saldo em tempo real via JS (#17), histórico/listagem (#18), cancelamento (#19).

This plan is the single source of truth for Code Generation desta unidade.
