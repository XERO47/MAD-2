from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Subject, Chapter, Quiz, Question
from app import db
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def admin_required():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return False
    return True

# Subject Management
@admin_bp.route('/subjects', methods=['POST'])
@jwt_required()
def create_subject():
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Subject name is required'}), 400
    
    subject = Subject(
        name=data['name'],
        description=data.get('description', '')
    )
    
    db.session.add(subject)
    db.session.commit()
    
    return jsonify({
        'id': subject.id,
        'name': subject.name,
        'description': subject.description
    }), 201

@admin_bp.route('/subjects', methods=['GET'])
@jwt_required()
def get_subjects():
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403
    
    subjects = Subject.query.all()
    return jsonify([{
        'id': subject.id,
        'name': subject.name,
        'description': subject.description,
        'chapters': [{
            'id': chapter.id,
            'name': chapter.name
        } for chapter in subject.chapters]
    } for subject in subjects]), 200

# Chapter Management
@admin_bp.route('/chapters', methods=['POST'])
@jwt_required()
def create_chapter():
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    if not data or not data.get('name') or not data.get('subject_id'):
        return jsonify({'error': 'Chapter name and subject_id are required'}), 400
    
    chapter = Chapter(
        name=data['name'],
        description=data.get('description', ''),
        subject_id=data['subject_id']
    )
    
    db.session.add(chapter)
    db.session.commit()
    
    return jsonify({
        'id': chapter.id,
        'name': chapter.name,
        'description': chapter.description,
        'subject_id': chapter.subject_id
    }), 201

# Quiz Management
@admin_bp.route('/quizzes', methods=['POST'])
@jwt_required()
def create_quiz():
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    required_fields = ['chapter_id', 'date_of_quiz', 'duration', 'questions']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    quiz = Quiz(
        chapter_id=data['chapter_id'],
        date_of_quiz=datetime.strptime(data['date_of_quiz'], '%Y-%m-%d %H:%M:%S'),
        duration=data['duration'],
        remarks=data.get('remarks', '')
    )
    
    db.session.add(quiz)
    db.session.commit()
    
    # Add questions
    for q in data['questions']:
        question = Question(
            quiz_id=quiz.id,
            question_statement=q['question_statement'],
            option1=q['option1'],
            option2=q['option2'],
            option3=q.get('option3'),
            option4=q.get('option4'),
            correct_option=q['correct_option'],
            marks=q.get('marks', 1)
        )
        db.session.add(question)
    
    db.session.commit()
    
    return jsonify({
        'id': quiz.id,
        'chapter_id': quiz.chapter_id,
        'date_of_quiz': quiz.date_of_quiz.strftime('%Y-%m-%d %H:%M:%S'),
        'duration': quiz.duration,
        'remarks': quiz.remarks
    }), 201

@admin_bp.route('/quizzes/<int:quiz_id>', methods=['GET'])
@jwt_required()
def get_quiz(quiz_id):
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403
    
    quiz = Quiz.query.get_or_404(quiz_id)
    return jsonify({
        'id': quiz.id,
        'chapter_id': quiz.chapter_id,
        'date_of_quiz': quiz.date_of_quiz.strftime('%Y-%m-%d %H:%M:%S'),
        'duration': quiz.duration,
        'remarks': quiz.remarks,
        'questions': [{
            'id': q.id,
            'question_statement': q.question_statement,
            'option1': q.option1,
            'option2': q.option2,
            'option3': q.option3,
            'option4': q.option4,
            'correct_option': q.correct_option,
            'marks': q.marks
        } for q in quiz.questions]
    }), 200

# User Management
@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403
    
    users = User.query.filter_by(is_admin=False).all()
    return jsonify([{
        'id': user.id,
        'email': user.email,
        'full_name': user.full_name,
        'qualification': user.qualification,
        'date_of_birth': user.date_of_birth.strftime('%Y-%m-%d') if user.date_of_birth else None,
        'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for user in users]), 200 