# models.py - Database Models

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()



# USER MODEL


class User(db.Model):
    """Unified user model for all roles (admin, company, student)"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), nullable=False)  # admin, company, student
    is_active = db.Column(db.Boolean, default=True)
    is_blacklisted = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student_profile = db.relationship(
        "StudentProfile",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    company_profile = db.relationship(
        "CompanyProfile",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "is_blacklisted": self.is_blacklisted
        }



# COMPANY PROFILE


class CompanyProfile(db.Model):
    """Company profile details"""
    __tablename__ = "company_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    company_name = db.Column(db.String(200), nullable=False)
    hr_contact = db.Column(db.String(200))
    website = db.Column(db.String(200))
    description = db.Column(db.Text)

    approval_status = db.Column(
        db.String(20),
        default="Pending"
    )  # Pending/Approved/Rejected

    # Relationships
    drives = db.relationship(
        "PlacementDrive",
        backref="company",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "company_name": self.company_name,
            "hr_contact": self.hr_contact,
            "website": self.website,
            "description": self.description,
            "approval_status": self.approval_status
        }


# STUDENT PROFILE


class StudentProfile(db.Model):
    """Student profile details"""
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    full_name = db.Column(db.String(200), nullable=False)
    branch = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    year = db.Column(db.Integer)
    phone = db.Column(db.String(20))

    resume_path = db.Column(db.String(255))

    # Relationships
    applications = db.relationship(
        "Application",
        backref="student",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "full_name": self.full_name,
            "email": self.user.email,
            "branch": self.branch,
            "cgpa": self.cgpa,
            "year": self.year,
            "phone": self.phone,
            "resume_path": self.resume_path
        }



# PLACEMENT DRIVE


class PlacementDrive(db.Model):
    """Placement drive/job posting"""
    __tablename__ = "placement_drives"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(
        db.Integer,
        db.ForeignKey("company_profiles.id", ondelete="CASCADE"),
        nullable=False
    )

    job_title = db.Column(db.String(200), nullable=False)
    job_description = db.Column(db.Text)

    min_cgpa = db.Column(db.Float, default=0.0)
    allowed_branches = db.Column(db.String(200))  # "CSE,ECE,IT"
    allowed_years = db.Column(db.String(50))      # "3,4"

    application_deadline = db.Column(db.Date, nullable=False)
    status = db.Column(
        db.String(20),
        default="Pending"
    )  # Pending/Approved/Rejected/Closed

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    applications = db.relationship(
        "Application",
        backref="drive",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "company_name": self.company.company_name,
            "job_title": self.job_title,
            "job_description": self.job_description,
            "min_cgpa": self.min_cgpa,
            "allowed_branches": self.allowed_branches,
            "allowed_years": self.allowed_years,
            "application_deadline": self.application_deadline.isoformat()
                if self.application_deadline else None,
            "status": self.status,
            "created_at": self.created_at.isoformat()
                if self.created_at else None,
            "total_applications": len(self.applications)
        }



# APPLICATION MODEL


class Application(db.Model):
    """Student application to placement drive"""
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False
    )
    drive_id = db.Column(
        db.Integer,
        db.ForeignKey("placement_drives.id", ondelete="CASCADE"),
        nullable=False
    )

    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(
        db.String(20),
        default="Applied"
    )  

    notes = db.Column(db.Text)

    __table_args__ = (
        db.UniqueConstraint(
            "student_id",
            "drive_id",
            name="unique_application"
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "drive_id": self.drive_id,
            "status": self.status,
            "notes": self.notes,
            "applied_on": self.applied_on.isoformat()
                if self.applied_on else None,

            "student": {
                "id": self.student.id,
                "full_name": self.student.full_name,
                "email": self.student.user.email,
                "branch": self.student.branch,
                "year": self.student.year,
                "cgpa": self.student.cgpa,
                "phone": self.student.phone,
                "resume_url": f"/api/company/resume/{self.student.id}"
                    if self.student.resume_path else None
            },

            "drive": {
                "id": self.drive.id,
                "job_title": self.drive.job_title,
                "company_name": self.drive.company.company_name
            }
        }
