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

### 3. Lint
```bash
ruff check core/
```

### 4. Revisar resultados
- **Expected**: 54 testes passam, 0 falhas (48 já existentes + 6 novos de `DoacaoTestCase`)
- **Test Coverage**: sem ferramenta de coverage configurada no projeto; cobertura funcional avaliada pelos critérios de aceite (ver tabela abaixo)
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
