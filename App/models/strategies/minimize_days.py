from .schedule_strategy import ScheduleStrategy

class MinimizeDaysStrategy(ScheduleStrategy):
    """Distribute shifts to minimize number of workdays per staff."""

    def generate(self, staff_list, shift_list):
        result = []
        work_count = {s.id: 0 for s in staff_list}

        for shift in shift_list:
            staff_id = min(work_count, key=work_count.get)
            shift.staff_id = staff_id
            work_count[staff_id] += 1
            result.append(shift)
        return result

