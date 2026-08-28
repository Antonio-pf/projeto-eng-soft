# E2 — Backlog e Termo de Aceite — Plano de Produção

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produzir os dois artefatos da E2 — Backlog Priorizado com histórias INVEST + MoSCoW + estimativas, e Termo de Aceite pronto para assinatura do professor.

**Architecture:** Tarefa de escrita de documentos, não de código. As histórias são derivadas do `docs/documento-de-visao.md` e organizadas em torno dos 4 apps definidos no design de stack. O Termo de Aceite formaliza a stack tecnológica e os critérios de pronto.

**Tech Stack:** Markdown; referências ao Django/PostgreSQL/Render conforme design de stack aprovado.

**Spec:** `docs/documento-de-visao.md`, `docs/superpowers/specs/2026-08-27-stack-design.md`, `spec-objetivo-projeto-avaliativo.md`, `spec-modelo-entrega.md`

## Global Constraints

- Histórias seguem o formato: "Como [perfil], quero [ação], para que [benefício]."
- Critérios de aceite devem ser objetivos e verificáveis (sem "deve funcionar bem")
- Priorização MoSCoW: Must / Should / Could / Won't (this semester)
- Estimativas em story points Fibonacci: 1, 2, 3, 5, 8
- Perfis válidos: Administrador, Voluntário
- Stack travada: Django + Templates + Tailwind/daisyUI + PostgreSQL + Render
- Sprints: 1 (auth + CRUD) · 2 (regra de negócio) · 3 (relatórios) · 4 (qualidade)

---

## Task 1: Histórias de usuário — `accounts` (autenticação e perfis)

**Files:**
- Modify: `docs/backlog.md` (linhas do módulo accounts)

**Interfaces:**
- Produz: linhas #1–#4 do backlog, referenciadas pelas tasks seguintes para numeração

- [ ] **Step 1: Escrever as histórias de autenticação no backlog**

Adicionar as seguintes linhas em `docs/backlog.md`, substituindo o placeholder existente:

```markdown
# Backlog Priorizado — Sistema de Gestão de ONG de Doações

## Módulo: Autenticação e Perfis

| #  | História | Critérios de aceite | Prioridade | Estimativa | Sprint |
|----|----------|---------------------|------------|------------|--------|
| 1  | Como usuário, quero fazer login com e-mail e senha, para que eu possa acessar o sistema de forma segura. | - Login com e-mail e senha válidos redireciona para o painel<br>- Credenciais inválidas exibem mensagem de erro sem revelar qual campo está errado<br>- Sessão expira após inatividade (configurable via SESSION_COOKIE_AGE) | Must | 3 | 1 |
| 2  | Como usuário autenticado, quero fazer logout, para que minha sessão seja encerrada com segurança. | - Botão de logout está visível no menu<br>- Após logout, redireciona para a tela de login<br>- Tentativa de acessar URL protegida após logout redireciona para login | Must | 1 | 1 |
| 3  | Como Administrador, quero cadastrar novos usuários com perfil Administrador ou Voluntário, para que eu controle quem acessa o sistema e com quais permissões. | - Formulário solicita nome, e-mail, senha e perfil<br>- E-mail duplicado exibe erro de validação<br>- Voluntário recém-criado não acessa funcionalidades exclusivas de Administrador | Must | 3 | 1 |
| 4  | Como Administrador, quero desativar um usuário sem excluí-lo, para que eu preserve o histórico de ações desse usuário. | - Usuário desativado não consegue fazer login<br>- Histórico de movimentações do usuário permanece intacto<br>- Lista de usuários distingue ativos de inativos | Should | 2 | 1 |
```

- [ ] **Step 2: Verificar checklist INVEST para cada história**

Para cada história acima, confirmar:
- **I**ndependente: pode ser implementada sem depender de outra história do mesmo módulo? ✓
- **N**egociável: os critérios são de aceite, não de implementação? ✓
- **V**aliosa: entrega valor direto a um perfil de usuário? ✓
- **E**stimável: a equipe consegue estimar em story points? ✓
- **S**mall: cabe em uma sprint? ✓
- **T**estável: os critérios são verificáveis objetivamente? ✓

- [ ] **Step 3: Commit parcial**

```bash
git add docs/backlog.md
git commit -m "docs(e2): histórias de usuário — módulo accounts"
```

---

## Task 2: Histórias de usuário — `core` (cadastros básicos)

**Files:**
- Modify: `docs/backlog.md` (linhas do módulo core, #5–#13)

**Interfaces:**
- Consome: estrutura de tabela definida na Task 1
- Produz: linhas #5–#13 do backlog

- [ ] **Step 1: Escrever histórias de Doadores**

Adicionar seção em `docs/backlog.md`:

```markdown
## Módulo: Cadastros Básicos (core)

### Doadores

| #  | História | Critérios de aceite | Prioridade | Estimativa | Sprint |
|----|----------|---------------------|------------|------------|--------|
| 5  | Como Voluntário, quero cadastrar um doador com nome e CPF, para que eu possa vincular doações a uma pessoa identificável. | - Formulário solicita nome (obrigatório), CPF (obrigatório, formato XXX.XXX.XXX-XX), telefone e e-mail (opcionais)<br>- CPF duplicado exibe erro de validação<br>- CPF com formato inválido exibe erro antes de submeter | Must | 3 | 1 |
| 6  | Como Voluntário, quero listar e buscar doadores pelo nome, para que eu encontre rapidamente um doador já cadastrado. | - Lista exibe nome, CPF e data de cadastro<br>- Campo de busca filtra por nome em tempo real (ou ao submeter)<br>- Lista é paginada (máximo 20 por página) | Must | 2 | 1 |
| 7  | Como Administrador, quero editar os dados de um doador, para que eu corrija informações desatualizadas. | - Formulário de edição pré-preenche os dados atuais<br>- Salvar atualiza os dados e redireciona para a lista<br>- CPF não pode ser alterado para um já usado por outro doador | Should | 2 | 1 |
```

- [ ] **Step 2: Escrever histórias de Famílias**

Adicionar na mesma seção:

```markdown
### Famílias

| #  | História | Critérios de aceite | Prioridade | Estimativa | Sprint |
|----|----------|---------------------|------------|------------|--------|
| 8  | Como Voluntário, quero cadastrar uma família com nome do responsável e endereço, para que eu possa vincular distribuições a beneficiários identificados. | - Formulário solicita nome do responsável (obrigatório), endereço (obrigatório), telefone (opcional) e número de membros (obrigatório, inteiro ≥ 1)<br>- Família salva aparece imediatamente na lista | Must | 3 | 1 |
| 9  | Como Voluntário, quero listar e buscar famílias pelo nome do responsável, para que eu localize rapidamente a família ao registrar uma distribuição. | - Lista exibe nome do responsável, endereço e número de membros<br>- Campo de busca filtra por nome do responsável<br>- Lista é paginada (máximo 20 por página) | Must | 2 | 1 |
```

- [ ] **Step 3: Escrever histórias de Categorias e Itens**

Adicionar na mesma seção:

```markdown
### Categorias de Itens e Itens

| #  | História | Critérios de aceite | Prioridade | Estimativa | Sprint |
|----|----------|---------------------|------------|------------|--------|
| 10 | Como Administrador, quero cadastrar categorias de itens (ex: Alimento, Roupa, Higiene), para que o estoque fique organizado por tipo. | - Formulário solicita nome da categoria (obrigatório) e descrição (opcional)<br>- Nome duplicado exibe erro de validação<br>- Categoria salva aparece na lista de categorias | Must | 2 | 1 |
| 11 | Como Voluntário, quero cadastrar um item vinculado a uma categoria e com unidade de medida (ex: kg, unidade, litro), para que o estoque reflita os tipos reais de doação recebidos. | - Formulário solicita nome (obrigatório), categoria (obrigatório, seleção), unidade de medida (obrigatório) e estoque mínimo (obrigatório, inteiro ≥ 0)<br>- Item salvo aparece na lista com saldo zero | Must | 3 | 1 |
| 12 | Como Voluntário, quero visualizar a lista de itens com o saldo atual de cada um, para que eu saiba o que está disponível antes de registrar uma distribuição. | - Lista exibe nome, categoria, unidade, saldo atual e estoque mínimo<br>- Itens com saldo ≤ estoque mínimo são destacados visualmente (badge de alerta daisyUI) | Must | 2 | 1 |
| 13 | Como Administrador, quero editar os dados de um item (nome, categoria, unidade, estoque mínimo), para que eu mantenha o cadastro atualizado sem perder o histórico de movimentações. | - Formulário de edição pré-preenche os dados atuais<br>- O campo de saldo atual não é editável diretamente (só movimentações alteram o saldo)<br>- Salvar atualiza os dados e redireciona para a lista | Should | 2 | 1 |
```

- [ ] **Step 4: Commit parcial**

```bash
git add docs/backlog.md
git commit -m "docs(e2): histórias de usuário — módulo core"
```

---

## Task 3: Histórias de usuário — `movimentacoes` (doações e distribuições)

**Files:**
- Modify: `docs/backlog.md` (linhas #14–#19)

**Interfaces:**
- Consome: histórias #5–#13 (doadores, famílias e itens devem existir para vincular)
- Produz: linhas #14–#19

- [ ] **Step 1: Escrever histórias de Doações (entrada)**

```markdown
## Módulo: Movimentações

### Doações (Entrada de Estoque)

| #  | História | Critérios de aceite | Prioridade | Estimativa | Sprint |
|----|----------|---------------------|------------|------------|--------|
| 14 | Como Voluntário, quero registrar uma doação vinculando um doador, um item e uma quantidade, para que o saldo do item aumente e o histórico da doação fique registrado. | - Formulário solicita doador (busca/seleção), item (seleção), quantidade (inteiro > 0) e data (padrão: hoje)<br>- Após salvar, o saldo do item aumenta exatamente pela quantidade informada<br>- A doação aparece no histórico do doador e no histórico do item | Must | 5 | 2 |
| 15 | Como Voluntário, quero visualizar o histórico de doações com filtro por doador e por período, para que eu consulte o que cada doador contribuiu. | - Lista exibe data, doador, item, quantidade e usuário que registrou<br>- Filtros por doador e por intervalo de datas funcionam isolados e combinados<br>- Lista é paginada | Should | 3 | 2 |
```

- [ ] **Step 2: Escrever histórias de Distribuições (saída)**

```markdown
### Distribuições (Saída de Estoque)

| #  | História | Critérios de aceite | Prioridade | Estimativa | Sprint |
|----|----------|---------------------|------------|------------|--------|
| 16 | Como Voluntário, quero registrar uma distribuição vinculando uma família, um item e uma quantidade, para que o saldo diminua e o beneficiário fique registrado. | - Formulário solicita família (busca/seleção), item (seleção), quantidade (inteiro > 0) e data (padrão: hoje)<br>- Se saldo atual < quantidade solicitada, a operação é bloqueada com mensagem de erro clara ("Saldo insuficiente: disponível X, solicitado Y")<br>- Após salvar com sucesso, o saldo diminui exatamente pela quantidade informada | Must | 5 | 2 |
| 17 | Como Voluntário, quero ver o saldo disponível do item ao preencher o formulário de distribuição, para que eu saiba antes de submeter se a quantidade é viável. | - O saldo atual do item selecionado é exibido em tempo real no formulário (via JS ou ao selecionar o item)<br>- Saldo é atualizado após cada distribuição sem recarregar a página inteira | Should | 3 | 2 |
| 18 | Como Voluntário, quero visualizar o histórico de distribuições com filtro por família e por período, para que eu consulte o que cada família recebeu. | - Lista exibe data, família, item, quantidade e usuário que registrou<br>- Filtros por família e por intervalo de datas funcionam isolados e combinados | Should | 3 | 2 |
| 19 | Como Administrador, quero cancelar uma movimentação registrada por engano, para que o saldo seja corrigido sem alterar o histórico. | - Cancelamento cria um registro de estorno (não apaga o registro original)<br>- O saldo é revertido ao valor anterior ao registro cancelado<br>- Somente Administrador pode cancelar movimentações | Could | 5 | 3 |
```

- [ ] **Step 3: Commit parcial**

```bash
git add docs/backlog.md
git commit -m "docs(e2): histórias de usuário — módulo movimentacoes"
```

---

## Task 4: Histórias de usuário — `relatorios` (dashboard e relatórios)

**Files:**
- Modify: `docs/backlog.md` (linhas #20–#23)

**Interfaces:**
- Consome: dados de todas as movimentações (tasks 2 e 3)
- Produz: linhas #20–#23

- [ ] **Step 1: Escrever histórias de dashboard e relatórios**

```markdown
## Módulo: Relatórios e Dashboard

| #  | História | Critérios de aceite | Prioridade | Estimativa | Sprint |
|----|----------|---------------------|------------|------------|--------|
| 20 | Como Administrador, quero ver um painel com o total de itens em estoque agrupado por categoria, para que eu tenha uma visão geral imediata da situação atual. | - Painel exibe um card por categoria com a soma de saldo de todos os itens da categoria<br>- Itens com saldo ≤ estoque mínimo são listados numa seção de alertas<br>- Dados refletem as movimentações registradas até o momento do acesso (sem cache manual) | Must | 5 | 3 |
| 21 | Como Administrador, quero gerar um relatório de distribuições filtrável por período e por família, para que eu apresente dados de prestação de contas a financiadores. | - Relatório exibe família, item, categoria, quantidade total distribuída e número de distribuições no período<br>- Filtros de data (início e fim) e família funcionam isolados e combinados<br>- Relatório usa JOIN de pelo menos 4 tabelas (Distribuição ↔ Família ↔ Item ↔ CategoriaItem)<br>- Resultado é exibido em tabela na tela | Must | 5 | 3 |
| 22 | Como Administrador, quero ver o histórico de doações por doador com totais por item, para que eu reconheça os maiores contribuidores. | - Relatório agrupa doações por doador, exibindo total de cada item doado<br>- Filtrável por período | Should | 3 | 3 |
| 23 | Como Administrador, quero exportar o relatório de distribuições em CSV, para que eu abra no Excel e compartilhe com parceiros sem acesso ao sistema. | - Botão "Exportar CSV" gera arquivo com os mesmos dados e filtros aplicados na tela<br>- Arquivo tem cabeçalho com nomes das colunas em português | Could | 3 | 3 |
```

- [ ] **Step 2: Commit parcial**

```bash
git add docs/backlog.md
git commit -m "docs(e2): histórias de usuário — módulo relatorios"
```

---

## Task 5: Histórias Won't (fora de escopo declarado)

**Files:**
- Modify: `docs/backlog.md` (seção Won't)

**Interfaces:**
- Produz: seção Won't do backlog, referenciada pelo Termo de Aceite

- [ ] **Step 1: Adicionar seção Won't ao backlog**

```markdown
## Won't — Fora de escopo neste semestre

| # | Funcionalidade | Justificativa |
|---|----------------|---------------|
| W1 | Arrecadação financeira online / links de pagamento | Foco exclusivo em gestão de itens físicos |
| W2 | Gestão contábil (despesas, fluxo de caixa) | Escopo ampliado; não é requisito mínimo da disciplina |
| W3 | Aplicativo mobile nativo | Interface web responsiva é suficiente para o MVP |
| W4 | Emissão de Nota Fiscal Eletrônica | Integração com SEFAZ fora do escopo técnico do semestre |
| W5 | Integração com APIs de validação (CNPJ, CPF, CEP) | Validação de formato é suficiente para o MVP |
| W6 | Cancelamento de movimentações (estorno) | Classificado como Could; entra apenas se Sprint 2 terminar adiantada |
```

- [ ] **Step 2: Commit parcial**

```bash
git add docs/backlog.md
git commit -m "docs(e2): seção won't — itens fora de escopo declarados"
```

---

## Task 6: Termo de Aceite

**Files:**
- Modify: `docs/termo-aceite.md`

**Interfaces:**
- Consome: backlog finalizado (Tasks 1–5), stack design (`docs/superpowers/specs/2026-08-27-stack-design.md`), documento de visão
- Produz: `docs/termo-aceite.md` pronto para assinatura do professor

- [ ] **Step 1: Escrever o Termo de Aceite**

Substituir o conteúdo vazio de `docs/termo-aceite.md` por:

```markdown
# Termo de Aceite do Projeto — Sistema de Gestão de ONG de Doações

**Equipe:**
- Alexandre Victoriano Ribeiro Ulhoa (2840482423007)
- Daniel Souza Monteiro de Carvalho (2840482211052)
- Cintia Marcelo de Oliveira (2840482421017)
- Antonio Pires Felipe (2840482211003)

**Trilha:** B — Banco de temas nº 4
**Data de emissão:** 2026-08-27
**Semestre:** 2026/2

---

## 1. MVP travado

O escopo deste semestre cobre as funcionalidades marcadas como **Must** no backlog priorizado (`docs/backlog.md`), totalizando as histórias #1, #2, #3, #5, #6, #8, #9, #10, #11, #12, #14, #16, #20 e #21.

Funcionalidades **Should** e **Could** poderão ser incluídas em sprints futuras somente após todas as histórias Must estarem aprovadas em revisão de sprint.

---

## 2. Stack tecnológica travada

| Camada | Escolha |
|---|---|
| Backend | Django (Python 3.12) |
| Frontend | Django Templates + Tailwind CSS CDN + daisyUI CDN |
| Banco de dados | PostgreSQL (Render free tier) |
| Deploy | Render (Web Service + PostgreSQL) |
| Repositório | Monorepo único no GitHub |

Qualquer alteração de stack após a assinatura deste termo exige aprovação explícita do professor.

---

## 3. Requisitos mínimos da disciplina — cobertura confirmada

| Requisito | Cobertura |
|---|---|
| Autenticação com 2+ perfis | Histórias #1–#3: login, logout, cadastro de Administrador e Voluntário com controle de acesso por decorator Django |
| 6+ entidades com N:N | Usuário, Doador, Família, CategoriaItem, Item, Doação (N:N Doador↔Item), Distribuição (N:N Família↔Item) — 7 entidades, 2 relacionamentos N:N |
| Regra de negócio não trivial | História #16: bloqueio de distribuição quando saldo < quantidade solicitada; saldo recalculado automaticamente a cada movimentação |
| Consulta agregada | História #20: dashboard com GROUP BY CategoriaItem; história #21: relatório com JOIN de 4 tabelas |
| Validações em interface e banco | Histórias #5, #8, #11, #14, #16: validações de formato, quantidade > 0, CPF único. Banco: FK, NOT NULL, UNIQUE, CHECK saldo ≥ 0 |
| Deploy público | Render — URL pública gerada automaticamente |
| Repositório Git com README | Cobertura no E4 — README com setup local, pré-requisitos e link do deploy |

---

## 4. Critérios de pronto (Definition of Done)

Uma história é considerada pronta quando:

1. Código revisado via Pull Request por pelo menos um outro membro da equipe
2. Testes automatizados escritos e passando na CI (Render ou GitHub Actions)
3. Funcionalidade demonstrável na URL de deploy público
4. Critérios de aceite verificados manualmente pelo Responsável por Qualidade da sprint
5. Sem erros no console do navegador nem no log do servidor

---

## 5. Fora de escopo (Won't)

Arrecadação financeira online, gestão contábil, aplicativo mobile nativo, emissão de NF-e e integrações com APIs governamentais. Detalhamento em `docs/backlog.md` — seção Won't.

---

## 6. Assinaturas

| Papel | Nome | Assinatura | Data |
|---|---|---|---|
| Professor | | | |
| Representante da equipe | Antonio Pires Felipe | | |
```

- [ ] **Step 2: Revisar coerência com o backlog**

Verificar:
- Os números de história citados na seção 1 existem no backlog? ✓ (verificar após Task 5)
- A stack da seção 2 bate com `docs/superpowers/specs/2026-08-27-stack-design.md`? ✓
- Todos os 7 requisitos mínimos do `spec-objetivo-projeto-avaliativo.md` estão cobertos na seção 3? ✓

- [ ] **Step 3: Commit final**

```bash
git add docs/backlog.md docs/termo-aceite.md
git commit -m "docs(e2): backlog priorizado e termo de aceite completos"
```
