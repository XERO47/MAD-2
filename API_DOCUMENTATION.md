# Quiz Master API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication
All API endpoints except registration and login require JWT authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Authentication

#### Register User
```http
POST /auth/register
```

Request Body:
```json
{
    "email": "user@example.com",
    "password": "password123",
    "full_name": "John Doe",
    "qualification": "Bachelor's Degree",
    "date_of_birth": "1990-01-01"
}
```

Response (201 Created):
```json
{
    "message": "User registered successfully"
}
```

#### User Login
```http
POST /auth/login
```

Request Body:
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

Response (200 OK):
```json
{
    "access_token": "jwt_token_here",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "full_name": "John Doe",
        "is_admin": false
    }
}
```

#### Admin Login
```http
POST /auth/admin/login
```

Request Body:
```json
{
    "email": "admin@quizmaster.com",
    "password": "admin123"
}
```

Response (200 OK):
```json
{
    "access_token": "jwt_token_here",
    "user": {
        "id": 1,
        "email": "admin@quizmaster.com",
        "full_name": "Admin User",
        "is_admin": true
    }
}
```

### Admin Routes

#### Create Subject
```http
POST /admin/subjects
```

Request Body:
```json
{
    "name": "Mathematics",
    "description": "Basic mathematics course"
}
```

Response (201 Created):
```json
{
    "id": 1,
    "name": "Mathematics",
    "description": "Basic mathematics course"
}
```

#### Get All Subjects
```http
GET /admin/subjects
```

Response (200 OK):
```json
[
    {
        "id": 1,
        "name": "Mathematics",
        "description": "Basic mathematics course",
        "chapters": [
            {
                "id": 1,
                "name": "Algebra"
            }
        ]
    }
]
```

#### Create Chapter
```http
POST /admin/chapters
```

Request Body:
```json
{
    "name": "Algebra",
    "description": "Basic algebraic concepts",
    "subject_id": 1
}
```

Response (201 Created):
```json
{
    "id": 1,
    "name": "Algebra",
    "description": "Basic algebraic concepts",
    "subject_id": 1
}
```

#### Create Quiz
```http
POST /admin/quizzes
```

Request Body:
```json
{
    "chapter_id": 1,
    "date_of_quiz": "2024-03-15 14:00:00",
    "duration": 60,
    "remarks": "Basic algebra quiz",
    "questions": [
        {
            "question_statement": "What is x + x?",
            "option1": "2x",
            "option2": "x²",
            "option3": "x",
            "option4": "0",
            "correct_option": 1,
            "marks": 1
        }
    ]
}
```

Response (201 Created):
```json
{
    "id": 1,
    "chapter_id": 1,
    "date_of_quiz": "2024-03-15 14:00:00",
    "duration": 60,
    "remarks": "Basic algebra quiz"
}
```

#### Get Quiz Details
```http
GET /admin/quizzes/{quiz_id}
```

Response (200 OK):
```json
{
    "id": 1,
    "chapter_id": 1,
    "date_of_quiz": "2024-03-15 14:00:00",
    "duration": 60,
    "remarks": "Basic algebra quiz",
    "questions": [
        {
            "id": 1,
            "question_statement": "What is x + x?",
            "option1": "2x",
            "option2": "x²",
            "option3": "x",
            "option4": "0",
            "correct_option": 1,
            "marks": 1
        }
    ]
}
```

#### Get All Users
```http
GET /admin/users
```

Response (200 OK):
```json
[
    {
        "id": 1,
        "email": "user@example.com",
        "full_name": "John Doe",
        "qualification": "Bachelor's Degree",
        "date_of_birth": "1990-01-01",
        "created_at": "2024-03-01 10:00:00"
    }
]
```

### User Routes

#### Get Available Subjects and Quizzes
```http
GET /user/subjects
```

Response (200 OK):
```json
[
    {
        "id": 1,
        "name": "Mathematics",
        "description": "Basic mathematics course",
        "chapters": [
            {
                "id": 1,
                "name": "Algebra",
                "quizzes": [
                    {
                        "id": 1,
                        "date_of_quiz": "2024-03-15 14:00:00",
                        "duration": 60,
                        "remarks": "Basic algebra quiz"
                    }
                ]
            }
        ]
    }
]
```

#### Get Quiz Details (User View)
```http
GET /user/quizzes/{quiz_id}
```

Response (200 OK):
```json
{
    "id": 1,
    "chapter_id": 1,
    "date_of_quiz": "2024-03-15 14:00:00",
    "duration": 60,
    "remarks": "Basic algebra quiz",
    "questions": [
        {
            "id": 1,
            "question_statement": "What is x + x?",
            "option1": "2x",
            "option2": "x²",
            "option3": "x",
            "option4": "0",
            "marks": 1
        }
    ]
}
```

#### Attempt Quiz
```http
POST /user/quizzes/{quiz_id}/attempt
```

Request Body:
```json
{
    "answers": [
        {
            "question_id": 1,
            "selected_option": 1
        }
    ]
}
```

Response (201 Created):
```json
{
    "attempt_id": 1,
    "score": 1,
    "total_questions": 1
}
```

#### Get User's Quiz Attempts
```http
GET /user/attempts
```

Response (200 OK):
```json
[
    {
        "id": 1,
        "quiz_id": 1,
        "score": 1,
        "start_time": "2024-03-15 14:00:00",
        "end_time": "2024-03-15 15:00:00",
        "quiz": {
            "chapter": "Algebra",
            "subject": "Mathematics"
        }
    }
]
```

#### Get Attempt Details
```http
GET /user/attempts/{attempt_id}
```

Response (200 OK):
```json
{
    "id": 1,
    "quiz_id": 1,
    "score": 1,
    "start_time": "2024-03-15 14:00:00",
    "end_time": "2024-03-15 15:00:00",
    "quiz": {
        "chapter": "Algebra",
        "subject": "Mathematics"
    },
    "answers": [
        {
            "question_id": 1,
            "selected_option": 1,
            "is_correct": true,
            "question": {
                "statement": "What is x + x?",
                "correct_option": 1,
                "marks": 1
            }
        }
    ]
}
```

#### Get User Statistics
```http
GET /user/stats
```

Response (200 OK):
```json
{
    "total_attempts": 1,
    "average_score": 1.0,
    "subject_stats": [
        {
            "subject": "Mathematics",
            "attempts": 1,
            "average_score": 1.0
        }
    ]
}
```

## Error Responses
All endpoints may return the following error responses:

### 400 Bad Request
```json
{
    "error": "Error message describing the issue"
}
```

### 401 Unauthorized
```json
{
    "error": "Invalid credentials"
}
```

### 403 Forbidden
```json
{
    "error": "Admin access required"
}
```

### 404 Not Found
```json
{
    "error": "Resource not found"
}
```

## Notes for Frontend Implementation

1. **Authentication Flow**:
   - Store the JWT token in localStorage or sessionStorage after successful login
   - Include the token in all subsequent API requests
   - Handle token expiration (1 hour) by redirecting to login

2. **Quiz Timer**:
   - Implement a countdown timer based on the quiz duration
   - Auto-submit the quiz when time expires
   - Show remaining time to the user

3. **Quiz Navigation**:
   - Allow users to navigate between questions
   - Save answers locally before submission
   - Show progress indicator

4. **Error Handling**:
   - Implement proper error handling for all API calls
   - Show user-friendly error messages
   - Handle network errors gracefully

5. **Loading States**:
   - Show loading indicators during API calls
   - Implement skeleton loading for better UX

6. **Form Validation**:
   - Implement client-side validation for all forms
   - Show validation errors inline
   - Prevent form submission if validation fails

7. **Responsive Design**:
   - Ensure the UI works well on both desktop and mobile
   - Implement proper spacing and layout for different screen sizes

8. **Accessibility**:
   - Use semantic HTML elements
   - Include proper ARIA labels
   - Ensure keyboard navigation works
   - Maintain sufficient color contrast 