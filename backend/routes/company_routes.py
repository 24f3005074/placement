# routes/company_routes.py

from flask import Blueprint, request, send_from_directory
from models import db, PlacementDrive, Application, CompanyProfile, StudentProfile
from utils import role_required, get_current_user, success_response, error_response
from datetime import datetime, date
import os

company_bp = Blueprint("company", __name__, url_prefix="/api/company")


@company_bp.route("/profile", methods=["GET"])
@role_required("company")
def get_company_profile():
    user = get_current_user()
    company = user.company_profile
    if not company:
        return error_response("Company profile not found", 404)
    return success_response("Profile retrieved", company.to_dict())


@company_bp.route("/profile", methods=["PUT"])
@role_required("company")
def update_company_profile():
    user = get_current_user()
    company = user.company_profile
    if not company:
        return error_response("Company profile not found", 404)
    data = request.get_json()
    company.company_name = data.get("company_name", company.company_name)
    company.hr_contact = data.get("hr_contact", company.hr_contact)
    company.website = data.get("website", company.website)
    company.description = data.get("description", company.description)
    db.session.commit()
    return success_response("Profile updated", company.to_dict())


@company_bp.route("/dashboard", methods=["GET"])
@role_required("company")
def company_dashboard():
    user = get_current_user()
    company = user.company_profile
    if not company:
        return error_response("Company profile not found", 404)
    drives = PlacementDrive.query.filter_by(company_id=company.id).all()
    dashboard = {
        "company": company.to_dict(),
        "total_drives": len(drives),
        "pending_drives": len([d for d in drives if d.status == "Pending"]),
        "approved_drives": len([d for d in drives if d.status == "Approved"]),
        "closed_drives": len([d for d in drives if d.status == "Closed"]),
        "total_applications": sum(len(d.applications) for d in drives)
    }
    return success_response("Dashboard data retrieved", dashboard)


@company_bp.route("/drives", methods=["POST"])
@role_required("company")
def create_drive():
    user = get_current_user()
    company = user.company_profile
    if not company:
        return error_response("Company profile not found", 404)
    if company.approval_status != "Approved":
        return error_response("Company not approved by admin", 403)
    data = request.get_json()
    required = ["job_title", "job_description", "application_deadline"]
    if not all(field in data for field in required):
        return error_response("Missing required fields: job_title, job_description, application_deadline", 400)
    try:
        deadline = datetime.strptime(data["application_deadline"], "%Y-%m-%d").date()
        if deadline < date.today():
            return error_response("Deadline cannot be in the past", 400)
        drive = PlacementDrive(
            company_id=company.id,
            job_title=data["job_title"],
            job_description=data["job_description"],
            min_cgpa=float(data.get("min_cgpa", 0.0)),
            allowed_branches=data.get("allowed_branches", ""),
            allowed_years=data.get("allowed_years", ""),
            application_deadline=deadline,
            status="Approved"  # Auto-approve for approved company
        )
        db.session.add(drive)
        db.session.commit()
        return success_response("Drive created successfully", drive.to_dict(), 201)
    except ValueError as e:
        return error_response(f"Invalid date format: {str(e)}", 400)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@company_bp.route("/drives", methods=["GET"])
@role_required("company")
def get_company_drives():
    user = get_current_user()
    company = user.company_profile
    if not company:
        return error_response("Company profile not found", 404)
    drives = PlacementDrive.query.filter_by(company_id=company.id).all()
    today = date.today()
    upcoming = []
    closed = []
    for drive in drives:
        d = drive.to_dict()
        if drive.status == "Approved" and drive.application_deadline >= today:
            upcoming.append(d)
        else:
            closed.append(d)
    return success_response("Drives retrieved", {"upcoming": upcoming, "closed": closed})


@company_bp.route("/drives/<int:drive_id>", methods=["GET"])
@role_required("company")
def get_drive_details(drive_id):
    user = get_current_user()
    company = user.company_profile
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id != company.id:
        return error_response("Unauthorized", 403)
    return success_response("Drive details retrieved", drive.to_dict())


@company_bp.route("/drives/<int:drive_id>", methods=["PUT"])
@role_required("company")
def update_drive(drive_id):
    user = get_current_user()
    company = user.company_profile
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id != company.id:
        return error_response("Unauthorized", 403)
    data = request.get_json()
    drive.job_title = data.get("job_title", drive.job_title)
    drive.job_description = data.get("job_description", drive.job_description)
    drive.min_cgpa = float(data.get("min_cgpa", drive.min_cgpa))
    drive.allowed_branches = data.get("allowed_branches", drive.allowed_branches)
    drive.allowed_years = data.get("allowed_years", drive.allowed_years)
    if "application_deadline" in data:
        try:
            deadline = datetime.strptime(data["application_deadline"], "%Y-%m-%d").date()
            drive.application_deadline = deadline
        except ValueError:
            return error_response("Invalid date format. Use YYYY-MM-DD", 400)
    db.session.commit()
    return success_response("Drive updated successfully", drive.to_dict())


@company_bp.route("/drives/<int:drive_id>/complete", methods=["PUT"])
@role_required("company")
def mark_drive_complete(drive_id):
    user = get_current_user()
    company = user.company_profile
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id != company.id:
        return error_response("Unauthorized", 403)
    drive.status = "Closed"
    db.session.commit()
    return success_response("Drive marked as completed", drive.to_dict())


# Keep /close alias for backward compat
@company_bp.route("/drives/<int:drive_id>/close", methods=["PUT"])
@role_required("company")
def mark_drive_close(drive_id):
    user = get_current_user()
    company = user.company_profile
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id != company.id:
        return error_response("Unauthorized", 403)
    drive.status = "Closed"
    db.session.commit()
    return success_response("Drive marked as completed", drive.to_dict())


@company_bp.route("/drives/<int:drive_id>/applications", methods=["GET"])
@role_required("company")
def get_drive_applications(drive_id):
    user = get_current_user()
    company = user.company_profile
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id != company.id:
        return error_response("Unauthorized", 403)
    applications = Application.query.filter_by(drive_id=drive.id).all()
    return success_response("Applications retrieved", [app.to_dict() for app in applications])


@company_bp.route("/applications/<int:application_id>/status", methods=["PUT"])
@role_required("company")
def update_application_status(application_id):
    user = get_current_user()
    company = user.company_profile
    application = Application.query.get_or_404(application_id)
    if application.drive.company_id != company.id:
        return error_response("Unauthorized", 403)
    data = request.get_json()
    valid_statuses = ["Applied", "Shortlisted", "Waiting", "Selected", "Rejected"]
    if "status" not in data:
        return error_response("Status is required", 400)
    if data["status"] not in valid_statuses:
        return error_response(f"Invalid status. Must be one of {valid_statuses}", 400)
    application.status = data["status"]
    application.notes = data.get("notes", application.notes)
    db.session.commit()
    return success_response("Application status updated", application.to_dict())


@company_bp.route("/resume/<int:student_id>", methods=["GET"])
@role_required("company")
def download_student_resume(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    if not student.resume_path:
        return error_response("Resume not found", 404)
    # Handle absolute and relative paths
    resume_path = student.resume_path
    if not os.path.isabs(resume_path):
        resume_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), resume_path)
    if not os.path.exists(resume_path):
        return error_response("Resume file not found on server", 404)
    directory = os.path.dirname(resume_path)
    filename = os.path.basename(resume_path)
    return send_from_directory(directory, filename, as_attachment=False)
