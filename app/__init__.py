# app/__init__.py
import os

from bson import ObjectId
from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# Load a local .env (never committed) so configuration stays out of the repo.
# Harmless when python-dotenv is unavailable.
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # noqa: BLE001 - dotenv is an optional convenience
    pass


# Initialize extensions
mongo = PyMongo()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)

    # Configurations - read from the environment, never hardcoded.
    # The session-signing key must not fall back to a guessable default, or
    # anyone could forge a signed session cookie.
    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        raise RuntimeError(
            "SECRET_KEY is not set. Copy .env.example to .env and provide a "
            "value before starting the app."
        )
    app.config["SECRET_KEY"] = secret_key
    # The connection string can carry a database username/password, so it also
    # comes from the environment. The local default is safe to keep.
    app.config["MONGO_URI"] = os.environ.get(
        "MONGO_URI", "mongodb://localhost:27017/ridehailing"
    )

    # Init extensions
    mongo.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "main.login"  # redirect if not logged in
    login_manager.login_message_category = "info"

    # User loader for Flask-Login
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if data:
            return User(
                name=data["name"],
                email=data["email"],
                phone=data["phone"],
                password_hash=data["password_hash"],  # don't re-hash
                role=data.get("role", "customer"),
                _id=data["_id"],
            )
        return None

    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)

    return app
