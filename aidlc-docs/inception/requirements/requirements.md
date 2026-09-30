# Requirements — História #17: Ver Saldo Disponível no Formulário de Distribuição

## Intent Analysis Summary
- **User Request**: "siga para a #17" — implementar a história #17 do `docs/backlog.md` (exibir o saldo disponível do item ao selecioná-lo no formulário de distribuição), na mesma branch da #16, sem commitar.
- **Request Type**: Enhancement (melhoria de UX sobre a tela `distribuicao_create` já implementada na história #16, sem tocar em regras de negócio de persistência)
- **Scope Estimate**: Single Component (app `core`; apenas a view/template de `distribuicao_create`)
- **Complexity Estimate**: Simple — é a única história do backlog até agora que precisa de uma pequena interação client-side (JS puro, sem framework/lib nova), pois exige atualizar a tela sem reload ao trocar o item selecionado.

## Por que Minimal Depth / sem novo arquivo de perguntas
O critério de aceite já é objetivo e o projeto não tem nenhum precedente de fetch/AJAX (nenhuma outra tela do projeto faz chamada assíncrona) — a abordagem mais simples e nativa do Django, sem inventar uma camada de API nova, é:
- A própria view já tem acesso a todos os `Item` (mesmo queryset usado no `ModelChoiceField`); ela monta um dicionário `{id_item: {saldo, unidade}}` e o expõe ao template via o filtro built-in `{{ ...|json_script }}` do Django (não é uma biblioteca externa, é parte do framework).
- Um pequeno `<script>` inline (vanilla JS, sem dependência nova) lê esse JSON e atualiza um texto ao lado do campo "Item" quando o usuário troca a seleção (`change` event) — e também na carga da página, cobrindo o caso em que o formulário volta preenchido após um erro de validação (ex.: saldo insuficiente da história #16).
- Nenhuma chamada de rede adicional é necessária: o saldo exibido é o mesmo calculado no momento em que a página é renderizada (`GET /distribuicoes/nova/`), o que satisfaz "saldo reflete sempre o valor mais atualizado" no mesmo padrão de atualidade já usado no resto do projeto (sem WebSocket/polling em nenhuma tela existente).

Por isso esta análise segue direto para o documento de requisitos, sem arquivo de perguntas de clarificação.

## Referência do Backlog (docs/backlog.md, item #17)
> Como Voluntário, quero ver o saldo disponível do item ao preencher o formulário de distribuição, para que eu saiba antes de submeter se a quantidade é viável.
>
> **Critérios de aceite**:
> - O saldo atual do item selecionado é exibido no formulário ao selecionar o item
> - Saldo reflete sempre o valor mais atualizado
>
> Prioridade: Deveria ter · Pontos: 3 · Sprint: 2

## Referência de Design (Figma)
Fonte: [Figma — E4 Conecta Social](https://www.figma.com/design/YChrqTf5IiwA9skwfSP8O7/E4---Conecta-Social), frame "distribuicao" (node `2603:641`), card "Nova Distribuição" (node `2603:701`).

Elementos confirmados no design que este ciclo deve seguir:
- Campo "Item" (dropdown): cada opção exibe o nome do item **e o saldo inline**, ex.: `"Arroz 5kg saldo: 62"`.
- Logo abaixo do campo "Item" (antes da linha Qtd/Data), um **box de destaque verde claro** ("Info-Box" no Figma) com o texto do saldo do item selecionado (placeholder no design: "Saldo disponível.").
- Ordem dos campos: Família → Item → **Info-Box de saldo** → Qtd + Data (lado a lado) → botão "Registrar".

Essas duas peças (opção com saldo inline + Info-Box dedicado) substituem/detalham FR2 e FR3 abaixo, mantendo a mesma fonte de dado (`Item.saldo_atual`) e a mesma abordagem sem AJAX.

## Functional Requirements

### FR1 — Dados de saldo disponíveis no template
- A view `distribuicao_create` (`core/views.py`, história #16) passa ao contexto do template um dicionário `itens_saldo`: `{str(item.pk): {"saldo": item.saldo_atual, "unidade": item.unidade_medida.sigla} for item in Item.objects.select_related("unidade_medida").all()}` — mesma fonte de dado (`Item.saldo_atual`) já usada em `item_list.html`, nenhuma lógica de cálculo nova.
- Aplicado tanto no branch GET quanto no branch de POST inválido (para que o saldo continue visível se o formulário voltar com erro, ex.: saldo insuficiente).

### FR2 — Opção do item exibe o saldo inline (conforme Figma)
- O campo `item` do `DistribuicaoForm` passa a usar um `ModelChoiceField` customizado (`label_from_instance` sobreposto) cujo rótulo de cada `<option>` é `"{nome} saldo: {saldo_atual:.2f}"`, ex.: `"Arroz 5kg saldo: 62.00"` — mesma fonte de dado (`Item.saldo_atual`), sem query extra (já é o queryset padrão do campo).

### FR3 — Info-Box de saldo disponível (conforme Figma)
- `templates/core/distribuicao_form.html` usa o filtro built-in `{{ itens_saldo|json_script:"distribuicao-itens-saldo" }}` (sem biblioteca externa) para expor ao JavaScript um dicionário `{id_item: {saldo, unidade}}`, montado na view (FR1).
- Um box de destaque (`data-testid="distribuicao-form-saldo-info"`, estilo verde claro reaproveitando os tokens já usados no projeto para indicadores positivos — mesmas classes `bg-green-100`/`text-primary` já usadas em `item_list.html`/`usuarios.html`) fica posicionado entre o campo "Item" e a linha Qtd/Data, exibindo "Saldo disponível: {saldo} {unidade}" — mesma posição e função do "Info-Box" do Figma.
- Oculto (`hidden`) quando nenhum item está selecionado.

### FR4 — Atualização client-side (JS puro, sem framework novo)
- Um `<script>` inline no template escuta o evento `change` do `<select>` de item (`id_item` / `data-testid="distribuicao-form-item-select"`) e atualiza o texto do Info-Box lendo o JSON de FR3.
- O mesmo script roda uma vez no carregamento da página (`DOMContentLoaded`), cobrindo o caso de reexibição do formulário após erro de validação com um item já selecionado.

### FR5 — Sem alteração de regra de negócio
- Nenhuma mudança na validação de saldo insuficiente da história #16 (`DistribuicaoForm.clean()`) — esta história é puramente informativa/UX, a validação de bloqueio continua sendo feita no backend no momento do submit.

## Non-Functional Requirements

Extensões já decididas para o projeto (não redecididas aqui): **Security Baseline** e **Resiliency Baseline** habilitadas e escopadas a regras de nível de código de aplicação; **Property-Based Testing** desabilitado.

### Security Baseline — regras aplicáveis ao código desta história
| Regra | Status | Como se aplica |
|---|---|---|
| SECURITY-05 (Input validation) | **N/A para esta história** | Nenhum novo input do usuário é processado; a mudança é somente leitura/exibição |
| SECURITY-09-like (XSS) | **Aplicável** | `json_script` do Django escapa o conteúdo automaticamente contra injeção de HTML/script — não usar `{{ valor|safe }}` nem concatenação manual de strings no JS |
| Demais regras | **N/A** | Mesma justificativa das histórias #14/#16 — sem infraestrutura como código no repositório |

### Resiliency Baseline
| Regra | Status | Como se aplica |
|---|---|---|
| Todas | **N/A** | Sem chamada de rede nova, sem infraestrutura afetada; mesma justificativa das histórias anteriores |

### Outras NFRs
- **Testabilidade**: como o projeto não tem framework de teste de JS, a cobertura automatizada (Django `TestCase`) verifica que o contexto da view contém `itens_saldo` com os valores corretos e que o template renderiza o `json_script` com o saldo esperado (via `assertContains` no HTML retornado). A interação de `change` do JS em si é validada manualmente (documentado em Build and Test).
- **Consistência de UX**: reaproveitar classes de texto já usadas no projeto (`text-xs text-gray-500`, mesmo padrão de textos auxiliares).

## Key Requirements Summary
1. View `distribuicao_create` passa `itens_saldo` (saldo + unidade por item) ao contexto, em GET e no POST inválido.
2. Opções do campo "Item" exibem o saldo inline (`"Arroz 5kg saldo: 62.00"`), conforme Figma.
3. Info-Box verde entre "Item" e a linha Qtd/Data exibe "Saldo disponível: X unidade" para o item selecionado, atualizado via `json_script` + JS vanilla ao trocar o item — mesma posição/estilo do Figma.
4. Nenhuma mudança na regra de bloqueio de saldo insuficiente (história #16) — puramente informativo.
5. Teste automatizado cobre o contexto da view/HTML gerado (incluindo o rótulo do item com saldo); interação JS validada manualmente em Build and Test.
