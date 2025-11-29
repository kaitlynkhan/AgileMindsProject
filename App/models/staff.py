from App.database import db
from .user import User
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from App.models.shift import Shift

class Staff(User):

  # Represents a staff user in system
  # Inherits from User and implements staff-specific attributes
  
    #Foreign key referring to User Class
    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "staff",
    }

    # ---------- Constructor ----------
    def __init__(self, username: str, password: str) -> None:
        super().__init__(username, password, "staff")
        # Staff specific initialisation can be place here in future
        # Note: self.shifts is available via backref from Shift model

    # ---------- Properties ----------
    # The following properties use self.shifts, which is created by the
    # backref in the Shift model's relationship to User

    @property
    def upcoming_shifts(self)-> List:
        """Return shifts starting after now."""
        now = datetime.now()
        return sorted([s for s in self.shifts if s.start_time > now], key=lambda s: s.start_time)

    @property
    def current_shift(self)-> Optional["Shift"]:
        """Return the shift currently in progress, or None if none."""
        now = datetime.now()
        for shift in self.shifts:
            if shift.start_time <= now <= shift.end_time:
                return shift
        return None

    @property
    def total_hours_scheduled(self) -> float:
        """Total hours scheduled across all shifts."""
        total = timedelta()
        for shift in self.shifts:
            total += (shift.end_time - shift.start_time)
        return total.total_seconds() / 3600  # convert to hours

    @property
    def completed_shifts(self) -> List["Shift"]:
        return [s for s in self.shifts if s.is_completed]

    def get_json(self) -> Dict:
        """Return Staff-specific JSON for frontend components."""
        return {
            "id": self.id,
            "username": self.username,
            "role": "staff",
            "total_hours_scheduled": self.total_hours_scheduled,
            "upcoming_shift_count": len(self.upcoming_shifts),
        }
