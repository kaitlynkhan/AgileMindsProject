# API Reference - AgileMinds Schedule Management

Quick reference for all API endpoints after refactoring.

---

## 🔐 Authentication

All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

---

## 👨‍💼 Admin Endpoints

### Create Schedule
**POST** `/createSchedule`

Create a new schedule, optionally assigned to a specific user.

**Request:**
```json
{
  "admin_id": 1,
  "name": "Weekly Roster",
  "user_id": 5  // Optional - assigns schedule to this user
}
```

**Response (201):**
```json
{
  "id": 10,
  "name": "Weekly Roster",
  "created_by": 1,
  "user_id": 5,
  "created_at": "2025-01-15T10:00:00+00:00",
  "shift_count": 0,
  "strategy_used": null,
  "shifts": []
}
```

---

### Add Shift
**POST** `/addShift`

Add a single shift to a schedule.

**Request:**
```json
{
  "admin_id": 1,
  "staff_id": 5,
  "schedule_id": 10,
  "start_time": "2025-01-15T09:00:00",
  "end_time": "2025-01-15T17:00:00",
  "shift_type": "day"  // Optional: "day" or "night"
}
```

**Response (201):**
```json
{
  "id": 25,
  "staff_id": 5,
  "staff_name": "john_doe",
  "schedule_id": 10,
  "start_time": "2025-01-15T09:00:00",
  "end_time": "2025-01-15T17:00:00",
  "clock_in": null,
  "clock_out": null,
  "is_completed": false,
  "is_active_shift": false,
  "is_late": false
}
```

---

### Auto-Populate Schedule
**POST** `/autoPopulateSchedule`

Auto-populate a schedule using a scheduling strategy.

**Request:**
```json
{
  "admin_id": 1,
  "schedule_id": 10,
  "strategy_name": "even_distribution"  // Options: "even_distribution", "minimize_days", "balance_day_night"
}
```

**Response (200):**
```json
{
  "message": "Schedule auto-populated successfully",
  "strategy_used": "even_distribution",
  "shifts_updated": 15
}
```

---

### Get Schedule Report
**GET** `/scheduleReport`

Get detailed report of a schedule with all shifts.

**Request (Query Params):**
```
GET /scheduleReport?admin_id=1&schedule_id=10
```

**Or Request (JSON Body):**
```json
{
  "admin_id": 1,
  "schedule_id": 10
}
```

**Response (200):**
```json
{
  "id": 10,
  "name": "Weekly Roster",
  "created_by": 1,
  "user_id": 5,
  "created_at": "2025-01-15T10:00:00+00:00",
  "shift_count": 15,
  "strategy_used": "even_distribution",
  "shifts": [
    {
      "id": 25,
      "staff_id": 5,
      "staff_name": "john_doe",
      "schedule_id": 10,
      "start_time": "2025-01-15T09:00:00",
      "end_time": "2025-01-15T17:00:00",
      "clock_in": null,
      "clock_out": null,
      "is_completed": false,
      "is_active_shift": false,
      "is_late": false
    }
    // ... more shifts
  ]
}
```

---

## 👷 Staff Endpoints

### Get All Shifts
**GET** `/allshifts`

Get all shifts in the combined roster for a staff member.

**Request (Query Params):**
```
GET /allshifts?staff_id=5
```

**Or Request (JSON Body):**
```json
{
  "staff_id": 5
}
```

**Response (200):**
```json
[
  {
    "id": 25,
    "staff_id": 5,
    "staff_name": "john_doe",
    "schedule_id": 10,
    "start_time": "2025-01-15T09:00:00",
    "end_time": "2025-01-15T17:00:00",
    "clock_in": null,
    "clock_out": null,
    "is_completed": false,
    "is_active_shift": false,
    "is_late": false
  }
  // ... more shifts
]
```

---

### Get Specific Shift
**GET** `/staffshift`

Get details of a specific shift for a staff member.

**Request (Query Params):**
```
GET /staffshift?staff_id=5&shift_id=25
```

**Or Request (JSON Body):**
```json
{
  "staff_id": 5,
  "shift_id": 25
}
```

**Response (200):**
```json
{
  "id": 25,
  "staff_id": 5,
  "staff_name": "john_doe",
  "schedule_id": 10,
  "start_time": "2025-01-15T09:00:00",
  "end_time": "2025-01-15T17:00:00",
  "clock_in": null,
  "clock_out": null,
  "is_completed": false,
  "is_active_shift": false,
  "is_late": false
}
```

---

### Get Combined Roster
**GET** `/staff/combinedRoster`

Get the combined roster (all shifts) for a staff member.

**Request (Query Params):**
```
GET /staff/combinedRoster?staff_id=5
```

**Response (200):**
```json
[
  {
    "id": 25,
    "staff_id": 5,
    "staff_name": "john_doe",
    "schedule_id": 10,
    "start_time": "2025-01-15T09:00:00",
    "end_time": "2025-01-15T17:00:00",
    "clock_in": null,
    "clock_out": null,
    "is_completed": false,
    "is_active_shift": false,
    "is_late": false
  }
  // ... more shifts
]
```

---

### Clock In
**POST** `/staff/clockIn`

Clock in to a shift.

**Request:**
```json
{
  "staff_id": 5,
  "shift_id": 25
}
```

**Response (200):**
```json
{
  "id": 25,
  "staff_id": 5,
  "staff_name": "john_doe",
  "schedule_id": 10,
  "start_time": "2025-01-15T09:00:00",
  "end_time": "2025-01-15T17:00:00",
  "clock_in": "2025-01-15T09:05:00",  // ✅ Now populated
  "clock_out": null,
  "is_completed": false,
  "is_active_shift": true,
  "is_late": true  // Clocked in after start time
}
```

---

### Clock Out
**POST** `/staff/clockOut`

Clock out from a shift.

**Request:**
```json
{
  "staff_id": 5,
  "shift_id": 25
}
```

**Response (200):**
```json
{
  "id": 25,
  "staff_id": 5,
  "staff_name": "john_doe",
  "schedule_id": 10,
  "start_time": "2025-01-15T09:00:00",
  "end_time": "2025-01-15T17:00:00",
  "clock_in": "2025-01-15T09:05:00",
  "clock_out": "2025-01-15T17:00:00",  // ✅ Now populated
  "is_completed": true,  // ✅ Both clock in and out recorded
  "is_active_shift": false,
  "is_late": true
}
```

---

### Get My Schedules ✨ NEW
**GET** `/staff/mySchedules`

Get all schedules assigned to a staff member.

**Request (Query Params):**
```
GET /staff/mySchedules?staff_id=5
```

**Response (200):**
```json
{
  "staff_id": 5,
  "username": "john_doe",
  "schedules": [
    {
      "id": 10,
      "name": "John's Weekly Schedule",
      "created_by": 1,
      "user_id": 5,
      "created_at": "2025-01-15T10:00:00+00:00",
      "shift_count": 15,
      "strategy_used": "even_distribution",
      "shifts": [...]
    },
    {
      "id": 12,
      "name": "John's Monthly Schedule",
      "created_by": 1,
      "user_id": 5,
      "created_at": "2025-01-20T10:00:00+00:00",
      "shift_count": 60,
      "strategy_used": "minimize_days",
      "shifts": [...]
    }
  ]
}
```

---

## 📋 Error Responses

### 400 Bad Request
Missing or invalid parameters.

```json
{
  "error": "admin_id and name are required"
}
```

### 403 Forbidden
Permission denied.

```json
{
  "error": "Only admins can create schedules"
}
```

### 404 Not Found
Resource not found.

```json
{
  "error": "Shift not found"
}
```

### 500 Internal Server Error
Database or unexpected error.

```json
{
  "error": "Database error"
}
```

---

## 🔑 Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET or general success |
| 201 | Created | Resource successfully created |
| 400 | Bad Request | Missing/invalid parameters |
| 403 | Forbidden | Permission denied |
| 404 | Not Found | Resource doesn't exist |
| 500 | Internal Server Error | Database/unexpected error |

---

## 📝 Notes

1. **Datetime Format:** All datetime fields use ISO 8601 format: `YYYY-MM-DDTHH:MM:SS`
2. **Timezone:** All datetimes are timezone-aware (UTC)
3. **JWT Required:** All endpoints require valid JWT token
4. **GET Flexibility:** GET endpoints accept both query params and JSON body
5. **Shift Types:** Valid values are `"day"` or `"night"`
6. **Strategies:** Valid values are `"even_distribution"`, `"minimize_days"`, or `"balance_day_night"`

---

## 🚀 Quick Start Examples

### Create a Complete Schedule

```bash
# 1. Create schedule for user
curl -X POST http://localhost:5000/createSchedule \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"admin_id": 1, "name": "Week 1", "user_id": 5}'

# 2. Add shifts
curl -X POST http://localhost:5000/addShift \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "admin_id": 1,
    "staff_id": 5,
    "schedule_id": 10,
    "start_time": "2025-01-15T09:00:00",
    "end_time": "2025-01-15T17:00:00"
  }'

# 3. Auto-populate remaining shifts
curl -X POST http://localhost:5000/autoPopulateSchedule \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"admin_id": 1, "schedule_id": 10, "strategy_name": "even_distribution"}'

# 4. View report
curl -X GET "http://localhost:5000/scheduleReport?admin_id=1&schedule_id=10" \
  -H "Authorization: Bearer $TOKEN"
```

### Staff Clock In/Out Workflow

```bash
# 1. View my schedules
curl -X GET "http://localhost:5000/staff/mySchedules?staff_id=5" \
  -H "Authorization: Bearer $TOKEN"

# 2. View all my shifts
curl -X GET "http://localhost:5000/allshifts?staff_id=5" \
  -H "Authorization: Bearer $TOKEN"

# 3. Clock in
curl -X POST http://localhost:5000/staff/clockIn \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"staff_id": 5, "shift_id": 25}'

# 4. Clock out
curl -X POST http://localhost:5000/staff/clockOut \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"staff_id": 5, "shift_id": 25}'
```

---

**Last Updated:** 2025-11-27  
**Version:** 2.0 (After Refactoring)
