# Quiz Master

A multi-user quiz application built with Flask, VueJS, and SQLite.

## Features

- User and Admin authentication
- Subject and Chapter management
- Quiz creation and management
- Quiz attempts and scoring
- Daily reminders for inactive users
- Monthly activity reports
- CSV export functionality
- Redis caching
- Background tasks with Celery

## Prerequisites

- Python 3.8+
- Redis
- Node.js and npm (for frontend)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd quiz-master
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password
```

5. Initialize the database:
```bash
python run.py
```

6. Start Redis server:
```bash
redis-server
```

7. Start Celery worker:
```bash
celery -A app.celery worker --loglevel=info
```

8. Start Celery beat (for scheduled tasks):
```bash
celery -A app.celery beat --loglevel=info
```

9. Run the application:
```bash
python run.py
```

## Default Admin Account

- Email: admin@quizmaster.com
- Password: admin123

**Note**: Change the admin password in production!

## API Endpoints

### Authentication
- POST `/api/auth/register` - Register a new user
- POST `/api/auth/login` - User login
- POST `/api/auth/admin/login` - Admin login

### Admin Routes
- POST `/api/admin/subjects` - Create a new subject
- GET `/api/admin/subjects` - Get all subjects
- POST `/api/admin/chapters` - Create a new chapter
- POST `/api/admin/quizzes` - Create a new quiz
- GET `/api/admin/quizzes/<quiz_id>` - Get quiz details
- GET `/api/admin/users` - Get all users

### User Routes
- GET `/api/user/subjects` - Get all subjects and available quizzes
- GET `/api/user/quizzes/<quiz_id>` - Get quiz details
- POST `/api/user/quizzes/<quiz_id>/attempt` - Attempt a quiz
- GET `/api/user/attempts` - Get user's quiz attempts
- GET `/api/user/attempts/<attempt_id>` - Get attempt details
- GET `/api/user/stats` - Get user statistics

## Background Tasks

The application includes the following background tasks:
- Daily reminders for inactive users (runs at 8 PM)
- Monthly activity reports (runs on the first day of each month)
- CSV export functionality (triggered by user/admin)

## Caching

Redis is used for caching to improve performance. The following endpoints are cached:
- Subject listing
- Quiz details
- User statistics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 