# Evidências de Teste — Sprint 4 — Conecta Social

**Equipe:**
- Alexandre Victoriano Ribeiro Ulhoa — RA 2840482423007
- Daniel Souza Monteiro de Carvalho — RA 2840482211052
- Antonio Pires Felipe — RA 2840482211003
- Luiz Henrique Neres — RA 2840482423005

Estado avaliado: `main` no commit `58ef94a` (29/10/2026). Os testes foram executados em 29/10/2026 com `python manage.py test`.

| ID | Caso de teste | Tipo | Resultado | Evidência |
|---|---|---|---|---|
| CT15 | Painel agrupa saldo total e reflete movimentações (#20) | Integração | Passou | `PainelTests.test_ct15_total_da_categoria_soma_os_saldos_e_reflete_movimentacao` (PR #47) |
| CT15 (complementares) | Painel: totais separados por unidade, movimentações canceladas fora do saldo, saldo igual ao mínimo conta como alerta, percentual acima do mínimo, até 5 pontos de atenção, banco vazio, acesso dos dois perfis | Integração | Passou | `PainelTests`: `test_categoria_com_unidades_diferentes_mostra_totais_separados`, `test_movimentacoes_canceladas_nao_entram_no_saldo`, `test_saldo_igual_ao_minimo_conta_como_alerta`, `test_percentual_de_itens_acima_do_minimo_por_categoria`, `test_pontos_de_atencao_listam_ate_cinco_itens_do_menor_saldo`, `test_painel_com_banco_vazio`, `test_voluntario_e_administrador_acessam_o_painel` |
| — | Painel: número de consultas ao banco não cresce com a quantidade de itens | Desempenho | Passou | `PainelTests.test_numero_de_consultas_nao_cresce_com_os_itens` (PR #47) |
| CT28 | Relatório de doações por doador e item (#22) | Integração | Passou | `DoacaoListTestCase`: `test_totais_agrupam_por_identidade_do_doador_e_item`, `test_totais_respeitam_doador_e_limites_inclusivos_do_periodo`, `test_totais_incluem_registros_de_todas_as_paginas` (PR #49) |
| CT16 | Relatório de distribuições filtrável por período (#21) | Integração | Passou | `DistribuicaoRelatorioTestCase.test_ct16_relatorio_distribuicoes_filtra_por_periodo` (PR #53) |
| CT17 | Relatório de distribuições filtrável por família (#21) | Integração | Passou | `DistribuicaoRelatorioTestCase.test_ct17_relatorio_distribuicoes_filtra_por_familia` (PR #53) |
| CT16/CT17 (complementares) | Relatório de distribuições: agrupamento por família e item, filtros combinados, acesso anônimo redirecionado, acesso do Administrador, data do último registro, distribuições canceladas fora do relatório, resumo por unidade, filtros inválidos ignorados, relatório vazio, link de exportação CSV com os filtros e item no menu lateral | Integração | Passou | `DistribuicaoRelatorioTestCase`: `test_relatorio_distribuicoes_agrupa_por_familia_e_item`, `test_relatorio_distribuicoes_filtra_combinado`, `test_relatorio_distribuicoes_acesso_anonimo_redireciona`, `test_administrador_acessa_o_relatorio`, `test_ultimo_registro_e_a_data_mais_recente_do_grupo`, `test_distribuicao_cancelada_fica_fora_do_relatorio`, `test_resumo_soma_por_unidade_e_conta_familias_e_distribuicoes`, `test_filtros_invalidos_sao_ignorados`, `test_relatorio_sem_distribuicoes`, `test_exportar_csv_leva_os_filtros_do_relatorio`, `test_menu_lateral_tem_o_relatorio_aberto_no_grupo_de_movimentacoes` (PR #53) |
| — | Relatório de distribuições: número de consultas ao banco não cresce com a quantidade de linhas | Desempenho | Passou | `DistribuicaoRelatorioTestCase.test_numero_de_consultas_nao_cresce_com_as_linhas` (PR #53) |
| — | Listas de doações e distribuições: pessoa ou data inválidas no filtro não derrubam a página | Integração | Passou | `FiltrosInvalidosTests.test_pessoa_e_data_invalidas_nao_derrubam_as_listas` (PR #54) |
| CT20 | Cancelamento de movimentação reverte saldo (#19) | Integração | Não executado | A #19 não foi implementada |
| CT21 | Exportação de relatório em CSV (#23) | Integração | Não executado | O código está na `main`. Só há teste de que o link de exportação do relatório leva os filtros (`test_exportar_csv_leva_os_filtros_do_relatorio`). O conteúdo do arquivo (cabeçalho em português e dados filtrados) não tem teste automatizado nem execução manual registrada |
| — | Deploy: `/health/` responde e o login leva ao painel em produção | Manual | Passou | Em 28/10/2026, depois da troca do banco: `GET /health/` → 200 `{"status": "ok"}`; `POST /login/` com `admin@conectasocial.org` → 302 para `/painel/`; `/painel/`, `/itens/` e `/distribuicoes/` → 200 com os dados do `seed` |

## Cobertura automatizada nesta sprint

121 testes, 100% passando no commit `58ef94a` (`Found 121 test(s)` — `OK`, em 29/10/2026). São 31 novos em relação ao fim da Sprint 3 (90 testes no commit `76acbde`): 13 do painel (#20), 3 dos totais por doador (#22), 14 do relatório de distribuições (#21) e 1 dos filtros inválidos (PR #54). Dos 14 testes da #21, Luiz Henrique escreveu os 5 primeiros (commit `56ce3c6`) e Antonio Felipe ajustou esses e acrescentou outros 9 (commit `d8c463f`).

O CI do GitHub Actions (jobs `lint` e `test`) passou nos merges de 28/10/2026, [`e1417c5`](https://github.com/Antonio-pf/projeto-eng-soft/actions/runs/40678087270) (PR #49), [`ef8b4b7`](https://github.com/Antonio-pf/projeto-eng-soft/actions/runs/40678119390) (PR #47) e [`410c821`](https://github.com/Antonio-pf/projeto-eng-soft/actions/runs/40678150017) (PR #46), e nos de 29/10/2026, [`a687538`](https://github.com/Antonio-pf/projeto-eng-soft/actions/runs/40970919518) (PRs #54 e #53) e [`58ef94a`](https://github.com/Antonio-pf/projeto-eng-soft/actions/runs/40970967973) (PR #51).

Continuam pendentes CT20 e CT21, além de CT01 (expiração de sessão) e CT08 (paginação de famílias), abertos desde a Sprint 2.
