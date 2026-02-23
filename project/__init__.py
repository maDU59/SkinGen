from flask import Flask, session
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
from datetime import timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

# Initialize SQLAlchemy instance (outside create_app for import access)
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    csrf = CSRFProtect()
    csrf.init_app(app)

    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[],
        storage_uri="memory://",
    )

    load_dotenv()
    app.secret_key = os.getenv("SESSION_KEY")
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv("SESSION_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.permanent_session_lifetime = timedelta(days=31)

    @app.before_request
    def make_session_permanent():
        session.permanent = True
    
    # Initialize extensions with app
    db.init_app(app)
    
    # Configure Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    # User loader function for Flask-Login
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from .auth import auth as auth_blueprint
    limiter.limit("15/hour")(auth_blueprint)
    app.register_blueprint(auth_blueprint)
    
    from .main import main as main_blueprint
    limiter.limit("60/minute")(main_blueprint)
    app.register_blueprint(main_blueprint)
    
    return app