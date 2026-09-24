# API Documentation

## Web Routes (server-rendered, não é API JSON — exceto `/health/`)

### Autenticação
- **GET/POST** `/login/` — `login_view` — autentica usuário
- **GET** `/logout/` — `logout_view`
- **GET** `/health/` — `health` — `JsonResponse({"status": "ok"})`

### Painel
- **GET** `/painel/` — `painel_view` (login obrigatório)

### Usuários (Admin)
- **GET/POST** `/usuarios/` — `usuarios_view`
- **POST** `/usuarios/<id_usuario>/status/` — `usuario_alternar_status_view`

### Doadores
- **GET** `/doadores/` — `doador_list` (busca `?q=`, paginação)
- **GET/POST** `/doadores/novo/` — `doador_create`
- **GET/POST** `/doadores/<pk>/editar/` — `doador_update` (admin obrigatório)

### Famílias
- **GET** `/familias/` — `familia_list`
- **GET/POST** `/familias/nova/` — `familia_create`

### Categorias e Itens
- **GET** `/categorias/`, **GET/POST** `/categorias/nova/`, **GET/POST** `/categorias/<pk>/editar/` (admin obrigatório)
- **GET** `/itens/`, **GET/POST** `/itens/novo/`, **GET/POST** `/itens/<pk>/editar/` (admin obrigatório)

### Movimentações (ainda não implementado — escopo da história #14)
- Nenhuma rota existe hoje para `Doacao`/`Distribuicao`, apesar dos models já existirem.

## Data Models

### Doacao (já existe em core/models.py, sem UI)
- **Fields**: `id_doacao` (PK), `doador` (FK Doador, PROTECT), `item` (FK Item, PROTECT), `registrado_por` (FK Usuario, PROTECT), `quantidade` (Decimal, min 0.01), `data` (Date), `cancelado` (bool, default False), `criado_em` (auto), `cancelado_em`/`cancelado_por` (nulos, usados apenas no cancelamento — história #19, fora de escopo aqui).
- **Relationships**: Doador 1—N Doacao; Item 1—N Doacao; Usuario 1—N Doacao (registrado_por).
- **Validation**: `quantidade` já validada no nível do model (`MinValueValidator(0.01)`); não há validação de negócio adicional (form ainda não existe).

### Item (contexto relevante para #14)
- **Fields relevantes**: `saldo_atual` (property, soma doações não canceladas − distribuições não canceladas).
- **Relationships**: `Item.doacao_set` usado no cálculo de saldo.
