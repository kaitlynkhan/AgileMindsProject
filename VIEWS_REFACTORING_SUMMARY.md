# Views Refactoring Summary

## Overview
Updated all views to align with the refactored models and controllers, improving error handling, consistency, and API documentation.

---

## Files Modified

### 1. `App/views/adminView.py` - Admin API Routes

#### Changes Made:

**✅ Added `user_id` Support to Schedule Creation**
- Updated `/createSchedule` endpoint to accept optional `user_id` parameter
- Allows admins to create schedules assigned to specific users
- Matches refactored `admin.create_schedule(admin_id, name, user_id=None)` signature

**✅ Fixed `add_shift` Parameter Order**
- Corrected parameter order to match controller: `admin_id, staff_id, schedule_id, start_time, end_time, shift_type`
- Previous version had incorrect order causing bugs

**✅ Separated Auto-Populate Functionality**
- Created new `/autoPopulateSchedule` endpoint
- Removed auto-populate logic from `/addShift` (was causing confusion)
- Now `/addShift` only adds a single shift
- `/autoPopulateSchedule` handles strategy-based scheduling

**✅ Improved Error Handling**
- Added comprehensive validation for all required fields
- Better error messages with specific field requirements
- Proper HTTP status codes (201 for created, 400 for bad request, 403 for forbidden, 500 for server error)
- Catches `PermissionError`, `ValueError`, and `SQLAlchemyError` separately

**✅ Enhanced `/scheduleReport` Endpoint**
- Now accepts both JSON body and query parameters
- More flexible for GET requests
- Better validation and error handling

**✅ Added API Documentation**
- Comprehensive docstrings for each endpoint
- Expected JSON format documented
- Parameter descriptions included

---

### 2. `App/views/staffView.py` - Staff API Routes

#### Changes Made:

**✅ Fixed Critical Bugs**
- **Bug 1:** `staff_clock_in` was hardcoded to use shift_id=4 instead of actual shift
- **Bug 2:** `staff_clock_out` had variable name collision (`staff` module vs `staff` variable)
- **Bug 3:** Missing `@jwt_required()` decorator on `/allshifts`
- **Bug 4:** Duplicate Blueprint declaration removed

**✅ Improved Parameter Handling**
- All endpoints now accept both JSON body and query parameters
- Better for GET requests which shouldn't have bodies
- Consistent parameter extraction across all endpoints

**✅ Enhanced Error Handling**
- Proper exception catching for `PermissionError`, `ValueError`, `SQLAlchemyError`
- Better error messages
- Correct HTTP status codes

**✅ Added New Endpoint: `/staff/mySchedules`**
- Allows staff to view all schedules assigned to them
- Leverages new `user.schedules` relationship from refactored models
- Returns schedule details with user information

**✅ Fixed Clock In/Out Logic**
- Now requires explicit `shift_id` parameter
- No longer relies on `current_shift` property (was unreliable)
- More explicit and less error-prone

**✅ Consistent Response Format**
- All endpoints return JSON
- Shift responses use `shift.get_json()` method
- Consistent error response format

**✅ Added API Documentation**
- Docstrings for all endpoints
- Expected parameters documented
- Clear descriptions of functionality

---

## API Endpoints Summary

### Admin Endpoints (`/admin_view`)

| Endpoint | Method | Purpose | New/Updated |
|----------|--------|---------|-------------|
| `/createSchedule` | POST | Create schedule (optionally for user) | ✅ Updated |
| `/addShift` | POST | Add single shift to schedule | ✅ Updated |
| `/autoPopulateSchedule` | POST | Auto-populate using strategy | ✨ New |
| `/scheduleReport` | GET | Get schedule details | ✅ Updated |

### Staff Endpoints (`/staff_views`)

| Endpoint | Method | Purpose | New/Updated |
|----------|--------|---------|-------------|
| `/allshifts` | GET | Get all shifts for staff | ✅ Updated |
| `/staffshift` | GET | Get specific shift details | ✅ Updated |
| `/staff/combinedRoster` | GET | Get combined roster | ✅ Updated |
| `/staff/clockIn` | POST | Clock in to shift | ✅ Updated |
| `/staff/clockOut` | POST | Clock out from shift | ✅ Updated |
| `/staff/mySchedules` | GET | Get assigned schedules | ✨ New |

---

## Breaking Changes

### ⚠️ `/addShift` Parameter Order Changed
**Before:**
```json
{
  "schedule_id": 1,
  "staff_id": 2,
  "admin_id": 3,
  "start_time": "2025-01-01T09:00:00",
  "end_time": "2025-01-01T17:00:00",
  "shift_type": "day"
}
```

**After:** (Same JSON, but controller expects different order)
- Controller now expects: `admin_id, staff_id, schedule_id, start_time, end_time, shift_type`
- View handles the conversion correctly

### ⚠️ `/addShift` No Longer Auto-Populates
**Before:** `/addShift` would automatically run auto-populate strategy

**After:** 
- `/addShift` only adds the single shift
- Use `/autoPopulateSchedule` separately for strategy-based scheduling

### ⚠️ Clock In/Out Requires `shift_id`
**Before:** Used `current_shift` property (unreliable)

**After:** Requires explicit `shift_id` parameter
```json
{
  "staff_id": 1,
  "shift_id": 5
}
```

---

## New Features

### 1. Schedule Assignment to Users
Admins can now create schedules for specific users:
```json
POST /createSchedule
{
  "admin_id": 1,
  "name": "John's Weekly Schedule",
  "user_id": 5  // Optional: assigns to user 5
}
```

### 2. Staff Can View Their Schedules
New endpoint for staff to see schedules assigned to them:
```json
GET /staff/mySchedules?staff_id=5

Response:
{
  "staff_id": 5,
  "username": "john_doe",
  "schedules": [
    {
      "id": 1,
      "name": "John's Weekly Schedule",
      "user_id": 5,
      "created_by": 1,
      "shifts": [...]
    }
  ]
}
```

### 3. Flexible Parameter Passing
All GET endpoints now accept parameters via:
- JSON body (for consistency)
- Query parameters (REST best practice)

Example:
```
GET /scheduleReport?admin_id=1&schedule_id=3
```
or
```
GET /scheduleReport
Body: {"admin_id": 1, "schedule_id": 3}
```

---

## Improvements

### Error Handling
**Before:**
```python
except (PermissionError):
    return jsonify({"error": "Admin access required"}), 403
```

**After:**
```python
except PermissionError as e:
    return jsonify({"error": str(e)}), 403
except ValueError as e:
    return jsonify({"error": str(e)}), 400
except SQLAlchemyError as e:
    return jsonify({"error": "Database error"}), 500
```

### Input Validation
**Before:**
```python
if data:
    schedule = admin.create_schedule(data.get("admin_id"), data.get("name"))
```

**After:**
```python
if not data:
    return jsonify({"error": "No data provided"}), 400

admin_id = data.get("admin_id")
name = data.get("name")

if not admin_id or not name:
    return jsonify({"error": "admin_id and name are required"}), 400
```

### Response Codes
- `200` - Success (GET, general success)
- `201` - Created (POST for new resources)
- `400` - Bad Request (missing/invalid parameters)
- `403` - Forbidden (permission denied)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error (database/unexpected errors)

---

## Testing the Updated Views

### Test Create Schedule with User Assignment
```bash
curl -X POST http://localhost:5000/createSchedule \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "admin_id": 1,
    "name": "Weekly Roster",
    "user_id": 5
  }'
```

### Test Add Shift (New Parameter Order)
```bash
curl -X POST http://localhost:5000/addShift \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "admin_id": 1,
    "staff_id": 5,
    "schedule_id": 3,
    "start_time": "2025-01-15T09:00:00",
    "end_time": "2025-01-15T17:00:00",
    "shift_type": "day"
  }'
```

### Test Auto-Populate Schedule
```bash
curl -X POST http://localhost:5000/autoPopulateSchedule \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "admin_id": 1,
    "schedule_id": 3,
    "strategy_name": "even_distribution"
  }'
```

### Test Staff View Schedules
```bash
curl -X GET "http://localhost:5000/staff/mySchedules?staff_id=5" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Test Clock In with Shift ID
```bash
curl -X POST http://localhost:5000/staff/clockIn \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "staff_id": 5,
    "shift_id": 10
  }'
```

---

## Migration Guide

### For Frontend Developers

1. **Update Schedule Creation Calls**
   - Add optional `user_id` field to assign schedules to users
   - Check response for `user_id` in schedule JSON

2. **Separate Add Shift and Auto-Populate**
   - Don't expect auto-populate to happen when adding shifts
   - Call `/autoPopulateSchedule` separately if needed

3. **Update Clock In/Out Calls**
   - Must now provide `shift_id` explicitly
   - Can no longer rely on automatic current shift detection

4. **Use New Staff Schedules Endpoint**
   - Staff can now view their assigned schedules via `/staff/mySchedules`

5. **Handle New Error Responses**
   - More specific error messages
   - Check for 400 vs 403 vs 404 vs 500 status codes

---

## Benefits

1. **✅ Consistency** - All views match refactored controllers
2. **✅ Better Errors** - Specific, actionable error messages
3. **✅ Documentation** - Every endpoint has clear docstrings
4. **✅ Flexibility** - GET endpoints accept query params or JSON
5. **✅ Bug Fixes** - Critical bugs in clock in/out resolved
6. **✅ New Features** - Schedule assignment, view my schedules
7. **✅ Maintainability** - Cleaner code, better structure
8. **✅ RESTful** - Proper HTTP methods and status codes

---

## Files Changed

- ✅ `App/views/adminView.py` - Complete refactor
- ✅ `App/views/staffView.py` - Complete refactor
- ℹ️ `App/views/admin.py` - No changes needed (Flask-Admin integration)
- ℹ️ `App/views/user.py` - No changes needed (basic CRUD)
- ℹ️ `App/views/auth.py` - No changes needed (authentication)
- ℹ️ `App/views/index.py` - No changes needed (static pages)

---

**All views are now aligned with the refactored models and controllers!** 🎉
