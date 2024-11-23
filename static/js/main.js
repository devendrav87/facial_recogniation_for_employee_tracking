document.addEventListener('DOMContentLoaded', function() {
    startVideoFeed();
    updateClock();
    setInterval(updateClock, 1000);
    listUsers();
    setInterval(listUsers, 30000);
});

function startVideoFeed() {
    const videoFeed = document.getElementById('videoFeed');
    if (videoFeed) {
        videoFeed.src = '/video_feed';
    }
}

function updateClock() {
    const clockElement = document.getElementById('clock');
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    const dateString = now.toLocaleDateString();
    clockElement.textContent = `${dateString} ${timeString}`;
}

function listUsers() {
    fetch('/users')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const userList = document.getElementById('userList');
                let html = `
                    <div class="user-list-container">
                        <h3>Registered Users</h3>
                        <table class="report-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Current Status</th>
                                    <th>Last Update</th>
                                </tr>
                            </thead>
                            <tbody>
                `;
                
                data.users.forEach(user => {
                    html += `
                        <tr>
                            <td>${user.id}</td>
                            <td>${user.name}</td>
                            <td class="status-${user.status.status}">${user.status.status}</td>
                            <td>${user.status.last_timestamp || 'N/A'}</td>
                        </tr>
                    `;
                });
                
                html += '</tbody></table></div>';
                userList.innerHTML = html;
            }
        })
        .catch(error => showAlert('Error fetching users: ' + error, 'error'));
}

function deleteAllUsers() {
    if (confirm('Are you sure you want to delete all users? This action cannot be undone.')) {
        fetch('/users/delete-all', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showAlert('All users deleted successfully', 'success');
                listUsers();
            } else {
                showAlert('Error deleting users: ' + data.message, 'error');
            }
        });
    }
}

function getDailyReport() {
    const employeeId = document.getElementById('employeeId').value;
    const date = document.getElementById('reportDate').value || new Date().toISOString().split('T')[0];
    
    fetch(`/reports/daily/${employeeId}?date=${date}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                displayReport(data.data);
            } else {
                showAlert('Error fetching report: ' + data.message, 'error');
            }
        })
        .catch(error => showAlert('Network error: ' + error, 'error'));
}

function getWeeklyReport() {
    const employeeId = document.getElementById('employeeId').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    
    if (!startDate || !endDate) {
        showAlert('Please select start and end dates', 'warning');
        return;
    }
    
    fetch(`/reports/weekly/${employeeId}?start_date=${startDate}&end_date=${endDate}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                displayWeeklyReport(data.data);
            } else {
                showAlert('Error fetching weekly report: ' + data.message, 'error');
            }
        })
        .catch(error => showAlert('Network error: ' + error, 'error'));
}

function displayReport(report) {
    const reportDiv = document.getElementById('reportDisplay');
    let html = `
        <div class="report-container">
            <h3>Daily Attendance Report</h3>
            <p class="report-date">Date: ${report.date}</p>
            
            <div class="time-analysis">
                <h4>Time Analysis</h4>
                <p>Total Time Inside: ${report.formatted_time}</p>
                <p>Total Hours: ${report.total_hours}</p>
                <p>Total Minutes: ${report.total_minutes}</p>
            </div>
            
            <table class="report-table">
                <thead>
                    <tr>
                        <th>Entry Time</th>
                        <th>Exit Time</th>
                        <th>Duration</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    // Use details array for attendance records
    report.details.forEach(detail => {
        html += `
            <tr>
                <td>${detail.entry}</td>
                <td>${detail.exit}</td>
                <td>${detail.duration} hours</td>
            </tr>
        `;
    });
    
    html += '</tbody></table></div>';
    reportDiv.innerHTML = html;
}


function displayWeeklyReport(report) {
    const reportDiv = document.getElementById('reportDisplay');
    let html = `
        <div class="report-container">
            <h3>Weekly Attendance Report</h3>
            <p class="total-hours">Total Time: ${report.total_time}</p>
            <table class="report-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Time Inside</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    report.daily_breakdown.forEach(day => {
        html += `
            <tr>
                <td>${day.date}</td>
                <td>${day.formatted_time}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table></div>';
    reportDiv.innerHTML = html;
}

function registerEmployee() {
    const name = document.getElementById('registerName').value;
    const employeeId = document.getElementById('registerEmployeeId').value;
    
    if (!name || !employeeId) {
        showAlert('Please fill in all fields', 'warning');
        return;
    }
    
    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            name: name,
            employee_id: employeeId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showAlert('Employee registered successfully!', 'success');
            document.getElementById('registerForm').reset();
            listUsers();
        } else {
            showAlert('Registration failed: ' + data.message, 'error');
        }
    })
    .catch(error => showAlert('Network error: ' + error, 'error'));
}

function showAlert(message, type) {
    const alertDiv = document.getElementById('alertBox');
    alertDiv.textContent = message;
    alertDiv.className = `alert alert-${type}`;
    alertDiv.style.display = 'block';
    
    setTimeout(() => {
        alertDiv.style.display = 'none';
    }, 3000);
}

function checkStatus() {
    const employeeId = document.getElementById('employeeId').value;
    
    fetch(`/status/${employeeId}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const status = data.data.status;
                const timestamp = data.data.last_timestamp;
                const statusDiv = document.getElementById('statusDisplay');
                statusDiv.innerHTML = `
                    <div class="status-container">
                        <p>Current Status: <span class="status-${status}">${status}</span></p>
                        <p>Last Update: ${timestamp || 'N/A'}</p>
                    </div>
                `;
            } else {
                showAlert('Error checking status: ' + data.message, 'error');
            }
        })
        .catch(error => showAlert('Network error: ' + error, 'error'));
}
