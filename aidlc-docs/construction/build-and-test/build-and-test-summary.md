# Build and Test Summary — Histórias #15 e #18 (Histórico de Doações e Distribuições)

## Build Status
- **Build Tool**: pip + Django management commands
- **Build Status**: Success
- **Build Artifacts**: N/A (aplicação interpretada; nenhuma migração nova)
- **Build Time**: N/A

## Test Execution Summary

### Unit / Integration Tests (`python manage.py test`)
- **Total Tests**: 77 (63 pré-existentes + 14 novos em `DoacaoListTestCase`/`DistribuicaoListTestCase`)
- **Passed**: 77
- **Failed**: 0
- **Status**: Pass

### Integration Tests
- **Test Scenarios**: 1 novo (filtros combinados + paginação + navegação recíproca) — ver Cenário 6 em `integration-test-instructions.md`
- **Passed**: automatizado via `manage.py test` (filtros e paginação); navegação e links recíprocos recomendados para validação manual
- **Status**: Pass (automatizado) / Manual pendente (navegação — mesma ressalva das histórias anteriores)

### Performance Tests
- **Status**: N/A — ver `performance-test-instructions.md`

### Additional Tests
- **Contract Tests**: N/A
- **Security Tests**: filtro de data usa `parse_date` (retorna `None` para formato inválido, sem erro 500) — testado em `test_filtro_com_data_invalida_e_ignorado_sem_erro_500`; acesso anônimo bloqueado — testado
- **E2E Tests**: N/A

## Verificações adicionais
- `ruff check core/ templates/` — sem erros
- `python manage.py makemigrations --check --dry-run` — nenhuma migração pendente
- `python manage.py test` (suíte completa) — 77/77 passando

## Rastreabilidade com o Plano de Testes do Professor (docs/plano-de-testes.md)
- **CT25** (história #15 — histórico de doações filtrável por doador e período): coberto por `DoacaoListTestCase`.
- **CT27** (história #18 — histórico de distribuições filtrável por família e período): coberto por `DistribuicaoListTestCase`.
- **Critério de bloqueio de merge §2.b** (regra de negócio nova sem teste): exclusão de movimentações canceladas coberta por teste dedicado em ambos os `TestCase`.

## Overall Status
- **Build**: Success
- **All Tests**: Pass (77/77)
- **Ready for Operations**: Yes (dentro do escopo desta história; Operations permanece placeholder)

## Next Steps
Critérios de aceite das histórias #15 e #18 implementados e testados, incluindo os casos de teste específicos que o professor já definiu (CT25/CT27). Recomenda-se validação manual rápida da navegação (Cenário 6).

**Pendências fora do escopo de código** (regras do professor, não deste ciclo AI-DLC):
1. Declarar uso de IA na descrição do PR #34 (e do próximo PR desta branch), conforme regra "sempre ativa" do professor.
2. Obter revisão de outro integrante do time antes de mergear qualquer PR desta branch — "nenhum merge sem revisão" é regra obrigatória.

Histórias #16, #17, #15 e #18 completas na branch `feature/historia-16-17-distribuicao`. História #19 (cancelamento de movimentação, Sprint 3) permanece pendente para ciclo AI-DLC futuro.
