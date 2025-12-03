# app/views/staff_views.py
from flask import Blueprint, jsonify, request
from App.controllers import staff, user
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

staff_views = Blueprint('staff_views', __name__, template_folder='../templates')

# Staff Routes
# Based on the controllers in App/controllers/staff.py, staff can do the following actions:
# 1. View combined roster (all shifts)
# 2. View specific shift details
# 3. Clock in to shift
# 4. Clock out from shift

@staff_views.route("/allshifts", methods=['GET'])
@jwt_required()
def get_all_shifts():
    try:    
        data = request.get_json()
        staffID =int(get_jwt_identity())
        staf = staff._assert_staff(staffID)
        if not staffID or not staf:
            return jsonify({"error": "Unauthorized access"}), 403
        shifts = staff.get_combined_roster(staffID)
        return jsonify(shifts), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError:
        return jsonify({"error": "Database error"}), 500

@staff_views.route('/staffshift', methods=['GET'])
@jwt_required()
def staff_get_shift():
    try:
        staff_id = int(get_jwt_identity())
        data = request.get_json()

        shift_id = data.get("shift_id")
        if not shift_id or not staff_id:
            return jsonify({"error": "valid shift_id and staff_id are required"}), 400
        staff_member = staff._assert_staff(staff_id)
        if not staff_member:
            return jsonify({"error": "Unauthorized access"}), 403
        shift = staff._get_shift_for_staff(staff_id, int(shift_id))

        return jsonify(shift.get_json()), 200

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except SQLAlchemyError:
        return jsonify({"error": "Database error"}), 500


@staff_views.route('/staff/combinedRoster', methods=['GET'])
@jwt_required()
def get_combinedRoster():
    """
    Get the combined roster (all shifts) for a staff member.
    
    Expected JSON or Query Parameters:
    {
        "staff_id": int
    }
    """
    try:
        staffId =int(get_jwt_identity())
        data=request.get_json()
        staf = staff._assert_staff(staffId)
        if staf:
            roster = staff.get_combined_roster(staffId)
            if not roster:
                return jsonify({"error": "no roster found"}), 404
            return jsonify(roster), 200
        else:
            return jsonify({"error": "unauthorized access"}), 403
    except(SQLAlchemyError) as e:
        return jsonify({"error": "database error"}), 500

@staff_views.route("/staff/clockIn", methods=["POST"])
@jwt_required()
def staff_clock_in():
    staffId=int(get_jwt_identity())
    staf = staff._assert_staff(staffId)
    if not staf:
        return jsonify({"error": "unauthorized access"}), 403
    shiftid = request.json.get("shift_id")
    currentshift = staff._get_shift_for_staff(staffId, shiftid)
    if currentshift is None:
        return jsonify({"error": " not currrent shift found "}), 404
    currentshift = staff.clock_in(staffId,int(shiftid))
    return jsonify(currentshift.get_json()), 200

@staff_views.route("/staff/clockOut", methods=["POST"])
@jwt_required()
def staff_clock_out():
    """
    Clock out from a shift.
    
    Expected JSON:
    C
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        staff_id = data.get("staff_id")
        shift_id = data.get("shift_id")
        
        if not staff_id or not shift_id:
            return jsonify({"error": "staff_id and shift_id are required"}), 400
        
        staff_id = int(staff_id)
        shift_id = int(shift_id)
        
        # Verify staff exists and has correct role
        try:
            staff_member = staff._assert_staff(staff_id)
        except PermissionError as e:
            return jsonify({"error": str(e)}), 403
        
        # Clock out
        updated_shift = staff.clock_out(staff_id, shift_id)
        return jsonify(updated_shift.get_json()), 200
        
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except SQLAlchemyError:
        return jsonify({"error": "Database error"}), 500

@staff_views.route("/staff/mySchedules", methods=["GET"])
@jwt_required()
def get_my_schedules():
    """
    Get all schedules assigned to a staff member.
    
    Expected JSON or Query Parameters:
    {
        "staff_id": int
    }
    """
    try:
        # Try JSON body first, then query parameters
        data = request.get_json() or {}
        staff_id = data.get("staff_id") or request.args.get("staff_id")
        
        if not staff_id:
            return jsonify({"error": "staff_id is required"}), 400
        
        staff_id = int(staff_id)
        
        # Get staff member
        staff_member = user.get_user(staff_id)
        
        if not staff_member or staff_member.role != "staff":
            return jsonify({"error": "Staff member not found"}), 404
        
        # Get schedules assigned to this staff member
        schedules = staff.get_combined_roster(staff_id)
        return jsonify({
            "staff_id": staff_id,
            "username": staff_member.username,
            "schedules": schedules
        }), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError:
        return jsonify({"error": "Database error"}), 500























