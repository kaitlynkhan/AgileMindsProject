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
from App.controllers.staff import clock_in, clock_out, get_combiner_roster
from App.controllers.admin import get_schedule_report
from App.controllers.schedule_controller import ScheduleController, schedule_shift, get_shift_report
from App.controllers.shift_controller import get_shift

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
        user= user_controller.create_user ("bob", "pass123", "user")
        self.assertEqual(user.username, "bob")
        self.assertEqual(user.role, "user")
        self.assertTrue(user.check_password("pass123"))

    def test_create_user_invalid_role(self):
        user = user_controller.create_user("bob", "pass123", "ceo")
        self.assertIsNone(user)

    def test_check_password_correct(self):
        user= create_user("alice", "pass123", "user")
        self.assertTrue (user.chech_password("pass123")

    def test_check_password_incorrect(self):
        user= create_user("alice2", "pass123", "user")
        self.assertFalse(user.check_password("wrongpassword"))
        
    def test_get_json(self):
        user = create_user("charlie", "pass123", "user")
        user_json= user.get_json()
        self.assertEqual(user.get_json["username"], "charlie")
        self.assertEqual(user_json["role"],"user")

    def test_update_username(self):
        user = create_user("dave", "pass123", "user")
        update_user (user.id, "newname")
        updates = get_user(user.id)
        self.assertEqual (updated.username, "newname")
    
### Admin unit test ###
                                            
class AdminUnitTests(unittest.TestCase):

    def test_create_staff(self):
        staff = staff_controller.create_staff ("Mrs.Jane")
        self.assertEqual (staff.username, "Mrs.Jane")

    def test_create_staff_empty_name(self):
        result = staff_controller.create_staff("")
        self.assertEqual(result, {"error": "staff name cannot be empty."})

    def test_create_staff_duplicate(self):
        staff_controller.create_stafff("Mrs.Jane")
        result = staff_controller.create_staff("Mrs.Jane")
        self.assertEqual(result, {"error": "Staff with name 'Mrs.Jane' already exists."})

    def test_confirm_hours_valid(self):
        #mock setup
        staff= staff_controller.create_staff("StaffA")
        hours_id = 1
        result = staff_controller.confirm_hours(hours_id, staff.id)
        self.assertEqual(result, "message": f"Hours record {hours_id} confirmed by staff {staff.id}."})

    def test_confirm_hours_invalid(self):
        hours_id=1
        result= staff_controller.confirm_hours(hours_id,"abc")
        self.assertEqual(result, {"error": "Staff member with IS 'abc' not found."})
        
    def test_confirm_hours_invalid_record(self):
        result = staff_controller.confirm_hours("abc", 3)
        self.assertEqual (result, {"error": "Invalid ID format providied"})

    def test_confirm_hours_previous_confirmed(self):
        #done assuming that hours_id=5 is already confirmed by staff 8
        result = staff_controller.confirm_hours(5,9)
        self.assertEqual(result, {"message": "Hours record 5 was already confirmed by staff ID 8"})

    
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
        self.assertEqual (staff.upcoming_shifts, sorted(staff.shofts, key= lambda s: start_time))

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
        self.assertAlmostEqual(staff.total_hours_schedules,5)

    def test_staff_completed_shifts(self):
        satff = Staff("dana", "pass123")
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
'''
    Integration Tests
'''

def test_authenticate():
    user = User("bob", "bobpass","user")
    assert loginCLI("bob", "bobpass") != None

class UsersIntegrationTests(unittest.TestCase):

    def test_get_all_users_json(self):
        user = create_user("bot", "bobpass","admin")
        user = create_user("pam", "pampass","staff")
        users_json = get_all_users_json()
        self.assertListEqual([{"id":1, "username":"bot", "role":"admin"}, {"id":2, "username":"pam","role":"staff"}], users_json)

    def test_update_user(self):
        user = create_user("bot", "bobpass","admin")
        update_user(1, "ronnie")
        user = get_user(1)
        assert user.username == "ronnie"

    def test_create_and_get_user(self):
        user = create_user("alex", "alexpass", "staff")
        retrieved = get_user(user.id)
        self.assertEqual(retrieved.username, "alex")
        self.assertEqual(retrieved.role, "staff")
    
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

        schedule = Schedule(name="Week 1 Schedule", created_by=admin.id)
        db.session.add(schedule)
        db.session.commit()

        start = datetime.now()
        end = start + timedelta(hours=8)

        shift = schedule_shift(admin.id, staff.id, schedule.id, start, end)
        retrieved = get_user(staff.id)

        self.assertIn(shift.id, [s.id for s in retrieved.shifts])
        self.assertEqual(shift.staff_id, staff.id)
        self.assertEqual(shift.schedule_id, schedule.id)

    def test_staff_view_combined_roster(self):
        admin = create_user("admin", "adminpass", "admin")
        staff = create_user("jane", "janepass", "staff")
        other_staff = create_user("mark", "markpass", "staff")

        schedule = Schedule(name="Shared Roster", created_by=admin.id)
        db.session.add(schedule)
        db.session.commit()

        start = datetime.now()
        end = start + timedelta(hours=8)

        schedule_shift(admin.id, staff.id, schedule.id, start, end)
        schedule_shift(admin.id, other_staff.id, schedule.id, start, end)

        roster = get_combined_roster(staff.id)
        self.assertTrue(any(s["staff_id"] == staff.id for s in roster))
        self.assertTrue(any(s["staff_id"] == other_staff.id for s in roster))

    def test_staff_clock_in_and_out(self):
        admin = create_user("admin", "adminpass", "admin")
        staff = create_user("lee", "leepass", "staff")

        schedule = Schedule(name="Daily Schedule", created_by=admin.id)
        db.session.add(schedule)
        db.session.commit()

        start = datetime.now()
        end = start + timedelta(hours=8)

        shift = schedule_shift(admin.id, staff.id, schedule.id, start, end)

        clock_in(staff.id, shift.id)
        clock_out(staff.id, shift.id)


        updated_shift = get_shift(shift.id)
        self.assertIsNotNone(updated_shift.clock_in)
        self.assertIsNotNone(updated_shift.clock_out)
        self.assertLess(updated_shift.clock_in, updated_shift.clock_out)
    
    def test_admin_generate_shift_report(self):
        admin = create_user("boss", "boss123", "admin")
        staff = create_user("sam", "sampass", "staff")

        schedule = Schedule(name="Weekly Schedule", created_by=admin.id)
        db.session.add(schedule)
        db.session.commit()

        start = datetime.now()
        end = start + timedelta(hours=8)

        schedule_shift(admin.id, staff.id, schedule.id, start, end)
        report = get_shift_report(admin.id)

        self.assertTrue(any("sam" in r["staff_name"] for r in report))
        self.assertTrue(all("start_time" in r and "end_time" in r for r in report))

    def test_permission_restrictions(self):
        admin = create_user("admin", "adminpass", "admin")
        staff = create_user("worker", "workpass", "staff")

        # Create schedule
        schedule = Schedule(name="Restricted Schedule", created_by=admin.id)
        db.session.add(schedule)
        db.session.commit()

        start = datetime.now()
        end = start + timedelta(hours=8)

        with self.assertRaises(PermissionError):
            schedule_shift(staff.id, staff.id, schedule.id, start, end)

        with self.assertRaises(PermissionError):
            get_combined_roster(admin.id)

        with self.assertRaises(PermissionError):
            get_shift_report(staff.id)
