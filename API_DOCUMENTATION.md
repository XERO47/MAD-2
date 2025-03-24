# Quiz Master API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication
The API uses JWT (JSON Web Token) for authentication. Include the token in the Authorization header:
```
Authorization: Bearer <access_token>
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
    "qualification": "BSc Computer Science",
    "date_of_birth": "1995-05-15"
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
    "access_token": "eyJhbGc...",
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
    "access_token": "eyJhbGc...",
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
    "name": "Computer Science",
    "description": "Fundamentals of Computer Science"
}
```

Response (201 Created):
```json
{
    "id": 1,
    "name": "Computer Science",
    "description": "Fundamentals of Computer Science"
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
        "name": "Computer Science",
        "description": "Fundamentals of Computer Science",
        "chapters": [
            {
                "id": 1,
                "name": "Data Structures"
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
    "name": "Data Structures",
    "description": "Basic data structures",
    "subject_id": 1
}
```

Response (201 Created):
```json
{
    "id": 1,
    "name": "Data Structures",
    "description": "Basic data structures",
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
    "date_of_quiz": "2025-03-25 10:00:00",
    "duration": 30,
    "remarks": "Basic data structures quiz",
    "questions": [
        {
            "question_statement": "What is the time complexity of accessing an element in an array?",
            "option1": "O(1)",
            "option2": "O(n)",
            "option3": "O(log n)",
            "option4": "O(n log n)",
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
    "date_of_quiz": "2025-03-25 10:00:00",
    "duration": 30,
    "remarks": "Basic data structures quiz"
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
    "date_of_quiz": "2025-03-25 10:00:00",
    "duration": 30,
    "remarks": "Basic data structures quiz",
    "questions": [
        {
            "id": 1,
            "question_statement": "What is the time complexity of accessing an element in an array?",
            "option1": "O(1)",
            "option2": "O(n)",
            "option3": "O(log n)",
            "option4": "O(n log n)",
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
        "id": 2,
        "email": "user@example.com",
        "full_name": "John Doe",
        "qualification": "BSc Computer Science",
        "date_of_birth": "1995-05-15",
        "created_at": "2025-03-24 13:03:04",
        "is_blocked": false
    }
]
```

#### Get User Details
```http
GET /admin/users/{user_id}
```

Response (200 OK):
```json
{
    "user_info": {
        "id": 2,
        "email": "user@example.com",
        "full_name": "John Doe",
        "qualification": "BSc Computer Science",
        "date_of_birth": "1995-05-15",
        "created_at": "2025-03-24 13:03:04",
        "is_blocked": false
    },
    "quiz_attempts": [
        {
            "id": 1,
            "quiz_id": 1,
            "score": 1.0,
            "start_time": "2025-03-24 13:03:12",
            "end_time": "2025-03-24 13:03:13",
            "quiz": {
                "chapter": "Data Structures",
                "subject": "Computer Science"
            },
            "answers": [
                {
                    "question_id": 1,
                    "selected_option": 1,
                    "is_correct": true,
                    "question": {
                        "statement": "What is the time complexity of accessing an element in an array?",
                        "correct_option": 1,
                        "marks": 1
                    }
                }
            ]
        }
    ],
    "statistics": {
        "total_attempts": 1,
        "average_score": 1.0,
        "best_score": 1.0,
        "worst_score": 1.0
    }
}
```

#### Toggle User Block Status
```http
POST /admin/users/{user_id}/block
```

Response (200 OK):
```json
{
    "message": "User blocked successfully",
    "is_blocked": true
}
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
        "name": "Computer Science",
        "description": "Fundamentals of Computer Science",
        "chapters": [
            {
                "id": 1,
                "name": "Data Structures",
                "quizzes": [
                    {
                        "id": 1,
                        "date_of_quiz": "2025-03-25 10:00:00",
                        "duration": 30,
                        "remarks": "Basic data structures quiz"
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
    "date_of_quiz": "2025-03-25 10:00:00",
    "duration": 30,
    "remarks": "Basic data structures quiz",
    "questions": [
        {
            "id": 1,
            "question_statement": "What is the time complexity of accessing an element in an array?",
            "option1": "O(1)",
            "option2": "O(n)",
            "option3": "O(log n)",
            "option4": "O(n log n)",
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
        "start_time": "2025-03-25 10:00:00",
        "end_time": "2025-03-25 10:00:30",
        "quiz": {
            "chapter": "Data Structures",
            "subject": "Computer Science"
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
    "start_time": "2025-03-25 10:00:00",
    "end_time": "2025-03-25 10:00:30",
    "quiz": {
        "chapter": "Data Structures",
        "subject": "Computer Science"
    },
    "answers": [
        {
            "question_id": 1,
            "selected_option": 1,
            "is_correct": true,
            "question": {
                "statement": "What is the time complexity of accessing an element in an array?",
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
            "subject": "Computer Science",
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
    "error": "Invalid input data"
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
   - Store the JWT token securely (e.g., in HttpOnly cookies)
   - Include the token in all subsequent requests
   - Handle token expiration and refresh

2. **User Block Status**:
   - Check user's block status after login
   - Show appropriate messages when a blocked user tries to access features
   - Implement UI for admins to manage user block status

3. **Quiz Attempts**:
   - Implement timer for quiz duration
   - Handle auto-submission when time expires
   - Show clear feedback for correct/incorrect answers after submission

4. **Admin Dashboard**:
   - Implement user management interface with:
     - List of all users with block status
     - Detailed view of user information and quiz attempts
     - Block/unblock functionality
   - Add sorting and filtering options for user list
   - Show user statistics and performance metrics

5. **Error Handling**:
   - Display appropriate error messages to users
   - Implement retry mechanisms for network failures
   - Handle session expiration gracefully

6. **Quiz Navigation**:
   - Allow users to navigate between questions
   - Save answers locally before submission
   - Show progress indicator

7. **Form Validation**:
   - Implement client-side validation for all forms
   - Show validation errors inline
   - Prevent form submission if validation fails

8. **Responsive Design**:
   - Ensure the UI works well on both desktop and mobile
   - Implement proper spacing and layout for different screen sizes

9. **Accessibility**:
   - Use semantic HTML elements
   - Include proper ARIA labels
   - Ensure keyboard navigation works
   - Maintain sufficient color contrast 