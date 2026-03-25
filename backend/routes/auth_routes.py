from flask import Blueprint, request, jsonify
from models import db, User, StudentProfile, CompanyProfile
from werkzeug.security import generate_password_hash
from utils import success_response, error_response
from flask_jwt_extended import create_access_token


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return error_response("Email and password required", 400)
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return error_response("Invalid credentials", 401)
    
    if user.is_blacklisted:
        return error_response("Account has been blacklisted", 403)
    
    token = create_access_token(identity=user.id)
    
    return success_response("Login successful", {
        "access_token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    })


@auth_bp.route("/register/student", methods=["POST"])
def register_student():
    data = request.get_json()
    
    required_fields = ["username", "email", "password", "full_name", "branch", "cgpa", "year"]
    for field in required_fields:
        if field not in data:
            return error_response(f"Missing field: {field}", 400)
    
    if User.query.filter_by(email=data["email"]).first():
        return error_response("Email already registered", 400)
    
    if User.query.filter_by(username=data["username"]).first():
        return error_response("Username already taken", 400)
    
    try:
        user = User(
            username=data["username"],
            email=data["email"],
            role="student"
        )
        user.set_password(data["password"])
        
        db.session.add(user)
        db.session.flush()
        
        student = StudentProfile(
            user_id=user.id,
            full_name=data["full_name"],
            branch=data["branch"],
            cgpa=float(data["cgpa"]),
            year=int(data["year"]),
            phone=data.get("phone", "")
        )
        
        db.session.add(student)
        db.session.commit()
        
        return success_response("Student registered successfully", {
            "user_id": user.id
        }, 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"Registration failed: {str(e)}", 500)


@auth_bp.route("/register/company", methods=["POST"])
def register_company():
    data = request.get_json()
    
    required_fields = ["username", "email", "password", "company_name"]
    for field in required_fields:
        if field not in data:
            return error_response(f"Missing field: {field}", 400)
    
    if User.query.filter_by(email=data["email"]).first():
        return error_response("Email already registered", 400)
    
    if User.query.filter_by(username=data["username"]).first():
        return error_response("Username already taken", 400)
    
    try:
        user = User(
            username=data["username"],
            email=data["email"],
            role="company"
        )
        user.set_password(data["password"])
        
        db.session.add(user)
        db.session.flush()
        
        company = CompanyProfile(
            user_id=user.id,
            company_name=data["company_name"],
            hr_contact=data.get("hr_contact", ""),
            website=data.get("website", ""),
            description=data.get("description", "")
        )
        
        db.session.add(company)
        db.session.commit()
        
        return success_response("Company registered successfully. Awaiting admin approval.", {
            "user_id": user.id
        }, 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"Registration failed: {str(e)}", 500)