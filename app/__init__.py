import os
from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from flask_mail import Mail
from flask_caching import Cache
from celery import Celery
from .cache import cache

# Initialize Flask extensions
db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
migrate = Migrate()
celery = Celery()

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    
    # Configure Celery
    celery.conf.update(app.config)
    
    # Register blueprints
    print("\nRegistering blueprints...")
    
    # Import and register blueprints
    from .auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    print("Auth blueprint registered")
    
    from .admin.routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    print("Admin blueprint registered")
    
    from .user.routes import user_bp
    app.register_blueprint(user_bp, url_prefix='/api/user')
    print("User blueprint registered")
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("Database tables created")
    
    # Enable CORS
    CORS(app)
    print("CORS enabled")
    
    # Print registered routes for debugging
    print("\nRegistered Routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.methods} {rule.rule}")
        
    # Print auth routes specifically
    print("\nAuth Routes:")
    auth_routes = [rule for rule in app.url_map.iter_rules() if rule.endpoint.startswith('auth.')]
    for rule in auth_routes:
        print(f"- {rule.endpoint}: {rule.methods} {rule.rule}")
    
    return app 