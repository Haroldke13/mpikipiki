# app/__init__.py
from bson import ObjectId
from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect


# Initialize extensions
mongo = PyMongo()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)

    # Configurations
    app.config["SECRET_KEY"] = "supersecretkey"  # 🔐 replace with env var in production
    app.config["MONGO_URI"] = "mongodb://localhost:27017/ridehailing"

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
