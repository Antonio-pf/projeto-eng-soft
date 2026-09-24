# Component Inventory

## Application Packages
- `conecta` — Configuração raiz do projeto Django (settings, urls, wsgi/asgi)
- `core` — Único app de domínio (models, views, forms, urls, templates, testes)

## Infrastructure Packages
- Nenhum (sem CDK/Terraform no repositório)

## Shared Packages
- Nenhum além do próprio app `core`

## Test Packages
- `core/tests.py` — Testes unitários/integração via `django.test.TestCase`

## Total Count
- **Total Packages**: 2
- **Application**: 2
- **Infrastructure**: 0
- **Shared**: 0
- **Test**: 1 (dentro de `core`)
