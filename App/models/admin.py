
from App.database import db
from App.models.user import User

from App.models.strategies.schedule_strategy import ScheduleStrategy
from App.models.strategies.even_distribution import EvenDistributionStrategy
from App.models.strategies.minimize_days import MinimizeDaysStrategy
from App.models.strategies.balance_day_night import BalanceDayNightStrategy

class Admin(User):
    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "admin",
    }

    def __init__(self, username, password):
        super().__init__(username, password, "admin")
        self.schedule_strategy = None

    # Strategy pattern methods
    def set_schedule_strategy(self, strategy: ScheduleStrategy):
        self.schedule_strategy = strategy

    def generate_schedule(self, staff_list, shift_list):
        if not self.schedule_strategy:
            raise ValueError("No strategy assigned")
        return self.schedule_strategy.generate(staff_list, shift_list)
