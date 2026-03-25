# routes/student_routes.py

from flask import Blueprint, request, jsonify, send_from_directory
from models import db, PlacementDrive, Application, StudentProfile, CompanyProfile
from utils import role_required, get_current_user, check_eligibility, success_response, error_response
from datetime import date
from werkzeug.utils import secure_filename
import os

student_bp = Blueprint("student", __name__, url_prefix="/api/student")


@student_bp.route("/profile", methods=["GET"])
@role_required("student")
def get_student_profile():
    user = get_current_user()
    student = user.student_profile
    if not student:
        return error_response("Student profile not found", 404)
    return success_response("Profile retrieved", student.to_dict())


@student_bp.route("/profile", methods=["PUT"])
@role_required("student")
def update_student_profile():
    user = get_current_user()
    student = user.student_profile
    if not student:
        return error_response("Student profile not found", 404)
    data = request.get_json()
    if "full_name" in data: student.full_name = data["full_name"]
    if "branch" in data: student.branch = data["branch"]
    if "cgpa" in data: student.cgpa = float(data["cgpa"])
    if "year" in data: student.year = int(data["year"])
    if "phone" in data: student.phone = data["phone"]
    db.session.commit()
    return success_response("Profile updated", student.to_dict())


@student_bp.route("/dashboard", methods=["GET"])
@role_required("student")
def student_dashboard():
    user = get_current_user()
    student = user.student_profile
    if not student:
        return error_response("Student profile not found", 404)
    available_drives = PlacementDrive.query.filter(
        PlacementDrive.status == "Approved",
        PlacementDrive.application_deadline >= date.today()
    ).all()
    my_applications = Application.query.filter_by(student_id=student.id).all()
    applied_drive_ids = {app.drive_id for app in my_applications}
    eligible_drives = []
    for drive in available_drives:
        eligible, message = check_eligibility(student, drive)
        eligible_drives.append({**drive.to_dict(), "eligible": eligible, "eligibility_message": message, "already_applied": drive.id in applied_drive_ids})
    dashboard = {
        "student": student.to_dict(),
        "available_drives": eligible_drives,
        "my_applications": [a.to_dict() for a in my_applications],
        "total_applications": len(my_applications),
        "selected_count": len([a for a in my_applications if a.status == "Selected"])
    }
    return success_response("Dashboard data", dashboard)


@student_bp.route("/drives", methods=["GET"])
@role_required("student")
def get_available_drives():
    user = get_current_user()
    student = user.student_profile
    search = request.args.get("search", "")
    branch = request.args.get("branch")
    query = PlacementDrive.query.filter(
        PlacementDrive.status == "Approved",
        PlacementDrive.application_deadline >= date.today()
    )
    if search:
        query = query.filter(PlacementDrive.job_title.ilike(f"%{search}%"))
    if branch:
        query = query.filter(PlacementDrive.allowed_branches.like(f"%{branch}%"))
    drives = query.all()
    my_applications = Application.query.filter_by(student_id=student.id).all()
    applied_drive_ids = {app.drive_id for app in my_applications}
    result = []
    for drive in drives:
        eligible, message = check_eligibility(student, drive)
        result.append({**drive.to_dict(), "eligible": eligible, "eligibility_message": message, "already_applied": drive.id in applied_drive_ids})
    return success_response("Drives retrieved", result)


@student_bp.route("/apply/<int:drive_id>", methods=["POST"])
@role_required("student")
def apply_to_drive(drive_id):
    user = get_current_user()
    student = user.student_profile
    if not student:
        return error_response("Student profile not found", 404)
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.status != "Approved":
        return error_response("Drive is not approved", 400)
    if drive.application_deadline < date.today():
        return error_response("Application deadline has passed", 400)
    eligible, message = check_eligibility(student, drive)
    if not eligible:
        return error_response(f"Not eligible: {message}", 400)
    existing = Application.query.filter_by(student_id=student.id, drive_id=drive_id).first()
    if existing:
        return error_response("Already applied to this drive", 400)
    try:
        application = Application(student_id=student.id, drive_id=drive_id)
        db.session.add(application)
        db.session.commit()
        return success_response("Applied successfully", application.to_dict(), 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Application failed: {str(e)}", 500)


@student_bp.route("/applications", methods=["GET"])
@role_required("student")
def get_my_applications():
    user = get_current_user()
    student = user.student_profile
    applications = Application.query.filter_by(student_id=student.id).all()
    return success_response("Applications retrieved", [a.to_dict() for a in applications])


@student_bp.route("/resume/upload", methods=["POST"])
@role_required("student")
def upload_resume():
    user = get_current_user()
    student = user.student_profile
    if not student:
        return error_response("Student profile not found", 404)
    if 'resume' not in request.files:
        return error_response("No file provided", 400)
    file = request.files['resume']
    if file.filename == '':
        return error_response("No file selected", 400)
    allowed_extensions = {'pdf', 'docx', 'doc'}
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if ext not in allowed_extensions:
        return error_response("Only PDF and DOCX files are allowed", 400)
    
    # Use absolute path based on app.py location
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    upload_dir = os.path.join(base_dir, 'uploads', 'resumes')
    os.makedirs(upload_dir, exist_ok=True)
    
    filename = secure_filename(f"resume_student_{student.id}.{ext}")
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)
    
    student.resume_path = filepath
    db.session.commit()
    
    return success_response("Resume uploaded successfully", {
        "resume_path": filepath,
        "filename": filename
    })


@student_bp.route("/resume/download", methods=["GET"])
@role_required("student")
def download_resume():
    user = get_current_user()
    student = user.student_profile
    if not student:
        return error_response("Student profile not found", 404)
    if not student.resume_path:
        return error_response("No resume found", 404)
    
    resume_path = student.resume_path
    if not os.path.isabs(resume_path):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        resume_path = os.path.join(base_dir, resume_path)
    
    if not os.path.exists(resume_path):
        return error_response("Resume file not found", 404)
    
    directory = os.path.dirname(resume_path)
    filename = os.path.basename(resume_path)
    return send_from_directory(directory, filename, as_attachment=True)


@student_bp.route("/resume/<int:student_id>", methods=["GET"])
def view_student_resume(student_id):
    """Public endpoint to view a student's resume (used by admin/company)"""
    student = StudentProfile.query.get_or_404(student_id)
    if not student.resume_path:
        return error_response("No resume found", 404)
    
    resume_path = student.resume_path
    if not os.path.isabs(resume_path):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        resume_path = os.path.join(base_dir, resume_path)
    
    if not os.path.exists(resume_path):
        return error_response("Resume file not found", 404)
    
    directory = os.path.dirname(resume_path)
    filename = os.path.basename(resume_path)
    return send_from_directory(directory, filename, as_attachment=False)


@student_bp.route("/companies", methods=["GET"])
@role_required("student")
def get_all_companies():
    """Get all approved companies for Organizations section"""
    companies = CompanyProfile.query.filter_by(approval_status="Approved").all()
    result = []
    for company in companies:
        result.append({
            "id": company.id,
            "company_name": company.company_name,
            "website": company.website,
            "description": company.description,
            "hr_contact": company.hr_contact
        })
    return success_response("Companies retrieved", result)


@student_bp.route("/companies/<int:company_id>", methods=["GET"])
@role_required("student")
def get_company_with_drives(company_id):
    company = CompanyProfile.query.filter_by(id=company_id, approval_status="Approved").first_or_404()
    drives = PlacementDrive.query.filter(
        PlacementDrive.company_id == company.id,
        PlacementDrive.status == "Approved",
        PlacementDrive.application_deadline >= date.today()
    ).all()
    return success_response("Company details retrieved", {
        "company": company.to_dict(),
        "drives": [drive.to_dict() for drive in drives]
    })


@student_bp.route("/history", methods=["GET"])
@role_required("student")
def student_history():
    user = get_current_user()
    student = user.student_profile
    applications = Application.query.filter_by(student_id=student.id).all()
    result = []
    for app in applications:
        drive = app.drive
        company = drive.company
        result.append({
            "application_id": app.id,
            "drive_id": drive.id,
            "job_title": drive.job_title,
            "company_name": company.company_name,
            "status": app.status,
            "notes": app.notes,
            "applied_on": app.applied_on.isoformat()
        })
    return success_response("History retrieved", result)


@student_bp.route("/drive/<int:drive_id>", methods=["GET"])
@role_required("student")
def get_drive_details(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.status != "Approved":
        return error_response("Drive not available", 404)
    return success_response("Drive details retrieved", drive.to_dict())
