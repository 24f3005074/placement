from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from flask_cors import CORS
from models import db, User
from config import config
from tasks import celery
import os


def create_app(config_name="development"):
    """Application factory"""
    app = Flask(__name__)
    
    app.config.from_object(config[config_name])
    

    db.init_app(app)
    jwt = JWTManager(app)
    cache = Cache(app)
    CORS(app) 
    

    celery.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"],
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )
    

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    

    from routes import auth_bp, admin_bp, company_bp, student_bp, drive_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(drive_bp)
    

    with app.app_context():
        db.create_all()
        create_admin_user()
        create_upload_directories()
    

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500
    

    @app.route("/")
    def index():
        return jsonify({
            "message": "Placement Portal API",
            "version": "2.0",
            "status": "running",
            "structure": "separate_routes"
        })
    
    @app.route("/health")
    def health():
        return jsonify({"status": "healthy"}), 200
    
    return app


def create_admin_user():
    """Create default admin user if doesn't exist"""
    admin = User.query.filter_by(role="admin").first()
    
    if not admin:
        admin = User(
            username="admin",
            email="admin@placement.com",
            role="admin"
        )
        admin.set_password("admin123")
        
        db.session.add(admin)
        db.session.commit()
        
        print("✓ Admin user created")
        print("  Username: admin")
        print("  Password: admin123")
        print("  Email: admin@placement.com")
    else:
        print("✓ Admin user already exists")


def create_upload_directories():
    """Create necessary upload directories"""
    directories = [
        "uploads/resumes",
        "exports/applications",
        "reports/monthly"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✓ Upload directories created")



app = create_app(os.environ.get("FLASK_ENV", "development"))


if __name__ == "__main__":
    print("\n" + "="*50)
    print("PLACEMENT PORTAL API - Starting...")
    print("Structure: Separate Routes Files")
    print("="*50 + "\n")
    
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )
