# Roteiro do Protótipo Navegável — Conecta Social

**Link do protótipo:** [Acessar no Figma](https://www.figma.com/design/YChrqTf5IiwA9skwfSP8O7/Conecta-Social--Copy-?node-id=1669-162202)

**Link do preview (navegável):** [Acessar preview](https://www.figma.com/proto/YChrqTf5IiwA9skwfSP8O7/Conecta-Social--Copy-?node-id=2603-15&starting-point-node-id=2603-15)



## Integrantes

**Equipe:**
- Alexandre Victoriano Ribeiro Ulhoa — RA 2840482423007
- Daniel Souza Monteiro de Carvalho — RA 2840482211052
- Cintia Marcelo de Oliveira — RA 2840482421017
- Antonio Pires Felipe — RA 2840482211003
- Luiz Henrique Neres — RA 2840482423005

## Índice de telas

As telas abaixo foram conferidas no arquivo do Figma. A coluna **Evidência no layout** descreve os dados e ações visíveis; a interação de cada botão deve ser testada no modo **Prototype**.

| Tela | Perfil | História relacionada (E2) | O que a tela mostra/permite | Evidência no layout |
|---|---|---|---|---|
| Login (`login`) | Administrador e Voluntário | #1 | Seleção de perfil, e-mail, senha, visibilidade da senha e botão **Entrar**. | Frame `2603:15`; estado Voluntário `2661:26`, com switch animado. |
| Painel (`painel`) | Administrador e Voluntário | #20 | Cards de estoque por categoria, alerta de item abaixo do mínimo e tabela com item, categoria, saldo, mínimo e ação **Receber**. | Administrador `2603:39`; variante Voluntário `2666:99`, sem Administração. |
| Itens e Categorias (`itens`) | Administrador e Voluntário; criação: Administrador | #10, #11, #12 | Lista de itens com categoria, unidade, saldo, estoque mínimo e status; ações de categoria, item e edição. | Administrador `2603:126`; variante Voluntário `2669:2`. |
| Doadores (`doadores`) | Voluntário | #5, #6 | Cadastro de doador e consulta da lista de doadores. | Administrador `2603:258`; variante Voluntário `2669:142`. |
| Famílias (`familias`) | Voluntário | #8, #9 | Cadastro de família e consulta da lista de famílias. | Administrador `2603:344`; variante Voluntário `2669:236`. |
| Registrar Doação (`doacoes-voluntario`) | Voluntário | #14 | Seleção de doador e item, quantidade, data e confirmação da entrada no estoque. | Frame `2669:334`. Não há tela equivalente para Administrador no protótipo — o Administrador acessa o registro de doação pelo mesmo fluxo operacional do Voluntário. |
| Registrar Distribuição (`distribuicao`) | Voluntário | #16 | Seleção de família e item, quantidade, data, saldo disponível e validação de saldo insuficiente. | Administrador `2603:641`; variante Voluntário `2669:421`. |
| Relatório (`relatorio`) | Voluntário | #21 | Filtros de período e família, tabela de distribuições e exportação dos dados. | Administrador `2603:727`; variante Voluntário `2669:508`. |
| Gestão de Usuários (`usuarios`) | Administrador | #3 | Cadastro de usuário com nome, e-mail, senha e perfil; listagem e controle de acesso. | Frame `2603:793`; área exclusiva de Administração. |

As variantes com sufixo `-voluntario` são versões de navegação e permissão das mesmas telas operacionais; não representam novas histórias nem aumentam a quantidade de telas do MVP. Elas exibem **Maria Voluntária** e não apresentam a seção **Administração**.

## Cobertura das histórias Must (E2)

| # | História do backlog | Tela do protótipo | Cobertura visual | Critério que ainda exige teste no Prototype |
|---|---|---|---|---|
| 1 | Login com e-mail e senha | Login | Sim | Credencial inválida, redirecionamento ao painel e expiração da sessão. |
| 2 | Logout | Painel | Sim | Botão **Sair** retorna ao login e bloqueia URL protegida. |
| 3 | Cadastrar usuários como Administrador | Gestão de Usuários | Sim | Nome, senha, e-mail duplicado e restrição de acesso do Voluntário. |
| 5 | Cadastrar doador | Doadores | Sim | Obrigatoriedade, formato e duplicidade de CPF/CNPJ. |
| 6 | Listar e buscar doadores | Doadores | Sim | Filtro por nome e paginação de até 20 registros. |
| 8 | Cadastrar família | Famílias | Sim | Campos obrigatórios e salvamento refletido imediatamente na lista. |
| 9 | Listar e buscar famílias | Famílias | Sim | Filtro por responsável e paginação de até 20 registros. |
| 10 | Cadastrar categorias | Itens e Categorias | Sim | Validação de nome duplicado. |
| 11 | Cadastrar item | Itens e Categorias | Sim | Categoria, unidade, estoque mínimo e saldo inicial zero. |
| 12 | Visualizar itens com saldo | Itens e Categorias | Sim | Destaque de itens com saldo menor ou igual ao mínimo. |
| 14 | Registrar doação | Registrar Doação | Sim | Atualização exata do saldo e registro no histórico. |
| 16 | Registrar distribuição | Registrar Distribuição | Sim | Bloqueio quando o saldo é insuficiente e redução exata do saldo. |
| 20 | Painel de estoque por categoria | Painel | Sim | Dados refletidos após movimentações e alertas conforme o mínimo. |
| 21 | Relatório de distribuições | Relatório | Sim | Filtros combinados e tabela com família, item, categoria, quantidade e número de distribuições. |

**Resultado:** as 14 histórias Must possuem uma tela correspondente no layout. A cobertura dos critérios de aceite depende da execução dos fluxos clicáveis no modo **Prototype**

## Fluxos navegáveis implementados

O protótipo é clicável no modo **Prototype** do Figma (conexões configuradas com `ON_CLICK` → `NAVIGATE` em todos os itens do menu lateral, no botão **Sair** e nos botões de ação principais de cada tela). Pontos de entrada (`flow starting points`): **Início — Administrador** (`login`) e **Início — Voluntário** (`login-voluntario`).

- **Comum:** Login → **Entrar no Conecta** → Painel → (menu lateral: Itens e categorias, Doadores, Famílias, Movimentações) → **Sair** → Login.
- **Administrador:** Login → Painel → **+ Nova movimentação** → Distribuição → **Registrar** → Relatório. O menu lateral leva a qualquer tela (Painel, Itens e categorias, Doadores, Famílias, Movimentações → Distribuição, Usuários) a partir de qualquer ponto do fluxo.
- **Voluntário:** Login (voluntário) → Painel → **Receber** (item abaixo do mínimo) → Registrar Doação → **Registrar** → Registrar Distribuição → **Registrar** → Relatório. O menu lateral do Voluntário não exibe **Administração/Usuários**, conforme a restrição de acesso da história #3.

Cada tela mantém o próprio item do menu lateral marcado como ativo; clicar num item já ativo permanece na mesma tela (sem link, por ser a página atual).

