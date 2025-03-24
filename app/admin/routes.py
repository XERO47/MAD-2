from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Subject, Chapter, Quiz, Question, QuizAttempt, UserAnswer
from app import db
from datetime import datetime
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

def admin_required():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    return None

@admin_bp.route('/subjects', methods=['POST', 'GET'])
@jwt_required()
def manage_subjects():
    if request.method == 'POST':
        # Check admin access
        error = admin_required()
        if error:
            return error
            
        data = request.get_json()
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
    else:
        # Check admin access
        error = admin_required()
        if error:
            return error
            
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

@admin_bp.route('/chapters', methods=['POST'])
@jwt_required()
def create_chapter():
    # Check admin access
    error = admin_required()
    if error:
        return error
        
    data = request.get_json()
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

@admin_bp.route('/quizzes', methods=['POST'])
@jwt_required()
def create_quiz():
    # Check admin access
    error = admin_required()
    if error:
        return error
        
    data = request.get_json()
    quiz = Quiz(
        chapter_id=data['chapter_id'],
        date_of_quiz=datetime.strptime(data['date_of_quiz'], '%Y-%m-%d %H:%M:%S'),
        duration=data['duration'],
        remarks=data.get('remarks', '')
    )
    db.session.add(quiz)
    db.session.commit()
    
    # Add questions
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
    return jsonify({
        'id': quiz.id,
        'chapter_id': quiz.chapter_id,
        'date_of_quiz': quiz.date_of_quiz.strftime('%Y-%m-%d %H:%M:%S'),
        'duration': quiz.duration,
        'remarks': quiz.remarks
    }), 201

@admin_bp.route('/quizzes/<int:quiz_id>', methods=['GET'])
@jwt_required()
def get_quiz_details(quiz_id):
    # Check admin access
    error = admin_required()
    if error:
        return error
        
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

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    # Check admin access
    error = admin_required()
    if error:
        return error
        
    users = User.query.filter_by(is_admin=False).all()
    return jsonify([{
        'id': user.id,
        'email': user.email,
        'full_name': user.full_name,
        'qualification': user.qualification,
        'date_of_birth': user.date_of_birth.strftime('%Y-%m-%d') if user.date_of_birth else None,
        'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'is_blocked': user.is_blocked
    } for user in users]), 200

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_details(user_id):
    # Check admin access
    error = admin_required()
    if error:
        return error
        
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        return jsonify({'error': 'Cannot view admin user details'}), 400
        
    # Get user's quiz attempts with detailed information
    attempts = QuizAttempt.query.filter_by(user_id=user_id).order_by(QuizAttempt.start_time.desc()).all()
    
    return jsonify({
        'user_info': {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'qualification': user.qualification,
            'date_of_birth': user.date_of_birth.strftime('%Y-%m-%d') if user.date_of_birth else None,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'is_blocked': user.is_blocked
        },
        'quiz_attempts': [{
            'id': attempt.id,
            'quiz_id': attempt.quiz_id,
            'score': attempt.score,
            'start_time': attempt.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': attempt.end_time.strftime('%Y-%m-%d %H:%M:%S') if attempt.end_time else None,
            'quiz': {
                'chapter': attempt.quiz.chapter.name,
                'subject': attempt.quiz.chapter.subject.name
            },
            'answers': [{
                'question_id': answer.question_id,
                'selected_option': answer.selected_option,
                'is_correct': answer.is_correct,
                'question': {
                    'statement': answer.question.question_statement,
                    'correct_option': answer.question.correct_option,
                    'marks': answer.question.marks
                }
            } for answer in attempt.answers]
        } for attempt in attempts],
        'statistics': {
            'total_attempts': len(attempts),
            'average_score': sum(attempt.score for attempt in attempts) / len(attempts) if attempts else 0,
            'best_score': max(attempt.score for attempt in attempts) if attempts else 0,
            'worst_score': min(attempt.score for attempt in attempts) if attempts else 0
        }
    }), 200

@admin_bp.route('/users/<int:user_id>/block', methods=['POST'])
@jwt_required()
def toggle_user_block(user_id):
    # Check admin access
    error = admin_required()
    if error:
        return error
        
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        return jsonify({'error': 'Cannot block admin user'}), 400
        
    user.is_blocked = not user.is_blocked
    db.session.commit()
    
    return jsonify({
        'message': f"User {'blocked' if user.is_blocked else 'unblocked'} successfully",
        'is_blocked': user.is_blocked
    }), 200 