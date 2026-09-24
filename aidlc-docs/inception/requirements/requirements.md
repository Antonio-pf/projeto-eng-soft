# Requirements — História #14: Registrar Doação

## Intent Analysis Summary
- **User Request**: "usando aidlc, quero fazer a tarefa do backlog.md #14 siga os padroes do django e evite reenvitar a roda" — implementar a história #14 do `docs/backlog.md` (registrar doação vinculando doador, item e quantidade), seguindo os padrões Django já estabelecidos no projeto e reaproveitando o que já existe (`Doacao` já modelado e migrado; `Item.saldo_atual` já calculado).
- **Request Type**: New Feature (adição de camada de apresentação — form/view/url/template — sobre um model já existente)
- **Scope Estimate**: Single Component (dentro do app `core` já existente; nenhum novo app/serviço)
- **Complexity Estimate**: Simple — segue exatamente o mesmo padrão de CRUD já usado para Doador/Família/Item; a regra de negócio de saldo já está implementada como property do model

## Referência do Backlog (docs/backlog.md, item #14)
> Como Voluntário, quero registrar uma doação vinculando um doador, um item e uma quantidade, para que o saldo aumente e o histórico fique registrado.
>
> **Critérios de aceite**:
> - Formulário solicita doador (seleção), item (seleção), quantidade (inteiro > 0) e data (padrão: hoje)
> - Após salvar, o saldo do item aumenta exatamente pela quantidade informada
> - A doação aparece no histórico do doador e do item
>
> Prioridade: Deve ter · Pontos: 5 · Sprint: 2

## Functional Requirements

### FR1 — Formulário de registro de doação
- Nova rota `doações/nova/` (nome de URL: `doacao_create`), acessível a qualquer usuário autenticado (Voluntário ou Administrador) — mesmo padrão de `doador_create`/`familia_create` (`@login_obrigatorio`, sem `@admin_obrigatorio`).
- Campos do formulário:
  - **Doador**: `ModelChoiceField` sobre `Doador` (seleção)
  - **Item**: `ModelChoiceField` sobre `Item` (seleção)
  - **Quantidade**: numérico, aceita valores decimais (fracionados), deve ser **maior que zero** — cobre casos de itens parciais/fracionados (ex.: 2.5 kg, meio pacote de item "quebrado")
  - **Data**: campo de data, valor inicial = hoje, **não pode ser data futura** (`data <= hoje`)
- `registrado_por` é preenchido automaticamente com `request.user` (não é campo do formulário).
- Ao submeter com sucesso: salva a `Doacao`, exibe mensagem de sucesso (`messages.success`, seguindo o padrão existente) e **redireciona para o próprio formulário limpo** (`doacao_create`), permitindo registrar doações em sequência sem sair da tela.

### FR2 — Atualização automática do saldo do item
- Nenhuma lógica nova necessária: `Item.saldo_atual` já soma `Doacao` não canceladas; ao salvar a nova `Doacao`, o saldo reflete automaticamente o acréscimo na próxima leitura (ex.: em `item_list`).

### FR3 — Rastreabilidade / histórico
- A doação registrada já fica associada a `Doador` e `Item` via chave estrangeira (histórico consultável por ORM), satisfazendo o critério "aparece no histórico do doador e do item" no nível de dados.
- **Fora de escopo desta história**: uma tela dedicada de listagem/histórico de doações é a história #15 do backlog (não solicitada agora).

### FR4 — Navegação
- O item "Movimentações" do menu lateral (`templates/partials/_sidebar.html`), hoje um `<span>` inerte, passa a ser um link (`<a>`) apontando para `doacao_create` — mesmo padrão visual/`data-testid` dos demais links do menu, incluindo destaque quando a rota ativa for `doacao_create`.
- Um botão de atalho "+ Doação" é adicionado à tela `item_list.html`, ao lado do botão "+ Item" existente, apontando para `doacao_create`.

## Non-Functional Requirements

Aplicáveis por decisão do usuário: **Security Baseline** e **Resiliency Baseline** habilitados, mas **escopados ao nível de código da aplicação** desta história — o repositório não contém infraestrutura como código (sem CDK/Terraform), pipeline de CI/CD formal, nem topologia multi-região/multi-zona definida em código; portanto as regras de infraestrutura/processo dessas duas extensões são marcadas **N/A** para esta tarefa (não são decisão de uma história de backlog isolada). **Property-Based Testing**: desabilitado (CRUD simples).

### Security Baseline — regras aplicáveis ao código desta história
| Regra | Status | Como se aplica |
|---|---|---|
| SECURITY-05 (Input validation) | **Aplicável** | `DoacaoForm` valida tipos, seleção via `ModelChoiceField` (não aceita IDs arbitrários fora do queryset), quantidade > 0, data não futura |
| SECURITY-08 (Application-level access control) | **Aplicável** | Rota exige `@login_obrigatorio`; nenhuma operação expõe dado de outro usuário por ID sem checagem de propriedade (não aplicável aqui pois não há ownership por usuário nesta entidade) |
| SECURITY-15 (Exception handling / fail-safe) | **Aplicável** | Segue o padrão existente do projeto: `form.is_valid()` falha fecha (não salva), sem exceptions não tratadas; erros de validação exibidos de forma genérica ao usuário |
| SECURITY-13 (Data integrity / auditabilidade) | **Aplicável (já satisfeito pelo model)** | `Doacao.registrado_por` + `criado_em` já tornam toda doação auditável (quem/quando) |
| SECURITY-01, 02, 06, 07, 10, 14 (infra: criptografia de storage, load balancer, IAM, rede, supply chain, alerting) | **N/A** | Sem infraestrutura definida no repositório; não é decisão desta história |
| SECURITY-03, 04, 09, 11, 12 (logging centralizado, headers HTTP, hardening, rate limiting, MFA) | **N/A para esta história** | São posturas de projeto inteiro já definidas/fora do escopo de uma tela de CRUD; nenhuma delas é alterada por esta mudança |

### Resiliency Baseline — regras aplicáveis ao código desta história
| Regra | Status | Como se aplica |
|---|---|---|
| RESILIENCY-06 (Health checks) | **N/A para esta mudança** | `/health/` já existe no projeto, não é afetado por esta história |
| RESILIENCY-10 (Timeouts/circuit breaking) | **N/A** | A view não faz chamadas externas (apenas ORM local) |
| RESILIENCY-01, 02, 03, 04, 05, 07, 08, 09, 11, 12, 13, 14, 15 (criticidade, RTO/RPO/DR, change management, CI/CD, observabilidade de infra, multi-zona/região, auto-scaling, backup, chaos engineering, incident response) | **N/A** | Decisões de infraestrutura/processo de projeto inteiro, sem infraestrutura definida no repositório; não fazem sentido escopadas a uma única história de backlog |

### Outras NFRs
- **Consistência de UX**: reutilizar `_CARD_INPUT_CLASS`/`_CARD_SELECT_CLASS` de `core/forms.py` e o layout `dashboard_base.html` + `_campo_formulario_dashboard.html`, sem introduzir novo padrão visual.
- **Testabilidade**: seguir o padrão de `core/tests.py` (um `TestCase` por feature, nomes de teste descritivos em português) cobrindo: cadastro com sucesso, quantidade inválida (zero/negativa), data futura rejeitada, saldo do item aumenta corretamente, acesso anônimo bloqueado.

## Key Requirements Summary
1. Formulário `doacao_create` (doador, item, quantidade decimal > 0, data ≤ hoje, `registrado_por` automático), acessível a Voluntário e Administrador.
2. Ao salvar: mensagem de sucesso + redireciona para o próprio formulário limpo.
3. Saldo do item já é resolvido pelo model existente (`Item.saldo_atual`) — nenhuma lógica nova de cálculo.
4. Sidebar "Movimentações" vira link ativo para `doacao_create`; botão "+ Doação" adicionado em `item_list.html`.
5. Nenhuma tela de histórico/listagem de doações nesta história (é a #15, fora de escopo).
6. Security/Resiliency Baseline aplicados apenas às regras de nível de aplicação relevantes; regras de infraestrutura/processo N/A e documentadas acima.
