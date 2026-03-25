# routes/drive_routes.py - Public Drive Routes

from flask import Blueprint, request, jsonify
from models import PlacementDrive
from utils import success_response
from datetime import date

drive_bp = Blueprint("drive", __name__, url_prefix="/api/drives")


@drive_bp.route("/", methods=["GET"])
def list_public_drives():
    """List all approved drives (public endpoint)"""
    search = request.args.get("search", "")
    
    query = PlacementDrive.query.filter(
        PlacementDrive.status == "Approved",
        PlacementDrive.application_deadline >= date.today()
    )
    
    if search:
        query = query.filter(PlacementDrive.job_title.ilike(f"%{search}%"))
    
    drives = query.all()
    
    return success_response("Drives retrieved", [d.to_dict() for d in drives])


@drive_bp.route("/<int:drive_id>", methods=["GET"])
def get_drive_details(drive_id):
    """Get single drive details (public endpoint)"""
    drive = PlacementDrive.query.get_or_404(drive_id)
    
    return success_response("Drive details", drive.to_dict())
