# Requirements Clarification Questions — História #14 (Registrar Doação)

Por favor, responda preenchendo a letra escolhida após cada tag `[Answer]:`.

## Question 1
Quem pode registrar uma doação?

A) Voluntário e Administrador (mesmo padrão de Doador/Família: qualquer usuário autenticado)

B) Apenas Administrador

C) Apenas Voluntário

X) Other (please describe after [Answer]: tag below)

[Answer]: a

## Question 2
O model `Doacao` já tem `quantidade` como `DecimalField` (permite casas decimais, ex.: 2.5 kg), enquanto o critério de aceite do backlog fala em "quantidade (inteiro > 0)". Como tratar isso no formulário?

A) Manter Decimal (não alterar o model/migração já existente) e apenas validar que é maior que zero — permite doações fracionadas (ex.: 2.5 kg de arroz)

B) Restringir o formulário para aceitar somente números inteiros positivos, mesmo o campo do banco sendo Decimal

X) Other (please describe after [Answer]: tag below)

[Answer]: x e para casos de inTENS quebrados?

## Question 3
O campo "data" deve ter alguma restrição além do padrão "hoje"?

A) Sem restrição além do padrão (usuário pode escolher qualquer data, inclusive passada ou futura)

B) Não permitir datas futuras (data ≤ hoje)

X) Other (please describe after [Answer]: tag below)

[Answer]: a

## Question 4
Após salvar a doação com sucesso, para onde o usuário deve ser redirecionado? (Ainda não existe uma tela de listagem/histórico de doações — essa é a história #15, fora do escopo atual.)

A) Para o próprio formulário de "Nova Doação" limpo, com mensagem de sucesso (permite registrar várias doações em sequência)

B) Para a listagem de Itens (`item_list`), já que lá dá para conferir o novo saldo

C) Para o Painel (`painel`)

X) Other (please describe after [Answer]: tag below)

[Answer]: a

## Question 5
O item do menu lateral "Movimentações" hoje é um placeholder inerte (`<span>`, sem link), aguardando a primeira rota de movimentação existir. O que fazer com ele nesta história?

A) Ativar como link (`<a>`) apontando direto para o formulário de "Nova Doação" (única movimentação implementada até agora)

B) Manter inerte por enquanto e só ativar quando houver uma página "hub" de Movimentações (com Doação e Distribuição) — a doação fica acessível apenas por URL direta nesta história

X) Other (please describe after [Answer]: tag below)

[Answer]: a

## Question 6
O formulário de "Nova Doação" deve ficar acessível a partir de algum outro lugar além do menu lateral (ex.: botão na tela de Itens ou na tela de Doadores)?

A) Não, apenas o link no menu lateral "Movimentações" é suficiente por agora

B) Sim, adicionar também um botão de atalho na listagem de Itens (`item_list`), similar ao "+ Item"

X) Other (please describe after [Answer]: tag below)

[Answer]: b

## Question 7 — Extensão: Segurança
As regras da extensão SECURITY BASELINE devem ser aplicadas nesta tarefa?

A) Sim — aplicar todas as regras de SECURITY como restrições obrigatórias (recomendado para aplicações em produção)

B) Não — pular as regras de SECURITY (adequado para PoCs/protótipos)

X) Other (please describe after [Answer]: tag below)

[Answer]: a

## Question 8 — Extensão: Resiliência
O baseline de RESILIENCY deve ser aplicado nesta tarefa?

**O que é**: um conjunto de boas práticas direcionais de design para tolerância a falhas, alta disponibilidade e observabilidade (baseado no AWS Well-Architected Framework). Não certifica produção nem garante SLA/RTO/RPO.

A) Sim — aplicar o baseline de resiliência como boas práticas direcionais (recomendado para workloads críticos)

B) Não — pular o baseline de resiliência (adequado para PoCs/protótipos e iteração rápida)

X) Other (please describe after [Answer]: tag below)

[Answer]: a

## Question 9 — Extensão: Testes baseados em propriedade
As regras de PROPERTY-BASED TESTING (PBT) devem ser aplicadas nesta tarefa?

A) Sim — aplicar todas as regras de PBT como restrições obrigatórias (recomendado para lógica de negócio complexa, transformação de dados, componentes com estado)

B) Parcial — aplicar PBT apenas a funções puras e round-trips de serialização

C) Não — pular PBT (adequado para CRUD simples, como é o caso desta história)

X) Other (please describe after [Answer]: tag below)

[Answer]: c
