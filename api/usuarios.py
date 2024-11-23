import psycopg2
from psycopg2.extras import DictCursor
import os
from flask import jsonify, session, redirect, url_for
from dotenv import load_dotenv
from functools import wraps

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Verifica login do usuário e se conecta ao devido banco de dados
def verificar_autenticacao(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
          #  return jsonify({'error': 'Usuário não autenticado.'}), 401
        kwargs['user_db_name'] = f'movimentacoes_{user_id}'  # Adiciona o nome do banco aos argumentos
        return f(*args, **kwargs)
    return decorated_function



def get_db_connection(db_name=None):
    """Estabelece uma conexão com o banco de dados de usuários."""  

    if db_name is None:
        db_name = os.environ.get('DB_GERAL')

    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    host = os.getenv('HOST')
    # port = os.getenv('PORT')

    print(f"DB Name: {db_name}, User: {user}, Host: {host}")

    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
            # port=port   
        )
        print("Conexão bem-sucedida!")
        return conn
    except psycopg2.Error as e:
        print(f"ERRO AO SE CONECTAR AO BANCO: {e}")
        return None

def find_user(codigo_acesso):
    """Busca um usuário pelo código de acesso."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    cursor.execute('SELECT * FROM USUARIOS WHERE codigo_acesso = %s', (codigo_acesso,))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    return user

def find_user_by_email(email):
    # Supondo que você tenha uma conexão com o banco de dados e uma tabela 'usuarios'
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    cursor.execute('SELECT * FROM usuarios WHERE email = %s', (email,))
    user = cursor.fetchone()
    conn.close()
    conn.close()
    return user

def user_exists(codigo_acesso):
    """Verifica se o usuário já existe no banco de dados."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    cursor.execute('SELECT COUNT(*) FROM USUARIOS WHERE codigo_acesso = %s', (codigo_acesso,))
    count = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    return count > 0

def create_user(codigo_acesso, senha):
    """Cria um novo usuário no banco de dados."""
    if user_exists(codigo_acesso):
        print(f"Usuário com código de acesso '{codigo_acesso}' já existe.")
        return False

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('INSERT INTO USUARIOS (id_cliente, codigo_acesso, senha) VALUES (1, %s, %s)', (codigo_acesso, senha))
    conn.commit()
    
    cursor.close()
    conn.close()
    print(f"Usuário '{codigo_acesso}' criado com sucesso.")
    return True
