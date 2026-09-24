# Dependencies

## Internal Dependencies

```mermaid
flowchart LR
    conecta["conecta (config)"] --> core["core (app)"]
```

### conecta depends on core
- **Type**: Runtime (INSTALLED_APPS, AUTH_USER_MODEL, urls include)
- **Reason**: `core` é o único app com models/views/urls do sistema.

## External Dependencies
### Django (>=5.2,<6.0)
- **Purpose**: Framework web (ORM, auth, forms, templates, admin)
- **License**: BSD-3-Clause

### dj-database-url (>=2.3,<3.0)
- **Purpose**: Parse de `DATABASE_URL` para configuração do Django DATABASES
- **License**: BSD

### psycopg[binary] (>=3.2,<4.0)
- **Purpose**: Driver PostgreSQL
- **License**: LGPL

### whitenoise (>=6.9,<7.0)
- **Purpose**: Servir arquivos estáticos direto pelo WSGI app
- **License**: MIT

### gunicorn (>=23.0,<24.0)
- **Purpose**: Servidor WSGI de produção
- **License**: MIT

### ruff / pre-commit (dev)
- **Purpose**: Lint e hooks de qualidade
- **License**: MIT / MIT
