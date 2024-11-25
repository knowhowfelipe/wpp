# models/stripe_model.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'  # Nome da tabela atualizado para minúsculas, EXATAMENTE como na tabela, pois trata como string
    id_usuario = db.Column(db.Integer, primary_key=True)
    codigo_acesso = db.Column(db.Integer, unique=True, nullable=False)
    nome = db.Column(db.String(255), nullable=False)
    identificador_comercial = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    is_premium = db.Column(db.Boolean, default=False)
    subscription_start_date = db.Column(db.Date)
    subscription_end_date = db.Column(db.Date)
    stripe_customer_id = db.Column(db.String(255))
    stripe_subscription_id = db.Column(db.String(255))

    def update_to_premium(self, stripe_subscription_id, stripe_customer_id):
        try:
            self.is_premium = True
            self.subscription_start_date = datetime.now()
            self.stripe_subscription_id = stripe_subscription_id
            self.stripe_customer_id = stripe_customer_id
            db.session.commit()
            print(f"Usuário {self.id_usuario} atualizado para premium")
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Erro ao atualizar usuário: {e}")
