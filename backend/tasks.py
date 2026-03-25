# tasks.py - Celery Background Tasks

from celery import Celery
from celery.schedules import crontab
from datetime import datetime, date, timedelta
from models import db, PlacementDrive, Application, StudentProfile, User, CompanyProfile
from utils import generate_applications_csv, generate_monthly_report_html
import os

# Celery instance (will be configured by app)
celery = Celery(__name__)



# DAILY DEADLINE REMINDERS


@celery.task(name="tasks.send_daily_reminders")
def send_daily_reminders():
    """
    Send daily reminders to students about upcoming deadlines.
    Runs daily at 9:00 AM.
    """
    tomorrow = date.today() + timedelta(days=1)
    
    # Get drives with deadline tomorrow
    upcoming_drives = PlacementDrive.query.filter(
        PlacementDrive.application_deadline == tomorrow,
        PlacementDrive.status == "Approved"
    ).all()
    
    if not upcoming_drives:
        return "No upcoming deadlines"
    
    # Get all students
    students = StudentProfile.query.all()
    
    reminders_sent = 0
    
    for drive in upcoming_drives:
        for student in students:
            # Check if student hasn't applied yet
            existing_app = Application.query.filter_by(
                student_id=student.id,
                drive_id=drive.id
            ).first()
            
            if not existing_app:
                message = f"""
                Reminder: Application deadline tomorrow!
                
                Drive: {drive.job_title}
                Company: {drive.company.company_name}
                Deadline: {drive.application_deadline.strftime('%B %d, %Y')}
                
                Apply now at the placement portal!
                """
                
                send_notification(
                    student.user.email,
                    "Application Deadline Reminder - Tomorrow",
                    message,
                    channel="email"
                )
                
                reminders_sent += 1
    
    return f"Sent {reminders_sent} deadline reminders"



# MONTHLY ACTIVITY REPORT


@celery.task(name="tasks.generate_monthly_report")
def generate_monthly_report():
    """
    Generate and send monthly placement activity report to admin.
    Runs on the 1st day of every month at 8:00 AM.
    """
    # Get previous month's data
    today = date.today()
    first_day_this_month = today.replace(day=1)
    last_day_prev_month = first_day_this_month - timedelta(days=1)
    first_day_prev_month = last_day_prev_month.replace(day=1)
    
    # Query data for previous month
    drives_last_month = PlacementDrive.query.filter(
        PlacementDrive.created_at >= first_day_prev_month,
        PlacementDrive.created_at < first_day_this_month
    ).all()
    
    applications_last_month = Application.query.filter(
        Application.applied_on >= first_day_prev_month,
        Application.applied_on < first_day_this_month
    ).all()
    
    selected_last_month = [a for a in applications_last_month if a.status == "Selected"]
    
    # Get company statistics
    company_stats = {}
    for app in applications_last_month:
        company_name = app.drive.company.company_name
        if company_name not in company_stats:
            company_stats[company_name] = {
                "name": company_name,
                "drives": set(),
                "applications": 0,
                "selected": 0
            }
        company_stats[company_name]["drives"].add(app.drive_id)
        company_stats[company_name]["applications"] += 1
        if app.status == "Selected":
            company_stats[company_name]["selected"] += 1
    
    # Convert to list and sort by selections
    top_companies = [
        {
            "name": stats["name"],
            "drives": len(stats["drives"]),
            "applications": stats["applications"],
            "selected": stats["selected"]
        }
        for stats in sorted(company_stats.values(), key=lambda x: x["selected"], reverse=True)
    ]
    
    data = {
        "month": last_day_prev_month.strftime("%B %Y"),
        "total_drives": len(drives_last_month),
        "total_applications": len(applications_last_month),
        "students_selected": len(selected_last_month),
        "active_companies": len(company_stats),
        "top_companies": top_companies[:5],
        "generated_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    report_html = generate_monthly_report_html(data)
    
    send_notification(
        config.ADMIN_EMAIL or "admin@placement.com",
        f"Monthly Placement Report - {data['month']}",
        "Monthly report generated. (HTML content would be attached in production email)",
        channel="email"
    )
    
    return "Monthly report generated and notification sent"


# STUDENT APPLICATION EXPORT


@celery.task(name="tasks.export_student_applications")
def export_student_applications_task(student_id):
    """
    Export student's application history as CSV.
    This is triggered by the student from their dashboard.
    """
    student = StudentProfile.query.get(student_id)
    
    if not student:
        return f"Student {student_id} not found"
    
    # Get all applications
    applications = Application.query.filter_by(student_id=student_id).all()
    
    if not applications:
        return "No applications to export"
    
    # Generate CSV
    exports_dir = "exports/applications"
    os.makedirs(exports_dir, exist_ok=True)
    
    filename = f"student_{student_id}_applications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(exports_dir, filename)
    
    generate_applications_csv(applications, filepath)
    
    send_notification(
        student.user.email,
        "Your Application History Export is Ready",
        f"Your application history has been exported as CSV.\nServer file path: {filepath}\n(In production: download link would be provided)",
        channel="email"
    )
    
    return f"Applications exported: {filepath}"



# AUTO-CLOSE EXPIRED DRIVES


@celery.task(name="tasks.auto_close_expired_drives")
def auto_close_expired_drives():
    """
    Automatically close drives whose deadline has passed.
    Runs every day at midnight.
    """
    today = date.today()
    
    expired_drives = PlacementDrive.query.filter(
        PlacementDrive.application_deadline < today,
        PlacementDrive.status == "Approved"
    ).all()
    
    closed_count = 0
    for drive in expired_drives:
        drive.status = "Closed"
        closed_count += 1
    
    if closed_count > 0:
        db.session.commit()
    
    return f"Closed {closed_count} expired drives"


# CELERY BEAT SCHEDULE (Periodic Tasks)

celery.conf.beat_schedule = {
    # Daily reminders at 9:00 AM
    "send-daily-reminders": {
        "task": "tasks.send_daily_reminders",
        "schedule": crontab(hour=9, minute=0),
    },
    
    # Monthly report on 1st of every month at 8:00 AM
    "generate-monthly-report": {
        "task": "tasks.generate_monthly_report",
        "schedule": crontab(day_of_month=1, hour=8, minute=0),
    },
    
    # Auto-close expired drives daily at midnight
    "auto-close-expired-drives": {
        "task": "tasks.auto_close_expired_drives",
        "schedule": crontab(hour=0, minute=0),
    },
}

celery.conf.timezone = "UTC"



# HELPER: Notification sender (improved simulation)


def send_notification(to, subject, body, channel="email"):
    """
    Unified notification sender
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"[{timestamp}] NOTIFICATION SENT ({channel.upper()}) → {to}"
    print("=" * 70)
    print(header)
    print(f"Subject: {subject}")
    print("-" * 70)
    print(body.strip())
    print("=" * 70 + "\n")
    return True