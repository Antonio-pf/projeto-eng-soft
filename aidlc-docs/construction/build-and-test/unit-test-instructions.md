# Unit Test Execution

## Run Unit Tests

### 1. Executar toda a suíte
```bash
source .venv/bin/activate
python manage.py test
```

### 2. Executar apenas os testes da história #14
```bash
python manage.py test core.tests.DoacaoTestCase -v 2
```

### 2.1 Executar apenas os testes das histórias #16/#17
```bash
python manage.py test core.tests.DistribuicaoTestCase -v 2
```

### 2.2 Executar apenas os testes das histórias #15/#18
```bash
python manage.py test core.tests.DoacaoListTestCase core.tests.DistribuicaoListTestCase -v 2
```

### 3. Lint
```bash
ruff check core/
```

### 4. Revisar resultados
- **Expected**: 77 testes passam, 0 falhas (54 pré-#16 + 7 de #16 + 2 de #17, todos em `DistribuicaoTestCase`; + 14 novos de #15/#18 em `DoacaoListTestCase`/`DistribuicaoListTestCase`)
- **Test Coverage**: sem ferramenta de coverage configurada no projeto; cobertura funcional avaliada pelos critérios de aceite (ver tabelas abaixo)
- **Test Report Location**: saída do terminal (`manage.py test` usa `unittest`, sem relatório em arquivo por padrão)

### 5. Corrigir testes com falha
1. Rever a saída do terminal (traceback do `unittest`)
2. Identificar o teste com falha
3. Corrigir o código (`core/forms.py`, `core/views.py`) ou o teste
4. Rerodar até passar

## Cobertura dos casos de teste de `DoacaoTestCase` (rastreabilidade com requirements.md / SECURITY baseline escopado)
| Teste | Critério coberto |
|---|---|
| `test_cadastrar_doacao_com_sucesso` | FR1/FR2 — cadastro válido, saldo do item aumenta exatamente pela quantidade |
| `test_cadastrar_doacao_quantidade_zero_ou_negativa_invalida` | FR1 — validação de quantidade > 0 (SECURITY-05 input validation) |
| `test_cadastrar_doacao_quantidade_fracionada_permitida` | FR1 — quantidade decimal aceita (decisão de requirements.md, Clarification Q1) |
| `test_cadastrar_doacao_data_futura_invalida` | FR1 — data ≤ hoje |
| `test_cadastrar_doacao_acesso_anonimo_redireciona_para_login` | FR1 — `@login_obrigatorio` (SECURITY-08 access control) |
| `test_administrador_tambem_pode_registrar_doacao` | FR1 — Voluntário e Administrador podem registrar |

## Cobertura dos casos de teste de `DistribuicaoTestCase` (rastreabilidade com requirements.md / SECURITY baseline escopado — história #16)
| Teste | Critério coberto |
|---|---|
| `test_registrar_distribuicao_com_sucesso` | FR1/FR2 — cadastro válido, saldo do item diminui exatamente pela quantidade |
| `test_registrar_distribuicao_quantidade_zero_ou_negativa_invalida` | FR1 — validação de quantidade > 0 (SECURITY-05 input validation) |
| `test_registrar_distribuicao_data_futura_invalida` | FR1 — data ≤ hoje |
| `test_registrar_distribuicao_saldo_insuficiente_bloqueada` | FR2 — bloqueio quando `quantidade > saldo_atual`, mensagem exata do backlog verificada |
| `test_registrar_distribuicao_saldo_exatamente_igual_permitida` | FR2 — caso-limite `quantidade == saldo_atual` é permitido |
| `test_registrar_distribuicao_acesso_anonimo_redireciona_para_login` | FR1 — `@login_obrigatorio` (SECURITY-08 access control) |
| `test_administrador_tambem_pode_registrar_distribuicao` | FR1 — Voluntário e Administrador podem registrar |
| `test_formulario_exibe_saldo_inline_na_opcao_do_item` | FR2 (história #17) — opção do item mostra saldo inline |
| `test_contexto_da_view_contem_saldo_por_item` | FR1/FR3 (história #17) — contexto da view expõe `itens_saldo` correto |

## Cobertura dos casos de teste de `DoacaoListTestCase`/`DistribuicaoListTestCase` (rastreabilidade com CT25/CT27 de docs/plano-de-testes.md — histórias #15 e #18)
| Teste | Critério coberto |
|---|---|
| `test_lista_todas_as_*_sem_filtro` | Lista exibe registros não cancelados; exclusão de cancelados (regra nova — critério de bloqueio de merge §2.b) |
| `test_filtro_por_doador_isolado` / `test_filtro_por_familia_isolado` | CT25/CT27 — filtro isolado por entidade |
| `test_filtro_por_periodo_isolado` | CT25/CT27 — filtro isolado por período |
| `test_filtro_por_doador_e_periodo_combinados` / `test_filtro_por_familia_e_periodo_combinados` | CT25/CT27 — filtros combinados |
| `test_filtro_com_data_invalida_e_ignorado_sem_erro_500` | SECURITY-05 — input inválido não gera erro 500 |
| `test_paginacao_lista_*` | Critério de aceite — lista paginada |
| `test_lista_*_acesso_anonimo_redireciona_para_login` | SECURITY-08 — controle de acesso |
