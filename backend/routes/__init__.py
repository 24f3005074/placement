# routes/__init__.py - Routes Package Initialization

from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.company_routes import company_bp
from routes.student_routes import student_bp
from routes.drive_routes import drive_bp

__all__ = ['auth_bp', 'admin_bp', 'company_bp', 'student_bp', 'drive_bp']
