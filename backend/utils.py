# utils.py - Utility Functions and Decorators

from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request
from models import User, StudentProfile, PlacementDrive
import os
from werkzeug.utils import secure_filename
from datetime import datetime




# AUTHENTICATION DECORATORS


def role_required(role):
    """Decorator to require specific role for access"""
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user:
                return jsonify({"error": "User not found"}), 404
            
            if user.role != role:
                return jsonify({"error": "Unauthorized - insufficient privileges"}), 403
            
            if not user.is_active:
                return jsonify({"error": "Account deactivated"}), 403
            
            if user.is_blacklisted:
                return jsonify({"error": "Account blacklisted"}), 403

            return fn(*args, **kwargs)
        return decorator
    return wrapper


def get_current_user():
    """Get current authenticated user"""
    verify_jwt_in_request()
    user_id = get_jwt_identity()
    return User.query.get(user_id)


# ============================================
# VALIDATION HELPERS
# ============================================

def validate_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_cgpa(cgpa):
    """Validate CGPA (0-10 scale)"""
    try:
        cgpa = float(cgpa)
        return 0.0 <= cgpa <= 10.0
    except (ValueError, TypeError):
        return False


def check_eligibility(student, drive):
    """Check if student is eligible for a placement drive"""
    # Check CGPA
    if drive.min_cgpa and student.cgpa < drive.min_cgpa:
        return False, f"Minimum CGPA required: {drive.min_cgpa}"
    
    # Check branch
    if drive.allowed_branches:
        allowed = [b.strip() for b in drive.allowed_branches.split(",")]
        if student.branch not in allowed:
            return False, f"Branch not allowed. Allowed: {drive.allowed_branches}"
    
    # Check year
    if drive.allowed_years:
        allowed = [int(y.strip()) for y in drive.allowed_years.split(",")]
        if student.year not in allowed:
            return False, f"Year not allowed. Allowed: {drive.allowed_years}"
    
    return True, "Eligible"


# ============================================
# FILE UPLOAD HELPERS
# ============================================

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_resume(file, student_id, upload_folder):
    """Save resume file and return path"""
    if not file:
        return None
    
    if not allowed_file(file.filename, {"pdf", "doc", "docx"}):
        return None
    
    # Create upload folder if it doesn't exist
    os.makedirs(upload_folder, exist_ok=True)
    
    # Generate secure filename
    filename = secure_filename(file.filename)
    file_ext = filename.rsplit('.', 1)[1].lower()
    new_filename = f"resume_{student_id}_{int(datetime.now().timestamp())}.{file_ext}"
    
    filepath = os.path.join(upload_folder, new_filename)
    file.save(filepath)
    
    return filepath


# ============================================
# PAGINATION HELPER
# ============================================

def paginate(query, page=1, per_page=10):
    """Paginate query results"""
    try:
        page = int(page)
        per_page = int(per_page)
    except (ValueError, TypeError):
        page = 1
        per_page = 10
    
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 10
    
    items = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return {
        "items": items.items,
        "total": items.total,
        "page": page,
        "per_page": per_page,
        "pages": items.pages,
        "has_next": items.has_next,
        "has_prev": items.has_prev
    }



# RESPONSE HELPERS


def success_response(message, data=None, status=200):
    """Standard success response"""
    response = {"success": True, "message": message}
    if data:
        response["data"] = data
    return jsonify(response), status


def error_response(message, status=400):
    """Standard error response"""
    return jsonify({"success": False, "error": message}), status



# CSV EXPORT HELPER


def generate_applications_csv(applications, filepath):
    """Generate CSV file from applications"""
    import csv
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        # Header
        writer.writerow([
            "Application ID",
            "Student Name",
            "Student Email",
            "Branch",
            "CGPA",
            "Company Name",
            "Job Title",
            "Application Date",
            "Status"
        ])
        
        # Data rows
        for app in applications:
            writer.writerow([
                app.id,
                app.student.full_name,
                app.student.user.email,
                app.student.branch,
                app.student.cgpa,
                app.drive.company.company_name,
                app.drive.job_title,
                app.applied_on.strftime("%Y-%m-%d %H:%M:%S"),
                app.status
            ])
    
    return filepath



# HTML REPORT GENERATOR


def generate_monthly_report_html(data):
    """Generate HTML monthly report"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Monthly Placement Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                margin: 30px 0;
            }}
            .stat-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
            }}
            .stat-card h3 {{
                margin: 0;
                font-size: 36px;
            }}
            .stat-card p {{
                margin: 10px 0 0 0;
                font-size: 16px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #3498db;
                color: white;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            .footer {{
                margin-top: 30px;
                text-align: center;
                color: #7f8c8d;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Monthly Placement Report - {data['month']}</h1>
            
            <div class="stats">
                <div class="stat-card">
                    <h3>{data['total_drives']}</h3>
                    <p>Total Drives</p>
                </div>
                <div class="stat-card">
                    <h3>{data['total_applications']}</h3>
                    <p>Total Applications</p>
                </div>
                <div class="stat-card">
                    <h3>{data['students_selected']}</h3>
                    <p>Students Selected</p>
                </div>
                <div class="stat-card">
                    <h3>{data['active_companies']}</h3>
                    <p>Active Companies</p>
                </div>
            </div>
            
            <h2>Top Performing Companies</h2>
            <table>
                <thead>
                    <tr>
                        <th>Company Name</th>
                        <th>Total Drives</th>
                        <th>Total Applications</th>
                        <th>Students Selected</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(f"<tr><td>{c['name']}</td><td>{c['drives']}</td><td>{c['applications']}</td><td>{c['selected']}</td></tr>" for c in data.get('top_companies', []))}
                </tbody>
            </table>
            
            <div class="footer">
                <p>Generated on {data['generated_on']}</p>
                <p>Placement Portal - Institute Placement Cell</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html
