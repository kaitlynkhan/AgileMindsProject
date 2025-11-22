# User management
from .user import (
    create_user,
    get_user,
    get_user_by_username,
    get_all_users,
    get_all_users_json,
    update_user
)

# Authentication
from .auth import login, loginCLI, logout

# Initialize database
from .initialize import initialize

# Staff actions
from .staff import (
    get_combined_roster,
    clock_in,
    clock_out,
    get_shift
)

# Admin schedule functions
from .admin import (
    create_schedule,
    add_shift,
    auto_populate_schedule,
    get_schedule_report
)

# Schedule controller (class)
from .schedule_controller import ScheduleController

