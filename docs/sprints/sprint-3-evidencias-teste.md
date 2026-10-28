# Evidências de Teste — Sprint 3 — Conecta Social

**Equipe:**
- Alexandre Victoriano Ribeiro Ulhoa — RA 2840482423007
- Daniel Souza Monteiro de Carvalho — RA 2840482211052
- Antonio Pires Felipe — RA 2840482211003
- Luiz Henrique Neres — RA 2840482423005

Estado avaliado: `main` no commit `76acbde` (09/10/2026), último antes do prazo da E7 (16/10/2026). Os testes foram executados em 28/10/2026 com `python manage.py test`.

| ID | Caso de teste | Tipo | Resultado | Evidência |
|---|---|---|---|---|
| CT15 | Painel agrupa saldo total e reflete movimentações (#20) | Integração | Não executado | A #20 não estava na `main` no prazo. O código e os testes estão no PR #47, integrado em 28/10/2026 (Sprint 4) |
| CT16 | Relatório de distribuições filtrável por período (#21) | Integração | Não executado | A tabela agregada da #21 não foi implementada. O filtro por período da tela de histórico (#18) é coberto por `DistribuicaoListTestCase`, mas não substitui o CT16 |
| CT17 | Relatório de distribuições filtrável por família (#21) | Integração | Não executado | Mesmo motivo do CT16. O filtro por família do histórico é coberto por `test_filtro_por_familia_isolado` e `test_filtro_por_familia_e_periodo_combinados` (#18) |
| CT20 | Cancelamento de movimentação reverte saldo (#19) | Integração | Não executado | A #19 não foi implementada |
| CT21 | Exportação de relatório em CSV (#23) | Integração | Não executado | O código da exportação está na `main` (`core/views.py`, `distribuicao_exportar_csv`), mas não há teste automatizado nem execução manual registrada |
| CT28 | Relatório de doações por doador e item (#22) | Integração | Não executado | A #22 não estava na `main` no prazo. Integrada pelo PR #49 em 28/10/2026 (Sprint 4) |
| CT11 / CT12 | Regressão: data padrão "hoje" nos formulários de doação e distribuição (#14, #16) | Unitário | Passou | `test_formulario_abre_com_data_de_hoje_em_formato_iso` (2 testes, um por formulário), PR #38 |
| — | Página inicial pública: visitante vê **Entrar**, usuário logado vê atalho do painel, seções do projeto e da equipe | Unitário | Passou | `test_visitante_ve_botao_de_entrar`, `test_usuario_logado_ve_atalho_para_o_painel`, `test_apresenta_secoes_e_equipe_sem_ra` (PR #42) |
| — | Layout: toda página estende um template base e carrega o CSS compilado | Unitário | Passou | `test_toda_pagina_estende_um_template_base`, `test_pagina_renderizada_usa_css_compilado`, `test_templates_base_carregam_css_compilado_e_app_css`, `test_app_css_ativa_view_transition`, `test_storage_de_producao_e_whitenoise_manifest` (PR #40) |
| — | Menu lateral: submenu de movimentações com links dos históricos, aberto só nas páginas do grupo | Unitário | Passou | `test_menu_lateral_tem_links_das_movimentacoes_e_dos_historicos`, `test_submenu_de_movimentacoes_abre_nas_paginas_do_grupo`, `test_submenu_de_movimentacoes_vem_fechado_fora_do_grupo` (PRs #38 e #39) |

## Cobertura automatizada nesta sprint

90 testes, 100% passando no commit `76acbde` (`Ran 90 tests in 118.163s — OK`). São 13 novos em relação ao fim da Sprint 2 (77 testes no commit `cc684e8`), todos de layout, navegação, data padrão e página inicial. Nenhum caso de teste das histórias planejadas para a sprint (#19 a #23) ganhou teste automatizado dentro do prazo.

O CI do GitHub Actions (jobs `lint` e `test`) passou em todos os merges da `main` da sprint, por exemplo o [run do commit `76acbde`](https://github.com/Antonio-pf/projeto-eng-soft/actions/runs/37998932083) em 09/10/2026 e o [run do commit `2da475a`](https://github.com/Antonio-pf/projeto-eng-soft/actions/runs/37144101482) em 03/10/2026.

Pendências que passam para a Sprint 4: CT15, CT16, CT17, CT20, CT21 e CT28, além de CT01 (expiração de sessão) e CT08 (paginação de famílias), abertos desde a Sprint 2.
