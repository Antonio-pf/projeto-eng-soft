# Requirements — Histórias #15 e #18: Histórico de Doações e Distribuições

## Intent Analysis Summary
- **User Request**: "ajuste a atribuição do board... e inicie com o aidlc a 15 e 18, lembre de seguir o que está no backlog e os entregáveis do professor / critérios" — implementar as histórias #15 (histórico de doações) e #18 (histórico de distribuições) do `docs/backlog.md`, os dois gaps restantes da Sprint 2 (além do merge do PR #34), seguindo também os casos de teste que o professor já definiu em `docs/plano-de-testes.md` (CT25 e CT27).
- **Request Type**: New Feature (duas telas de listagem/histórico, mesmo padrão, sobre models já existentes e migrados)
- **Scope Estimate**: Single Component (app `core`), mas **duas histórias tratadas em um único ciclo AI-DLC** por serem estruturalmente idênticas (mesma forma, uma para `Doacao`/`Doador`, outra para `Distribuicao`/`Familia`)
- **Complexity Estimate**: Simple — é o mesmo padrão de listagem paginada com busca já usado em `item_list`/`doador_list`/`familia_list`, acrescido de filtro por entidade relacionada (select) e por intervalo de datas

## Por que Minimal Depth / sem novo arquivo de perguntas
Os critérios de aceite do backlog já são objetivos, e o professor já formalizou o comportamento esperado como casos de teste específicos:

> **CT25** (`docs/plano-de-testes.md`) — História #15: "doador selecionado; intervalo de datas; filtros isolados e combinados" → "Lista paginada exibe data, doador, item, quantidade e usuário que registrou, respeitando os filtros."
>
> **CT27** — História #18: "família selecionada; intervalo de datas; filtros isolados e combinados" → "Lista exibe data, família, item, quantidade e usuário que registrou, respeitando os filtros."

Isso remove qualquer ambiguidade sobre colunas, tipos de filtro e comportamento de combinação — a única decisão de implementação em aberto é de navegação (ver seção seguinte), resolvida por precedente sem necessidade de pergunta ao usuário.

## Referência do Backlog

> **#15** — Como Voluntário, quero visualizar o histórico de doações com filtro por doador e por período, para que eu consulte o que cada doador contribuiu.
> **Critérios**: Lista exibe data, doador, item, quantidade e usuário que registrou · Filtros por doador e por intervalo de datas funcionam isolados e combinados · Lista é paginada.
> Prioridade: Deveria ter · Pontos: 3 · Sprint: 2

> **#18** — Como Voluntário, quero visualizar o histórico de distribuições com filtro por família e por período, para que eu consulte o que cada família recebeu.
> **Critérios**: Lista exibe data, família, item, quantidade e usuário que registrou · Filtros por família e por intervalo de datas funcionam isolados e combinados.
> Prioridade: Deveria ter · Pontos: 3 · Sprint: 2

## Decisão de Navegação (sem precedente 1:1 — resolvida por analogia)
`doacao_create`/`distribuicao_create` (história #14/#16) já existem como páginas de formulário dedicadas, aprovadas em ciclos anteriores — não serão fundidas com a listagem (diferente do padrão `doador_list`/`familia_list`, que combinam formulário + tabela numa única página). Para não reabrir uma decisão já aprovada, `doacao_list`/`distribuicao_list` serão páginas de listagem **independentes**, no padrão visual de `item_list.html` (tabela + filtros + paginação), com:
- Um link "Ver histórico" no topo de `doacao_form.html`/`distribuicao_form.html`, apontando para a nova listagem.
- Um botão "+ Nova Doação"/"+ Nova Distribuição" no topo de `doacao_list.html`/`distribuicao_list.html`, apontando de volta para o formulário — mesmo padrão recíproco já usado entre `item_list.html` e `doacao_create`.
- O link "Movimentações" da sidebar **não é alterado** nesta história (continua apontando para `doacao_create`, decisão já aprovada em #14/#16) — evita redesenhar a informação de navegação de "Movimentações" sem necessidade, já que nem o backlog nem o Figma especificam esse comportamento para as telas de histórico.

## Functional Requirements

### FR1 — Histórico de Doações (`doacao_list`)
- Nova rota `doacoes/` (nome de URL: `doacao_list`), acessível a qualquer usuário autenticado (`@login_obrigatorio`), mesmo padrão de acesso de `doacao_create`.
- Filtros via `GET`: `doador` (select, `ModelChoiceField`-like — id do `Doador`), `data_inicio` e `data_fim` (datas, inclusivas). Todos opcionais, funcionam isolados e combinados (critério do backlog/CT25).
- Lista paginada (20 por página, mesmo padrão de `Paginator` já usado no projeto), ordenada por `data` decrescente (mais recente primeiro — mesmo critério de ordenação de `criado_em` usado em `doador_list`/`familia_list`).
- Colunas exibidas: Data, Doador, Item, Quantidade, Usuário que registrou (`registrado_por.nome`) — exatamente as colunas exigidas pelo CT25.
- Doações canceladas (`cancelado=True`) **não aparecem** na listagem (mesmo raciocínio de `Item.saldo_atual`, que já exclui movimentações canceladas — consistência de dado).

### FR2 — Histórico de Distribuições (`distribuicao_list`)
- Nova rota `distribuicoes/` (nome de URL: `distribuicao_list`), mesmo padrão de acesso.
- Filtros via `GET`: `familia`, `data_inicio`, `data_fim` — isolados e combinados (CT27).
- Lista paginada (20 por página), ordenada por `data` decrescente.
- Colunas: Data, Família, Item, Quantidade, Usuário que registrou — exatamente as colunas exigidas pelo CT27.
- Distribuições canceladas não aparecem na listagem.

### FR3 — Navegação (ver seção de decisão acima)
- Link "Ver histórico de doações" em `doacao_form.html` → `doacao_list`.
- Link "Ver histórico de distribuições" em `distribuicao_form.html` → `distribuicao_list`.
- Botão "+ Nova Doação" em `doacao_list.html` → `doacao_create`.
- Botão "+ Nova Distribuição" em `distribuicao_list.html` → `distribuicao_create`.

## Non-Functional Requirements

Extensões já decididas para o projeto (não redecididas aqui): **Security Baseline** e **Resiliency Baseline** habilitadas e escopadas a regras de nível de código de aplicação; **Property-Based Testing** desabilitado.

### Security Baseline
| Regra | Status | Como se aplica |
|---|---|---|
| SECURITY-05 (Input validation) | **Aplicável** | Filtros de data usam `forms`/parsing seguro (data inválida é ignorada, não gera exception 500); filtro de doador/família usa apenas o `pk` para `.filter()`, sem risco de injeção (ORM parametrizado) |
| SECURITY-08 (Application-level access control) | **Aplicável** | Rotas exigem `@login_obrigatorio`, mesmo padrão das demais listagens |
| Demais regras | **N/A** | Mesma justificativa das histórias #14/#16/#17 — sem infraestrutura como código no repositório |

### Resiliency Baseline
| Regra | Status |
|---|---|
| Todas | **N/A** — mesma justificativa das histórias anteriores |

### Critério de bloqueio de merge (docs/plano-de-testes.md §2)
Aplicável a esta história: "(b) nova regra de negócio sem teste unitário correspondente" — a exclusão de movimentações canceladas da listagem é uma regra de negócio nova (ainda que pequena) e será coberta por teste unitário dedicado.

### Outras NFRs
- **Testabilidade**: `DoacaoListTestCase`/`DistribuicaoListTestCase` cobrindo os cenários de CT25/CT27 (filtro isolado por entidade, filtro isolado por período, filtros combinados, paginação, exclusão de canceladas, acesso anônimo bloqueado) — mesmo padrão de `core/tests.py` já estabelecido.
- **Consistência de UX**: reaproveitar 100% do layout de `item_list.html` (tabela, paginação, `data-testid`), sem introduzir novo componente visual.

## Key Requirements Summary
1. `doacao_list` (`doacoes/`) e `distribuicao_list` (`distribuicoes/`) — listagens paginadas com filtros por entidade relacionada + intervalo de datas, isolados e combinados, exatamente como especificado em CT25/CT27.
2. Colunas: Data, Doador/Família, Item, Quantidade, Usuário — sem coluna extra, sem funcionalidade além do pedido (ex.: sem exportação, sem edição — fora de escopo).
3. Movimentações canceladas excluídas da listagem (nova regra de negócio, com teste dedicado — exigência do critério de bloqueio de merge do plano de testes).
4. Navegação via links recíprocos form↔lista, sem alterar o link "Movimentações" da sidebar (decisão já aprovada em ciclos anteriores, preservada).
