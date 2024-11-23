import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv
from usuarios import get_db_connection
import os

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

### CRIA AS TABELAS DO BANCO DE DADOS CENTRAL
def init_user_db():
    """Inicializa o banco de dados de usuários, criando a tabela se não existir."""
    try:
        conn = get_db_connection(db_name='wpp_db')
        cursor = conn.cursor(cursor_factory=DictCursor)
        print("Conexão ao banco de dados estabelecida.")

        #sql_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scriptsdb', 'bancogeral.sql')
        # Exemplo de leitura de um arquivo SQL com codificação UTF-8
        sql_file_path = 'scriptsdb/bancogeral.sql'

        # Ler o conteúdo do arquivo SQL
        with open(sql_file_path, 'r') as sql_file:
            sql_script = sql_file.read()
        print("Script SQL banco GERAL lido com sucesso.")

        # Executar o script SQL
        cursor.execute(sql_script)
        print("Script SQL banco GERAL executado com sucesso.")

        conn.commit()
        print("Alterações commitadas com sucesso.")

    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
    finally:
        cursor.close()
        conn.close()
        print("Conexão ao banco de dados fechada.")


###### FUNÇÕES PARA CRIAR BANCO DE DADOS INDIVIDUAIS
def create_user_database(user_id):
    """Cria um banco de dados específico para o usuário."""
    db_name = f'dados_{user_id}'  # Nome do banco de dados baseado no ID do usuário
    create_database(db_name)

def create_database(db_name):
    """Cria um novo banco de dados se ele não existir."""
    conn = get_db_connection()
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    cursor = conn.cursor()
    cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}';")
    exists = cursor.fetchone()

    if not exists:
        cursor.execute(f'CREATE DATABASE {db_name};')
        print(f"Banco de dados '{db_name}' criado com sucesso.")
    else:
        print(f"Banco de dados '{db_name}' já existe.")
    
    cursor.close()
    conn.close()

def create_tables(db_name):
    """Cria as tabelas necessárias no banco de dados do usuário a partir de um script SQL."""
    try:
        conn = get_db_connection(db_name)
        cursor = conn.cursor(cursor_factory=DictCursor)
        print("Conexão ao banco de dados do usuário estabelecida.")

        # Caminho do arquivo SQL
        sql_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scriptsdb', 'bancouser.sql')

        # Ler o conteúdo do arquivo SQL
        with open(sql_file_path, 'r') as sql_file:
            sql_script = sql_file.read()
        print("Script SQ banco DO USUARIO lido com sucesso.")

        # Executar o script SQL
        cursor.execute(sql_script)
        print("Script SQL banco DO USUARIO  executado com sucesso.")

        conn.commit()
        print("Alterações commitadas com sucesso.")

    except Exception as e:
        print(f"Erro ao criar tabelas no banco de dados: {e}")
    finally:
        cursor.close()
        conn.close()
        print("Conexão ao banco de dados fechada.")
