# Diagramas UML — Conecta Social

**Equipe:**
- Alexandre Victoriano Ribeiro Ulhoa — RA 2840482423007
- Daniel Souza Monteiro de Carvalho — RA 2840482211052
- Cintia Marcelo de Oliveira — RA 2840482421017
- Antonio Pires Felipe — RA 2840482211003
- Luiz Henrique Neres — RA 2840482423005

**Entrega:** E3 — Modelagem de Dados e UML  
**Semestre:** 2026/2

---

## 1. Diagrama de Casos de Uso

O sistema possui dois perfis de ator. O **Voluntário** executa os fluxos operacionais, enquanto o **Administrador** executa operações exclusivas de gestão. O cancelamento é um fluxo opcional que estende o registro de uma doação ou distribuição.

### Voluntário


```mermaid
flowchart LR
  Voluntario((Voluntario))

  subgraph auth["Autenticação"]
    UC1[Fazer login]
    UC2[Fazer logout]
  end

  subgraph cad["Cadastros"]
    UC5[Cadastrar doador]
    UC6[Listar/buscar doadores]
    UC8[Cadastrar família]
    UC9[Listar/buscar famílias]
    UC12[Visualizar saldo de itens]
  end

  subgraph mov["Movimentações"]
    UC14[Registrar doação]
    UC15[Histórico de doações]
    UC16[Registrar distribuição]
    UC17[Ver saldo no formulário]
    UC18[Histórico de distribuições]
  end

  subgraph rel["Relatórios"]
    UC20[Painel de estoque]
    UC21[Relatório de distribuições]
    UC22[Histórico por doador]
    UC23[Exportar CSV]
  end

  Voluntario --> UC1 & UC2
  Voluntario --> UC5 & UC6 & UC8 & UC9 & UC12
  Voluntario --> UC14 & UC15 & UC16 & UC17 & UC18
  Voluntario --> UC20 & UC21 & UC22 & UC23
```

### Administrador

```mermaid
flowchart LR
  Administrador((Administrador))

  subgraph excl["Exclusivos do Administrador"]
    UC3[Cadastrar usuário]
    UC4[Desativar usuário]
    UC7[Editar dados de doador]
    UC10[Cadastrar categoria]
    UC11[Cadastrar item]
    UC13[Editar item]
    UC19[Cancelar movimentação]
  end

  subgraph mov["Casos de uso base"]
    UC14[Registrar doação]
    UC16[Registrar distribuição]
  end

  Administrador --> UC3 & UC4
  Administrador --> UC7 & UC10 & UC11 & UC13
  Administrador --> UC19
  UC19 -. "<<extend>>" .-> UC14
  UC19 -. "<<extend>>" .-> UC16
```

---

## 2. Diagrama de Classes

```mermaid
classDiagram
  class Usuario {
    +id_usuario: int
    +nome: string
    +email: string
    +senha_hash: string
    +perfil: string
    +ativo: bool
    +criado_em: datetime
    +autenticar() bool
    +desativar() void
  }

  class Doador {
    +id_doador: int
    +nome: string
    +cpf_cnpj: string
    +telefone: string
    +email: string
    +criado_em: datetime
  }

  class Familia {
    +id_familia: int
    +nome_responsavel: string
    +endereco: string
    +telefone: string
    +num_membros: int
    +criado_em: datetime
  }

  class CategoriaItem {
    +id_categoria_item: int
    +nome: string
    +descricao: string
  }

  class UnidadeMedida {
    +id_unidade_medida: int
    +nome: string
    +sigla: string
  }

  class Item {
    +id_item: int
    +nome: string
    +estoque_minimo: int
    +criado_em: datetime
    +getSaldoAtual() int
  }

  class Doacao {
    +id_doacao: int
    +quantidade: int
    +data: date
    +cancelado: bool
    +criado_em: datetime
    +cancelar() void
  }

  class Distribuicao {
    +id_distribuicao: int
    +quantidade: int
    +data: date
    +cancelado: bool
    +criado_em: datetime
    +cancelar() void
    +validarSaldo() bool
  }

  Usuario "1" --> "0..*" Doacao : registra
  Usuario "1" --> "0..*" Distribuicao : registra
  Doador "1" --> "0..*" Doacao : realiza
  Familia "1" --> "0..*" Distribuicao : recebe
  CategoriaItem "1" --> "0..*" Item : classifica
  UnidadeMedida "1" --> "0..*" Item : define unidade
  Item "1" --> "0..*" Doacao : entra via
  Item "1" --> "0..*" Distribuicao : sai via
```

---

## 3. Rastreabilidade — caso de uso → história do backlog

| Caso de uso | História(s) relacionada(s) (E2) |
|---|---|
| Fazer login | #1 |
| Fazer logout | #2 |
| Cadastrar usuário | #3 |
| Desativar usuário | #4 |
| Cadastrar doador | #5 |
| Listar/buscar doadores | #6 |
| Editar dados de doador | #7 |
| Cadastrar família | #8 |
| Listar/buscar famílias | #9 |
| Cadastrar categoria | #10 |
| Cadastrar item | #11 |
| Visualizar saldo de itens | #12 |
| Editar item | #13 |
| Registrar doação | #14 |
| Histórico de doações | #15 |
| Registrar distribuição | #16 |
| Ver saldo no formulário de distribuição | #17 |
| Histórico de distribuições | #18 |
| Cancelar movimentação | #19 |
| Painel de estoque por categoria | #20 |
| Relatório de distribuições | #21 |
| Histórico de doações por doador | #22 |
| Exportar relatório em CSV | #23 |

### Classes × Histórias do backlog

| Classe | Histórias relacionadas |
|---|---|
| `Usuario` | #1, #2, #3, #4 |
| `Doador` | #5, #6, #7, #14, #15, #22 |
| `Familia` | #8, #9, #16, #18, #21, #23 |
| `CategoriaItem` | #10, #11, #12, #20 |
| `UnidadeMedida` | #11, #12, #13 |
| `Item` | #11, #12, #13, #14, #15, #16, #17, #18, #20, #21, #22, #23 |
| `Doacao` | #14, #15, #19, #22 |
| `Distribuicao` | #16, #17, #18, #19, #21, #23 |
