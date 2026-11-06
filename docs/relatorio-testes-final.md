# Relatório de Testes Executados — Conecta Social

**Equipe:**
- Alexandre Victoriano Ribeiro Ulhoa — RA 2840482423007
- Antonio Pires Felipe — RA 2840482211003
- Daniel Souza Monteiro de Carvalho — RA 2840482211052
- Luiz Henrique Neres — RA 2840482423005

**Data da bateria final:** 04/11/2026  
**Escopo testado:** funcionalidades aceitas no Termo de Aceite do Projeto (E2b) e as histórias #19 e #24, entregues além dele; histórias #1 a #24 do backlog, casos de teste CT01 a CT33

## 1. Resumo executivo
| Métrica | Valor |
|---|---|
| Total de casos de teste | 33 |
| Passaram | 33 |
| Falharam | 1 (CT21, corrigido até 05/11, ver seção 3) |
| Cobertura automatizada (linhas/branches) | 98% (229 testes automatizados no CI) |

## 2. Casos de teste — visão consolidada
| ID | Área | Tipo | Resultado | Observação |
|---|---|---|---|---|
| CT01 | Autenticação e Perfis | Integração | Passou | #1. Expiração da sessão testada nesta bateria |
| CT02 | Autenticação e Perfis | Unitário/integração | Passou | #1. Herdado da Sprint 1 |
| CT03 | Autenticação e Perfis | Unitário/integração | Passou | #3. Herdado da Sprint 1 |
| CT04 | Autenticação e Perfis | Unitário/integração | Passou | #3. Herdado da Sprint 1 |
| CT05 | Cadastros Básicos | Integração | Passou | #5. Herdado da Sprint 2 |
| CT06 | Cadastros Básicos | Integração | Passou | #5. Herdado da Sprint 2 |
| CT07 | Cadastros Básicos | Integração | Passou | #8. Herdado da Sprint 2 |
| CT08 | Cadastros Básicos | Integração | Passou | #9. Paginação testada nesta bateria |
| CT09 | Cadastros Básicos | Integração | Passou | #10. Herdado da Sprint 2 |
| CT10 | Cadastros Básicos | Integração | Passou | #11. Herdado da Sprint 2 |
| CT11 | Movimentações | Integração | Passou | #14. Herdado da Sprint 2 |
| CT12 | Movimentações | Integração | Passou | #16. Herdado da Sprint 2 |
| CT13 | Movimentações | Integração | Passou | #16. Herdado da Sprint 2 |
| CT14 | Cadastros Básicos | Integração | Passou | #12. Herdado da Sprint 2 |
| CT15 | Relatórios e Painel | Integração | Passou | #20. Herdado da Sprint 4 |
| CT16 | Relatórios e Painel | Integração | Passou | #21. Herdado da Sprint 4 |
| CT17 | Relatórios e Painel | Integração | Passou | #21. Herdado da Sprint 4 |
| CT18 | Autenticação e Perfis | Integração | Passou | #2. Herdado da Sprint 1 |
| CT19 | Autenticação e Perfis | Unitário/integração | Passou | #4. Herdado da Sprint 1 |
| CT20 | Movimentações | Unitário/integração | Passou | #19. Entregue em 02/11 (PR #63); o estorno fica registrado na própria movimentação, com data e administrador |
| CT21 | Relatórios e Painel | Integração | Passou | #23. Falhou na 1ª verificação; passou após a correção (PR #66) |
| CT22 | Cadastros Básicos | Integração | Passou | #6. Herdado da Sprint 2 |
| CT23 | Cadastros Básicos | Integração | Passou | #7. Herdado da Sprint 2 |
| CT24 | Cadastros Básicos | Integração | Passou | #13. Herdado da Sprint 2 |
| CT25 | Movimentações | Integração | Passou | #15. Herdado da Sprint 2 |
| CT26 | Movimentações | Integração + manual | Passou | #17. Herdado da Sprint 2 |
| CT27 | Movimentações | Integração | Passou | #18. Herdado da Sprint 2 |
| CT28 | Relatórios e Painel | Integração | Passou | #22. Herdado da Sprint 4 |
| CT29 | Movimentações | Banco | Passou | #14, #16. Adicionado na Sprint 4 |
| CT30 | Cadastros Básicos | Banco | Passou | #8. Adicionado na Sprint 4 |
| CT31 | Autenticação e Perfis | Banco | Passou | #3. Adicionado na Sprint 4 |
| CT32 | Banco de dados | Banco | Passou | E3. Migrations iguais ao `db/schema.sql` |
| CT33 | Relatórios e Painel | Integração | Passou | #24. Entregue em 03/11 (PR #64) |

## 3. Bugs encontrados nesta bateria
| # | Descrição | Severidade | Status |
|---|---|---|---|
| 1 | CSV do relatório de distribuições não neutralizava fórmulas (`=`, `+`, `-`, `@`) | Média | Corrigido (PR #66) |
| 2 | CSV gravava o BOM no começo de cada linha, e não só no início do arquivo | Média | Corrigido (PR #66) |
| 3 | CSV não trazia os mesmos dados da tela do relatório, como pede a #23 | Média | Corrigido (PR #66) |

## 4. Testes de aceitação com cliente/PO
Pendente. Será realizado com o professor.
