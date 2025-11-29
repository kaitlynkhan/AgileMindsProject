import pytest
import unittest
from datetime import datetime, timedelta
from App.main import create_app
from App.database import db, create_db
from App.models import User, Staff, Admin, Schedule, Shift
from App.controllers.admin import create_schedule, add_shift
from App.controllers.user import create_user, get_user

@pytest.fixture(autouse=True)
def clean_db():
    db.drop_all()
    create_db()
    db.session.remove()
    yield

class RefactoredModelTests(unittest.TestCase):

    def setUp(self):
        # Create app context for tests
        self.app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test_refactor.db'})
        self.app_context = self.app.app_context()
        self.app_context.push()
        create_db()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_admin_create_schedule_for_user(self):
        admin = create_user("admin_test", "password", "admin")
        staff = create_user("staff_test", "password", "staff")
        
        # Admin creates schedule for staff
        schedule = create_schedule(admin.id, "Staff Schedule", user_id=staff.id)
        
        self.assertIsNotNone(schedule)
        self.assertEqual(schedule.name, "Staff Schedule")
        self.assertEqual(schedule.created_by, admin.id)
        self.assertEqual(schedule.user_id, staff.id)
        
        # Verify relationships
        # Reload objects to ensure relationships are populated
        staff = get_user(staff.id)
        admin = get_user(admin.id)
        
        self.assertIn(schedule, staff.schedules)
        self.assertIn(schedule, admin.created_schedules)

    def test_schedule_shifts_relationship(self):
        admin = create_user("admin_test", "password", "admin")
        staff = create_user("staff_test", "password", "staff")
        schedule = create_schedule(admin.id, "Staff Schedule", user_id=staff.id)
        
        start = datetime.now()
        end = start + timedelta(hours=8)
        
        shift = add_shift(admin.id, staff.id, schedule.id, start, end)
        
        # Reload schedule
        schedule = db.session.get(Schedule, schedule.id)
        
        self.assertIn(shift, schedule.shifts)
        self.assertEqual(shift.schedule_id, schedule.id)

    def test_create_schedule_without_user(self):
        admin = create_user("admin_test", "password", "admin")
        schedule = create_schedule(admin.id, "General Schedule")
        
        self.assertIsNone(schedule.user_id)
        self.assertEqual(schedule.created_by, admin.id)
