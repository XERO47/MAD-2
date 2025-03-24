from app import celery, mail
from app.models import User, Quiz, QuizAttempt
from flask_mail import Message
from datetime import datetime, timedelta
import csv
from io import StringIO
import os

@celery.task
def send_daily_reminder():
    """Send daily reminders to users about new quizzes and inactivity."""
    # Get users who haven't attempted any quiz in the last 7 days
    inactive_users = User.query.filter(
        ~User.quiz_attempts.any(),
        User.is_admin == False
    ).all()
    
    # Get new quizzes created in the last 24 hours
    new_quizzes = Quiz.query.filter(
        Quiz.created_at >= datetime.utcnow() - timedelta(days=1)
    ).all()
    
    for user in inactive_users:
        msg = Message(
            'Daily Quiz Reminder',
            sender=os.environ.get('MAIL_USERNAME'),
            recipients=[user.email]
        )
        
        if new_quizzes:
            quiz_list = "\n".join([
                f"- {quiz.chapter.name} ({quiz.chapter.subject.name})"
                for quiz in new_quizzes
            ])
            msg.body = f"""
            Hello {user.full_name},
            
            We noticed you haven't attempted any quizzes recently. Here are some new quizzes available:
            
            {quiz_list}
            
            Visit our platform to take these quizzes!
            """
        else:
            msg.body = f"""
            Hello {user.full_name},
            
            We noticed you haven't attempted any quizzes recently. Visit our platform to explore available quizzes!
            """
        
        mail.send(msg)

@celery.task
def send_monthly_report():
    """Generate and send monthly activity reports to users."""
    # Get all users except admin
    users = User.query.filter_by(is_admin=False).all()
    
    for user in users:
        # Get user's attempts for the previous month
        last_month = datetime.utcnow().replace(day=1) - timedelta(days=1)
        attempts = QuizAttempt.query.filter(
            QuizAttempt.user_id == user.id,
            QuizAttempt.start_time >= last_month.replace(day=1),
            QuizAttempt.start_time <= last_month.replace(hour=23, minute=59, second=59)
        ).all()
        
        if attempts:
            # Calculate statistics
            total_attempts = len(attempts)
            total_score = sum(attempt.score for attempt in attempts)
            average_score = total_score / total_attempts
            
            # Generate HTML report
            html_content = f"""
            <html>
                <body>
                    <h2>Monthly Activity Report - {last_month.strftime('%B %Y')}</h2>
                    <p>Hello {user.full_name},</p>
                    
                    <h3>Your Quiz Performance</h3>
                    <ul>
                        <li>Total Quizzes Attempted: {total_attempts}</li>
                        <li>Total Score: {total_score}</li>
                        <li>Average Score: {average_score:.2f}</li>
                    </ul>
                    
                    <h3>Quiz Details</h3>
                    <table border="1">
                        <tr>
                            <th>Subject</th>
                            <th>Chapter</th>
                            <th>Score</th>
                            <th>Date</th>
                        </tr>
                        {''.join(f"""
                        <tr>
                            <td>{attempt.quiz.chapter.subject.name}</td>
                            <td>{attempt.quiz.chapter.name}</td>
                            <td>{attempt.score}</td>
                            <td>{attempt.start_time.strftime('%Y-%m-%d')}</td>
                        </tr>
                        """ for attempt in attempts)}
                    </table>
                </body>
            </html>
            """
            
            msg = Message(
                f'Monthly Quiz Report - {last_month.strftime("%B %Y")}',
                sender=os.environ.get('MAIL_USERNAME'),
                recipients=[user.email],
                html=html_content
            )
            
            mail.send(msg)

@celery.task
def export_quiz_data(user_id, is_admin=False):
    """Export quiz data as CSV for a user or admin."""
    user = User.query.get(user_id)
    if not user:
        return
    
    output = StringIO()
    writer = csv.writer(output)
    
    if is_admin:
        # Admin export: All users' quiz data
        writer.writerow(['User', 'Subject', 'Chapter', 'Score', 'Date'])
        attempts = QuizAttempt.query.all()
        for attempt in attempts:
            writer.writerow([
                attempt.user.full_name,
                attempt.quiz.chapter.subject.name,
                attempt.quiz.chapter.name,
                attempt.score,
                attempt.start_time.strftime('%Y-%m-%d %H:%M:%S')
            ])
    else:
        # User export: Their own quiz data
        writer.writerow(['Subject', 'Chapter', 'Score', 'Date'])
        attempts = QuizAttempt.query.filter_by(user_id=user_id).all()
        for attempt in attempts:
            writer.writerow([
                attempt.quiz.chapter.subject.name,
                attempt.quiz.chapter.name,
                attempt.score,
                attempt.start_time.strftime('%Y-%m-%d %H:%M:%S')
            ])
    
    # Send email with CSV attachment
    msg = Message(
        'Quiz Data Export',
        sender=os.environ.get('MAIL_USERNAME'),
        recipients=[user.email]
    )
    
    msg.attach(
        'quiz_data.csv',
        'text/csv',
        output.getvalue()
    )
    
    msg.body = 'Please find your quiz data export attached.'
    mail.send(msg) 