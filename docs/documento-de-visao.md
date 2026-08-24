# Documento de Visão — Sistema de Gestão de ONG de Doações

**Equipe:**

- Alexandre Victoriano Ribeiro Ulhoa (2840482423007)
- Daniel Souza Monteiro de Carvalho (2840482211052)
- Cintia Marcelo de Oliveira (2840482421017)
- Antonio Pires Felipe (2840482211003)

**Trilha:** B
**Origem do problema:** Banco de temas nº 4
**Data:** 21/08/2026

---

## 1. Problema

O Brasil conta hoje com quase 917 mil Organizações da Sociedade Civil (OSCs) ativas, segundo o [Mapa das OSCs](https://mapaosc.ipea.gov.br/) do Ipea — um crescimento de mais de 100 mil entidades na última década. Apesar desse volume, a maioria das ONGs de pequeno e médio porte ainda gerencia suas operações com planilhas, cadernos físicos ou grupos de WhatsApp.

Na prática, isso gera gargalos concretos: um gestor típico gasta entre 3 e 5 horas semanais apenas consolidando registros de entrada e saída de itens doados; erros de contagem resultam em distribuições duplicadas ou famílias ignoradas em ciclos de entrega; e a ausência de relatórios confiáveis dificulta a prestação de contas para financiadores e parceiros. A rotatividade de voluntários agrava o problema — sem sistema centralizado, o conhecimento operacional fica na cabeça de cada pessoa, e qualquer saída representa perda de histórico.

O sistema proposto resolve esse cenário ao centralizar o cadastro de doadores, o controle de estoque de itens, o registro das famílias atendidas e a geração de relatórios de distribuição, eliminando a dependência de processos manuais e tornando a operação da ONG rastreável e auditável.

---

## 2. Público-alvo e perfis de usuário

| Perfil        | Quem é                                                               | O que faz no sistema                                                                                                                                               |
| ------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Administrador | Gestor ou coordenador da ONG, responsável pela operação geral        | Cadastra e gerencia usuários, categorias de itens e famílias; visualiza o painel geral; gera relatórios de distribuição e estoque; acessa todas as funcionalidades |
| Voluntário    | Colaborador que auxilia nas atividades de recebimento e distribuição | Registra entradas de doações no estoque, registra saídas (distribuições para famílias), consulta saldo de itens disponíveis                                        |

---

## 3. Visão da solução

O sistema é uma aplicação web que centraliza a gestão operacional de uma ONG de doações, cobrindo o ciclo completo de cada item: do registro da doação recebida de um doador até a distribuição para uma família beneficiada. O software mantém o estoque atualizado em tempo real por categoria de item, bloqueia distribuições quando o saldo é insuficiente e emite alertas quando itens atingem o estoque mínimo configurado. Um painel de indicadores e relatórios filtráveis por período, família e item substituem as planilhas manuais, oferecendo aos gestores dados confiáveis para tomada de decisão e prestação de contas a financiadores.

---

## 4. Objetivos do MVP (o que o semestre entrega)

- Eliminar o uso de planilhas para controle de estoque, mantendo o saldo de itens atualizado automaticamente a cada entrada ou saída registrada
- Reduzir o tempo de consulta de informações operacionais (histórico de doações, famílias atendidas, saldo por categoria) de processo manual para acesso imediato via sistema
- Centralizar os registros de doações vinculando cada item ao doador de origem e cada distribuição à família beneficiada, com rastreabilidade completa
- Implementar autenticação com dois perfis (Administrador e Voluntário) com controle de acesso diferenciado por papel
- Gerar relatório de distribuição por período e por família, substituindo o levantamento manual semanal
- Disponibilizar o sistema em URL pública, acessível sem instalação local

---

## 5. Fora de escopo (explicitamente)

- **Arrecadação financeira online e links de pagamento:** o sistema não processa doações em dinheiro nem integra com gateways de pagamento (PagSeguro, Stripe etc.); o foco é exclusivamente na gestão de itens físicos doados
- **Gestão contábil completa:** controle de despesas, fluxo de caixa e balanço patrimonial não fazem parte deste semestre; o sistema gerencia estoque de itens, não finanças da ONG
- **Aplicativo mobile nativo:** a interface será uma plataforma web responsiva, otimizando o tempo de desenvolvimento; não haverá app publicado na App Store ou Google Play
- **Emissão de Nota Fiscal Eletrônica e documentos com validade jurídica:** o sistema poderá gerar comprovantes simples em tela, mas sem integração com órgãos governamentais (SEFAZ, Receita Federal)
- **Integração com APIs externas (CNPJ, CPF, CEP automático):** validações de documentos serão de formato apenas, sem consulta a serviços governamentais

---

## 6. Requisitos mínimos do §3 do Manual — como este projeto cobre cada um

| Requisito mínimo                        | Como este projeto cobre                                                                                                                                                                                                                                                                                                                           |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Autenticação com 2+ perfis              | Login com e-mail e senha; perfil **Administrador** com acesso total (usuários, relatórios, configurações) e **Voluntário** com acesso restrito a registros de entrada e saída — rotas protegidas por decorators de permissão no Django                                                                                                            |
| 6+ entidades com relacionamento N:N     | **Usuário**, **Doador**, **Família**, **CategoriaItem**, **Item** (estoque), **Doação** (N:N Doador ↔ Item via tabela intermediária com quantidade e data), **Distribuição** (N:N Família ↔ Item via tabela intermediária com quantidade e data) — 7 entidades, dois relacionamentos N:N explícitos                                               |
| Regra de negócio não trivial            | Ao registrar uma distribuição, o sistema verifica se o saldo atual do item é suficiente para a quantidade solicitada — se não for, bloqueia a operação e exibe mensagem de erro; adicionalmente, o saldo é recalculado automaticamente a cada movimentação (entrada de doação soma, saída de distribuição subtrai), sem entrada manual de estoque |
| Consulta agregada (relatório/dashboard) | Dashboard com total de itens em estoque agrupado por categoria (GROUP BY CategoriaItem); relatório de distribuição com JOIN de 4 tabelas (Distribuição ↔ Família ↔ Item ↔ CategoriaItem), filtrável por período e família, exibindo quantidade total distribuída por agrupamento                                                                  |
| Validações em interface e banco         | Interface: campos obrigatórios, quantidade > 0, formato de CPF de doadores, período válido nos filtros. Banco: FK entre todas as entidades relacionadas, NOT NULL em campos essenciais (nome, quantidade, data), UNIQUE em e-mail de usuário e CPF de doador, CHECK de saldo ≥ 0 no item                                                          |
| Deploy público por URL                  | Deploy no Render (Web Service Python + PostgreSQL free tier), acessível por URL pública tipo `https://ong-doacoes.onrender.com`, sem necessidade de instalação local                                                                                                                                                                              |
| Repositório Git com README              | Repositório público no GitHub com README contendo: descrição do projeto, pré-requisitos, passo a passo de instalação local, variáveis de ambiente necessárias (`.env.example`) e link para o deploy — suficiente para um terceiro subir o projeto do zero                                                                                         |

---

## 7. Riscos identificados

| Risco                                                                                        | Impacto                                            | Mitigação                                                                                                                                               |
| -------------------------------------------------------------------------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Escopo crescer com funcionalidades extras de ONG (financeiro, contábil, mobile)              | Alto — atraso nas entregas do semestre             | Usar a seção "Fora de escopo" como critério de corte; qualquer nova funcionalidade passa por aprovação do grupo antes de entrar no backlog              |
| Vulnerabilidades de segurança (SQL Injection, roubo de sessão, vazamento de dados sensíveis) | Médio — dados de famílias e doadores são sensíveis | Usar o ORM do Django (evita SQL Injection nativo), HTTPS no deploy, senhas armazenadas com hash (Django padrão), variáveis de ambiente para credenciais |
| Banco de dados free do Render expira em 90 dias                                              | Médio — perda de dados em produção                 | Recriar o banco antes do vencimento; manter script de seed com dados de teste para repopular rapidamente                                                |
| Rotatividade na equipe ou disponibilidade desigual de membros                                | Médio — acúmulo de tarefas em poucos               | Distribuir responsabilidades por módulo desde a E2; documentar decisões técnicas no README conforme o desenvolvimento avança                            |
| Dificuldade em modelar o controle de estoque com múltiplas categorias e unidades de medida   | Baixo-Médio — inconsistências de dados             | Finalizar e revisar o modelo de entidades na E2 antes de começar a implementação                                                                        |

---
