# Roteiro do Vídeo — Conecta Social

**Equipe:** Alexandre Victoriano Ribeiro Ulhoa (RA 2840482423007), Antonio Pires Felipe (RA 2840482211003), Daniel Souza Monteiro de Carvalho (RA 2840482211052), Luiz Henrique Neres (RA 2840482423005)  
**Link do vídeo (não listado):** [link]  
**Duração final:** [mm:ss] (entre 8 e 12 min)

## 1. Planejamento dos blocos
| Bloco | Tempo | Quem fala | O que aparece na tela |
|---|---|---|---|
| 1 · Abertura | 0:00–0:25 | Luiz | Capa com o nome Conecta Social, a frase "Do doador à família, sem perder o fio." e os nomes da equipe |
| 2 · Problema e cliente | 0:25–1:20 | Luiz | Seção 1 do Documento de Visão (ONGs pequenas controlando doações em planilha, caderno e WhatsApp, com 3 a 5 horas por semana só para consolidar entradas e saídas) e a tabela de perfis Administrador e Voluntário. Cliente: o Prof. Lucas, na aceitação da E9; PO: Antonio |
| 3 · Demonstração (deploy público) | 1:20–4:40 | Alexandre narra a parte da voluntária (1:20–3:20) e Luiz a do administrador (3:20–4:40) | Maria Voluntária cadastra uma doadora, registra a doação de arroz e entrega à família Josefa Santos; o sistema barra a entrega maior que o saldo; o Admin abre o painel e o relatório e cancela uma entrega lançada por engano |
| 4 · Engenharia: rastreabilidade | 4:40–6:25 | Daniel | História #5 no backlog → caso de uso e DER (`cpf_cnpj` UNIQUE) → PR #30 com a aprovação de Antonio → CT05 e CT06 no relatório final e o CI verde |
| 5 · Processo ágil | 6:25–8:35 | Antonio (board, planejado × entregue, escopo e PRs) e Alexandre (retrospectiva e papéis) | Board no GitHub Projects e prints das Sprints 1, 2 e 4, tabela planejado × entregue, ata da retrospectiva da Sprint 4, PR #63 da história #19, lista de PRs integrados |
| 6 · Depoimentos individuais | 8:35–10:35 | todos | Câmera de cada integrante, com o nome na tela |
| Fechamento | 10:35–10:55 | Antonio | URL do deploy, repositório, tecnologias (Django, PostgreSQL, htmx, Render, GitHub Actions) e nomes da equipe, parados por 5 s |

## 2. Requisitos mínimos na demonstração (bloco 3)
| Requisito mínimo | Momento do vídeo | Como aparece |
|---|---|---|
| Autenticação com 2+ perfis | 1:20 e 3:20 | Login como Maria (Voluntária) e como Admin; Maria abre `/usuarios/` e recebe "Acesso restrito a administradores."; o Admin vê o menu Administração → Usuários |
| Regra de negócio não trivial (caso normal + borda) | 2:45 e 3:05 | Entrega de 4 pacotes de arroz com o saldo exibido no formulário; depois, pedido de 500 pacotes barrado com "Saldo insuficiente: disponível X, solicitado 500"; aos 4:25, o cancelamento da entrega devolve o saldo |
| Consulta agregada (relatório/dashboard) | 3:40 e 4:05 | Painel com o estoque agrupado por categoria e os itens em alerta; relatório de distribuições filtrado por período e família, com o total por família e item |
| Validações em interface e banco | 1:50 | Doadora com CPF de 10 números ("Informe um CPF com 11 números ou CNPJ com 14 números.") e com CPF já cadastrado ("Este CPF/CNPJ já está cadastrado."); no bloco 4, o UNIQUE da coluna no DER |
| 6+ entidades com N:N | 5:20 | DER no bloco 4: 8 entidades; Doação liga Doador e Item, e Distribuição liga Família e Item |
| Deploy público (URL visível) | todo o bloco 3 | `conecta-social-wcxa.onrender.com` na barra do navegador |
| Repositório com README | 10:40 | README aberto no GitHub |

## 3. História rastreada (bloco 4)
**História escolhida:** #5 — Como Voluntário, quero cadastrar um doador com nome e CPF/CNPJ, para que eu possa vincular doações a uma pessoa identificável
| Etapa | Artefato mostrado | Link |
|---|---|---|
| Requisito | História #5 (Must, 3 pontos) com os critérios "CPF/CNPJ duplicado exibe erro de validação" e "CPF/CNPJ com formato inválido exibe erro antes de submeter" | `docs/backlog.md` |
| Modelo | Caso de uso "Cadastrar doador" (ator Voluntário) e classe Doador; tabela `doador` com `cpf_cnpj` NOT NULL e UNIQUE | `docs/uml.md`, `docs/der.md` |
| Código | PR #30 (Daniel), aprovado por Antonio em 22/09/2026 antes do merge, com `lint` e `test` verdes | https://github.com/Antonio-pf/projeto-eng-soft/pull/30 |
| Teste | CT05 (formato inválido) e CT06 (CPF/CNPJ duplicado) como "Passou" no relatório final; `test_cpf_formato_invalido` e `test_cpf_duplicado` rodando no GitHub Actions | `docs/relatorio-testes-final.md`, https://github.com/Antonio-pf/projeto-eng-soft/actions/runs/43657453857 |

**Decisão técnica justificada:** antes de comparar com o banco, o formulário tira tudo o que não é número e grava o documento sempre com a mesma máscara, porque "123.456.789-00" e "12345678900" passariam como dois doadores com o mesmo CPF. A conferência é só da quantidade de números (11 ou 14), sem consulta à Receita, porque o Documento de Visão deixou a consulta a serviços do governo fora do escopo.

## 4. Evidências de processo ágil (bloco 5)
| Evidência | Sprint | Artefato mostrado na tela |
|---|---|---|
| Planejado × entregue por sprint | 1–4 | S1: 4 de 13 histórias (as #5 a #13 passaram para a S2) · S2: 5 de 5, mais as 9 que sobraram da S1 · S3: 1 de 5 no prazo, 1 parcial · S4: 3 de 4; a #19 entrou depois, em 02/11 (seção 1 de cada `docs/sprints/sprint-N-relatorio.md`) |
| Retrospectiva com ação aplicada | 3 → 4 | Ata da Sprint 3: "terminar a #21 com os testes CT16 e CT17"; aplicada na Sprint 4 pelo PR #53 (seção 1 da `docs/sprints/sprint-4-retrospectiva.md`). Contraponto: CT01 e CT08 ficaram pendentes em três atas e só saíram na E9 (PR #66), quando a cobertura mínima de 95% virou regra do CI |
| Mudança de escopo negociada | 3–4 | História #19 (cancelar movimentação, Could, fora do E2b): ficou em "Todo" nas Sprints 3 e 4, a ata pediu "implementar ou negociar o corte com o professor", e ela entrou em 02/11 pelo PR #63, com o cancelamento marcado na própria movimentação (seção 2 da `docs/documentacao-final.md`) |
| PR com revisão relevante | 4 | PR #49 (história #22, Daniel), aprovado por Antonio antes do merge. Contraponto: entre os PRs de código, só o #30 e o #49 têm revisão registrada, apesar da regra combinada na retrospectiva da Sprint 1 |
| Rodízio de papéis | 1–4 | Sprint 1: Alexandre Scrum Master, Antonio PO, Daniel responsável por dados e Luiz facilitador (`docs/termo-aceite.md` e contribuições da Sprint 1). Antonio acumulou PO e Scrum Master nas quatro sprints; os papéis das Sprints 2 a 4 dos demais [a confirmar — alinhar com o Alexandre antes do envio, já que `docs/termo-aceite.md` ainda lista só ele como Scrum Master] |

## 5. Depoimentos (bloco 6)
| Integrante | Papéis exercidos | Conceito aprendido na prática | Evidência citada | O que faria diferente |
|---|---|---|---|---|
| Alexandre | Product Owner (S1); S2–S4 [a confirmar] | [Alexandre] | [Alexandre; ex.: testes manuais da interface, seção 4 do relatório da E9] | [Alexandre] |
| Antonio | Scrum Master (S1–S4) | Escopo e processo andam juntos: uma decisão de PO (fazer ou cortar a #19) só vira entrega quando o Scrum Master garante que isso vira ação com dono e prazo, não só intenção na ata | PR #63 (decisão sobre a #19) e PR #66 (cobertura mínima de 95% no CI, que destravou CT01/CT08 pendentes desde a Sprint 2) | Checar o board contra a `main` toda semana, não só no fim da sprint — foi o que faltou entre 09/10 e 28/10, quando a `main` ficou quase 3 semanas sem merge |
| Daniel | Dados (S1); S2–S4 [a confirmar] | [Daniel] | [Daniel; ex.: PR #30, PR #49 ou o manual do usuário, PR #78] | [Daniel] |
| Luiz | Facilitador (S1); S2–S4 [a confirmar] | [Luiz] | [Luiz; ex.: PR #31 ou o relatório de distribuições, commit `56ce3c6` do PR #53] | [Luiz] |

## 6. Checagem antes do envio
- [ ] Sem senhas, tokens, `.env` ou dados pessoais reais na tela
- [ ] Autorização de imagem de quem aparece e do cliente (se citado)
- [ ] Link testado em janela anônima
- [ ] Ficha da mostra em `docs/mostra-virtual.md` + capa + 3 capturas enviadas
