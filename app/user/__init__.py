from flask import Blueprint

user_bp = Blueprint('user', __name__)

# Import routes after blueprint creation to avoid circular imports
from app.user import routes

# Import routes into the blueprint's namespace
from app.user.routes import get_subjects, get_quiz, attempt_quiz, get_attempts, get_attempt_details, get_stats 