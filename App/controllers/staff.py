from datetime import datetime

from App.database import db
from App.models import Shift
from App.controllers.user import get_user

def _assert_staff(staff_id):
    """Ensure the user exists and has the 'staff' role."""
    staff = get_user(staff_id)
    if not staff or staff.role != "staff":
        raise PermissionError("Only staff members can perform this action")
    return staff


def _get_shift_for_staff(staff_id, shift_id):
    """Fetch a shift and verify it belongs to the given staff member."""
    shift = db.session.get(Shift, shift_id)
    if not shift or shift.staff_id != staff_id:
        raise ValueError("Invalid shift for staff")
    return shift

def get_combined_roster(staff_id):
    _assert_staff(staff_id)
    shifts = Shift.query.order_by(Shift.start_time).all()
    return [shift.get_json() for shift in shifts]


def clock_in(staff_id, shift_id):
    _assert_staff(staff_id)
    shift = _get_shift_for_staff(staff_id, shift_id)

    shift.clock_in = datetime.now()
    db.session.commit()
    return shift


def clock_out(staff_id, shift_id):
    _assert_staff(staff_id)
    shift = _get_shift_for_staff(staff_id, shift_id)

    shift.clock_out = datetime.now()
    db.session.commit()
    return shift


def get_shift(shift_id):
    return db.session.get(Shift, shift_id)
