# ID PREÇO: price_1QO4d6ClJp9dPNzNwWRwSWPs
# ID PRODUTO: prod_RGbqXVhS1rJ7tz
# chave secreta privada: sk_test_51QO4bDClJp9dPNzNNXexw8suWr8QJm9qGqD4OatMp1MkxzlQcJwnbkXUOx5Z2TrRbew7LtLbEuKL0k3etPrBxlFL007TNSN80l
# chave publica: pk_test_51QO4bDClJp9dPNzNZume9C1l88aNt7gNY2lDe5vH8Zl1j341TVJrD1grpmo9fh59qZERsxdKXOaUqsCj5GXovSwo00TPcyhrCM

# Visa: 4242 4242 4242 4242
# Mastercard: 5555 5555 5555 4444
# Falha de pagamento: 4000 0000 0000 9995
# Use qualquer data de validade futura e qualquer CVC (por exemplo, 123).

import os
from flask import Blueprint, Flask, render_template, jsonify, request, redirect
import stripe
import logging
from datetime import datetime
from api.auth import db, User
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

stripe_plans_bp = Blueprint('stripe_plans', __name__)
db = SQLAlchemy()

# Crie o aplicativo Flask
app = Flask(__name__)

# Configure sua chave secreta Stripe
stripe.api_key = "sk_test_51QO4bDClJp9dPNzNNXexw8suWr8QJm9qGqD4OatMp1MkxzlQcJwnbkXUOx5Z2TrRbew7LtLbEuKL0k3etPrBxlFL007TNSN80l"

# Configuração de logging
logging.basicConfig(level=logging.INFO)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sua_uri_do_banco_de_dados_aqui'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@stripe_plans_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    id_usuario = request.json.get('id_usuario')
    logging.info(f"id_usuario recebido: {id_usuario}")

    success_url = request.host_url + 'success'
    cancel_url = request.host_url + 'cancel'

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': 'price_1QO4d6ClJp9dPNzNwWRwSWPs',  # Substitua pelo ID do preço do produto criado no Stripe
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=id_usuario
        )
        logging.info(f"Sessão de checkout criada: {checkout_session.id}")
        return jsonify({
            'id': checkout_session.id
        })
    except Exception as e:
        logging.error(f"Erro ao criar sessão de checkout: {e}")
        return jsonify(error=str(e)), 403

@stripe_plans_bp.route('/success')
def success():
    return "Pagamento bem-sucedido!"

@stripe_plans_bp.route('/cancel')
def cancel():
    return "Pagamento cancelado."

@stripe_plans_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = 'whsec_FOlf7C7LfKLW86FpeJHozBJYbPUw43EQ'

    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        logging.error(f"Erro no payload: {e}")
        return jsonify(success=False), 400
    except stripe.error.SignatureVerificationError as e:
        logging.error(f"Erro na verificação da assinatura: {e}")
        return jsonify(success=False), 400

    if event['type'] == 'checkout.session.completed':
        print("CHECKOUT COMPLETO")
        session = event['data']['object']
        print(session)
        user_id = session['client_reference_id']
        stripe_subscription_id = session['subscription']
        print(stripe_subscription_id)
        stripe_customer_id = session['customer']
        print(stripe_customer_id)
        logging.info(f"Evento recebido para user_id: {user_id}, subscription_id: {stripe_subscription_id}, customer_id: {stripe_customer_id}")
        update_user_to_premium(user_id, stripe_subscription_id, stripe_customer_id)

    return jsonify(success=True), 200

def update_user_to_premium(user_id, stripe_subscription_id, stripe_customer_id):
    try:
        # Definir o SQL de atualização diretamente e declarar como texto
        sql = text("""
        UPDATE public."Usuarios" 
        SET is_premium = true,
            subscription_start_date = NOW(),
            stripe_subscription_id = :subscription_id,
            stripe_customer_id = :customer_id
        WHERE id_usuario = :user_id
        """)
        # Executar a consulta com os parâmetros
        db.session.execute(sql, {
            'subscription_id': stripe_subscription_id,
            'customer_id': stripe_customer_id,
            'user_id': user_id
        })
        db.session.commit()
        print(f"Usuário {user_id} atualizado para premium")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Erro ao atualizar usuário: {e}")

# Finalmente, registrar o blueprint
app.register_blueprint(stripe_plans_bp)
