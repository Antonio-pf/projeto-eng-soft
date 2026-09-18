# Evidências de Teste — Sprint 1 — Conecta Social

> Atualiza (não substitui) o [Plano de Testes](../plano-de-testes.md) (E4b). Todo caso de teste com ID (CTxx) implementado nesta sprint precisa de evidência verificável abaixo.

| ID | Caso de teste | Tipo | Resultado | Evidência |
|---|---|---|---|---|
| CT01 | Login com credenciais válidas e expiração de sessão | Integração | 🟡 Parcial | Login válido: `test_login_valido_redireciona_para_painel` (`core/tests.py`) — passou. Expiração de sessão: configurada (`SESSION_COOKIE_AGE`, `SESSION_SAVE_EVERY_REQUEST` em `conecta/settings.py`), **sem teste automatizado** — pendência para a próxima sprint. |
| CT02 | Login com credenciais inválidas | Unidade + Integração | ✅ Passou | `test_senha_errada_retorna_none`, `test_email_inexistente_retorna_none` (`core/auth.py`) e `test_login_invalido_mostra_erro_generico_e_nao_autentica` (`core/tests.py`) |
| CT18 | Logout encerra sessão e bloqueia acesso | Integração | ✅ Passou | `test_logout_limpa_sessao_e_bloqueia_painel` e `test_painel_sem_sessao_redireciona_para_login` (`core/tests.py`) |
| CT03 | Administrador cadastra Voluntário | Unidade + Integração | ✅ Passou | `test_dados_validos_sao_aceitos` (`UsuarioFormTests`) e `test_admin_cria_usuario_e_aparece_na_listagem`, `test_acesso_anonimo_redireciona_para_login`, `test_voluntario_recebe_403`, `test_voluntario_recem_criado_nao_acessa_usuarios` (`UsuariosViewTests`, `core/tests.py`) |
| CT04 | E-mail duplicado no cadastro de usuário | Unidade + Integração | ✅ Passou | `test_email_duplicado_e_rejeitado` (`UsuarioFormTests`) e `test_email_duplicado_mostra_erro_e_nao_duplica` (`UsuariosViewTests`, `core/tests.py`) |
| CT19 | Usuário desativado não consegue logar | Unidade + Integração | ✅ Passou | `test_usuario_inativo_retorna_none` (`AutenticarTests`) e `test_admin_desativa_usuario`, `test_admin_reativa_usuario`, `test_usuario_desativado_nao_consegue_fazer_login`, `test_usuario_desativado_com_sessao_ativa_perde_acesso`, `test_admin_nao_consegue_desativar_a_si_mesmo`, `test_voluntario_nao_pode_alternar_status`, `test_get_nao_e_permitido`, `test_listagem_distingue_ativos_e_inativos` (`UsuarioAlternarStatusViewTests`, `core/tests.py`) |

## Cobertura automatizada nesta sprint

26 testes, 100% passando (`python manage.py test`, 18/09/2026):

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
test_admin_desativa_usuario ... ok
test_admin_nao_consegue_desativar_a_si_mesmo ... ok
test_admin_reativa_usuario ... ok
test_get_nao_e_permitido ... ok
test_listagem_distingue_ativos_e_inativos ... ok
test_usuario_desativado_com_sessao_ativa_perde_acesso ... ok
test_usuario_desativado_nao_consegue_fazer_login ... ok
test_voluntario_nao_pode_alternar_status ... ok
test_dados_validos_sao_aceitos ... ok
test_email_duplicado_e_rejeitado ... ok
test_senha_fraca_e_rejeitada ... ok
test_acesso_anonimo_redireciona_para_login ... ok
test_admin_cria_usuario_e_aparece_na_listagem ... ok
test_email_duplicado_mostra_erro_e_nao_duplica ... ok
test_voluntario_recebe_403 ... ok
test_voluntario_recem_criado_nao_acessa_usuarios ... ok

Ran 26 tests in 50.978s
OK
```

`test_senha_fraca_e_rejeitada` (`UsuarioFormTests`) é cobertura extra do
formulário de usuário, além dos critérios de aceite de CT03/CT04.

**Pendência para a próxima sprint:** CT01 não tem teste automatizado pra
expiração de sessão por inatividade (precisaria simular passagem de tempo,
ex. com `freezegun`).
