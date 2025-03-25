from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

# Import routes after blueprint creation to avoid circular imports
from app.admin import routes

# Import routes into the blueprint's namespace
from app.admin.routes import (
    create_subject, get_subjects,
    create_chapter,
    create_quiz, get_quiz,
    get_users, get_user, toggle_user_block
) 