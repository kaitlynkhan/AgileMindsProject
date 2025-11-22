from App.database import db
from .user import User
from datetime import datetime, timedelta

class Staff(User):
  
    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "staff",
    }

    # ---------- Constructor ----------
    def __init__(self, username, password):
        super().__init__(username, password, "staff")

    @property
    def upcoming_shifts(self):
        """Return shifts starting after now."""
        now = datetime.now()
        return sorted([s for s in self.shifts if s.start_time > now], key=lambda s: s.start_time)

    @property
    def current_shift(self):
        """Return the shift currently in progress."""
        now = datetime.now()
        for shift in self.shifts:
            if shift.start_time <= now <= shift.end_time:
                return shift
        return None

    @property
    def total_hours_scheduled(self):
        """Total hours scheduled across all shifts."""
        total = timedelta()
        for shift in self.shifts:
            total += (shift.end_time - shift.start_time)
        return total.total_seconds() / 3600  # convert to hours

    @property
    def completed_shifts(self):
        return [s for s in self.shifts if s.is_completed]

    @property
    def get_json(self):
        """Return Staff-specific JSON for frontend components."""
        return {
            "id": self.id,
            "username": self.username,
            "role": "staff",
            "total_hours_scheduled": self.total_hours_scheduled,
            "upcoming_shift_count": len(self.upcoming_shifts),
        }
