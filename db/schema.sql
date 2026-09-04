-- ============================================================
-- Conecta Social — Schema DDL
-- PostgreSQL 15+
-- Uso: psql -d conecta_social -f db/schema.sql
-- ============================================================

BEGIN;

-- --------------------------------------------------------
-- Limpeza (ordem reversa de dependências)
-- --------------------------------------------------------
DROP TABLE IF EXISTS distribuicao      CASCADE;
DROP TABLE IF EXISTS doacao            CASCADE;
DROP TABLE IF EXISTS item              CASCADE;
DROP TABLE IF EXISTS unidade_medida    CASCADE;
DROP TABLE IF EXISTS categoria_item    CASCADE;
DROP TABLE IF EXISTS familia           CASCADE;
DROP TABLE IF EXISTS doador            CASCADE;
DROP TABLE IF EXISTS usuario           CASCADE;

-- Sem ENUM nativo: Django armazena perfil como VARCHAR + CHECK, evitando
-- conflito entre o tipo PostgreSQL e as migrations do framework.

-- --------------------------------------------------------
-- Tabelas
-- --------------------------------------------------------

CREATE TABLE usuario (
    id_usuario      SERIAL          PRIMARY KEY,
    nome            VARCHAR(150)    NOT NULL,
    email           VARCHAR(255)    NOT NULL UNIQUE,
    senha_hash      VARCHAR(255)    NOT NULL,
    perfil          VARCHAR(15)     NOT NULL CHECK (perfil IN ('administrador', 'voluntario')),
    ativo           BOOLEAN         NOT NULL DEFAULT TRUE,
    criado_em       TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE TABLE doador (
    id_doador       SERIAL          PRIMARY KEY,
    nome            VARCHAR(150)    NOT NULL,
    cpf_cnpj        VARCHAR(18)     NOT NULL UNIQUE,
    telefone        VARCHAR(20),
    email           VARCHAR(255),
    criado_em       TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE TABLE familia (
    id_familia          SERIAL          PRIMARY KEY,
    nome_responsavel    VARCHAR(150)    NOT NULL,
    endereco            TEXT            NOT NULL,
    telefone            VARCHAR(20),
    num_membros         INTEGER         NOT NULL CHECK (num_membros >= 1),
    criado_em           TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE TABLE categoria_item (
    id_categoria_item   SERIAL          PRIMARY KEY,
    nome                VARCHAR(100)    NOT NULL UNIQUE,
    descricao           TEXT
);

CREATE TABLE unidade_medida (
    id_unidade_medida   SERIAL          PRIMARY KEY,
    nome                VARCHAR(50)     NOT NULL UNIQUE,
    sigla               VARCHAR(10)     NOT NULL UNIQUE
);

CREATE TABLE item (
    id_item             SERIAL          PRIMARY KEY,
    nome                VARCHAR(150)    NOT NULL,
    id_categoria        INTEGER         NOT NULL REFERENCES categoria_item(id_categoria_item),
    id_unidade_medida   INTEGER         NOT NULL REFERENCES unidade_medida(id_unidade_medida),
    estoque_minimo      INTEGER         NOT NULL DEFAULT 0 CHECK (estoque_minimo >= 0),
    criado_em           TIMESTAMP       NOT NULL DEFAULT NOW()
);

-- saldo_atual não é persistido em item (mantém 3FN) — calculado via ORM.

CREATE TABLE doacao (
    id_doacao           SERIAL          PRIMARY KEY,
    id_doador           INTEGER         NOT NULL REFERENCES doador(id_doador),
    id_item             INTEGER         NOT NULL REFERENCES item(id_item),
    id_registrado_por   INTEGER         NOT NULL REFERENCES usuario(id_usuario),
    quantidade          INTEGER         NOT NULL CHECK (quantidade > 0),
    data                DATE            NOT NULL,
    cancelado           BOOLEAN         NOT NULL DEFAULT FALSE,
    criado_em           TIMESTAMP       NOT NULL DEFAULT NOW(),
    cancelado_em        TIMESTAMP,
    id_cancelado_por    INTEGER         REFERENCES usuario(id_usuario)
);

CREATE TABLE distribuicao (
    id_distribuicao     SERIAL          PRIMARY KEY,
    id_familia          INTEGER         NOT NULL REFERENCES familia(id_familia),
    id_item             INTEGER         NOT NULL REFERENCES item(id_item),
    id_registrado_por   INTEGER         NOT NULL REFERENCES usuario(id_usuario),
    quantidade          INTEGER         NOT NULL CHECK (quantidade > 0),
    data                DATE            NOT NULL,
    cancelado           BOOLEAN         NOT NULL DEFAULT FALSE,
    criado_em           TIMESTAMP       NOT NULL DEFAULT NOW(),
    cancelado_em        TIMESTAMP,
    id_cancelado_por    INTEGER         REFERENCES usuario(id_usuario)
);

-- --------------------------------------------------------
-- Índices: adicionei alguns indices para melhorar performance de consultas frequentes pensando em relatórios e buscas.
-- --------------------------------------------------------
CREATE INDEX idx_item_id_unidade       ON item         (id_unidade_medida);
CREATE INDEX idx_doacao_id_item        ON doacao       (id_item);
CREATE INDEX idx_doacao_id_doador      ON doacao       (id_doador);
CREATE INDEX idx_doacao_data           ON doacao       (data);
CREATE INDEX idx_dist_id_item          ON distribuicao (id_item);
CREATE INDEX idx_dist_id_familia       ON distribuicao (id_familia);
CREATE INDEX idx_dist_data             ON distribuicao (data);

-- --------------------------------------------------------
-- Seed: dados de teste
-- --------------------------------------------------------

-- Usuários
INSERT INTO usuario (nome, email, senha_hash, perfil) VALUES
    ('Admin Sistema',    'admin@conectasocial.org', '!alterar_senha', 'administrador'),
    ('Maria Voluntária', 'maria@conectasocial.org', '!alterar_senha', 'voluntario'),
    ('João Voluntário',  'joao@conectasocial.org',  '!salterar_senha', 'voluntario');

-- Categorias
INSERT INTO categoria_item (nome, descricao) VALUES
    ('Alimento', 'Alimentos não perecíveis e secos'),
    ('Higiene',  'Produtos de higiene pessoal'),
    ('Roupa',    'Vestuário e calçados'),
    ('Limpeza',  'Materiais de limpeza doméstica');

-- Unidades de medida
INSERT INTO unidade_medida (nome, sigla) VALUES
    ('Pacote',    'pct'),   -- 1
    ('Garrafa',   'grf'),   -- 2
    ('Unidade',   'uni'),   -- 3
    ('Quilograma','kg'),    -- 4
    ('Litro',     'l'),     -- 5
    ('Metro',     'm');     -- 6

-- Itens (id_categoria, id_unidade_medida)


INSERT INTO item (nome, id_categoria, id_unidade_medida, estoque_minimo) VALUES
    ('Arroz 5kg',          1, 1, 10),  -- Alimento, Pacote
    ('Feijão 1kg',         1, 1, 10),  -- Alimento, Pacote
    ('Óleo de soja 900ml', 1, 2,  5),  -- Alimento, Garrafa
    ('Sabonete',           2, 3, 20),  -- Higiene,  Unidade
    ('Pasta de dente',     2, 3, 15),  -- Higiene,  Unidade
    ('Camiseta adulto',    3, 3,  5),  -- Roupa,    Unidade
    ('Calça jeans',        3, 3,  5),  -- Roupa,    Unidade
    ('Detergente 500ml',   4, 3, 10);  -- Limpeza,  Unidade

-- Doadores
INSERT INTO doador (nome, cpf_cnpj, telefone, email) VALUES
    ('Carlos Mendonça',        '123.456.789-00',      '(11) 99001-1234', 'carlos@email.com'),
    ('Supermercado Bom Preço', '12.345.678/0001-99',  '(11) 3200-5678', 'doacoes@bompreco.com.br'),
    ('Ana Paula Ramos',        '987.654.321-00',      '(11) 97654-3210', NULL);

-- Famílias
INSERT INTO familia (nome_responsavel, endereco, telefone, num_membros) VALUES
    ('Josefa Santos',   'Rua das Flores 45, Bairro Esperança',      '(11) 98765-0001', 4),
    ('Roberto Lima',    'Av. Principal 200, Apto 3, Bairro Centro', '(11) 98765-0002', 6),
    ('Maria das Dores', 'Rua Boa Vista 12, Bairro São Pedro',       NULL,              3);

-- Doações (entradas de estoque)
INSERT INTO doacao (id_doador, id_item, id_registrado_por, quantidade, data) VALUES
    (1, 1, 2, 20, '2026-09-01'),  -- Carlos doa 20 Arroz
    (1, 2, 2, 20, '2026-09-01'),  -- Carlos doa 20 Feijão
    (2, 1, 2, 50, '2026-09-02'),  -- Bom Preço doa 50 Arroz
    (2, 4, 2, 100,'2026-09-02'),  -- Bom Preço doa 100 Sabonete
    (3, 3, 3, 15, '2026-09-03');  -- Ana doa 15 Óleo
    

-- Distribuições (saídas de estoque)
INSERT INTO distribuicao (id_familia, id_item, id_registrado_por, quantidade, data) VALUES
    (1, 1, 2,  5, '2026-09-02'),  -- Josefa recebe 5 Arroz
    (1, 2, 2,  3, '2026-09-02'),  -- Josefa recebe 3 Feijão
    (2, 1, 3,  8, '2026-09-03'),  -- Roberto recebe 8 Arroz
    (3, 4, 3, 10, '2026-09-03');  -- Maria recebe 10 Sabonete

COMMIT;

