from datetime import datetime
from App.database import db

class Shift(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    # Who the shift belongs to
    staff_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # Which schedule this shift is part of
    schedule_id = db.Column(db.Integer, db.ForeignKey("schedule.id"), nullable=True)

    # Time range for the shift
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    #day or night shift
    type = db.Column(db.String(10), default="day")   


    # Times of clock in or out
    clock_in = db.Column(db.DateTime, nullable=True)
    clock_out = db.Column(db.DateTime, nullable=True)

    staff = db.relationship(
        "Staff",
        backref="shifts",
        foreign_keys=[staff_id],
        lazy=True
    )

    @property
    def is_completed(self):
        return self.clock_in is not None and self.clock_out is not None

    @property
    def is_active_shift(self):
        """True if now is between start_time and end_time."""
        now = datetime.now()
        return self.start_time <= now <= self.end_time

    @property
    def is_late(self):
        """True if the staff clocked in after shift start."""
        return self.clock_in and self.clock_in > self.start_time

    def get_json(self):
        return {
            "id": self.id,
            "staff_id": self.staff_id,
            "staff_name": self.staff.username if self.staff else None,
            "schedule_id": self.schedule_id,

            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),

            "clock_in": self.clock_in.isoformat() if self.clock_in else None,
            "clock_out": self.clock_out.isoformat() if self.clock_out else None,

            "is_completed": self.is_completed,
            "is_active_shift": self.is_active_shift,
            "is_late": self.is_late,
        }

