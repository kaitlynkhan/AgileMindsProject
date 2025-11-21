from datetime import datetime

from App.database import db
from App.models import Shift, Schedule
from App.controllers.user import get_user


def _assert_admin(admin_id):
    admin = get_user(admin_id)
    if not admin or admin.role != "admin":
        raise PermissionError("Only admins can perform this action")
    return admin


def create_schedule(admin_id, schedule_name):
    _assert_admin(admin_id)

    new_schedule = Schedule(
        created_by=admin_id,
        name=schedule_name,
        created_at=datetime.utcnow()
    )

    db.session.add(new_schedule)
    db.session.commit()
    return new_schedule


def schedule_shift(admin_id, staff_id, schedule_id, start_time, end_time):
    _assert_admin(admin_id)

    staff = get_user(staff_id)
    if not staff or staff.role != "staff":
        raise ValueError("Invalid staff member")

    schedule = db.session.get(Schedule, schedule_id)
    if not schedule:
        raise ValueError("Invalid schedule ID")

    new_shift = Shift(
        staff_id=staff_id,
        schedule_id=schedule_id,
        start_time=start_time,
        end_time=end_time
    )

    db.session.add(new_shift)
    db.session.commit()
    return new_shift


def get_shift_report(admin_id):
    _assert_admin(admin_id)

    shifts = Shift.query.order_by(Shift.start_time).all()
    return [shift.get_json() for shift in shifts]
