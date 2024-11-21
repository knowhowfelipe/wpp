from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from psycopg2.extras import DictCursor
import secrets
import os
import bcrypt
from usuarios import find_user, user_exists, find_user_by_email, verificar_autenticacao, get_db_connection
from db import get_db_connection, init_user_db, create_user_database, create_tables
from dotenv import load_dotenv
import random
from datetime import datetime



# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))
#app.register_blueprint(categorias_bp)

def atualiza_data_acesso(user_db_name):
    conn = get_db_connection(user_db_name)
    cursor = cursor = conn.cursor()
    cursor.execute("""
            UPDATE USUARIOS_INTERNOS
            SET data_acesso = %s
            WHERE ID_user_interno = 1;
        """, (datetime.now(),))
    conn.commit()
    conn.close()

# Inicializa o banco de dados de usuários
try:
    init_user_db()
    print("Banco de usuários inicializado com sucesso.")
except Exception as e:
    print(f"Erro ao inicializar o banco de usuários: {e}. Prosseguindo com o restante do código...")


@app.route('/')
def index():
#    if 'user_id' in session:
#        return redirect(url_for('home'))  # Redireciona para a página home se estiver autenticado
#    return redirect(url_for('login'))  # Redireciona para a página de login se não estiver autenticado
    return render_template('index.html')

@app.route('/home')
def home():
    if 'user_id' in session:
        return render_template('home.html')  # Ou a página que deseja renderizar
    return redirect(url_for('login'))  # Redireciona para a página de login se não estiver autenticado


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_method = request.form.get('loginMethod')  # Captura o método de login
        senha = request.form.get('senha')

        if not login_method or not senha:
            return jsonify({'mensagem': 'Por favor, preencha todos os campos.'}), 400

        if login_method == 'accessCode':
            codigo_acesso = request.form.get('codigo_acesso')
            user = find_user(codigo_acesso)  # Busca pelo código de acesso
        elif login_method == 'email':
            email = request.form.get('email')
            user = find_user_by_email(email)  # Busca pelo e-mail

        if user:
            id_usuario = user['id_usuario']
            hashed_password = user['senha']  # A senha aqui já é a hash

            # Verifica se a senha fornecida corresponde à senha armazenada
            if bcrypt.checkpw(senha.encode('utf-8'), hashed_password.encode('utf-8')):
                session['user_id'] = id_usuario
                create_user_database(id_usuario)  # Cria o banco de dados do usuário
                create_tables(f'movimentacoes_{id_usuario}')  # Chama a função para criar a tabela
                user_db_name = f"movimentacoes_{id_usuario}"
                atualiza_data_acesso(user_db_name)
                return jsonify({'mensagem': 'Login bem-sucedido'}), 200  # Retorna JSON de sucesso
            else:
                return jsonify({'mensagem': 'Senha incorreta.'}), 401
        else:
            return jsonify({'mensagem': 'Usuário não encontrado.'}), 404

    return render_template('login.html')  # Para GET, retorna a página HTML



@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['POST'])
def register():
    nome = request.form.get('name')
    email = request.form.get('email')
    #identificador_comercial = request.form.get('identificador_comercial')
    senha = request.form.get('senha')
    repeat_senha = request.form.get('repeat_senha')

    if not nome or not email or not senha or not repeat_senha:
        return jsonify({'error': 'Por favor, preencha todos os campos.'}), 400

    # Verifica se as senhas coincidem no backend também
    if senha != repeat_senha:
        return jsonify({'error': 'As senhas não coincidem.'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Validação 1: Verificar se o e-mail já existe
    cursor.execute('SELECT COUNT(*) FROM USUARIOS WHERE email = %s', (email,))
    if cursor.fetchone()[0] > 0:
        return jsonify({'error': 'O e-mail já está em uso.'}), 400

    # Gerar código de acesso único
    codigo_acesso = None


    while True:
        codigo_acesso = random.randint(1, 9999)
        cursor.execute('SELECT COUNT(*) FROM USUARIOS WHERE codigo_acesso = %s', (codigo_acesso,))
        exists = cursor.fetchone()[0]
        if exists == 0:  # O código de acesso é único
            break

    # Criptografar a senha
    #hashed_password = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
    hashed_password = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')  # Converte para string

    # Inserir no banco de dados
    cursor.execute('INSERT INTO USUARIOS (email, nome, codigo_acesso, senha, identificador_comercial) VALUES (%s, %s, %s, %s, %s)',
                   (email, nome, codigo_acesso, hashed_password, codigo_acesso))
    conn.commit()
    cursor.close()
    conn.close()

    # Retorna uma resposta de sucesso em formato JSON para ser exibida no frontend
    return jsonify({'message': 'Registrado com sucesso!', 'codigo_acesso': codigo_acesso}), 201


if __name__ == '__main__':
    app.run(debug=True)
