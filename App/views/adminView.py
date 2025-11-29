# app/views/admin_views.py
from flask import Blueprint, jsonify, request
from datetime import datetime
from App.controllers import admin
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

admin_view = Blueprint('admin_view', __name__, template_folder='../templates')

# Admin Routes
# Based on the controllers in App/controllers/admin.py, admins can do the following actions:
# 1. Create Schedule (optionally for a specific user)
# 2. Add Shift to Schedule
# 3. Auto-populate Schedule with Strategy
# 4. Get Schedule Report

@admin_view.route('/createSchedule', methods=['POST'])
@jwt_required()
def admin_createSchedule():
    """
    Create a new schedule, optionally assigned to a specific user.
    
    Expected JSON:
    {
        "admin_id": int,
        "name": str,
        "user_id": int (optional) - ID of user to assign schedule to
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        admin_id = data.get("admin_id")
        name = data.get("name")
        user_id = data.get("user_id")  # Optional
        
        if not admin_id or not name:
            return jsonify({"error": "admin_id and name are required"}), 400
        
        # Create schedule with optional user assignment
        schedule = admin.create_schedule(admin_id, name, user_id=user_id)
        
        if schedule:
            return jsonify(schedule.get_json()), 201
        else:
            return jsonify({"error": "Failed to create schedule"}), 500
            
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error"}), 500

@admin_view.route('/addShift', methods=['POST'])
@jwt_required()
def admin_add_Shift():
    """
    Add a shift to a schedule.
    
    Expected JSON:
    {
        "admin_id": int,
        "staff_id": int,
        "schedule_id": int,
        "start_time": str (ISO format),
        "end_time": str (ISO format),
        "shift_type": str (optional, default="day")
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        admin_id = data.get("admin_id")
        staff_id = data.get("staff_id")
        schedule_id = data.get("schedule_id")
        start_time_str = data.get("start_time")
        end_time_str = data.get("end_time")
        shift_type = data.get("shift_type", "day")
        
        # Validate required fields
        if not all([admin_id, staff_id, schedule_id, start_time_str, end_time_str]):
            return jsonify({
                "error": "admin_id, staff_id, schedule_id, start_time, and end_time are required"
            }), 400
        
        # Parse datetime strings
        try:
            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.fromisoformat(end_time_str)
        except ValueError:
            return jsonify({"error": "Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400
        
        # Add shift with corrected parameter order: admin_id, staff_id, schedule_id, start_time, end_time, shift_type
        shift = admin.add_shift(
            admin_id=admin_id,
            staff_id=staff_id,
            schedule_id=schedule_id,
            start_time=start_time,
            end_time=end_time,
            shift_type=shift_type
        )
        
        if shift:
            return jsonify(shift.get_json()), 201
        else:
            return jsonify({"error": "Failed to add shift"}), 500
            
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error"}), 500

@admin_view.route('/autoPopulateSchedule', methods=['POST'])
@jwt_required()
def admin_auto_populate():
    """
    Auto-populate a schedule using a scheduling strategy.
    
    Expected JSON:
    {
        "admin_id": int,
        "schedule_id": int,
        "strategy_name": str ("even_distribution", "minimize_days", or "balance_day_night")
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        admin_id = data.get("admin_id")
        schedule_id = data.get("schedule_id")
        strategy_name = data.get("strategy_name", "even_distribution")
        
        if not admin_id or not schedule_id:
            return jsonify({"error": "admin_id and schedule_id are required"}), 400
        
        # Auto-populate schedule
        updated_shifts = admin.auto_populate_schedule(admin_id, schedule_id, strategy_name)
        
        return jsonify({
            "message": "Schedule auto-populated successfully",
            "strategy_used": strategy_name,
            "shifts_updated": len(updated_shifts) if updated_shifts else 0
        }), 200
        
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error"}), 500
    
@admin_view.route('/scheduleReport', methods=['GET'])
@jwt_required()
def scheduleReport():
    """
    Get a detailed report of a schedule.
    
    Expected JSON (in request body) or Query Parameters:
    {
        "admin_id": int,
        "schedule_id": int
    }
    """
    try:
        # Try to get from JSON body first, then query parameters
        data = request.get_json() or {}
        admin_id = data.get('admin_id') or request.args.get('admin_id')
        schedule_id = data.get('schedule_id') or request.args.get('schedule_id')
        
        if not admin_id or not schedule_id:
            return jsonify({"error": "admin_id and schedule_id are required"}), 400
        
        # Convert to int if they're strings from query params
        admin_id = int(admin_id)
        schedule_id = int(schedule_id)
        
        report = admin.get_schedule_report(admin_id, schedule_id)
        return jsonify(report), 200
        
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error"}), 500