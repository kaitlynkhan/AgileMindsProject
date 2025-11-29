import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash
from App.main import create_app
from App.database import db, create_db
from datetime import datetime, timedelta
#modelz
from App.models import User, Staff, Admin, Schedule, Shift
from App.models.strategies.even_distribution import EvenDistributionStrategy
from App.models.strategies.minimize_days import MinimizeDaysStrategy
from App.models.strategies.balance_day_night import BalanceDayNightStrategy
#controllerz
from App.controllers.user import create_user, get_user, update_user, get_all_users_json
import App.controllers.staff as staff_controller
import App.controllers.admin as admin_controller
from App.controllers.schedule_controller import ScheduleController
from App.controllers.auth import loginCLI

@pytest.fixture(autouse=True)
def clean_db():
    db.drop_all()
    create_db()
    db.session.remove()
    yield

@pytest.fixture(autouse= True, scope="module")
def empty_db():
    app= create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite://test.db'})
    create_db()
    db.session.remove()
    yield app.test_client()
    db.drop_all()

LOGGER = logging.getLogger(__name__)


### User unit tests ###


class UserUnitTests(unittest.TestCase):

    def test_create_user_valid(self):
        user= create_user ("bob", "pass123", "user")
        self.assertEqual(user.username, "bob")
        self.assertEqual(user.role, "user")
        self.assertTrue(user.check_password("pass123"))

    def test_create_user_invalid_role(self):
        user = create_user("bob", "pass123", "ceo")
        self.assertIsNone(user)

    def test_check_password_correct(self):
        user= create_user("alice", "pass123", "user")
        self.assertTrue (user.check_password("pass123"))

    def test_check_password_incorrect(self):
        user= create_user("alice2", "pass123", "user")
        self.assertFalse(user.check_password("wrongpassword"))
        
    def test_get_json(self):
        user = create_user("charlie", "pass123", "user")
        user_json= user.get_json()
        self.assertEqual(user.get_json())
        self.assertEqual(user_json["role"],"user")

    def test_update_username(self):
        user = create_user("dave", "pass123", "user")
        update_user (user.id, "newname")
        updated = get_user(user.id)
        self.assertEqual (updated.username, "newname")
    
### Admin unit test ###
                                            
class AdminUnitTests(unittest.TestCase):

    def test_create_schedule_valid(self):
        admin = create_user("admin1", "adminpass", "admin")
        schedule = admin_controller.create_schedule(admin.id, "Week Schedule")
        self.assertEqual(schedule.name, "Week Schedule")
        self.assertEqual(schedule.created_by, admin.id)

    def test_create_schedule_invalid_user(self):
        non_admin = create_user("user1", "userpass", "user")
        with self.assertRaises(PermissionError):
            admin_controller.create_schedule(non_admin.id, "Invalid Schedule")

    def test_add_shift_valid(self):
        admin = create_user("admin2", "adminpass", "admin")
        staff = create_user("staff1", "staffpass", "staff")
        schedule = admin_controller.create_schedule(admin.id, "Shift Test Schedule")

        start = datetime.now()
        end = start + timedelta(hours=8)
        shift = admin_controller.add_shift(admin.id, staff.id, schedule.id, start, end)

        # Reload staff to check assigned shift
        retrieved_staff = get_user(staff.id)
        self.assertIn(shift, retrieved_staff.shifts)
        self.assertEqual(shift.staff_id, staff.id)
        self.assertEqual(shift.schedule_id, schedule.id)

    def test_add_shift_invalid_user(self):
        non_admin = create_user("user2", "userpass", "user")
        staff = create_user("staff2", "staffpass", "staff")
        schedule = admin_controller.create_schedule(create_user("admin3", "adminpass", "admin").id, "Schedule")
        start = datetime.now()
        end = start + timedelta(hours=8)

        with self.assertRaises(PermissionError):
            admin_controller.add_shift(non_admin.id, staff.id, schedule.id, start, end)

### Staff unit tests ###

class StaffUnitTests(unittest.TestCase):

    def test_staff_creation_valid(self):
        staff= Staff ("john", "pass123")
        self.assertEqual(staff.role, "staff")
        self.assertTrue(staff.check_password("pass123"))

    def test_staff_upcoming_shifts(self):
        staff= Staff ("alice", "pass123")
        shift1= Shift(staff_id=staff.id, schedule_id=1, start_time=datetime.now()+timedelta(hours=1), end_time=datetime.now()+timedelta(hours=3))
        shift2= Shift(staff_id=staff.id, schedule_id=1, start_time=datetime.now()+timedelta(hours=2), end_time=datetime.now()+timedelta(hours=4))
        staff.shifts = [shift2, shift1]
        self.assertEqual (staff.upcoming_shifts, sorted(staff.shifts, key= lambda s: s.start_time))

    def test_staff_current_shift(self):
        staff = Staff ("bob" , "pass123")
        now = datetime.now()
        active_shift = Shift (staff_id= staff.id, schedule_id=1, start_time=now - timedelta(hours=1), end_time=now + timedelta(hours=1))
        staff.shifts= [active_shift]
        self.assertEqual(staff.current_shift, active_shift)

    def test_staff_total_hours_scheduled(self):
        staff = Staff("charlie", "pass123")
        shift1= Shift (staff_id= staff.id, schedule_id=1, start_time=datetime.now(), end_time= datetime.now() + timedelta(hours=1))
        shift2= Shift (staff_id= staff.id, schedule_id=1, start_time=datetime.now(), end_time= datetime.now() + timedelta(hours=1))
        staff.shifts= [shift1, shift2]
        self.assertAlmostEqual(staff.total_hours_scheduled,5)

    def test_staff_completed_shifts(self):
        staff = Staff("dana", "pass123")
        shift1= Shift (staff_id= staff.id, schedule_id=1, start_time=datetime.now(), end_time= datetime.now() + timedelta(hours=1))
        shift2= Shift (staff_id= staff.id, schedule_id=1, start_time=datetime.now(), end_time= datetime.now() + timedelta(hours=1))
        shift1.clock_in= datetime.now()
        shift1.clock_out = datetime.now() +timedelta(hours=1)
        shift2.clock_in = datetime.now()
        staff.shifts= [shift1, shift2]
        self.assertEqual (staff.completed_shifts, [shift1])

    def test_get_json_staff(self):
        staff = Staff("emma", "pass123")
        shift1 = Shift(staff_id=staff.id, schedule_id=1, start_time=datetime.now(), end_time=datetime.now() + timedelta(hours=2))
        staff.shifts = [shift1]
        json_data = staff.get_json()
        self.assertEqual(json_data["username"], "emma")
        self.assertEqual(json_data["role"], "staff")
        self.assertEqual(json_data["upcoming_shift_count"], len(staff.upcoming_shifts))

    def test_clock_in_valid(self):
        staff = Staff("frank", "pass123")
        shift = Shift(staff_id=staff.id, schedule_id=1, start_time=datetime.now(), end_time=datetime.now() + timedelta(hours=2))
        db.session.add(shift)
        db.session.commit()
        shift = staff_controller.clock_in(staff.id, shift.id)
        self.assertIsNotNone(shift.clock_in)

    def test_clock_in_invalid_shift(self):
        staff = Staff("george", "pass123")
        with self.assertRaises(ValueError):
            staff_controller.clock_in(staff.id, 999)

    def test_clock_out_valid(self):
        staff = Staff("harry", "pass123")
        shift = Shift(staff_id=staff.id, schedule_id=1, start_time=datetime.now(), end_time=datetime.now() + timedelta(hours=2))
        db.session.add(shift)
        db.session.commit()
        shift = staff_controller.clock_out(staff.id, shift.id)
        self.assertIsNotNone(shift.clock_out)

    def test_clock_out_invalid_shift(self):
        staff = Staff("ivan", "pass123")
        with self.assertRaises(ValueError):
            staff_controller.clock_out(staff.id, 999)

    def test_combined_roster(self):
        staff = Staff("jack", "pass123")
        shift1 = Shift(staff_id=staff.id, schedule_id=1, start_time=datetime.now(), end_time=datetime.now() + timedelta(hours=2))
        shift2 = Shift(staff_id=staff.id, schedule_id=2, start_time=datetime.now(), end_time=datetime.now() + timedelta(hours=2))
        staff.shifts = [shift1, shift2]
        roster = staff_controller.get_combined_roster(staff.id)
        self.assertEqual(len(roster), 2)

    def test_staff_permission_block(self):
        non_staff = create_user("kelly", "pass123", "user")
        shift = Shift(staff_id=1, schedule_id=1, start_time=datetime.now(), end_time=datetime.now() + timedelta(hours=2))
        with self.assertRaises(PermissionError):
            staff_controller.clock_in(non_staff.id, shift.id)

###  Integration Tests   ###

def test_authenticate():
    user = User("bob", "bobpass","user")
    assert loginCLI("bob", "bobpass") != None

class UsersIntegrationTests(unittest.TestCase):

    def test_create_and_get_user(self):
        user= create_user("alice","pass123", "user")
        retrieved = get_user(user.id)
        self.assertEqual(retrieved.username, "alice")
        self.assertEqual(retrieved.role, "user")

    
    def test_get_all_users_json_integration(self):
        create_user("bot", "bobpass", "admin")
        create_user("pam", "pampass", "staff")
        users_json = get_all_users_json()
        expected = [
            {"id": 1, "username": "bot", "role": "admin"},
            {"id": 2, "username": "pam", "role": "staff"},
        ]
        self.assertEqual(users_json, expected)
        
    def test_admin_schedule_shift_for_staff(self):
        admin = create_user("admin1", "adminpass", "admin")
        staff = create_user("staff1", "staffpass", "staff")

        schedule = ScheduleController.create_schedule(admin.id, "Week Schedule")

        start = datetime.now()
        end = start + timedelta(hours=8)

        shift = ScheduleController.add_shift(schedule.id, staff.id, start, end)
        retrieved = get_user(staff.id)

        self.assertIn(shift, retrieved.shifts)
        self.assertEqual(shift.staff_id, staff.id)
        self.assertEqual(shift.schedule_id, schedule.id)

    def test_staff_view_combined_roster(self):
        admin = create_user("admin", "adminpass", "admin")
        staff = create_user("jane", "janepass", "staff")
        other_staff = create_user("mark", "markpass", "staff")

        schedule = ScheduleController.create_schedule(admin.id,"Shared Roster")

        start = datetime.now()
        end = start + timedelta(hours=8)

        ScheduleController.add_shift(schedule.id, staff.id, start, end)
        ScheduleController.add_shift(schedule.id, other_staff.id, start, end)

        roster = staff_controller.get_combined_roster(staff.id)
        self.assertTrue(any(s["staff_id"] == staff.id for s in roster))
        self.assertTrue(any(s["staff_id"] == other_staff.id for s in roster))

    def test_staff_clock_in_and_out(self):
        admin = create_user("admin", "adminpass", "admin")
        staff = create_user("lee", "leepass", "staff")

        schedule = ScheduleController.create_schedule(admin.id, "Daily Schedule")
        
        start = datetime.now()
        end = start + timedelta(hours=8)

        shift = ScheduleController.add_shift(schedule.id, staff.id, start, end)

        staff_controller.clock_in(staff.id, shift.id)
        staff_controller.clock_out(staff.id, shift.id)


        updated_shift = Shift.query.get(shift.id)
        self.assertIsNotNone(updated_shift.clock_in)
        self.assertIsNotNone(updated_shift.clock_out)
        self.assertLess(updated_shift.clock_in, updated_shift.clock_out)
    
    def test_admin_generate_shift_report(self):
        admin = create_user("boss", "boss123", "admin")
        staff = create_user("sam", "sampass", "staff")

        schedule = ScheduleController.create_schedule(admin.id, "Weekly Schedule")

        start = datetime.now()
        end = start + timedelta(hours=8)

        ScheduleController.add_shift(schedule.id, staff.id, start, end)
        report = ScheduleController.get_Schedule_report(schedule.id)

        self.assertTrue(any(s["staff_id"]==staff.id for s in report ["shifts"]))
        self.assertTrue("start_time" in report["shifts"][0] and "end_time" in report ["shifts"][0])

    def test_permission_restrictions(self):
        admin = create_user("admin4", "adminpass", "admin")
        staff = create_user("worker", "workpass", "staff")

        # Create schedule
        schedule = ScheduleController.create_schedule(admin.id, "Restricted Schedule")

        start = datetime.now()
        end = start + timedelta(hours=8)

        with self.assertRaises(PermissionError):
            ScheduleController.add_shift(schedule.id, staff.id, start, end)

        with self.assertRaises(PermissionError):
            staff_controller.get_combined_roster(admin.id)
