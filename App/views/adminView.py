# app/views/staff_views.py
from flask import Blueprint, jsonify, request
from datetime import datetime
from App.controllers import staff, auth, admin
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

admin_view = Blueprint('admin_view', __name__, template_folder='../templates')

# Admin authentication decorator
# def admin_required(fn):
#     @jwt_required()
#     def wrapper(*args, **kwargs):
#         user_id = get_jwt_identity()
#         user = auth.get_user(user_id)
#         if not user or not user.is_admin:
#             return jsonify({"error": "Admin access required"}), 403
#         return fn(*args, **kwargs)
#     return wrapper
# Based on the controllers in App/controllers/admin.py, admins can do the following actions:
# 1. Create Schedule
# 2. Get Schedule Report

@admin_view.route('/createSchedule', methods=['POST'])
@jwt_required()
def admin_createSchedule():
    try:
        #admin_id= get_jwt_identity()
        data = request.get_json()
        if data:
            schedule =  admin.create_schedule(data.get("admin_id"), data.get("name"))
            if schedule:
                return jsonify(schedule.get_json()), 200
            else:
                return jsonify({"error": "Failed to create schedule"}), 500
    except (PermissionError):
        return jsonify({"error": "Admin access required"}), 403

@admin_view.route('/addShift', methods=['POST'])
@jwt_required()
def admin_add_Shift():
    try:
        #admin_id = get_jwt_identity()
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid input"}), 400
        
        shift = admin.add_shift(
            schedule_id=data.get("schedule_id"),
            staff_id=data.get("staff_id"),
            start_time=datetime.fromisoformat(data.get("start_time")),
            end_time=datetime.fromisoformat(data.get("end_time")),
            shift_type=data.get("shift_type", "day"),
            admin_id=data.get("admin_id")
        )

        if shift:
            shiftid= shift.id
            updated_shift = admin.auto_populate_schedule(admin_id=data.get("admin_id"),schedule_id=data.get("schedule_id"), strategy_name=data.get("strategy_name", "even_distribution"))
            dict_shift = str(updated_shift)
            return jsonify(dict_shift), 200
    except (PermissionError, ValueError) as e:
            return jsonify({"error": str(e)}), 500
    
@admin_view.route('/scheduleReport', methods=['GET'])
@jwt_required()
def scheduleReport():
    try:
        #admin_id = get_jwt_identity()
        data = request.get_json()
        report = admin.get_schedule_report(data['admin_id'], data['schedule_id']) 
        return jsonify(report), 200
    except (PermissionError, ValueError) as e:
        return jsonify({"error": str(e)}), 403
    except SQLAlchemyError:
        return jsonify({"error": "Database error"}), 500