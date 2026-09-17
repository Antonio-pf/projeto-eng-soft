# Evidências de Teste — Sprint 1 — Conecta Social

> Atualiza (não substitui) o [Plano de Testes](../plano-de-testes.md) (E4b). Todo caso de teste com ID (CTxx) implementado nesta sprint precisa de evidência verificável abaixo.

| ID | Caso de teste | Tipo | Resultado | Evidência |
|---|---|---|---|---|
| CT01 | Login com credenciais válidas e expiração de sessão | Integração | 🟡 Parcial | Login válido: `test_login_valido_redireciona_para_painel` (`core/tests.py`) — passou. Expiração de sessão: configurada (`SESSION_COOKIE_AGE`, `SESSION_SAVE_EVERY_REQUEST` em `conecta/settings.py`), **sem teste automatizado** — pendência para a próxima sprint. |
| CT02 | Login com credenciais inválidas | Unidade + Integração | ✅ Passou | `test_senha_errada_retorna_none`, `test_email_inexistente_retorna_none` (`core/auth.py`) e `test_login_invalido_mostra_erro_generico_e_nao_autentica` (`core/tests.py`) |
| CT18 | Logout encerra sessão e bloqueia acesso | Integração | ✅ Passou | `test_logout_limpa_sessao_e_bloqueia_painel` e `test_painel_sem_sessao_redireciona_para_login` (`core/tests.py`) |
| CT19 | Usuário desativado não consegue logar | Unidade | ✅ Passou (adiantado) | `test_usuario_inativo_retorna_none` (`core/tests.py`) — história #4 não é desta sprint, mas a trava já existe em `autenticar()` e está coberta |

## Cobertura automatizada nesta sprint

10 testes, 100% passando (`python manage.py test`, 17/09/2026):

```
test_credenciais_validas_retornam_usuario ... ok
test_email_inexistente_retorna_none ... ok
test_senha_errada_retorna_none ... ok
test_usuario_inativo_retorna_none ... ok
test_health_endpoint_returns_ok ... ok
test_home_page_is_available ... ok
test_login_invalido_mostra_erro_generico_e_nao_autentica ... ok
test_login_valido_redireciona_para_painel ... ok
test_logout_limpa_sessao_e_bloqueia_painel ... ok
test_painel_sem_sessao_redireciona_para_login ... ok

Ran 10 tests in 8.853s
OK
```

**Pendência para a próxima sprint:** CT01 não tem teste automatizado pra
expiração de sessão por inatividade (precisaria simular passagem de tempo,
ex. com `freezegun`). CT03/CT04 (cadastro de usuário, história #3) ainda não
foram implementados.
