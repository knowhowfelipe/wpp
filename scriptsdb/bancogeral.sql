-- Banco Central

------- 1. CRIAR TABELAS USUARIOS
CREATE TABLE Usuarios (
    id_usuario SERIAL PRIMARY KEY,                   -- Identificador �nico para cada usu�rio
    codigo_acesso INT UNIQUE NOT NULL,               -- C�digo de acesso �nico
    nome VARCHAR(255) NOT NULL,                     -- Nome do usu�rio
    identificador_comercial VARCHAR(255) UNIQUE NOT NULL, -- Identificador comercial �nico
    email VARCHAR(255) UNIQUE NOT NULL,             -- Email �nico do usu�rio
    senha VARCHAR(255) NOT NULL                      -- Senha do usu�rio (deve ser armazenada de forma segura)
);

-- �ndices para a tabela de Usu�rios
CREATE INDEX idx_email ON Usuarios(email);
CREATE INDEX idx_codigo_acesso ON Usuarios(codigo_acesso);

------- 2. CRIAR TABELAS BANCOS
CREATE TABLE Categorias (
    cod_compensacao VARCHAR(255) NOT NULL,                
    nome VARCHAR(255) NOT NULL                    
);

-- Tabela de Clientes
CREATE TABLE Clientes (
    cliente_id SERIAL PRIMARY KEY,                  -- Identificador �nico para cada cliente
    nome VARCHAR(255) NOT NULL,                     -- Nome do cliente
    email VARCHAR(255) UNIQUE NOT NULL,             -- Email do cliente
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Data de cadastro
);

-- �ndices para a tabela de Clientes
CREATE INDEX idx_cliente_nome ON Clientes(nome);
CREATE INDEX idx_cliente_email ON Clientes(email);

-- Tabela Intermedi�ria para rela��o Usu�rios-Clientes
CREATE TABLE Usuario_Cliente (
    id SERIAL PRIMARY KEY,                             -- Identificador �nico para a rela��o
    id_usuario INT REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,  -- Refer�ncia ao Usu�rio
    cliente_id INT REFERENCES Clientes(cliente_id) ON DELETE CASCADE,   -- Refer�ncia ao Cliente
    nivel_permissao VARCHAR(50) NOT NULL,             -- N�vel de permiss�o (ex: 'leitura', 'escrita', 'admin')
    UNIQUE (id_usuario, cliente_id)                   -- Garantir que a combina��o de usu�rio e cliente seja �nica
);

-- �ndice para a tabela de Usu�rio_Cliente
CREATE INDEX idx_usuario_cliente ON Usuario_Cliente(id_usuario, cliente_id);


-- Trigger para auditoria no cadastro de usu�rios
CREATE OR REPLACE FUNCTION auditoria_usuario()
RETURNS TRIGGER AS $$
BEGIN
    RAISE NOTICE 'Usu�rio % criado com o email %', NEW.nome, NEW.email;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_auditoria_usuario
AFTER INSERT ON Usuarios
FOR EACH ROW EXECUTE PROCEDURE auditoria_usuario();
