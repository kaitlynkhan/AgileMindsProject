from .schedule_strategy import ScheduleStrategy

class BalanceDayNightStrategy(ScheduleStrategy):
    """Distribute day/night shifts to prevent imbalance."""

    def generate(self, staff_list, shift_list):
        result = []
        night_count = {s.id: 0 for s in staff_list}

        for shift in shift_list:
            if getattr(shift, "type", "day") == "night":
                staff_id = min(night_count, key=night_count.get)
                night_count[staff_id] += 1
            else:
                staff_id = staff_list[0].id
            shift.staff_id = staff_id
            result.append(shift)
        return result
