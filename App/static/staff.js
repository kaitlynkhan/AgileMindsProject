document.addEventListener('DOMContentLoaded', function () {
    var modalElems = document.querySelectorAll('.modal');
    var modalInstances = M.Modal.init(modalElems);

    loadShifts();

    let selectedShiftId = null;
    let actionType = null; // 'in' or 'out'

    async function loadShifts() {
        const container = document.getElementById('shiftsContainer');

        try {
            const response = await fetch(`/allshifts?staff_id=${CURRENT_USER_ID}`);
            const shifts = await response.json();

            container.innerHTML = '';

            if (shifts.length === 0) {
                container.innerHTML = '<p class="center-align grey-text">No shifts assigned.</p>';
                return;
            }

            shifts.forEach(shift => {
                const shiftDate = new Date(shift.start_time);
                const endDate = new Date(shift.end_time);

                const card = document.createElement('div');
                card.className = 'col s12 m6 l4 animate-fade-in';
                card.innerHTML = `
                    <div class="card">
                        <div class="card-content">
                            <span class="card-title">${shift.type.toUpperCase()} Shift</span>
                            <p><i class="material-icons tiny">event</i> ${shiftDate.toLocaleDateString()}</p>
                            <p><i class="material-icons tiny">access_time</i> ${shiftDate.toLocaleTimeString()} - ${endDate.toLocaleTimeString()}</p>
                            <div class="mt-4 center-align" style="margin-top: 20px;">
                                <button class="btn waves-effect waves-light green darken-1 clock-btn" 
                                    data-id="${shift.id}" data-action="in">
                                    Clock In
                                </button>
                                <button class="btn waves-effect waves-light red darken-1 clock-btn" 
                                    data-id="${shift.id}" data-action="out" style="margin-left: 10px;">
                                    Clock Out
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                container.appendChild(card);
            });

            // Attach event listeners
            document.querySelectorAll('.clock-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    selectedShiftId = e.target.dataset.id;
                    actionType = e.target.dataset.action;

                    const modal = M.Modal.getInstance(document.getElementById('clockModal'));
                    document.getElementById('modalTitle').innerText = actionType === 'in' ? 'Clock In' : 'Clock Out';
                    document.getElementById('actionText').innerText = actionType === 'in' ? 'clock in' : 'clock out';
                    document.getElementById('shiftDetails').innerText = `Shift ID: ${selectedShiftId}`;
                    modal.open();
                });
            });

        } catch (error) {
            console.error('Error:', error);
            container.innerHTML = '<p class="center-align red-text">Error loading shifts.</p>';
        }
    }

    document.getElementById('confirmClockBtn').addEventListener('click', async () => {
        if (!selectedShiftId || !actionType) return;

        const endpoint = actionType === 'in' ? '/staff/clockIn' : '/staff/clockOut';

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    staff_id: CURRENT_USER_ID,
                    shift_id: parseInt(selectedShiftId)
                })
            });

            const data = await response.json();

            if (response.ok) {
                M.toast({ html: `Successfully clocked ${actionType}!`, classes: 'green' });
            } else {
                M.toast({ html: data.error || 'Error processing request', classes: 'red' });
            }
        } catch (error) {
            console.error('Error:', error);
            M.toast({ html: 'Network error', classes: 'red' });
        }

        const modal = M.Modal.getInstance(document.getElementById('clockModal'));
        modal.close();
    });
});
