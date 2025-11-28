from datetime import datetime
from App.database import db
from App.controllers.user import get_user
from App.models.admin import Admin
from App.controllers.schedule_controller import ScheduleController

def create_schedule(admin_id, schedule_name, user_id=None):
    """Allow an admin to create a new schedule."""
    admin = get_user(admin_id)
    if not admin or admin.role != "admin":
        raise PermissionError("Only admins can create schedules")

    return ScheduleController.create_schedule(admin_id, schedule_name, user_id)

def add_shift(admin_id, staff_id, schedule_id, start_time, end_time, shift_type="day"):
    """Allow an admin to manually add a shift."""
    admin = get_user(admin_id)
    if not admin or admin.role != "admin":
        raise PermissionError("Only admins can schedule shifts")

    return ScheduleController.add_shift(schedule_id, staff_id, start_time, end_time, shift_type)

def auto_populate_schedule(admin_id, schedule_id, strategy_name):
    """Allow an admin to auto-populate shifts using a strategy."""
    admin = get_user(admin_id)
    if not admin or admin.role != "admin":
        raise PermissionError("Only admins can populate schedules")

    return ScheduleController.auto_populate(schedule_id, strategy_name)

def get_schedule_report(admin_id, schedule_id):
    """Allow an admin to view the schedule report."""
    admin = get_user(admin_id)
    if not admin or admin.role != "admin":
        raise PermissionError("Only admins can view schedule reports")

    return ScheduleController.get_Schedule_report(schedule_id)
