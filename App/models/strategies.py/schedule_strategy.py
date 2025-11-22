from abc import ABC, abstractmethod

class ScheduleStrategy(ABC):
    """Base class for schedule generation strategies."""

    @abstractmethod
    def generate(self, staff_list, shift_list):
        pass
