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
from dotenv import load_dotenv
import stripe
import logging
from datetime import datetime
from api.models.stripe_model import db, Usuario

stripe_plans_bp = Blueprint('stripe_plans', __name__)

load_dotenv()
stripe_api_key = os.getenv('STRIPE_SECRET_KEY')
stripe_public_key = os.getenv('STRIPE_PUBLIC_KEY')

webhook_id_checkout = 'we_1QP6ThK91woPpT0pPoRwTOwr'

# Configure sua chave secreta Stripe
# stripe.api_key = "sk_test_51QO4bDClJp9dPNzNNXexw8suWr8QJm9qGqD4OatMp1MkxzlQcJwnbkXUOx5Z2TrRbew7LtLbEuKL0k3etPrBxlFL007TNSN80l"
stripe.api_key = stripe_api_key


# Configurar logging
logging.basicConfig(level=logging.INFO)

@stripe_plans_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    id_usuario = request.json.get('id_usuario')
    logging.info(f"id_usuario recebido: {id_usuario}")

    # Verificar se o usuário já possui um stripe_customer_id
    usuario = Usuario.query.filter_by(id_usuario=id_usuario).first()
    if not usuario:
        return jsonify(error="Usuário não encontrado"), 404

    stripe_customer_id = usuario.stripe_customer_id

    # Se o usuário não tiver um stripe_customer_id, cria um novo cliente no Stripe
    if not stripe_customer_id:
        try:
            customer = stripe.Customer.create(
                description=f"Cliente para o usuário {usuario.nome}",
                email=usuario.email
            )
            stripe_customer_id = customer.id
            usuario.stripe_customer_id = stripe_customer_id
            db.session.commit()
        except Exception as e:
            logging.error(f"Erro ao criar cliente no Stripe: {e}")
            return jsonify(error=str(e)), 403

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
            client_reference_id=id_usuario,
            customer=stripe_customer_id
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
    endpoint_secret = webhook_id_checkout

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
        logging.info("Checkout concluído com sucesso.")
        session = event['data']['object']
        user_id = session.get('client_reference_id')
        stripe_subscription_id = session.get('subscription')
        stripe_customer_id = session.get('customer')

        if not all([user_id, stripe_subscription_id, stripe_customer_id]):
            logging.error("Dados incompletos no evento de webhook.")
            return jsonify(success=False), 400

        logging.info(f"Evento recebido para user_id: {user_id}, subscription_id: {stripe_subscription_id}, customer_id: {stripe_customer_id}")

        try:
            # Buscar detalhes da assinatura no Stripe
            subscription = stripe.Subscription.retrieve(stripe_subscription_id)
            subscription_start_date = datetime.utcfromtimestamp(subscription.start_date)
            subscription_end_date = datetime.utcfromtimestamp(subscription.current_period_end)

            user = Usuario.query.filter_by(id_usuario=user_id).first()
            if user:
                user.update_to_premium(stripe_subscription_id, stripe_customer_id)
                user.subscription_start_date = subscription_start_date
                user.subscription_end_date = subscription_end_date
                db.session.commit()
                logging.info(f"Usuário {user_id} atualizado para premium com início da assinatura: {subscription_start_date} e término: {subscription_end_date}")
            else:
                logging.error(f"Usuário com id {user_id} não encontrado.")
                return jsonify(success=False), 404
        except Exception as e:
            logging.error(f"Erro ao atualizar o usuário: {e}")
            return jsonify(success=False), 500

    return jsonify(success=True), 200

@stripe_plans_bp.route('/get-subscription-details', methods=['GET'])
def get_subscription_details():
    if 'user_id' in session:
        user = Usuario.query.filter_by(id_usuario=session['user_id']).first()
        if user and user.stripe_subscription_id:
            try:
                subscription = stripe.Subscription.retrieve(user.stripe_subscription_id)
                subscription_details = {
                    'id': subscription.id,
                    'status': subscription.status,
                    'start_date': subscription.start_date,
                    'current_period_end': subscription.current_period_end
                }
                return jsonify(subscription=subscription_details), 200
            except stripe.error.StripeError as e:
                logging.error(f"Erro ao recuperar detalhes da assinatura: {e}")
                return jsonify(error="Erro ao recuperar detalhes da assinatura"), 500
        else:
            return jsonify(error="Usuário não possui uma assinatura ativa"), 404
    else:
        return jsonify(error="Usuário não está logado"), 403
    
@stripe_plans_bp.route('/cancel-subscription', methods=['POST'])
def cancel_subscription():
    if 'user_id' in session:
        user = Usuario.query.filter_by(id_usuario=session['user_id']).first()
        if user and user.stripe_subscription_id:
            try:
                subscription = stripe.Subscription.retrieve(user.stripe_subscription_id)
                subscription.delete()
                user.is_premium = False
                user.subscription_end_date = datetime.now()
                db.session.commit()
                return jsonify(success=True), 200
            except stripe.error.StripeError as e:
                logging.error(f"Erro ao cancelar a assinatura: {e}")
                return jsonify(error="Erro ao cancelar a assinatura"), 500
        else:
            return jsonify(error="Usuário não possui uma assinatura ativa"), 404
    else:
        return jsonify(error="Usuário não está logado"), 403
