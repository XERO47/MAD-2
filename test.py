import requests
import json
from datetime import datetime, timedelta
import time

BASE_URL = "http://localhost:5000/api"

def print_response(response, description):
    print(f"\n{description}")
    print(f"Status Code: {response.status_code}")
    try:
        print("Response:", json.dumps(response.json(), indent=2))
    except:
        print("Response:", response.text)
    print("-" * 80)

def get_auth_headers(token):
    """Helper function to get authorization headers"""
    return {"Authorization": f"Bearer {token}"}

def simulate_admin_workflow():
    print("\n=== ADMIN WORKFLOW SIMULATION ===")
    
    # Admin login
    login_data = {
        "email": "admin@quizmaster.com",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/auth/admin/login", json=login_data)
    print_response(response, "Admin Login")
    
    if response.status_code != 200:
        print("Admin login failed, exiting...")
        return
    
    token = response.json()["access_token"]
    headers = get_auth_headers(token)
    
    # Create a subject
    subject_data = {
        "name": "Computer Science",
        "description": "Fundamentals of Computer Science"
    }
    response = requests.post(f"{BASE_URL}/admin/subjects", json=subject_data, headers=headers)
    print_response(response, "Create Subject")
    
    if response.status_code != 201:
        print("Failed to create subject, exiting...")
        return
        
    subject_id = response.json()["id"]
    
    # Create a chapter
    chapter_data = {
        "name": "Data Structures",
        "description": "Basic data structures",
        "subject_id": subject_id
    }
    response = requests.post(f"{BASE_URL}/admin/chapters", json=chapter_data, headers=headers)
    print_response(response, "Create Chapter")
    
    if response.status_code != 201:
        print("Failed to create chapter, exiting...")
        return
        
    chapter_id = response.json()["id"]
    
    # Create a quiz
    quiz_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    quiz_data = {
        "chapter_id": chapter_id,
        "date_of_quiz": quiz_date,
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
            },
            {
                "question_statement": "Which data structure uses FIFO principle?",
                "option1": "Stack",
                "option2": "Queue",
                "option3": "Tree",
                "option4": "Graph",
                "correct_option": 2,
                "marks": 1
            }
        ]
    }
    response = requests.post(f"{BASE_URL}/admin/quizzes", json=quiz_data, headers=headers)
    print_response(response, "Create Quiz")
    
    if response.status_code != 201:
        print("Failed to create quiz, exiting...")
        return
        
    quiz_id = response.json()["id"]
    
    # Get quiz details
    response = requests.get(f"{BASE_URL}/admin/quizzes/{quiz_id}", headers=headers)
    print_response(response, "Get Quiz Details")
    
    # Get all users
    response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
    print_response(response, "Get All Users")
    
    print("\nAdmin workflow simulation complete!")

def simulate_user_workflow():
    print("\n=== USER WORKFLOW SIMULATION ===")
    
    # User registration
    register_data = {
        "email": "testuser@example.com",
        "password": "user123",
        "full_name": "Test User",
        "qualification": "BSc Computer Science",
        "date_of_birth": "1995-05-15"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print_response(response, "User Registration")
    
    if response.status_code == 400 and "already registered" in response.json().get("error", ""):
        print("User already registered, proceeding with login...")
    elif response.status_code != 201:
        print("User registration failed, exiting...")
        return
    
    # User login
    login_data = {
        "email": "testuser@example.com",
        "password": "user123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print_response(response, "User Login")
    
    if response.status_code != 200:
        print("User login failed, exiting...")
        return
    
    token = response.json()["access_token"]
    headers = get_auth_headers(token)
    
    # Get available subjects and quizzes
    response = requests.get(f"{BASE_URL}/user/subjects", headers=headers)
    print_response(response, "Get Available Subjects/Quizzes")
    
    if response.status_code != 200:
        print("Failed to get subjects, exiting...")
        return
    
    # Get quiz details
    quiz_id = 1  # Assuming we know the quiz ID from the admin workflow
    response = requests.get(f"{BASE_URL}/user/quizzes/{quiz_id}", headers=headers)
    print_response(response, "Get Quiz Details (User View)")
    
    if response.status_code != 200:
        print("Failed to get quiz details, exiting...")
        return
        
    quiz_details = response.json()
    
    # Simulate quiz attempt
    answers = []
    for question in quiz_details["questions"]:
        answers.append({
            "question_id": question["id"],
            "selected_option": 1  # Just selecting first option for simulation
        })
    
    attempt_data = {
        "answers": answers
    }
    response = requests.post(f"{BASE_URL}/user/quizzes/{quiz_id}/attempt", 
                            json=attempt_data, headers=headers)
    print_response(response, "Attempt Quiz")
    
    if response.status_code != 201:
        print("Failed to attempt quiz, exiting...")
        return
    
    # Get user's quiz attempts
    response = requests.get(f"{BASE_URL}/user/attempts", headers=headers)
    print_response(response, "Get User's Quiz Attempts")
    
    if response.status_code != 200 or not response.json():
        print("Failed to get quiz attempts, exiting...")
        return
        
    attempt_id = response.json()[0]["id"]
    
    # Get attempt details
    response = requests.get(f"{BASE_URL}/user/attempts/{attempt_id}", headers=headers)
    print_response(response, "Get Attempt Details")
    
    # Get user statistics
    response = requests.get(f"{BASE_URL}/user/stats", headers=headers)
    print_response(response, "Get User Statistics")
    
    print("\nUser workflow simulation complete!")

def test_quiz_attempt():
    print("\n=== TESTING QUIZ ATTEMPT ===")
    
    # First, login as a user
    login_data = {
        "email": "testuser@example.com",
        "password": "user123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print_response(response, "User Login")
    
    if response.status_code != 200:
        print("Login failed, exiting...")
        return
    
    token = response.json()["access_token"]
    headers = get_auth_headers(token)
    
    # Get quiz details first to get question IDs
    quiz_id = 1
    response = requests.get(f"{BASE_URL}/user/quizzes/{quiz_id}", headers=headers)
    print_response(response, "Get Quiz Details")
    
    if response.status_code != 200:
        print("Failed to get quiz details, exiting...")
        return
    
    quiz_details = response.json()
    
    # Create answers array with proper format
    answers = []
    for question in quiz_details["questions"]:
        answers.append({
            "question_id": question["id"],
            "selected_option": 1  # Just selecting first option for testing
        })
    
    # Make the quiz attempt
    attempt_data = {
        "answers": answers
    }
    response = requests.post(
        f"{BASE_URL}/user/quizzes/{quiz_id}/attempt",
        json=attempt_data,
        headers=headers
    )
    print_response(response, "Quiz Attempt")

def test_admin_user_management():
    print("\n=== TESTING ADMIN USER MANAGEMENT ===")
    
    # First, login as admin
    login_data = {
        "email": "admin@quizmaster.com",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/auth/admin/login", json=login_data)
    print_response(response, "Admin Login")
    
    if response.status_code != 200:
        print("Admin login failed, exiting...")
        return
    
    token = response.json()["access_token"]
    headers = get_auth_headers(token)
    
    # Get all users
    response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
    print_response(response, "Get All Users")
    
    if response.status_code != 200:
        print("Failed to get users list, exiting...")
        return
    
    users = response.json()
    if not users:
        print("No users found, exiting...")
        return
    
    # Get detailed information for the first user
    user_id = users[0]["id"]
    response = requests.get(f"{BASE_URL}/admin/users/{user_id}", headers=headers)
    print_response(response, "Get User Details")
    
    # Toggle user block status
    response = requests.post(f"{BASE_URL}/admin/users/{user_id}/block", headers=headers)
    print_response(response, "Toggle User Block Status")
    
    # Get updated user details
    response = requests.get(f"{BASE_URL}/admin/users/{user_id}", headers=headers)
    print_response(response, "Get Updated User Details")

if __name__ == "__main__":
    print("Starting Quiz Master Simulation...")
    
    try:
        # First simulate admin workflow to create data
        simulate_admin_workflow()
        
        # Then simulate user workflow to interact with the data
        simulate_user_workflow()
        
        # Then test quiz attempt
        test_quiz_attempt()
        
        # Finally test admin user management
        test_admin_user_management()
        
        print("\nAll tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the server. Make sure the Flask server is running.")
    except Exception as e:
        print(f"\nError: An unexpected error occurred: {str(e)}")