from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Subject, Chapter, Quiz, Question, QuizAttempt, UserAnswer
from app import db
from datetime import datetime
from sqlalchemy import func
from ..cache import cache_response, clear_cache_for_user, clear_quiz_cache

user_bp = Blueprint('user', __name__)

@user_bp.route('/subjects', methods=['GET'])
@jwt_required()
@cache_response(timeout=300)  # Cache for 5 minutes
def get_subjects():
    subjects = Subject.query.all()
    return jsonify([{
        'id': subject.id,
        'name': subject.name,
        'description': subject.description,
        'chapters': [{
            'id': chapter.id,
            'name': chapter.name,
            'quizzes': [{
                'id': quiz.id,
                'date_of_quiz': quiz.date_of_quiz.strftime('%Y-%m-%d %H:%M:%S'),
                'duration': quiz.duration,
                'remarks': quiz.remarks
            } for quiz in chapter.quizzes]
        } for chapter in subject.chapters]
    } for subject in subjects]), 200

@user_bp.route('/quizzes/<int:quiz_id>', methods=['GET'])
@jwt_required()
@cache_response(timeout=300)  # Cache for 5 minutes
def get_quiz(quiz_id):
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
            'marks': q.marks
        } for q in quiz.questions]
    }), 200

@user_bp.route('/quizzes/<int:quiz_id>/attempt', methods=['POST'])
@jwt_required()
def attempt_quiz(quiz_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.is_blocked:
        return jsonify({'error': 'Your account is blocked'}), 403
        
    quiz = Quiz.query.get_or_404(quiz_id)
    data = request.get_json()
    
    # Create quiz attempt
    attempt = QuizAttempt(
        user_id=user_id,
        quiz_id=quiz_id,
        start_time=datetime.utcnow(),
        score=0  # Initialize with 0
    )
    db.session.add(attempt)
    db.session.commit()  # Commit to get the attempt.id
    
    # Calculate score
    total_score = 0
    total_marks = 0
    
    for answer_data in data['answers']:
        question = Question.query.get(answer_data['question_id'])
        if not question or question.quiz_id != quiz_id:
            return jsonify({'error': 'Invalid question ID'}), 400
            
        total_marks += question.marks
        is_correct = answer_data['selected_option'] == question.correct_option
        if is_correct:
            total_score += question.marks
            
        user_answer = UserAnswer(
            attempt_id=attempt.id,
            question_id=question.id,
            selected_option=answer_data['selected_option'],
            is_correct=is_correct
        )
        db.session.add(user_answer)
    
    attempt.score = total_score
    attempt.end_time = datetime.utcnow()
    db.session.commit()
    
    # Clear cache for this quiz and user
    clear_quiz_cache(quiz_id)
    clear_cache_for_user(user_id)
    
    return jsonify({
        'attempt_id': attempt.id,
        'score': total_score,
        'total_marks': total_marks
    }), 201

@user_bp.route('/attempts', methods=['GET'])
@jwt_required()
@cache_response(timeout=300)  # Cache for 5 minutes
def get_attempts():
    user_id = get_jwt_identity()
    attempts = QuizAttempt.query.filter_by(user_id=user_id).order_by(QuizAttempt.start_time.desc()).all()
    return jsonify([{
        'id': attempt.id,
        'quiz_id': attempt.quiz_id,
        'score': attempt.score,
        'start_time': attempt.start_time.strftime('%Y-%m-%d %H:%M:%S'),
        'end_time': attempt.end_time.strftime('%Y-%m-%d %H:%M:%S') if attempt.end_time else None,
        'quiz': {
            'chapter': attempt.quiz.chapter.name,
            'subject': attempt.quiz.chapter.subject.name
        }
    } for attempt in attempts]), 200

@user_bp.route('/attempts/<int:attempt_id>', methods=['GET'])
@jwt_required()
@cache_response(timeout=300)  # Cache for 5 minutes
def get_attempt_details(attempt_id):
    user_id = get_jwt_identity()
    attempt = QuizAttempt.query.filter_by(id=attempt_id, user_id=user_id).first_or_404()
    return jsonify({
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
    }), 200

@user_bp.route('/stats', methods=['GET'])
@jwt_required()
@cache_response(timeout=300)  # Cache for 5 minutes
def get_stats():
    user_id = get_jwt_identity()
    attempts = QuizAttempt.query.filter_by(user_id=user_id).all()
    
    if not attempts:
        return jsonify({
            'total_attempts': 0,
            'average_score': 0,
            'subject_stats': []
        })
    
    # Calculate overall statistics
    total_attempts = len(attempts)
    total_score = sum(attempt.score for attempt in attempts)
    average_score = total_score / total_attempts
    
    # Calculate subject-wise statistics
    subject_stats = {}
    for attempt in attempts:
        subject_name = attempt.quiz.chapter.subject.name
        if subject_name not in subject_stats:
            subject_stats[subject_name] = {
                'attempts': 0,
                'total_score': 0
            }
        subject_stats[subject_name]['attempts'] += 1
        subject_stats[subject_name]['total_score'] += attempt.score
    
    # Format subject statistics
    subject_stats_list = [
        {
            'subject': subject,
            'attempts': stats['attempts'],
            'average_score': stats['total_score'] / stats['attempts']
        }
        for subject, stats in subject_stats.items()
    ]
    
    return jsonify({
        'total_attempts': total_attempts,
        'average_score': average_score,
        'subject_stats': subject_stats_list
    }) 