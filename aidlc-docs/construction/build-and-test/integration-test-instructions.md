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
