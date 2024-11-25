#from __init__ import create_app
from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from flask_login import current_user, login_required
from psycopg2.extras import DictCursor
import secrets
import os
import bcrypt
from dotenv import load_dotenv
import random
from datetime import datetime
import requests
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from api.usuarios import find_user, user_exists, find_user_by_email, verificar_autenticacao, get_db_connection
from api.db import get_db_connection, init_user_db, create_user_database, create_tables
from api.stripe_plans import stripe_plans_bp
from api.models.stripe_model import db, Usuario


# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()
db_user = os.getenv('USER')
db_host = os.getenv('HOST')
db_password = os.getenv('PASSWORD')
#db_port = os.getenv('PORT')
db_name = os.getenv('DB_GERAL')

#app = create_app()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:admin@localhost:5432/wpp_db'
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(stripe_plans_bp)


# Inicializa o banco de dados de usuários
try:
    init_user_db()
    print("Banco de usuários inicializado com sucesso.")
except Exception as e:
    print(f"Erro ao inicializar o banco de usuários: {e}. Prosseguindo com o restante do código...")


@app.route('/')
def index():
#    if 'user_id' in session:
#        return redirect(url_for('form'))  # Redireciona para a página form se estiver autenticado
#    return redirect(url_for('login'))  # Redireciona para a página de login se não estiver autenticado
    #stripe_public_key = os.getenv('STRIPE_PUBLIC_KEY')
    return render_template('form.html')

@app.route('/form')
def form():
    return render_template('form.html')  # Ou a página que deseja renderizar


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        if not email or not senha:
            return jsonify({'mensagem': 'Por favor, preencha todos os campos.'}), 400

        user = find_user_by_email(email)  # Busca pelo e-mail

        if user:
            id_usuario = user['id_usuario']
            hashed_password = user['senha']  # A senha aqui já é a hash
            nome_usuario = user['nome']

            # Verifica se a senha fornecida corresponde à senha armazenada
            if bcrypt.checkpw(senha.encode('utf-8'), hashed_password.encode('utf-8')):
                session['user_id'] = id_usuario
                session['user_name'] = nome_usuario
                create_user_database(id_usuario)  # Cria o banco de dados do usuário
                create_tables(f'dados_{id_usuario}')  # Chama a função para criar a tabela
                user_db_name = f"dados_{id_usuario}"
                return jsonify({'mensagem': 'Login bem-sucedido'}), 200  # Retorna JSON de sucesso
            else:
                return jsonify({'mensagem': 'Senha incorreta.'}), 401
        else:
            return jsonify({'mensagem': 'Usuário não encontrado.'}), 404

    return render_template('login.html')  # Para GET, retorna a página HTML

@app.route('/get-user-id', methods=['GET'])
def get_user_id():
    print(f"Session data: {session}")  # Depurar a sessão
    if 'user_id' in session:
        user = find_user(session['user_id'])  # Supondo que você tenha uma função para buscar o usuário pelo ID
        return jsonify({'user_id': session['user_id'], 'user_name': session.get('user_name')}), 200
    else:
        return jsonify({'error': 'Usuário não está logado.'}), 403

@app.route('/get-user-status', methods=['GET'])
def get_user_status():
    if 'user_id' in session:
        user = find_user(session['user_id'])  # Supondo que você tenha uma função para buscar o usuário pelo ID
        if user:
            return jsonify(is_premium=user.is_premium)
    return jsonify(is_premium=False)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get('name')
        email = request.form.get('email')
        senha = request.form.get('senha')
        repeat_senha = request.form.get('repeat_senha')

        if not nome or not email or not senha or not repeat_senha:
            return jsonify({'error': 'Por favor, preencha todos os campos.'}), 400

        if senha != repeat_senha:
            return jsonify({'error': 'As senhas não coincidem.'}), 400

        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Erro ao se conectar ao banco de dados.'}), 500

        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM USUARIOS WHERE email = %s', (email,))
        if cursor.fetchone()[0] > 0:
            cursor.close()
            conn.close()
            return jsonify({'error': 'O e-mail já está em uso.'}), 400

        codigo_acesso = None

        while True:
            codigo_acesso = random.randint(1, 9999)
            cursor.execute('SELECT COUNT(*) FROM USUARIOS WHERE codigo_acesso = %s', (codigo_acesso,))
            exists = cursor.fetchone()[0]
            if exists == 0:
                break

        hashed_password = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        cursor.execute('INSERT INTO USUARIOS (email, nome, codigo_acesso, senha, identificador_comercial) VALUES (%s, %s, %s, %s, %s)',
                       (email, nome, codigo_acesso, hashed_password, codigo_acesso))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Registrado com sucesso!', 'codigo_acesso': codigo_acesso}), 201

    return render_template('register.html')

@app.route('/politica-de-devolucoes')
def politica_de_devolucoes():
    return render_template('politica-de-devolucoes.html')

@app.route('/politica-de-reembolsos')
def politica_de_reembolsos():
    return render_template('politica-de-reembolsos.html')

@app.route('/politica-de-cancelamento')
def politica_de_cancelamento():
    return render_template('politica-de-cancelamento.html')

@app.route('/termos-e-condicoes')
def termos_e_condicoes():
    return render_template('termos-e-condicoes.html')

if __name__ == '__main__':
    app.run(debug=True)
