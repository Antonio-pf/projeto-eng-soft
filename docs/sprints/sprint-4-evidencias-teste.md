# Evidências de Teste — Sprint 4 — Conecta Social

**Equipe:**
- Alexandre Victoriano Ribeiro Ulhoa — RA 2840482423007
- Daniel Souza Monteiro de Carvalho — RA 2840482211052
- Antonio Pires Felipe — RA 2840482211003
- Luiz Henrique Neres — RA 2840482423005

Estado avaliado: `main` no commit `410c821` (28/10/2026). Os testes foram executados em 28/10/2026 com `python manage.py test`.

| ID | Caso de teste | Tipo | Resultado | Evidência |
|---|---|---|---|---|
| CT15 | Painel agrupa saldo total e reflete movimentações (#20) | Integração | Passou | `PainelTests.test_ct15_total_da_categoria_soma_os_saldos_e_reflete_movimentacao` (PR #47) |
| CT15 (complementares) | Painel: totais separados por unidade, movimentações canceladas fora do saldo, saldo igual ao mínimo conta como alerta, percentual acima do mínimo, até 5 pontos de atenção, banco vazio, acesso dos dois perfis | Integração | Passou | `PainelTests`: `test_categoria_com_unidades_diferentes_mostra_totais_separados`, `test_movimentacoes_canceladas_nao_entram_no_saldo`, `test_saldo_igual_ao_minimo_conta_como_alerta`, `test_percentual_de_itens_acima_do_minimo_por_categoria`, `test_pontos_de_atencao_listam_ate_cinco_itens_do_menor_saldo`, `test_painel_com_banco_vazio`, `test_voluntario_e_administrador_acessam_o_painel` |
| — | Painel: número de consultas ao banco não cresce com a quantidade de itens | Desempenho | Passou | `PainelTests.test_numero_de_consultas_nao_cresce_com_os_itens` (PR #47) |
| CT28 | Relatório de doações por doador e item (#22) | Integração | Passou | `DoacaoListTestCase`: `test_totais_agrupam_por_identidade_do_doador_e_item`, `test_totais_respeitam_doador_e_limites_inclusivos_do_periodo`, `test_totais_incluem_registros_de_todas_as_paginas` (PR #49) |
| CT16 | Relatório de distribuições filtrável por período (#21) | Integração | Não executado na `main` | Os testes existem no commit `a632519` (branch `feature/distribuicoes-historico-estorno`, Luiz Henrique), mas a branch não tem PR e não foi integrada |
| CT17 | Relatório de distribuições filtrável por família (#21) | Integração | Não executado na `main` | Mesmo motivo do CT16 |
| CT20 | Cancelamento de movimentação reverte saldo (#19) | Integração | Não executado | A #19 não foi implementada |
| CT21 | Exportação de relatório em CSV (#23) | Integração | Não executado | O código está na `main`, mas não há teste automatizado nem execução manual registrada |
| — | Deploy: `/health/` responde e o login leva ao painel em produção | Manual | Passou | Em 28/10/2026, depois da troca do banco: `GET /health/` → 200 `{"status": "ok"}`; `POST /login/` com `admin@conectasocial.org` → 302 para `/painel/`; `/painel/`, `/itens/` e `/distribuicoes/` → 200 com os dados do `seed` |

## Cobertura automatizada nesta sprint

106 testes, 100% passando no commit `410c821` (`Ran 106 tests in 149.186s — OK`). São 16 novos em relação ao fim da Sprint 3 (90 testes no commit `76acbde`): 13 do painel (#20) e 3 dos totais por doador (#22).

O CI do GitHub Actions (jobs `lint` e `test`) passou nos três merges de 28/10/2026: [`e1417c5`](https://github.com/Antonio-pf/projeto-eng-soft/actions/runs/40678087270) (PR #49), [`ef8b4b7`](https://github.com/Antonio-pf/projeto-eng-soft/actions/runs/40678119390) (PR #47) e [`410c821`](https://github.com/Antonio-pf/projeto-eng-soft/actions/runs/40678150017) (PR #46).

Continuam pendentes CT16, CT17, CT20 e CT21, além de CT01 (expiração de sessão) e CT08 (paginação de famílias), abertos desde a Sprint 2.
