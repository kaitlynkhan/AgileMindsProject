# app/views/staff_views.py
from flask import Blueprint, jsonify, request
from App.controllers import staff, auth,user, get_all_users
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

staff_views = Blueprint('staff_views', __name__, template_folder='../templates')

#Based on the controllers in App/controllers/staff.py, staff can do the following actions:
# 1. View combined roster
# 2. Clock in 
# 3. Clock out
# 4. View specific shift details

staff_views = Blueprint('staff_views', __name__, template_folder='../templates')

@staff_views.route("/allshifts", methods=['GET'])
def get_all_shifts():
        data = request.get_json()
        staffId =int(get_jwt_identity())
        staf = staff._assert_staff(staffID)
        if not staffID or not staf:
            return jsonify({"error": "Unauthorized access"}), 403
        shifts = staff.get_combined_roster(staffID)
        return jsonify(shifts), 200


#get shift for staff
@staff_views.route('/staffshift', methods=['GET'])
@jwt_required()
def staff_get_shift():
    try: 
        staffID =int(get_jwt_identity())
        
        data=request.get_json()
        shiftID = data.get("shift_id")
        #staffID = data.get("staff_id")
        if not shiftID or not staffID:
            return jsonify({"error": "valid shift_id and staff_id are required"}), 400
        staf = staff._assert_staff(staffID)
        if not staffID or not staf:
            return jsonify({"error": "Unauthorized access"}), 403
        shift = staff._get_shift_for_staff(int(staffID), int(shiftID))
        return jsonify(shift.get_json()), 200
    except(SQLAlchemyError) as e:
        return jsonify({"error": "Database error"}), 500
    except(ValueError) as ve:
        return jsonify({"error": str(ve)}), 404
        

@staff_views.route('/staff/combinedRoster', methods=['GET'])
@jwt_required()
def get_combinedRoster():
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
    currentshift = staf.current_shift 
    if currentshift is None:
        return jsonify({"error": " not currrent shift found "}), 404
    shiftid = currentshift.id
    currentshift = staff.clock_in(staffId,4)
    return jsonify(currentshift), 200

@staff_views.route("/staff/clockOut", methods=["POST"])
@jwt_required()
def staff_clock_out():
    staffId=int(get_jwt_identity())
    staff= staff._assert_staff(staffId)
    if not staff:
        return jsonify({"error": "unauthorized access"}), 403
    current_shift = staff.current_shift
    if not current_shift:
        return jsonify({"error": " not currrent shift found "}), 404
    shiftid = current_shift.id
    current_shift = staff.clock_out(staffId,shiftid)
    return jsonify(current_shift), 200






















