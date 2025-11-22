from App.database import db
from App.models.schedule import Schedule
from App.models.shift import Shift
from App.models import Staff, Admin
from datetime import datetime

# Import strategies
from App.models.strategies.even_distribution import EvenDistributionStrategy
from App.models.strategies.minimize_days import MinimizeDaysStrategy
from App.models.strategies.balance_day_night import BalanceDayNightStrategy

class ScheduleController:
    """Controller to manage schedules and auto-assign shifts using strategies."""

    @staticmethod
    def create_schedule(admin_id, name):
        """Create a new schedule for the admin."""
        admin = db.session.get(Admin, admin_id)
        if not admin:
            raise PermissionError("Only admins can create schedules")

        new_schedule = Schedule(
            name=name,
            created_by=admin_id,
            created_at=datetime.utcnow()
        )
        db.session.add(new_schedule)
        db.session.commit()
        return new_schedule

    @staticmethod
    def add_shift(schedule_id, staff_id, start_time, end_time, shift_type="day"):
        """Add a shift for a specific staff to a schedule."""
        schedule = db.session.get(Schedule, schedule_id)
        staff = db.session.get(Staff, staff_id)
        if not schedule or not staff:
            raise ValueError("Invalid schedule or staff")

        shift = Shift(
            staff_id=staff_id,
            schedule_id=schedule_id,
            start_time=start_time,
            end_time=end_time,
        )
        # Optional type attribute for day/night shifts
        shift.type = shift_type

        db.session.add(shift)
        db.session.commit()
        return shift

    @staticmethod
    def auto_populate(schedule_id, strategy_name):
        """Auto-populate the shifts of a schedule using a strategy."""
        schedule = db.session.get(Schedule, schedule_id)
        if not schedule:
            raise ValueError("Schedule not found")

        staff_list = Staff.query.all()
        shift_list = schedule.shifts  # Existing shifts in the schedule

        # Assign strategy
        if strategy_name == "even_distribution":
            strategy = EvenDistributionStrategy()
        elif strategy_name == "minimize_days":
            strategy = MinimizeDaysStrategy()
        elif strategy_name == "balance_day_night":
            strategy = BalanceDayNightStrategy()
        else:
            raise ValueError("Invalid strategy name")

        # Generate schedule using the strategy
        updated_shifts = strategy.generate(staff_list, shift_list)

        # Commit updated staff assignments
        db.session.commit()
        return updated_shifts

    @staticmethod
    def get_schedule_report(schedule_id):
        """Return JSON data for a schedule and its shifts."""
        schedule = db.session.get(Schedule, schedule_id)
        if not schedule:
            raise ValueError("Schedule not found")
        return schedule.get_json()
