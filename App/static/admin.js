document.addEventListener('DOMContentLoaded', function () {
    // Initialize Materialize components
    var dateElems = document.querySelectorAll('.datepicker');
    M.Datepicker.init(dateElems, {
        format: 'yyyy-mm-dd',
        autoClose: true,
        showClearBtn: true
    });

    var selectElems = document.querySelectorAll('select');
    M.FormSelect.init(selectElems);

    // --- Create Schedule ---
    const createScheduleForm = document.getElementById('createScheduleForm');
    if (createScheduleForm) {
        createScheduleForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('schedule_name').value;
            const userId = document.getElementById('user_id').value;

            const payload = {
                admin_id: CURRENT_USER_ID,
                name: name
            };
            if (userId) payload.user_id = parseInt(userId);

            try {
                const response = await fetch('/createSchedule', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();
                if (response.ok) {
                    M.toast({ html: 'Schedule created successfully!', classes: 'green' });
                    createScheduleForm.reset();
                } else {
                    M.toast({ html: data.error || 'Error creating schedule', classes: 'red' });
                }
            } catch (error) {
                console.error('Error:', error);
                M.toast({ html: 'Network error', classes: 'red' });
            }
        });
    }

    // --- Add Shift ---
    const addShiftForm = document.getElementById('addShiftForm');
    if (addShiftForm) {
        addShiftForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const scheduleId = document.getElementById('shift_schedule_id').value;
            const staffId = document.getElementById('staff_id').value;
            const startDate = document.getElementById('start_time').value;
            const endDate = document.getElementById('end_time').value;
            const shiftType = document.getElementById('shift_type').value;

            if (!startDate || !endDate) {
                M.toast({ html: 'Please select start and end dates', classes: 'red' });
                return;
            }

            // Construct ISO strings (assuming 9am to 5pm for simplicity if time not picked, 
            // but the UI only has datepicker. Ideally we need timepicker too.
            // For now, let's append default times or ask user to input full ISO string?
            // The view expects ISO format. 
            // Let's append T09:00:00 and T17:00:00 for demo purposes if only date is picked.
            // Or better, use a datetime-local input type in HTML instead of materialize datepicker?
            // Materialize doesn't have a native datetime picker.
            // Let's stick to appending time for now to keep it simple, or use the value as is if user types it.

            const startDateTime = `${startDate}T09:00:00`;
            const endDateTime = `${endDate}T17:00:00`;

            const payload = {
                admin_id: CURRENT_USER_ID,
                staff_id: parseInt(staffId),
                schedule_id: parseInt(scheduleId),
                start_time: startDateTime,
                end_time: endDateTime,
                shift_type: shiftType
            };

            try {
                const response = await fetch('/addShift', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();
                if (response.ok) {
                    M.toast({ html: 'Shift added successfully!', classes: 'green' });
                    addShiftForm.reset();
                } else {
                    M.toast({ html: data.error || 'Error adding shift', classes: 'red' });
                }
            } catch (error) {
                console.error('Error:', error);
                M.toast({ html: 'Network error', classes: 'red' });
            }
        });
    }

    // --- Auto Populate ---
    const autoPopulateForm = document.getElementById('autoPopulateForm');
    if (autoPopulateForm) {
        autoPopulateForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const scheduleId = document.getElementById('auto_schedule_id').value;
            const strategy = document.getElementById('strategy_name').value;

            const payload = {
                admin_id: CURRENT_USER_ID,
                schedule_id: parseInt(scheduleId),
                strategy_name: strategy
            };

            try {
                const response = await fetch('/autoPopulateSchedule', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();
                if (response.ok) {
                    M.toast({ html: data.message, classes: 'green' });
                    autoPopulateForm.reset();
                } else {
                    M.toast({ html: data.error || 'Error running strategy', classes: 'red' });
                }
            } catch (error) {
                console.error('Error:', error);
                M.toast({ html: 'Network error', classes: 'red' });
            }
        });
    }

    // --- Get Report ---
    const getReportBtn = document.getElementById('getReportBtn');
    if (getReportBtn) {
        getReportBtn.addEventListener('click', async () => {
            const scheduleId = document.getElementById('report_schedule_id').value;
            if (!scheduleId) {
                M.toast({ html: 'Please enter a Schedule ID', classes: 'red' });
                return;
            }

            try {
                // Use query parameters
                const url = `/scheduleReport?admin_id=${CURRENT_USER_ID}&schedule_id=${scheduleId}`;
                const response = await fetch(url);
                const data = await response.json();

                if (response.ok) {
                    displayReport(data);
                } else {
                    M.toast({ html: data.error || 'Error fetching report', classes: 'red' });
                }
            } catch (error) {
                console.error('Error:', error);
                M.toast({ html: 'Network error', classes: 'red' });
            }
        });
    }

    function displayReport(data) {
        const resultDiv = document.getElementById('reportResult');
        const tbody = document.getElementById('reportTableBody');
        tbody.innerHTML = '';

        if (data.shifts && data.shifts.length > 0) {
            data.shifts.forEach(shift => {
                const row = `
                    <tr>
                        <td>${shift.id}</td>
                        <td>${shift.staff_id}</td>
                        <td>${new Date(shift.start_time).toLocaleString()}</td>
                        <td>${new Date(shift.end_time).toLocaleString()}</td>
                        <td>${shift.type}</td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });
            resultDiv.style.display = 'block';
        } else {
            M.toast({ html: 'No shifts found for this schedule', classes: 'orange' });
            resultDiv.style.display = 'none';
        }
    }
});
