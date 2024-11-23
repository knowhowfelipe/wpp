from flask import Flask
from auth import db
from stripe_plans import stripe_plans_bp
import os
import secrets

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:admin@localhost:5432/wpp_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    
    with app.app_context():
        pass

    app.register_blueprint(stripe_plans_bp)

    return app
