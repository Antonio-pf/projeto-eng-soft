# Ficha da Mostra Virtual — E10

> Rascunho. Campos marcados com `[a confirmar]` ou `[pendente]` precisam da equipe antes do envio.

## Nome do projeto
Conecta Social

## Frase de destaque (até 120 caracteres)
Do doador à família, sem perder o fio: gestão de doações para ONGs pequenas.

## Resumo (até 600 caracteres)
ONGs pequenas ainda controlam doações em planilha, caderno e WhatsApp, gastando de 3 a 5 horas por semana só para consolidar entradas e saídas. O Conecta Social registra doações e distribuições, mantém o saldo de estoque sempre correto, bloqueia entregas maiores que o saldo disponível e gera relatórios agregados para prestação de contas. Dois perfis — Administrador e Voluntário — têm acesso diferenciado às mesmas telas. Construído em Django com PostgreSQL, já está no ar e em uso de demonstração pela equipe.

## Equipe
| Integrante | RA | Papel na Sprint 1 | Papéis nas Sprints 2–4 |
|---|---|---|---|
| Antonio Pires Felipe | 2840482211003 | Product Owner e Scrum Master | Product Owner e Scrum Master (seguiu nas 4 sprints) |
| Alexandre Victoriano Ribeiro Ulhoa | 2840482423007 | Product Owner |  Product Owner |
| Daniel Souza Monteiro de Carvalho | 2840482211052 | Responsável por Dados | `[a confirmar]` |
| Luiz Henrique Neres | 2840482423005 | Facilitador | `[a confirmar]` |

## Cliente/PO
Prof. Lucas, professor da disciplina Laboratório de Engenharia de Software, atuando como cliente/PO (aceitação em `docs/termo-aceite-cliente.md`).

## Tecnologias
Python 3.12+, Django 5.2+, PostgreSQL 15+, Django Templates + Tailwind CSS/daisyUI (CSS compilado no build) + htmx 2.0.11, deploy no Render (gunicorn + whitenoise), CI no GitHub Actions com cobertura mínima de 95%.

## Links
- Vídeo: `[pendente — inserir após upload]`
- Deploy: https://conecta-social-wcxa.onrender.com/
- Repositório: https://github.com/Antonio-pf/projeto-eng-soft

## Capa
`[pendente]` — imagem 1280×720 (PNG/JPG), miniatura do vídeo. Sugestão: tela de abertura do próprio vídeo (bloco 1) ou o painel do Administrador.
Caminho sugerido: `docs/sprints/assets/mostra-virtual-capa.png`

## Capturas (3 imagens, 1920×1080)
`[pendente]` — sugestões, reaproveitando telas já demonstradas no vídeo:
1. Painel do Administrador (estoque agrupado por categoria + alertas)
2. Formulário de distribuição com bloqueio por saldo insuficiente
3. Relatório de distribuições com filtro por período/família
Caminho sugerido: `docs/sprints/assets/mostra-virtual-captura-{1,2,3}.png`

## Aprendizado da equipe (até 400 caracteres)
Aprendemos que escopo só é cumprido com decisão explícita: a história #19 ficou dois ciclos parada até a equipe decidir, na retrospectiva, implementá-la em vez de adiar de novo. E que "pronto" sem teste automatizado não é pronto — foi preciso tornar a cobertura mínima de 95% regra do CI para os testes pendentes desde a Sprint 2 saírem do papel.
