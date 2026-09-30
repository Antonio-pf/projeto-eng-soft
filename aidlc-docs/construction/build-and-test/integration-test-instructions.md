# Integration Test Instructions

## Purpose
Este projeto é um monólito Django de unidade única (app `core`) — não há múltiplos serviços/units para integrar. Os testes gerados em `DoacaoTestCase` (via `django.test.Client`) já funcionam como testes de integração de ponta a ponta dentro do processo: requisição HTTP → URL → View → Form → Model → banco de dados → resposta, exatamente como os demais `TestCase` do projeto (`DoadorTestCase`, `ItemTestCase`, etc.).

## Test Scenarios

### Cenário 1: Registro de doação → atualização de saldo do item
- **Description**: Verifica que registrar uma `Doacao` via `doacao_create` reflete corretamente no `Item.saldo_atual` (que agrega `Doacao`/`Distribuicao` via ORM)
- **Setup**: usuário autenticado, `Doador` e `Item` pré-cadastrados (feito no `setUp` de `DoacaoTestCase`)
- **Test Steps**: `POST /doacoes/nova/` com dados válidos → `GET` implícito via `item.refresh_from_db()` e `item.saldo_atual`
- **Expected Results**: saldo aumenta exatamente pela quantidade informada (`test_cadastrar_doacao_com_sucesso`)
- **Cleanup**: automático (banco de teste transacional do Django `TestCase`)

### Cenário 2: Navegação — sidebar e listagem de itens
- **Description**: Validação manual (não automatizada nesta história) de que o link "Movimentações" na sidebar e o botão "+ Doação" em `item_list.html` levam à rota `doacao_create`
- **Setup**: rodar o servidor de desenvolvimento (`python manage.py runserver`) e navegar autenticado
- **Test Steps**: login → Itens → clicar "+ Doação" → preencher formulário → confirmar redirecionamento e mensagem de sucesso
- **Expected Results**: fluxo completo funciona sem erros 404/500

### Cenário 3: Registro de distribuição → diminuição de saldo do item (história #16)
- **Description**: Verifica que registrar uma `Distribuicao` via `distribuicao_create` reflete corretamente no `Item.saldo_atual`, incluindo o bloqueio por saldo insuficiente
- **Setup**: usuário autenticado, `Familia` e `Item` (com saldo prévio via `Doacao`) pré-cadastrados (feito no `setUp` de `DistribuicaoTestCase`)
- **Test Steps**: `POST /distribuicoes/nova/` com dados válidos → `item.refresh_from_db()` e `item.saldo_atual`; e `POST` com quantidade acima do saldo disponível
- **Expected Results**: saldo diminui exatamente pela quantidade informada quando há saldo suficiente (`test_registrar_distribuicao_com_sucesso`); operação bloqueada com mensagem "Saldo insuficiente: disponível X, solicitado Y" quando não há (`test_registrar_distribuicao_saldo_insuficiente_bloqueada`)
- **Cleanup**: automático (banco de teste transacional do Django `TestCase`)

### Cenário 4: Navegação — sidebar e listagem de itens (história #16)
- **Description**: Validação manual (não automatizada) de que o link "Movimentações" (agora também ativo em `distribuicao_create`) e o botão "+ Distribuição" em `item_list.html` levam à rota `distribuicao_create`
- **Setup**: rodar o servidor de desenvolvimento e navegar autenticado
- **Test Steps**: login → Itens → clicar "+ Distribuição" → preencher formulário → confirmar redirecionamento e mensagem de sucesso; testar também com quantidade acima do saldo e confirmar a mensagem de erro na tela
- **Expected Results**: fluxo completo funciona sem erros 404/500, mensagem de saldo insuficiente exibida corretamente no formulário

### Cenário 5: Info-Box de saldo ao trocar o item (história #17)
- **Description**: Validação manual do comportamento client-side (JS) que não é exercitado pelos testes Django (`Client` não executa JavaScript)
- **Setup**: rodar o servidor de desenvolvimento, ter ao menos 2 itens com saldos diferentes cadastrados
- **Test Steps**: login → Itens → "+ Distribuição" → confirmar que a opção de cada item no dropdown mostra "saldo: X"; trocar o item selecionado e confirmar que o Info-Box verde abaixo do campo exibe "Saldo disponível: X unidade" correspondente ao item recém-selecionado; submeter com erro (ex.: saldo insuficiente) e confirmar que o Info-Box continua correto após a reexibição do formulário
- **Expected Results**: Info-Box atualiza corretamente a cada troca de item, sem chamadas de rede adicionais (inspecionar aba Network do navegador para confirmar ausência de requisições)

## Setup Integration Test Environment

### 1. Não há serviços externos a iniciar
```bash
# Banco SQLite local já configurado por padrão — nenhum docker-compose necessário
```

## Run Integration Tests

### 1. Executar a suíte completa (cobre os testes de integração dentro do processo)
```bash
python manage.py test
```

### 2. Verificação manual do fluxo de navegação (Cenário 2)
```bash
python manage.py runserver
# Acessar http://localhost:8000/login/ e seguir o fluxo descrito no Cenário 2
```

### 3. Cleanup
```bash
# Nenhum — banco de teste é destruído automaticamente ao final de `manage.py test`
```
