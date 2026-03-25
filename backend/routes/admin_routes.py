# routes/admin_routes.py - Admin Routes

from flask import Blueprint, request
from sqlalchemy import or_
from models import db, User, StudentProfile, CompanyProfile, PlacementDrive, Application
from utils import role_required, success_response, error_response

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


# ==============================
# DASHBOARD
# ==============================
@admin_bp.route("/dashboard", methods=["GET"])
@role_required("admin")
def admin_dashboard():
    """Get admin dashboard statistics"""
    stats = {
        "total_students": StudentProfile.query.count(),
        "total_companies": CompanyProfile.query.count(),
        "total_drives": PlacementDrive.query.count(),
        "total_applications": Application.query.count(),
        "pending_companies": CompanyProfile.query.filter_by(approval_status="Pending").count(),
        "pending_drives": PlacementDrive.query.filter_by(status="Pending").count(),
        "approved_drives": PlacementDrive.query.filter_by(status="Approved").count(),
        "closed_drives": PlacementDrive.query.filter_by(status="Closed").count(),
        "selected_students": Application.query.filter_by(status="Selected").count()
    }

    return success_response("Dashboard data retrieved", stats)


# ==============================
# COMPANIES
# ==============================
@admin_bp.route("/companies", methods=["GET"])
@role_required("admin")
def get_companies():
    """Get all companies with filtering and search"""
    status = request.args.get("status")  # Pending, Approved, Rejected
    search = request.args.get("search", "").strip()

    query = CompanyProfile.query

    if status:
        query = query.filter_by(approval_status=status)

    if search:
        query = query.filter(
            CompanyProfile.company_name.ilike(f"%{search}%")
        )

    companies = query.all()

    return success_response("Companies retrieved", [c.to_dict() for c in companies])


@admin_bp.route("/companies/<int:company_id>/approve", methods=["PUT"])
@role_required("admin")
def approve_company(company_id):
    """Approve company and auto-approve its drives"""
    company = CompanyProfile.query.get_or_404(company_id)

    company.approval_status = "Approved"

    # Auto-approve all pending drives
    for drive in company.drives:
        if drive.status == "Pending":
            drive.status = "Approved"

    db.session.commit()
    return success_response("Company and its drives approved successfully")


@admin_bp.route("/companies/<int:company_id>/reject", methods=["PUT"])
@role_required("admin")
def reject_company(company_id):
    """Reject company and reject all its drives"""
    company = CompanyProfile.query.get_or_404(company_id)

    company.approval_status = "Rejected"

    for drive in company.drives:
        drive.status = "Rejected"

    db.session.commit()
    return success_response("Company and its drives rejected successfully")


# ==============================
# STUDENTS
# ==============================
@admin_bp.route("/students", methods=["GET"])
@role_required("admin")
def get_students():
    """Get all students with filtering and search"""
    search = request.args.get("search", "").strip()
    branch = request.args.get("branch")
    year = request.args.get("year")

    query = StudentProfile.query.join(User)

    if search:
        query = query.filter(
            or_(
                StudentProfile.full_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )

    if branch:
        query = query.filter(StudentProfile.branch == branch)

    if year:
        query = query.filter(StudentProfile.year == int(year))

    students = query.all()

    return success_response("Students retrieved", [s.to_dict() for s in students])


# ==============================
# DRIVES
# ==============================
@admin_bp.route("/drives", methods=["GET"])
@role_required("admin")
def get_all_drives():
    """Get all drives with filtering and search"""
    status = request.args.get("status")  # Pending, Approved, Rejected, Closed
    search = request.args.get("search", "").strip()

    query = PlacementDrive.query.join(CompanyProfile)

    if status:
        query = query.filter(PlacementDrive.status == status)

    if search:
        query = query.filter(
            or_(
                PlacementDrive.job_title.ilike(f"%{search}%"),
                CompanyProfile.company_name.ilike(f"%{search}%")
            )
        )

    drives = query.all()

    return success_response("Drives retrieved", [d.to_dict() for d in drives])


@admin_bp.route("/drives/<int:drive_id>", methods=["GET"])
@role_required("admin")
def get_drive_details(drive_id):
    """Get detailed drive info"""
    drive = PlacementDrive.query.get_or_404(drive_id)
    return success_response("Drive details retrieved", drive.to_dict())


@admin_bp.route("/drives/<int:drive_id>/approve", methods=["PUT"])
@role_required("admin")
def approve_drive(drive_id):
    """Approve a drive (only if company approved)"""
    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.company.approval_status != "Approved":
        return error_response("Company not approved. Cannot approve drive.")

    drive.status = "Approved"
    db.session.commit()

    return success_response("Drive approved successfully")


@admin_bp.route("/drives/<int:drive_id>/reject", methods=["PUT"])
@role_required("admin")
def reject_drive(drive_id):
    """Reject a drive"""
    drive = PlacementDrive.query.get_or_404(drive_id)

    drive.status = "Rejected"
    db.session.commit()

    return success_response("Drive rejected successfully")


@admin_bp.route("/drives/<int:drive_id>/close", methods=["PUT"])
@role_required("admin")
def close_drive(drive_id):
    """Mark drive as closed/completed"""
    drive = PlacementDrive.query.get_or_404(drive_id)

    drive.status = "Closed"
    db.session.commit()

    return success_response("Drive marked as complete")


# ==============================
# APPLICATIONS
# ==============================
@admin_bp.route("/applications", methods=["GET"])
@role_required("admin")
def get_all_applications():
    """Get applications with filtering"""
    drive_id = request.args.get("drive_id", type=int)
    student_id = request.args.get("student_id", type=int)
    status = request.args.get("status")

    query = Application.query

    if drive_id:
        query = query.filter_by(drive_id=drive_id)

    if student_id:
        query = query.filter_by(student_id=student_id)

    if status:
        query = query.filter_by(status=status)

    applications = query.all()

    return success_response("Applications retrieved", [a.to_dict() for a in applications])


# ==============================
# USER MANAGEMENT
# ==============================
@admin_bp.route("/users/<int:user_id>/blacklist", methods=["PUT"])
@role_required("admin")
def blacklist_user(user_id):
    """Blacklist a user (company or student)"""
    user = User.query.get_or_404(user_id)

    user.is_blacklisted = True

    # If company → close all its drives
    if user.role == "company" and user.company_profile:
        for drive in user.company_profile.drives:
            drive.status = "Closed"

    db.session.commit()

    return success_response("User blacklisted successfully")


@admin_bp.route("/users/<int:user_id>/deactivate", methods=["PUT"])
@role_required("admin")
def deactivate_user(user_id):
    """Deactivate a user"""
    user = User.query.get_or_404(user_id)

    user.is_active = False
    db.session.commit()

    return success_response("User deactivated successfully")
