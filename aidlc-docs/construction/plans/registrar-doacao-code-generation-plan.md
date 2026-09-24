# Code Generation Plan — Unit: registrar-doacao

## Unit Context
- **Stories implemented**: Backlog #14 — "Como Voluntário, quero registrar uma doação vinculando um doador, um item e uma quantidade, para que o saldo aumente e o histórico fique registrado."
- **Dependencies on other units/services**: Nenhuma (modelos `Doacao`, `Item`, `Doador`, `Usuario` já existem e já estão migrados)
- **Expected interfaces/contracts**: Rota web `GET/POST /doacoes/nova/` → view `doacao_create`
- **Database entities owned**: `Doacao` (já existe, sem alteração de schema)
- **Service boundaries**: Tudo dentro do app `core` existente; nenhum novo app/serviço

**Workspace root**: `/home/afelipe/projects/projeto-eng-soft` (lido de `aidlc-docs/aidlc-state.md`)
**Application code location**: raiz do workspace, dentro do app `core/` já existente (brownfield — modificar arquivos existentes in-place; nenhum arquivo novo de config)

---

## Steps

### Step 1: Business Logic — DoacaoForm
- [x] Modificar `core/forms.py` (arquivo existe): adicionar `DoacaoForm(forms.ModelForm)` para o model `Doacao`, com campos `doador`, `item`, `quantidade`, `data`.
  - Seguir o padrão de `ItemForm`/`FamiliaForm`: `Meta.widgets` usando `_CARD_SELECT_CLASS` para `doador`/`item` (Select) e `_CARD_INPUT_CLASS` para `quantidade` (NumberInput, `step="0.01"`, `min="0.01"`) e `data` (DateInput `type="date"`).
  - `clean_quantidade`: validar `> 0` (mensagem de erro clara; embora o model já valide via `MinValueValidator(0.01)`, replicar a validação no form segue o padrão de `clean_estoque_minimo` em `ItemForm` para dar erro amigável antes de tocar o banco).
  - `clean_data`: validar `data <= timezone.localdate()` (rejeitar datas futuras, conforme requirements.md).
  - `labels`: "Doador", "Item", "Quantidade", "Data".
  - `data-testid` nos widgets: `doacao-form-doador-select`, `doacao-form-item-select`, `doacao-form-quantidade-input`, `doacao-form-data-input`.

### Step 2: Business Logic Unit Testing — DoacaoForm/View
- [x] Adicionar `DoacaoTestCase(TestCase)` em `core/tests.py`, seguindo o padrão de `ItemTestCase`/`FamiliaTestCase` (setUp cria usuário Voluntário logado, doador, categoria, unidade, item):
  - `test_cadastrar_doacao_com_sucesso`: POST válido cria `Doacao`, `registrado_por` = usuário logado, `Item.saldo_atual` aumenta exatamente pela quantidade, mensagem de sucesso, redireciona para `doacao_create`.
  - `test_cadastrar_doacao_quantidade_zero_ou_negativa_invalida`: quantidade `0` e quantidade negativa são rejeitadas, nenhuma `Doacao` criada.
  - `test_cadastrar_doacao_quantidade_fracionada_permitida`: quantidade decimal (ex.: `2.5`) é aceita.
  - `test_cadastrar_doacao_data_futura_invalida`: data futura é rejeitada com mensagem de erro.
  - `test_cadastrar_doacao_acesso_anonimo_redireciona_para_login`: usuário não autenticado é redirecionado para login.
  - `test_administrador_tambem_pode_registrar_doacao`: usuário Administrador também consegue registrar (sem `@admin_obrigatorio`).

### Step 3: Business Logic Summary
- [x] Nenhuma alteração de model/migração necessária — `Doacao` já existe e já está migrado; `Item.saldo_atual` já calcula o saldo automaticamente a partir das doações não canceladas.

### Step 4: API Layer — View e URL
- [x] Modificar `core/views.py` (arquivo existe): adicionar seção `# Doações` com view `doacao_create(request)`:
  - `@login_obrigatorio` (sem `@admin_obrigatorio` — Voluntário e Administrador podem registrar, conforme requirements.md).
  - GET: renderiza `DoacaoForm()` vazio, com `data` inicial = hoje.
  - POST: `DoacaoForm(request.POST)`; se válido, `doacao = form.save(commit=False)`; `doacao.registrado_por = request.user`; `doacao.save()`; `messages.success(request, "Doação registrada com sucesso!")`; `redirect("doacao_create")` (formulário limpo, permite registrar em sequência — conforme requirements.md FR1).
  - Renderiza `core/doacao_form.html`.
- [x] Modificar `core/urls.py` (arquivo existe): adicionar `path("doacoes/nova/", views.doacao_create, name="doacao_create")` na seção de rotas, próximo às demais rotas de criação.

### Step 5: API Layer Unit Testing
- [x] Coberto no Step 2 (mesmos testes cobrem view + form, seguindo o padrão já usado no projeto onde não há separação de testes de form vs. view para as views mais simples).

### Step 6: API Layer Summary
- [x] Nova rota `doacoes/nova/` (`doacao_create`) segue exatamente o mesmo padrão de `doador_create`/`familia_create`: função baseada em view, sem `@admin_obrigatorio`, `messages.success` + redirect.

### Step 7: Repository Layer
- [x] N/A — projeto usa Django ORM diretamente nas views (sem camada de repositório separada), conforme padrão existente. Nenhuma alteração necessária.

### Step 8: Frontend Components — Template
- [x] Criar `templates/core/doacao_form.html`, seguindo o esqueleto de `templates/core/doador_form.html` / `familia_form.html`:
  - `{% extends "dashboard_base.html" %}`, `block title` = "Nova Doação | Conecta Social", `block page_title` = "Nova Doação", `block page_subtitle` = texto curto.
  - Card com `data-testid="doacao-form-card"`, `<form method="post" data-testid="doacao-form">`, `{% csrf_token %}`.
  - Campos via `{% include "partials/_campo_formulario_dashboard.html" with field=form.<campo> %}` para `doador`, `item`, `quantidade`, `data` (layout em duas colunas `sm:flex-row`, como em `doador_form.html`).
  - Botão "Registrar doação" (`data-testid="doacao-form-submit-button"`) + link "Cancelar" para `item_list` (não existe `doacao_list` nesta história).

### Step 9: Frontend Components — Navegação
- [x] Modificar `templates/partials/_sidebar.html`: trocar o `<span data-testid="sidebar-link-movimentacoes">` por `<a href="{% url 'doacao_create' %}" ...>`, mantendo o mesmo ícone (`icons/sidebar/movimentacoes.svg`) e aplicando a classe de destaque (`bg-secondary text-white`) quando `request.resolver_match.url_name == 'doacao_create'`, seguindo exatamente o padrão dos demais links (ex.: `sidebar-link-doadores`).
- [x] Modificar `templates/core/item_list.html`: adicionar `<a href="{% url 'doacao_create' %}" class="btn btn-secondary btn-sm rounded-md" data-testid="item-list-nova-doacao-link">+ Doação</a>` ao lado do botão "+ Item" já existente.

### Step 10: Frontend Components Unit Testing
- [x] N/A — sem framework de teste de frontend no projeto (JS); validação da UI ocorre via testes Django (`core/tests.py`, Step 2) que verificam status code, conteúdo do form e redirecionamento.

### Step 11: Frontend Components Summary
- [x] Novo template `doacao_form.html` reaproveita 100% dos partials e classes CSS já existentes (`_campo_formulario_dashboard.html`, `dashboard_base.html`); sidebar e listagem de itens ganham pontos de entrada para a nova tela.

### Step 12: Database Migration Scripts
- [x] N/A — nenhuma alteração de model; `Doacao` já migrado em `0001_initial`. Build and Test irá rodar `makemigrations --check` para confirmar que nenhuma migração ficou pendente.

### Step 13: Documentation Generation
- [x] Criar `aidlc-docs/construction/registrar-doacao/code/summary.md` com resumo em markdown dos arquivos modificados/criados e como os critérios de aceite da #14 são atendidos.

### Step 14: Deployment Artifacts Generation
- [x] N/A — nenhuma mudança de deploy/infraestrutura (confirmado em Workflow Planning); projeto continua servido pelo mesmo processo Gunicorn/WhiteNoise já configurado.

---

## Story Traceability
- Backlog #14 (Deve ter, 5 pontos, Sprint 2): coberto pelos Steps 1, 4, 8, 9.
- Critério "saldo aumenta exatamente pela quantidade": coberto pelo Step 1 (validação) + Step 4 (persistência) + já implementado em `Item.saldo_atual`; verificado no teste `test_cadastrar_doacao_com_sucesso` (Step 2).
- Critério "aparece no histórico do doador e do item": satisfeito pelas FKs `doador`/`item` em `Doacao` (já existentes); tela de histórico dedicada é a história #15, fora de escopo.

This plan is the single source of truth for Code Generation desta unidade.
