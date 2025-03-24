from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(email='admin@quizmaster.com').first()
        if not admin:
            admin = User(
                email='admin@quizmaster.com',
                full_name='Admin User',
                is_admin=True
            )
            admin.set_password('admin123')  # Change this in production
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 