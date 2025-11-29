from datetime import datetime, timezone
from App.database import db

class Schedule(db.Model):
    """
    full schedule containing multiple shifts.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    # Relationships
    creator = db.relationship("User", foreign_keys=[created_by], backref="created_schedules")
    user = db.relationship("User", foreign_keys=[user_id], backref="schedules")

    # One-to-many relationship with Shift
    shifts = db.relationship("Shift", backref="schedule", lazy=True, cascade="all, delete-orphan")

    strategy_used = db.Column(db.String(50), nullable=True)

    def __init__(self, name, created_by, user_id=None):
        """Initialize a schedule with name, creator, and optional user assignment."""
        self.name = name
        self.created_by = created_by
        self.user_id = user_id


    def shift_count(self):
        return len(self.shifts)

    def set_strategy_used(self, strategy):
      
        self.strategy_used = strategy.__class__.__name__

    def get_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "user_id": self.user_id,
            "shift_count": self.shift_count(),
            "strategy_used": self.strategy_used,
            "shifts": [shift.get_json() for shift in self.shifts]
        }



