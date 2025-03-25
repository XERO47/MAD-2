from flask import request, jsonify
from flask_jwt_extended import create_access_token
from app.models import User
from app import db
from datetime import datetime

def register():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'full_name', 'qualification', 'date_of_birth']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new user
    user = User(
        email=data['email'],
        full_name=data['full_name'],
        qualification=data['qualification'],
        date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'is_admin': user.is_admin
            }
        }), 200
    
    return jsonify({'error': 'Invalid email or password'}), 401

def admin_login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400
    
    user = User.query.filter_by(email=data['email'], is_admin=True).first()
    
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'is_admin': True
            }
        }), 200
    
    return jsonify({'error': 'Invalid admin credentials'}), 401 