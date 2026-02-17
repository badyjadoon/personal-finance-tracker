from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message = 'Please log in to continue.'
login_manager.login_message_category = 'info'

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wallet.db'
    db.init_app(app)
    login_manager.init_app(app)
    from .routes import main
    app.register_blueprint(main)
    return app