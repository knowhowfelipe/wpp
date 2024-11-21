------- 0. CRIAR TABELAS USUARIOS INTERNOS

CREATE TABLE USUARIOS_INTERNOS (
    ID_user_interno SERIAL PRIMARY KEY,  -- Identificador único do usuário interno, auto-incrementado
    rotulo_user VARCHAR(20) NOT NULL,   -- Rótulo ou nome do usuário
    data_acesso TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Data e hora do acesso, com valor padrão como a data e hora atual
);


------- 1. CRIAR TABELAS CATEGORIAS
CREATE TABLE Categorias (
    categoria_id SERIAL PRIMARY KEY,                 -- Identificador único para cada categoria
    grupo VARCHAR(255) NOT NULL,                    --Receita, Impostos, Custos, Despesas, Investimento
    descricao VARCHAR(255) NOT NULL,                  -- Grupo da categoria (ex: Receita de Vendas)
	cod_reduzido INTEGER,
	 
);

------- 2. CRIAR TABELAS PESSOAS
CREATE TABLE Pessoas (
    pessoa_id SERIAL PRIMARY KEY,        -- Identificador único da pessoa
    nome VARCHAR(255) NOT NULL,          -- Nome da pessoa (fornecedor, cliente, etc.)
    identificador VARCHAR(255) NOT NULL, -- Identificador (ex: CPF/CNPJ ou outro documento)
    tipo_pessoa CHAR(1) CHECK (tipo_pessoa IN ('F', 'J')) NOT NULL,  -- F = Física, J = Jurídica
	relacao CHAR(1) CHECK (tipo_pessoa IN ('F', 'C', 'T', 'P', 'O')) -- F = Fornecedor, C = Cliente, T = Transportador, P = Parceiro, O = Outros
);

CREATE TABLE ITENS (
    item_id SERIAL PRIMARY KEY,        -- Identificador único da pessoa
	tipo CHAR(1) CHECK (tipo IN ('C', 'D')) NOT NULL, -- Se é uma entrada então é C; saída = D
    rotulo VARCHAR(20) NOT NULL, -- algum codigo ou identificação
	descricao_pag VARCHAR(255), -- descrição detalhada
    categoria_id INT NOT NULL, -- FK da coluna categoria_id da tabela CATEGORIAS
	recorrencia BOOLEAN, -- Se é uma compra com recorrencia (sem data fim prevista) ou não
	valor_padrao DECIMAL(15, 2) NOT NULL, -- valor padrão
	FOREIGN KEY (categoria_id) REFERENCES CATEGORIAS(categoria_id) ON DELETE CASCADE
);

------- 3. CRIAR TABELAS CONTAS BANCARIAS
CREATE TABLE contas_bancarias (
    conta_bancaria_id SERIAL PRIMARY KEY,
	banco_cod_comp VARCHAR(15) NOT NULL,
    numero_conta VARCHAR(50) UNIQUE NOT NULL,
	agencia VARCHAR(10) NOT NULL,
    data_abertura DATE,
    tipo_conta VARCHAR(50) NOT NULL,
	descricao_banco VARCHAR(50) NOT NULL,
    status BOOLEAN DEFAULT TRUE,
	data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Inserir um registro padrão na tabela contas_bancarias
INSERT INTO contas_bancarias (banco_cod_comp, numero_conta, agencia, tipo_conta, status)
VALUES ('999', '999', '999', 'meu_caixa', TRUE);

------- 3.2 CRIAR TABELAS DE SALDOS CONTAS BANCARIAS
CREATE TABLE contas_bancarias_saldos (
    saldo_id SERIAL PRIMARY KEY,
    conta_bancaria_id INT REFERENCES contas_bancarias(conta_bancaria_id),
    data_saldo DATE NOT NULL,
    saldo NUMERIC(15, 2) NOT NULL,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


------- 3. CRIAR TABELAS CENTRO DE CUSTOS
CREATE TABLE CENTRO_CUSTOS (
    ccustos_id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL,
    descricao VARCHAR NOT NULL,
    ativo BOOLEAN DEFAULT TRUE
);



CREATE TABLE extratos (
    extrato_id SERIAL PRIMARY KEY,
    conta_bancaria_id INT NOT NULL,
    data_ext DATE NOT NULL,
    valor DECIMAL(15, 2) NOT NULL,
    historico_bc VARCHAR(255) NOT NULL,
    ent_sai CHAR(1) CHECK (ent_sai IN ('C', 'D')) NOT NULL,
    codigo_transacao VARCHAR(255) NOT NULL,
	conciliado BOOLEAN DEFAULT FALSE,
	data_saldo_ini DATE,
	saldo_inicial DECIMAL(15, 2),
    FOREIGN KEY (conta_bancaria_id) REFERENCES contas_bancarias(conta_bancaria_id)
);

               
------- 5. CRIAR TABELAS MOVIMENTACOES
CREATE TABLE movimentacoes (
    id SERIAL PRIMARY KEY,
    tipo_movimentacao CHAR(1) CHECK (tipo_movimentacao IN ('C', 'D')) NOT NULL,
    data_fato DATE,  -- data que ocorreu o fato
    historico VARCHAR(255), -- observações
    tipo_doc VARCHAR(50),          -- tipo de documento (nota fiscal, fatura, boleto etc)
    doc VARCHAR(50),               -- codigo ou numero que identifica o documento
    recor_id INT,                  -- O id da conta de recorrência
    pessoa_id INT,                 -- Relacionamento opcional com a tabela Pessoas
    categoria_id INT,              -- Relacionamento opcional com a tabela Categorias
    valor_fato DECIMAL(15, 2) NOT NULL,
	ccustos_id INT, -- O id do centro de custo
    conciliada BOOLEAN DEFAULT FALSE,  -- se já foi conciliada
    tags_sugeridas TEXT[],         -- para tags de IA
    saldo_apos_pagamentos DECIMAL(15, 2) DEFAULT 0.0, -- Corrigido para adicionar vírgula
    origem_mov VARCHAR(50),         -- origem da movimentação

    CONSTRAINT fk_pessoa
        FOREIGN KEY (pessoa_id)
        REFERENCES Pessoas(pessoa_id)
        ON DELETE SET NULL,                         -- Se a pessoa for deletada, o campo é setado para NULL
    CONSTRAINT fk_categoria
        FOREIGN KEY (categoria_id)
        REFERENCES Categorias(categoria_id)
        ON DELETE SET NULL,                          -- Se a categoria for deletada, o campo é setado para NULL
    CONSTRAINT fk_recorrencia
        FOREIGN KEY (recor_id)                     -- FK para movi_recorrencias
        REFERENCES movi_recorrencias(recorrencia_id) 
        ON DELETE SET NULL,                          -- Se a recorrência for deletada, as movimentações associadas também são deletadas
    CONSTRAINT fk_ccusto
        FOREIGN KEY (ccusto_id)                     -- FK para movi_recorrencias
        REFERENCES centro_custos(ccusto_id) 
        ON DELETE SET NULL,  
);

	---- infos do fluxo financeiro
CREATE TABLE pagamentos (
    pagto_id SERIAL PRIMARY KEY,
	parcela INT,  
	data_vencimento DATE NOT NULL,            -- prazo de pagamento (data de vencimento)
	valor_parcela DECIMAL(15, 2) NOT NULL,
    historico_pagto VARCHAR(255),
    valor_pagto DECIMAL(15, 2) NOT NULL,
	juros DECIMAL(15, 2) DEFAULT 0.0;
	multa DECIMAL(15, 2) DEFAULT 0.0;
	desconto DECIMAL(15, 2) DEFAULT 0.0;
	modal_pagto VARCHAR(255) NOT NULL,
    data_pagto DATE NOT NULL,         -- data que entrou/saiu o dinheiro
    chave_transacao VARCHAR(255),  -- número ou chave do documento
    origem VARCHAR(50),                    -- se veio do extrato, lançado manualmente etc.
    mov_id INT,                             -- FK para a movimentação associada
	conta_bancaria_id INT NOT NULL,                 -- ID da conta bancária associada
	saldo_parcela DECIMAL(15, 2) DEFAULT 0.0;
	pago BOOLEAN DEFAULT FALSE
    data_atualizacao TIMESTAMP DEFAULT NOW(),  -- data de atualização
    CONSTRAINT fk_movimentacao FOREIGN KEY (mov_id) REFERENCES movimentacoes(id),
    CONSTRAINT fk_conta_bancaria FOREIGN KEY (conta_bancaria_id) REFERENCES contas_bancarias(conta_bancaria_id) -- Relacionamento com a tabela de contas bancárias
);

----- Função e trigger para calcular o saldo a quitar da MOVIMENTAÇÃO
CREATE OR REPLACE FUNCTION atualizar_saldo_apos_pagamento()
RETURNS TRIGGER AS $$
BEGIN
    -- Atualiza o saldo após pagamento
    UPDATE movimentacoes
    SET saldo_apos_pagamentos = valor_fato - (
        SELECT SUM(valor_pagto)
        FROM pagamentos
        WHERE mov_id = NEW.mov_id
    )
    WHERE id = NEW.mov_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

---- trigger
CREATE TRIGGER trigger_atualizar_saldo
AFTER INSERT OR UPDATE ON pagamentos
FOR EACH ROW
EXECUTE PROCEDURE atualizar_saldo_apos_pagamento();


----- Função e trigger para calcular o saldo a quitar da PARCELA
CREATE OR REPLACE FUNCTION atualizar_saldo_parcela()
RETURNS TRIGGER AS $$
BEGIN
    -- Atualizar o saldo da parcela diretamente com o valor da parcela menos o valor do pagamento
    NEW.saldo_parcela := NEW.valor_parcela - NEW.valor_pagto;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

--- trigger
CREATE TRIGGER trigger_atualizar_saldo_parcela
BEFORE INSERT OR UPDATE ON pagamentos
FOR EACH ROW
EXECUTE FUNCTION atualizar_saldo_parcela();


----- Função e trigger para marcar como PAGO a parcela
CREATE OR REPLACE FUNCTION atualizar_status_pagamento()
RETURNS TRIGGER AS $$
DECLARE
    total_pagto DECIMAL(15, 2);
BEGIN
    -- Calcular o total de pagamentos para a parcela
    SELECT COALESCE(SUM(valor_pagto), 0) INTO total_pagto
    FROM pagamentos
    WHERE pagto_id = NEW.pagto_id;  -- Usar pagto_id para a soma dos pagamentos

    -- Atualizar o saldo da parcela
    NEW.saldo_parcela := NEW.valor_parcela - total_pagto;

    -- Atualizar o status de pagamento
    IF NEW.saldo_parcela <= 0 THEN
        NEW.pago := TRUE;  -- Marca como pago se saldo for 0 ou negativo
    ELSE
        NEW.pago := FALSE;  -- Caso contrário, não está pago
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

---- trigger
CREATE TRIGGER trigger_atualizar_status_pagamento
BEFORE INSERT OR UPDATE ON pagamentos
FOR EACH ROW
EXECUTE PROCEDURE atualizar_status_pagamento();


-- Índices para otimizar consultas
CREATE INDEX idx_data ON Movimentacoes(data);
CREATE INDEX idx_valor ON Movimentacoes(valor);
CREATE INDEX idx_conciliada ON Movimentacoes(conciliada);

-- Trigger para atualizar saldo após a inserção de uma nova movimentação
CREATE OR REPLACE FUNCTION atualizar_saldo()
RETURNS TRIGGER AS $$
DECLARE
    saldo_anterior DECIMAL(15, 2);
BEGIN
    -- Recupera o saldo da última movimentação
    SELECT saldo_apos_movimentacao INTO saldo_anterior
    FROM Movimentacoes
    WHERE data <= NEW.data
    ORDER BY data DESC, id DESC
    LIMIT 1;

    -- Atualiza o saldo da nova movimentação com base no saldo anterior
    IF saldo_anterior IS NULL THEN
        NEW.saldo_apos_movimentacao := NEW.valor;  -- Primeira movimentação
    ELSE
        NEW.saldo_apos_movimentacao := saldo_anterior + NEW.valor;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Criação da trigger
CREATE TRIGGER trigger_atualizar_saldo
BEFORE INSERT ON Movimentacoes
FOR EACH ROW
EXECUTE FUNCTION atualizar_saldo();


------- 6. CRIAR TABELAS MOV_FUTURO
CREATE TABLE movi_recorrencias (
    recorrencia_id SERIAL PRIMARY KEY,  -- Nome mais claro
    item_id INT NOT NULL,  -- FK para ITENS
    pessoa_id INT,  -- FK para PESSOAS
    data_primeiro_pagamento DATE NOT NULL,  -- Primeira data de pagamento
    data_ultimo_pagamento DATE,  -- Permite NULL para recorrências ativas
    valor DECIMAL(15, 2) NOT NULL,  -- Valor da parcela ou assinatura
    dia_vencimento INTEGER NOT NULL,  -- Dia do vencimento
    dia_lanca_mov INTEGER,  -- E gerar o movimento
    periodicidade INTEGER NOT NULL CHECK (periodicidade IN (1, 3, 6, 9)),  -- 1 = mensal, 3 = trimestral, 6 = semestral, 9 = anual
    ativo BOOLEAN DEFAULT TRUE,  -- Indica se está ativo
	tipo_doc VARCHAR(50),
	obs  VARCHAR(255),
	data_ativacao_cli DATE,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Data de atualização automática
    FOREIGN KEY (item_id) REFERENCES itens(item_id) ON DELETE CASCADE,  -- FK para ITENS
    FOREIGN KEY (pessoa_id) REFERENCES pessoas(pessoa_id) ON DELETE SET NULL  -- FK para PESSOAS
);

---------- Função e trigger para inserir recorrencia na movimentação
CREATE OR REPLACE FUNCTION inserir_movimentacoes_recorrentes()
RETURNS TRIGGER AS $$
DECLARE
    mov_futuro_registro RECORD;
    monta_data_fato DATE;
    monta_data_vencimento DATE;  -- Adicionada declaração
    origem TEXT := 'recorrencia';  -- Corrigida atribuição
    new_mov_id INTEGER;  -- Declarando a variável para armazenar o ID da nova movimentação

BEGIN
    -- Determina o dia atual
    FOR mov_futuro_registro IN
        SELECT * FROM movi_recorrencias mr LEFT JOIN ITENS I ON mr.item_id = I.item_id
        WHERE mr.ativo = TRUE
          AND mr.dia_lanca_mov = EXTRACT(DAY FROM CURRENT_DATE)
    LOOP
        -- Define o data_fato com o mês e ano atuais
		monta_data_fato := DATE_TRUNC('MONTH', CURRENT_DATE) + (mov_futuro_registro.dia_lanca_mov - 1) * INTERVAL '1 day';
		monta_data_vencimento := DATE_TRUNC('MONTH', CURRENT_DATE) + (mov_futuro_registro.dia_vencimento - 1) * INTERVAL '1 day';

        -- Verifica se já existe uma movimentação com o mesmo recor_id e data_fato
        IF NOT EXISTS (
            SELECT 1 FROM movimentacoes
            WHERE recor_id = mov_futuro_registro.recorrencia_id
              AND data_fato = monta_data_fato
        ) THEN
            -- Insere o novo registro em movimentacoes
            INSERT INTO movimentacoes (
                recor_id,
                tipo_movimentacao,
                historico,
                categoria_id,
                pessoa_id,
                valor_fato,
                data_fato,
				origem_mov
            ) VALUES (
                mov_futuro_registro.recorrencia_id,
                mov_futuro_registro.tipo,
                COALESCE(mov_futuro_registro.rotulo, mov_futuro_registro.descricao_pag),  -- Escolhe entre rotulo e descricao_pag
                mov_futuro_registro.categoria_id,
                mov_futuro_registro.pessoa_id,
                mov_futuro_registro.valor,
                monta_data_fato,
				origem
            )
			RETURNING id INTO new_mov_id;  -- Captura o id da nova movimentação
			
			INSERT INTO PAGAMENTOS (
			mov_id,
			data_vencimento,
			origem,
			valor_parcela
			)
			VALUES (
			new_mov_id,
			monta_data_vencimento,
			origem,
			mov_futuro_registro.valor
			);	
        END IF;
    END LOOP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

----- TRIGGER
CREATE TRIGGER trigger_inserir_movimentacoes_recorrentes
AFTER UPDATE OF data_acesso ON usuarios_internos
FOR EACH ROW
WHEN (OLD.data_acesso IS DISTINCT FROM NEW.data_acesso)
EXECUTE FUNCTION inserir_movimentacoes_recorrentes();

