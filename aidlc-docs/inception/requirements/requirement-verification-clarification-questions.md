# Clarification Questions — História #14 (Registrar Doação)

Detectei uma ambiguidade na Question 2 original e um possível desalinhamento de escopo nas extensões de Segurança/Resiliência que você habilitou. Por favor, responda abaixo.

## Ambiguidade 1: Quantidade decimal vs. inteiro (Question 2 original)
Sua resposta foi "X" com o comentário: *"e para casos de itens quebrados?"*. Não ficou claro se isso significa que você quer permitir quantidades fracionadas (ex.: 2.5 kg, meio pacote) para cobrir esses casos, ou se é outra preocupação.

### Clarification Question 1
Itens "quebrados" (ex.: metade de um pacote, fração de kg) devem poder ser registrados como doação?

A) Sim — manter `quantidade` como Decimal (já é o tipo no model/migração existente) e aceitar valores fracionados maiores que zero (ex.: 2.5 kg, 0.5 pct)

B) Não — cada doação representa unidades inteiras completas; itens parcialmente danificados/abertos não entram como fração, ficam de fora do registro ou seriam tratados em uma funcionalidade futura

X) Other (please describe after [Answer]: tag below)

[Answer]: a

---

## Ambiguidade 2: Escopo das extensões Security Baseline e Resiliency Baseline
Você habilitou (resposta A) as extensões **Security Baseline** e **Resiliency Baseline**. Essas extensões têm ~15 regras cada, várias sobre infraestrutura cloud que **não existe neste repositório** (não há IaC/CDK/Terraform, não há multi-região, não há pipeline de CI/CD formal, não há load balancer configurado em código) — o projeto é uma aplicação Django única, para uma disciplina, com deploy simples.

Se eu aplicar as regras à risca, a Resiliency Baseline exige que eu pergunte sobre RTO/RPO, estratégia de DR, ferramenta de CI/CD, mecanismo de rollback, estilo de deploy, topologia multi-região, processo de change management e processo de resposta a incidentes — perguntas de nível de projeto/organização, não de uma única história de backlog (#14).

### Clarification Question 2
Como você quer que eu trate essas duas extensões nesta tarefa?

A) Aplicar apenas as regras de nível de **código da aplicação** que fazem sentido para esta história (ex.: validação de entrada no form, controle de acesso via decorators, tratamento de erros, não expor stack traces, auditabilidade da doação via `registrado_por`/`criado_em`) e marcar como **N/A** as regras de infraestrutura/processo (multi-zona, DR, CI/CD, rollback, auto-scaling, chaos engineering, change management, incident response, etc.), já que não existem no repositório e não são decisão desta história isoladamente

B) Aplicar o baseline completo, incluindo as perguntas de infraestrutura/processo (RTO/RPO, DR, CI/CD, rollback, deployment style, topologia regional, change management, incident response) — vou criar um arquivo de perguntas adicional para isso

C) Desabilitar as duas extensões para esta tarefa (tratar como protótipo/projeto acadêmico) — volto a marcar como "Não" no Requirements

X) Other (please describe after [Answer]: tag below)

[Answer]: a
