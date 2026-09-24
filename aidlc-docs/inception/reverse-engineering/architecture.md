# System Architecture

## System Overview
Aplicação web monolítica Django (padrão MVT), servida por Gunicorn + WhiteNoise, com um único app (`core`) e banco relacional (SQLite em dev, Postgres via `dj-database-url` em produção). Frontend server-side renderizado com templates Django + Tailwind/DaisyUI, sem SPA/API JSON além do endpoint `health`.

## Architecture Diagram

```mermaid
flowchart TD
    Browser["Navegador"] -->|HTTP| Django["Django app (conecta/core)"]
    Django -->|ORM| DB[("PostgreSQL / SQLite")]
    Django --> Static["WhiteNoise (static files)"]
```

## Component Descriptions

### conecta (projeto Django)
- **Purpose**: Configuração raiz (settings, urls, wsgi/asgi).
- **Responsibilities**: Roteamento raiz, configuração de banco, middlewares, auth.
- **Dependencies**: core
- **Type**: Application (config)

### core (app Django)
- **Purpose**: Implementa todo o domínio de negócio do sistema.
- **Responsibilities**: models, views, forms, urls, decorators de autorização, templates.
- **Dependencies**: Django ORM, django.contrib.auth (customizado via `AUTH_USER_MODEL = core.Usuario`)
- **Type**: Application

## Data Flow (fluxo típico de cadastro/CRUD)

```mermaid
sequenceDiagram
    participant U as Usuário (Voluntário)
    participant V as View (core/views.py)
    participant F as Form (core/forms.py)
    participant M as Model (core/models.py)
    participant T as Template

    U->>V: GET /doadores/novo/
    V->>F: instancia Form vazio
    V->>T: render(form)
    U->>V: POST /doadores/novo/ (dados)
    V->>F: Form(request.POST)
    F->>F: is_valid() + clean_*()
    F->>M: form.save()
    M-->>V: instância salva
    V-->>U: redirect + mensagem de sucesso
```

## Integration Points
- **External APIs**: Nenhuma.
- **Databases**: PostgreSQL (produção) via `dj-database-url`; SQLite (dev/local), configurado em `conecta/settings.py`.
- **Third-party Services**: Nenhum.

## Infrastructure Components
- **CDK Stacks**: N/A (sem IaC no repositório).
- **Deployment Model**: Gunicorn + WhiteNoise servindo estáticos; scripts em `scripts/`.
- **Networking**: N/A (fora do escopo do código-fonte analisado).
