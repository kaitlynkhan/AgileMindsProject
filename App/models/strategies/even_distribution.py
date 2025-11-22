from .schedule_strategy import ScheduleStrategy

class EvenDistributionStrategy(ScheduleStrategy):
    """Assign shifts evenly across staff."""

    def generate(self, staff_list, shift_list):
        result = []
        n = len(staff_list)
        for i, shift in enumerate(shift_list):
            staff = staff_list[i % n]
            shift.staff_id = staff.id
            result.append(shift)
        return result
