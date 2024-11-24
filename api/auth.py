from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'Usuarios'
    __table_args__ = {'schema': 'public'}  # Esquema público explicitamente definido

    id_usuario = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    codigo_acesso = db.Column(db.Integer, unique=True, nullable=False)
    nome = db.Column(db.String(255), nullable=False)
    identificador_comercial = db.Column(db.String(255), unique=True, nullable=False)
    is_premium = db.Column(db.Boolean, default=False)
    subscription_start_date = db.Column(db.Date)
    subscription_end_date = db.Column(db.Date)
    stripe_customer_id = db.Column(db.String(255))
    stripe_subscription_id = db.Column(db.String(255))

    def __init__(self, email, senha, codigo_acesso, nome, identificador_comercial):
        self.email = email
        self.senha = senha
        self.codigo_acesso = codigo_acesso
        self.nome = nome
        self.identificador_comercial = identificador_comercial
