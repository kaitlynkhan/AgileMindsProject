"""
Comprehensive tests for the refactored models and controllers.
Tests verify:
1. User.get_json() works for all user types
2. Schedule.get_json() includes user_id
3. Shift relationships work correctly
4. Admin can create schedules for users
5. Permission checks work properly
"""
import unittest
from datetime import datetime, timedelta, timezone
from App.main import create_app
from App.database import db, create_db
from App.models import User, Staff, Admin, Schedule, Shift
from App.controllers.admin import create_schedule, add_shift
from App.controllers.user import create_user, get_user


class ModelConsistencyTests(unittest.TestCase):
    """Tests for model logic consistency after refactoring."""

    def setUp(self):
        """Set up test database before each test."""
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///test_consistency.db'
        })
        self.app_context = self.app.app_context()
        self.app_context.push()
        create_db()

    def tearDown(self):
        """Clean up test database after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # ========== User.get_json() Tests ==========
    
    def test_user_get_json_base_user(self):
        """Test that base User has get_json() method."""
        user = create_user("base_user", "password", "user")
        json_data = user.get_json()
        
        self.assertIsNotNone(json_data)
        self.assertEqual(json_data["username"], "base_user")
        self.assertEqual(json_data["role"], "user")
        self.assertIn("id", json_data)

    def test_user_get_json_admin(self):
        """Test that Admin inherits get_json() properly."""
        admin = create_user("admin_user", "password", "admin")
        json_data = admin.get_json()
        
        self.assertIsNotNone(json_data)
        self.assertEqual(json_data["username"], "admin_user")
        self.assertEqual(json_data["role"], "admin")

    def test_user_get_json_staff(self):
        """Test that Staff overrides get_json() with additional fields."""
        staff = create_user("staff_user", "password", "staff")
        json_data = staff.get_json()
        
        self.assertIsNotNone(json_data)
        self.assertEqual(json_data["username"], "staff_user")
        self.assertEqual(json_data["role"], "staff")
        # Staff should have additional fields
        self.assertIn("total_hours_scheduled", json_data)
        self.assertIn("upcoming_shift_count", json_data)

    # ========== Schedule.get_json() Tests ==========

    def test_schedule_get_json_includes_user_id(self):
        """Test that Schedule.get_json() includes user_id field."""
        admin = create_user("admin", "password", "admin")
        staff = create_user("staff", "password", "staff")
        
        schedule = create_schedule(admin.id, "Test Schedule", user_id=staff.id)
        json_data = schedule.get_json()
        
        self.assertIn("user_id", json_data)
        self.assertEqual(json_data["user_id"], staff.id)
        self.assertEqual(json_data["created_by"], admin.id)

    def test_schedule_get_json_user_id_none(self):
        """Test that Schedule.get_json() handles None user_id."""
        admin = create_user("admin", "password", "admin")
        schedule = create_schedule(admin.id, "General Schedule")
        
        json_data = schedule.get_json()
        
        self.assertIn("user_id", json_data)
        self.assertIsNone(json_data["user_id"])

    # ========== Shift Relationship Tests ==========

    def test_shift_staff_relationship_polymorphic(self):
        """Test that Shift.staff relationship works with User polymorphism."""
        admin = create_user("admin", "password", "admin")
        staff = create_user("staff", "password", "staff")
        schedule = create_schedule(admin.id, "Test Schedule")
        
        start = datetime.now(timezone.utc)
        end = start + timedelta(hours=8)
        shift = add_shift(admin.id, staff.id, schedule.id, start, end)
        
        # Reload shift to ensure relationship is loaded
        shift = db.session.get(Shift, shift.id)
        
        self.assertIsNotNone(shift.staff)
        self.assertEqual(shift.staff.id, staff.id)
        self.assertEqual(shift.staff.username, "staff")

    def test_staff_shifts_backref(self):
        """Test that Staff can access shifts via backref."""
        admin = create_user("admin", "password", "admin")
        staff = create_user("staff", "password", "staff")
        schedule = create_schedule(admin.id, "Test Schedule")
        
        start = datetime.now(timezone.utc)
        end = start + timedelta(hours=8)
        shift1 = add_shift(admin.id, staff.id, schedule.id, start, end)
        shift2 = add_shift(admin.id, staff.id, schedule.id, start + timedelta(days=1), end + timedelta(days=1))
        
        # Reload staff
        staff = get_user(staff.id)
        
        self.assertEqual(len(staff.shifts), 2)
        self.assertIn(shift1, staff.shifts)
        self.assertIn(shift2, staff.shifts)

    # ========== Schedule Creation Tests ==========

    def test_admin_create_schedule_for_user(self):
        """Test admin can create schedule for specific user."""
        admin = create_user("admin", "password", "admin")
        staff = create_user("staff", "password", "staff")
        
        schedule = create_schedule(admin.id, "Staff Schedule", user_id=staff.id)
        
        self.assertEqual(schedule.name, "Staff Schedule")
        self.assertEqual(schedule.created_by, admin.id)
        self.assertEqual(schedule.user_id, staff.id)

    def test_schedule_user_relationship(self):
        """Test Schedule.user relationship works correctly."""
        admin = create_user("admin", "password", "admin")
        staff = create_user("staff", "password", "staff")
        
        schedule = create_schedule(admin.id, "Staff Schedule", user_id=staff.id)
        
        # Reload to ensure relationships are loaded
        schedule = db.session.get(Schedule, schedule.id)
        staff = get_user(staff.id)
        
        self.assertEqual(schedule.user.id, staff.id)
        self.assertIn(schedule, staff.schedules)

    def test_schedule_creator_relationship(self):
        """Test Schedule.creator relationship works correctly."""
        admin = create_user("admin", "password", "admin")
        staff = create_user("staff", "password", "staff")
        
        schedule = create_schedule(admin.id, "Staff Schedule", user_id=staff.id)
        
        # Reload to ensure relationships are loaded
        schedule = db.session.get(Schedule, schedule.id)
        admin = get_user(admin.id)
        
        self.assertEqual(schedule.creator.id, admin.id)
        self.assertIn(schedule, admin.created_schedules)

    # ========== Permission Tests ==========

    def test_non_admin_cannot_create_schedule(self):
        """Test that non-admin users cannot create schedules."""
        staff = create_user("staff", "password", "staff")
        
        with self.assertRaises(PermissionError):
            create_schedule(staff.id, "Invalid Schedule")

    def test_non_admin_cannot_add_shift(self):
        """Test that non-admin users cannot add shifts."""
        admin = create_user("admin", "password", "admin")
        staff = create_user("staff", "password", "staff")
        schedule = create_schedule(admin.id, "Test Schedule")
        
        start = datetime.now(timezone.utc)
        end = start + timedelta(hours=8)
        
        with self.assertRaises(PermissionError):
            add_shift(staff.id, staff.id, schedule.id, start, end)

    # ========== Timezone Tests ==========

    def test_schedule_created_at_timezone_aware(self):
        """Test that Schedule.created_at uses timezone-aware datetime."""
        admin = create_user("admin", "password", "admin")
        schedule = create_schedule(admin.id, "Test Schedule")
        
        # Reload to get the actual saved value
        schedule = db.session.get(Schedule, schedule.id)
        
        self.assertIsNotNone(schedule.created_at)
        # The datetime should be recent (within last minute)
        now = datetime.now(timezone.utc)
        time_diff = now - schedule.created_at.replace(tzinfo=timezone.utc)
        self.assertLess(time_diff.total_seconds(), 60)

    # ========== Integration Tests ==========

    def test_full_workflow_admin_creates_schedule_with_shifts(self):
        """Test complete workflow: admin creates schedule for user with shifts."""
        admin = create_user("admin", "password", "admin")
        staff1 = create_user("staff1", "password", "staff")
        staff2 = create_user("staff2", "password", "staff")
        
        # Admin creates schedule for staff1
        schedule = create_schedule(admin.id, "Week Schedule", user_id=staff1.id)
        
        # Admin adds shifts for both staff members
        start = datetime.now(timezone.utc)
        shift1 = add_shift(admin.id, staff1.id, schedule.id, start, start + timedelta(hours=8))
        shift2 = add_shift(admin.id, staff2.id, schedule.id, start + timedelta(hours=8), start + timedelta(hours=16))
        
        # Verify schedule
        schedule = db.session.get(Schedule, schedule.id)
        self.assertEqual(len(schedule.shifts), 2)
        self.assertEqual(schedule.user_id, staff1.id)
        
        # Verify staff1 has access to their schedule
        staff1 = get_user(staff1.id)
        self.assertIn(schedule, staff1.schedules)
        self.assertEqual(len(staff1.shifts), 1)
        
        # Verify staff2 has their shift but not the schedule ownership
        staff2 = get_user(staff2.id)
        self.assertEqual(len(staff2.shifts), 1)
        self.assertNotIn(schedule, staff2.schedules)

    def test_schedule_json_complete(self):
        """Test that schedule JSON contains all expected fields."""
        admin = create_user("admin", "password", "admin")
        staff = create_user("staff", "password", "staff")
        schedule = create_schedule(admin.id, "Test Schedule", user_id=staff.id)
        
        start = datetime.now(timezone.utc)
        add_shift(admin.id, staff.id, schedule.id, start, start + timedelta(hours=8))
        
        json_data = schedule.get_json()
        
        # Check all required fields
        required_fields = ["id", "name", "created_at", "created_by", "user_id", 
                          "shift_count", "strategy_used", "shifts"]
        for field in required_fields:
            self.assertIn(field, json_data, f"Missing field: {field}")
        
        # Verify values
        self.assertEqual(json_data["name"], "Test Schedule")
        self.assertEqual(json_data["created_by"], admin.id)
        self.assertEqual(json_data["user_id"], staff.id)
        self.assertEqual(json_data["shift_count"], 1)
        self.assertEqual(len(json_data["shifts"]), 1)


if __name__ == '__main__':
    unittest.main()
