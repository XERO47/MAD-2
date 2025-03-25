from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

# Import routes after blueprint creation to avoid circular imports
from app.auth.routes import register, login, admin_login

# Register routes with the blueprint
auth_bp.add_url_rule('/register', 'register', register, methods=['POST'])
auth_bp.add_url_rule('/login', 'login', login, methods=['POST'])
auth_bp.add_url_rule('/admin/login', 'admin_login', admin_login, methods=['POST'])

# Make sure routes are registered
routes.auth_bp = auth_bp 