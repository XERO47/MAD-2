from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Subject, Chapter, Quiz, Question, QuizAttempt, UserAnswer
from app import db
from datetime import datetime
from sqlalchemy import func

user_bp = Blueprint('user', __name__)

@user_bp.route('/subjects', methods=['GET'])
@jwt_required()
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
    quiz = Quiz.query.get_or_404(quiz_id)
    
    data = request.get_json()
    if not data or 'answers' not in data:
        return jsonify({'error': 'Answers are required'}), 400
    
    # Create quiz attempt
    attempt = QuizAttempt(
        user_id=user_id,
        quiz_id=quiz_id,
        start_time=datetime.utcnow(),
        score=0
    )
    db.session.add(attempt)
    db.session.commit()
    
    # Process answers and calculate score
    total_score = 0
    for answer_data in data['answers']:
        question = Question.query.get(answer_data['question_id'])
        if not question:
            continue
        
        is_correct = question.correct_option == answer_data['selected_option']
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
    
    return jsonify({
        'attempt_id': attempt.id,
        'score': total_score,
        'total_questions': len(quiz.questions)
    }), 201

@user_bp.route('/attempts', methods=['GET'])
@jwt_required()
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
def get_user_stats():
    user_id = get_jwt_identity()
    
    # Get total attempts and average score
    stats = db.session.query(
        func.count(QuizAttempt.id).label('total_attempts'),
        func.avg(QuizAttempt.score).label('average_score')
    ).filter(QuizAttempt.user_id == user_id).first()
    
    # Get subject-wise performance
    subject_stats = db.session.query(
        Subject.name,
        func.count(QuizAttempt.id).label('attempts'),
        func.avg(QuizAttempt.score).label('average_score')
    ).join(Chapter, Chapter.subject_id == Subject.id)\
     .join(Quiz, Quiz.chapter_id == Chapter.id)\
     .join(QuizAttempt, QuizAttempt.quiz_id == Quiz.id)\
     .filter(QuizAttempt.user_id == user_id)\
     .group_by(Subject.name).all()
    
    return jsonify({
        'total_attempts': stats.total_attempts or 0,
        'average_score': float(stats.average_score or 0),
        'subject_stats': [{
            'subject': stat.name,
            'attempts': stat.attempts,
            'average_score': float(stat.average_score or 0)
        } for stat in subject_stats]
    }), 200 