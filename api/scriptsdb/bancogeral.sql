-- Banco Central

------- 1. CRIAR TABELAS USUARIOS
CREATE TABLE Usuarios (
    id_usuario SERIAL PRIMARY KEY,                   -- Identificador único para cada usuário
    codigo_acesso INT UNIQUE NOT NULL,               -- Código de acesso único
    nome VARCHAR(255) NOT NULL,                      -- Nome do usuário
    identificador_comercial VARCHAR(255) UNIQUE NOT NULL, -- Identificador comercial único
    email VARCHAR(255) UNIQUE NOT NULL,              -- Email único do usuário
    senha VARCHAR(255) NOT NULL,                     -- Senha do usuário (deve ser armazenada de forma segura)
    is_premium BOOLEAN DEFAULT FALSE,
    subscription_start_date DATE,
    subscription_end_date DATE,
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255)
);

-- Índices para a tabela de Usuários
CREATE INDEX idx_email ON Usuarios(email);
CREATE INDEX idx_codigo_acesso ON Usuarios(codigo_acesso);

-- Inserir dados na tabela Usuários
INSERT INTO Usuarios (codigo_acesso, nome, identificador_comercial, email, senha)
VALUES (999, 'Teste', '00000', 'teste9@gmail.com', '$2b$12$nWUp63PwH40zXMAWiulc.eOjH9J9EMlGJ220tglhwraSaQsDKjpOW');

-- Tabela de Clientes
CREATE TABLE Clientes (
    cliente_id SERIAL PRIMARY KEY,                  -- Identificador único para cada cliente
    nome VARCHAR(255) NOT NULL,                     -- Nome do cliente
    email VARCHAR(255) UNIQUE NOT NULL,             -- Email do cliente
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Data de cadastro
);

-- Índices para a tabela de Clientes
CREATE INDEX idx_cliente_nome ON Clientes(nome);
CREATE INDEX idx_cliente_email ON Clientes(email);

-- Tabela Intermediária para relação Usuários-Clientes
CREATE TABLE Usuario_Cliente (
    id SERIAL PRIMARY KEY,                             -- Identificador único para a relação
    id_usuario INT REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,  -- Referência ao Usuário
    cliente_id INT REFERENCES Clientes(cliente_id) ON DELETE CASCADE,   -- Referência ao Cliente
    nivel_permissao VARCHAR(50) NOT NULL,             -- Nível de permissão (ex: 'leitura', 'escrita', 'admin')
    UNIQUE (id_usuario, cliente_id)                   -- Garantir que a combinação de usuário e cliente seja única
);

-- Índice para a tabela de Usuário_Cliente
CREATE INDEX idx_usuario_cliente ON Usuario_Cliente(id_usuario, cliente_id);

-- Trigger para auditoria no cadastro de usuários
CREATE OR REPLACE FUNCTION auditoria_usuario()
RETURNS TRIGGER AS $$
BEGIN
    RAISE NOTICE 'Usuário % criado com o email %', NEW.nome, NEW.email;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_auditoria_usuario
AFTER INSERT ON Usuarios
FOR EACH ROW EXECUTE PROCEDURE auditoria_usuario();
