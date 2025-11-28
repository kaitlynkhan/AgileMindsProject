# Running Tests for AgileMinds Project

This guide explains how to run the tests for the refactored models and controllers.

## Test Files

1. **`test_model_consistency.py`** - Comprehensive tests for the refactored models
   - Tests User.get_json() for all user types
   - Tests Schedule.get_json() includes user_id
   - Tests Shift relationships work correctly
   - Tests Admin can create schedules for users
   - Tests permission checks work properly
   - Tests timezone-aware datetime handling

2. **`test_refactored_models.py`** - Basic tests for schedule creation and relationships

3. **`test_app.py`** - Original application tests (updated to work with refactored code)

## How to Run Tests

### Run All Tests in a Specific File

```powershell
# Run the comprehensive model consistency tests
python -m unittest App.tests.test_model_consistency -v

# Run the basic refactored model tests
python -m unittest App.tests.test_refactored_models -v

# Run the original app tests
python -m unittest App.tests.test_app -v
```

### Run All Tests in the Project

```powershell
# Discover and run all tests
python -m unittest discover App/tests -v
```

### Run a Specific Test Class

```powershell
# Run only the ModelConsistencyTests class
python -m unittest App.tests.test_model_consistency.ModelConsistencyTests -v
```

### Run a Specific Test Method

```powershell
# Run a single test method
python -m unittest App.tests.test_model_consistency.ModelConsistencyTests.test_user_get_json_base_user -v
```

## Test Output

- **`-v`** flag provides verbose output showing each test name and result
- **OK** means all tests passed
- **FAILED** shows which tests failed with error details

## Expected Results

All 15 tests in `test_model_consistency.py` should pass:

```
test_admin_create_schedule_for_user ... ok
test_full_workflow_admin_creates_schedule_with_shifts ... ok
test_non_admin_cannot_add_shift ... ok
test_non_admin_cannot_create_schedule ... ok
test_schedule_created_at_timezone_aware ... ok
test_schedule_creator_relationship ... ok
test_schedule_get_json_includes_user_id ... ok
test_schedule_get_json_user_id_none ... ok
test_schedule_json_complete ... ok
test_schedule_user_relationship ... ok
test_shift_staff_relationship_polymorphic ... ok
test_staff_shifts_backref ... ok
test_user_get_json_admin ... ok
test_user_get_json_base_user ... ok
test_user_get_json_staff ... ok

----------------------------------------------------------------------
Ran 15 tests in ~17s

OK
```

## What Was Fixed

The following issues were identified and fixed:

### Critical Fixes
1. ✅ Added `User.get_json()` method - Base class now has JSON serialization
2. ✅ Added `user_id` to `Schedule.get_json()` - Exposes schedule ownership
3. ✅ Fixed `Staff.get_json()` - Changed from property to method for consistency

### Design Improvements
4. ✅ Removed incomplete `Admin.create_schedule()` - Controllers handle persistence
5. ✅ Updated `Shift.staff` relationship - Uses User instead of Staff for polymorphism
6. ✅ Removed duplicate permission checks - Only in admin controller now
7. ✅ Renamed `controller_add_shift` to `add_shift` - Consistent naming

### Code Quality
8. ✅ Updated to timezone-aware datetime - Uses `datetime.now(timezone.utc)`
9. ✅ Added documentation - Explained backref relationships in Staff model
10. ✅ Added `Schedule.__init__()` - Proper initialization method

## Database Cleanup

Test databases are automatically created and cleaned up. If you see leftover test databases:

```powershell
# Clean up test databases
del test_consistency.db
del test_refactor.db
```

## Troubleshooting

### Import Errors
If you get import errors, make sure you're running from the project root directory:
```powershell
cd "c:\Users\ronel\Desktop\New folder\AgileMindsProject-main"
```

### Database Locked Errors
If tests fail with "database is locked", close any database viewers and try again.

### Module Not Found
Ensure all dependencies are installed:
```powershell
pip install -r requirements.txt
```
