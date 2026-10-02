# Evidências de Teste — Sprint 2 — Conecta Social

**Equipe:** Alexandre Victoriano Ribeiro Ulhoa (RA 2840482423007) — Daniel Souza Monteiro de Carvalho (RA 2840482211052) — Cintia Marcelo de Oliveira (RA 2840482421017) — Antonio Pires Felipe (RA 2840482211003) — Luiz Henrique Neres (RA 2840482423005)

> Atualiza (não substitui) o [Plano de Testes](../plano-de-testes.md) (E4b). Todo caso de teste com ID (CTxx) implementado nesta sprint precisa de evidência verificável abaixo. Os testes ficam em `core/tests.py`; os nomes citados são métodos das classes indicadas.

| ID | Caso de teste | Tipo | Resultado | Evidência |
|---|---|---|---|---|
| CT05 | Cadastro de doador com CPF/CNPJ inválido | Integração | ✅ Passou | `test_cpf_formato_invalido` (`DoadorTestCase`) |
| CT06 | CPF/CNPJ duplicado no cadastro de doador | Integração | ✅ Passou | `test_cpf_duplicado` (`DoadorTestCase`) |
| CT22 | Listagem, busca e paginação de doadores | Integração | ✅ Passou | `test_listar_doadores`, `test_buscar_doador_por_nome`, `test_paginacao_doadores` (`DoadorTestCase`) |
| CT23 | Edição de doador com CPF/CNPJ duplicado | Integração | ✅ Passou | `test_doador_edit_get_prefilled`, `test_doador_edit_success`, `test_doador_edit_duplicate_cpf_cnpj` (`DoadorUpdateTestCase`) |
| CT07 | Cadastro de família com dados obrigatórios | Integração | ✅ Passou | `test_cadastrar_familia_com_sucesso`, `test_cadastrar_familia_num_membros_invalido`, `test_cadastrar_familia_telefone_opcional` (`FamiliaTestCase`) |
| CT08 | Busca e paginação de famílias pelo nome | Integração | 🟡 Parcial | Busca coberta por `test_listar_e_buscar_familias` (`FamiliaTestCase`). A paginação (20 por página, `Paginator` em `core/views.py`) funciona na view, mas **não tem teste automatizado**; pendência para a Sprint 3 |
| CT09 | Cadastro de categoria de itens | Integração | ✅ Passou | `test_cadastrar_categoria_com_sucesso`, `test_cadastrar_categoria_nome_duplicado`, `test_editar_categoria`, `test_listar_categorias` (`CategoriaTestCase`) |
| CT10 | Cadastro de item com estoque mínimo | Integração | ✅ Passou | `test_cadastrar_item_com_sucesso`, `test_cadastrar_item_estoque_minimo_invalido` (`ItemTestCase`) |
| CT14 | Itens com saldo ≤ estoque mínimo destacados na listagem | Integração | ✅ Passou | `test_listar_itens_com_saldo_e_destaque` (`ItemTestCase`); GIF de navegação mostra o selo "Baixo Estoque" |
| CT24 | Edição de item sem alterar saldo diretamente | Integração | ✅ Passou | `test_editar_item` (`ItemTestCase`) |
| CT11 | Registro de doação aumenta o saldo do item | Integração | ✅ Passou (após correção) | `test_cadastrar_doacao_com_sucesso`, `test_cadastrar_doacao_quantidade_zero_ou_negativa_invalida`, `test_cadastrar_doacao_data_futura_invalida`, `test_cadastrar_doacao_quantidade_fracionada_permitida`, `test_cadastrar_doacao_acesso_anonimo_redireciona_para_login`, `test_administrador_tambem_pode_registrar_doacao` (`DoacaoTestCase`). Falhou na verificação manual: a data padrão "hoje" era definida em `DoacaoForm`, mas o navegador mostrava o campo vazio (o `DateInput` renderizava `01/10/2026`, formato que `type="date"` ignora). Corrigido em 01/10/2026 com `format="%Y-%m-%d"`; regressão coberta por `test_formulario_abre_com_data_de_hoje_em_formato_iso` (`DoacaoTestCase`), que falha sem a correção. GIF: [registrar doação](assets/conecta-social-sprint2-registrar-doacao-e-historico.gif) (saldo da "Pasta de dente" 0 → 20) |
| CT12 | Distribuição com saldo suficiente diminui o saldo | Integração | ✅ Passou | `test_registrar_distribuicao_com_sucesso`, `test_registrar_distribuicao_saldo_exatamente_igual_permitida` (`DistribuicaoTestCase`); a mesma correção da data padrão vale aqui, com `test_formulario_abre_com_data_de_hoje_em_formato_iso` (`DistribuicaoTestCase`). GIF: [registrar distribuição](assets/conecta-social-sprint2-registrar-distribuicao-e-historico.gif) (saldo 20 → 15) |
| CT13 | Distribuição bloqueada por saldo insuficiente | Integração | ✅ Passou | `test_registrar_distribuicao_saldo_insuficiente_bloqueada` (`DistribuicaoTestCase`); outras validações: `test_registrar_distribuicao_quantidade_zero_ou_negativa_invalida`, `test_registrar_distribuicao_data_futura_invalida`. GIF mostra o erro ao pedir 50 com saldo 20 |
| CT25 | Histórico de doações filtrável por doador e período | Integração | ✅ Passou | `test_lista_todas_as_doacoes_sem_filtro`, `test_filtro_por_doador_isolado`, `test_filtro_por_periodo_isolado`, `test_filtro_por_doador_e_periodo_combinados`, `test_filtro_com_data_invalida_e_ignorado_sem_erro_500`, `test_paginacao_lista_doacoes`, `test_lista_doacoes_acesso_anonimo_redireciona_para_login` (`DoacaoListTestCase`) |
| CT26 | Saldo disponível no formulário de distribuição | Integração | ✅ Passou | `test_formulario_exibe_saldo_inline_na_opcao_do_item`, `test_contexto_da_view_contem_saldo_por_item` (`DistribuicaoTestCase`). A interação em JavaScript (caixa de informação ao escolher o item) foi validada manualmente no navegador (descrição do PR #34 e GIF de distribuição) |
| CT27 | Histórico de distribuições filtrável por família e período | Integração | ✅ Passou | `test_lista_todas_as_distribuicoes_sem_filtro`, `test_filtro_por_familia_isolado`, `test_filtro_por_periodo_isolado`, `test_filtro_por_familia_e_periodo_combinados`, `test_filtro_com_data_invalida_e_ignorado_sem_erro_500`, `test_paginacao_lista_distribuicoes`, `test_lista_distribuicoes_acesso_anonimo_redireciona_para_login` (`DistribuicaoListTestCase`) |

## Cobertura automatizada nesta sprint

79 testes, 100% passando (`python manage.py test`, 01/10/2026, 106 s, após a correção da data padrão):

```
Found 79 test(s).
Ran 79 tests in 105.712s
OK
System check identified no issues (0 silenced).
```

Composição: 26 testes da Sprint 1 (autenticação e usuários, ver
[`sprint-1-evidencias-teste.md`](sprint-1-evidencias-teste.md)) + 22 dos cadastros (doadores 10,
famílias 4, categorias 4, itens 4) + 31 de movimentações (doação 7, distribuição 10, histórico de
doações 7, histórico de distribuições 7). O PR #34 registrou `ruff check` e 77/77 antes da correção da data; `ruff check core` também passou depois dela.

Evidência manual: os três GIFs em [`assets/`](assets/) (`conecta-social-sprint2-*.gif`) foram
gravados em 01/10/2026 com a `main` desta sprint rodando localmente.

**Pendências para a Sprint 3:** teste de paginação de famílias (CT08); teste de expiração de sessão
(CT01, herdado da Sprint 1);
casos CT15 a CT17, CT20, CT21 e CT28 do plano de testes (painel, relatórios, estorno e CSV).
