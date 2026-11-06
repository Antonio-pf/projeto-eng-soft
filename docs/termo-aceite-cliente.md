# Termo de Aceite do Cliente — Conecta Social

**Cliente/PO:** professor da disciplina Laboratório de Engenharia de Software, atuando como cliente/PO (tema nº 4 do banco de temas, Trilha B)

**Data:** \_\_\_/\_\_\_/\_\_\_\_\_\_

**Sistema avaliado:** [https://conecta-social-wcxa.onrender.com/](https://conecta-social-wcxa.onrender.com/), seguindo o roteiro em [`docs/roteiro-aceitacao.md`](roteiro-aceitacao.md)

## 1. Escopo avaliado (comparado ao Termo de Aceite do Projeto — E2b)

| Funcionalidade aceita na E2b | Histórias do backlog (prioridade) | Entregue? | Observação do cliente |
|---|---|---|---|
| 1. Cadastro e autenticação de usuário voluntário e administrador | #3 (Deve ter) | Sim (CT03, CT04, CT31) | |
| 2. Login | #1 (Deve ter) | Sim (CT01, CT02) | |
| 3. Logout | #2 (Deve ter) | Sim (CT18) | |
| 4. Cadastro de categorias, itens e doador | #5, #6, #10, #11 (Deve ter); #7, #13 (Deveria ter) | Sim (CT05, CT06, CT09, CT10, CT22, CT23, CT24) | |
| 5. Desativação de usuário sem exclusão | #4 (Deveria ter) | Sim (CT19) | |
| 6. Registro das doações realizadas | #14 (Deve ter); #15 (Deveria ter) | Sim (CT11, CT25, CT29) | |
| 7. Controle de entrada de doações no estoque | #12 (Deve ter) | Sim (CT14) | |
| 8. Controle de saída de doações para as famílias | #8, #9, #16 (Deve ter); #17, #18 (Deveria ter) | Sim (CT07, CT08, CT12, CT13, CT26, CT27, CT30) | |
| 9. Relatório para prestação de contas | #20, #21 (Deve ter); #22 (Deveria ter); #23 (Poderia ter) | Sim (CT15, CT16, CT17, CT21, CT28) | |
| Além do escopo da E2b | #19 (Poderia ter): cancelar movimentação, com o estorno registrado na própria movimentação (data e administrador), sem apagar o original; #24 (Deveria ter): painel do mês | Sim (CT20, CT33) | |

A #23 (exportação em CSV) consta do item 9 da E2b, mas é Poderia ter no backlog. Os casos de teste estão no [`docs/relatorio-testes-final.md`](relatorio-testes-final.md).

## 2. Ressalvas / pendências

- LGPD: o sistema guarda dados pessoais (nome, endereço e telefone das famílias; nome, CPF/CNPJ, telefone e e-mail dos doadores), mas não mostra aviso ao titular nem registra a base legal e o prazo de retenção desses dados
- Segurança: não há limite de tentativas de login
- \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

## 3. Parecer

- [ ] Aceito sem ressalvas
- [ ] Aceito com ressalvas (listadas acima, não bloqueantes)
- [ ] Não aceito — motivo: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

## 4. Assinatura

A assinatura pode ser física, digital ou um e-mail de confirmação, anexado em PDF.

- Cliente/PO: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ (nome e assinatura)
- Integrantes que acompanharam o teste (nome completo — RA): \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
