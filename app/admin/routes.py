from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Subject, Chapter, Quiz, Question, QuizAttempt, UserAnswer
from app import db
from datetime import datetime
from sqlalchemy import func
from ..auth.utils import admin_required
from ..cache import admin_cache_response, clear_admin_cache, clear_subject_cache, clear_quiz_cache

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/subjects', methods=['POST'])
@jwt_required()
@admin_required
def create_subject():
    data = request.get_json()
    subject = Subject(name=data['name'], description=data.get('description', ''))
    db.session.add(subject)
    db.session.commit()
    clear_admin_cache()
    return jsonify(subject.to_dict()), 201

@admin_bp.route('/subjects', methods=['GET'])
@jwt_required()
@admin_required
@admin_cache_response(timeout=300)  # Cache for 5 minutes
def get_subjects():
    subjects = Subject.query.all()
    return jsonify([subject.to_dict() for subject in subjects])

@admin_bp.route('/chapters', methods=['POST'])
@jwt_required()
@admin_required
def create_chapter():
    data = request.get_json()
    chapter = Chapter(
        name=data['name'],
        description=data.get('description', ''),
        subject_id=data['subject_id']
    )
    db.session.add(chapter)
    db.session.commit()
    clear_subject_cache(data['subject_id'])
    return jsonify(chapter.to_dict()), 201

@admin_bp.route('/quizzes', methods=['POST'])
@jwt_required()
@admin_required
def create_quiz():
    data = request.get_json()
    quiz = Quiz(
        chapter_id=data['chapter_id'],
        date_of_quiz=datetime.strptime(data['date_of_quiz'], '%Y-%m-%d %H:%M:%S'),
        duration=data['duration'],
        remarks=data.get('remarks', '')
    )
    db.session.add(quiz)
    db.session.commit()
    
    # Create questions
    for q_data in data['questions']:
        question = Question(
            quiz_id=quiz.id,
            question_statement=q_data['question_statement'],
            option1=q_data['option1'],
            option2=q_data['option2'],
            option3=q_data.get('option3'),
            option4=q_data.get('option4'),
            correct_option=q_data['correct_option'],
            marks=q_data.get('marks', 1)
        )
        db.session.add(question)
    
    db.session.commit()
    clear_admin_cache()
    return jsonify(quiz.to_dict()), 201

@admin_bp.route('/quizzes/<int:quiz_id>', methods=['GET'])
@jwt_required()
@admin_required
@admin_cache_response(timeout=300)  # Cache for 5 minutes
def get_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return jsonify(quiz.to_dict())

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
@admin_cache_response(timeout=300)  # Cache for 5 minutes
def get_users():
    users = User.query.filter_by(is_admin=False).all()
    return jsonify([user.to_dict() for user in users])

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required
@admin_cache_response(timeout=300)  # Cache for 5 minutes
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@admin_bp.route('/users/<int:user_id>/block', methods=['POST'])
@jwt_required()
@admin_required
def toggle_user_block(user_id):
    user = User.query.get_or_404(user_id)
    user.is_blocked = not user.is_blocked
    db.session.commit()
    clear_admin_cache()
    return jsonify(user.to_dict()) 