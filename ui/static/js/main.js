/* MSME Stress Score Advisor - Main JavaScript */

// Document ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('MSME UI Loaded');
    initializeTooltips();
    initializePopovers();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize Bootstrap popovers
function initializePopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Format currency
function formatCurrency(amount) {
    return '₹ ' + parseFloat(amount).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Format percentage
function formatPercentage(value) {
    return (parseFloat(value) * 100).toFixed(2) + '%';
}

// Get stress level color
function getStressLevelColor(score) {
    if (score >= 0.7) return 'danger';
    if (score >= 0.5) return 'warning';
    if (score >= 0.3) return 'info';
    return 'success';
}

// Get stress level text
function getStressLevelText(score) {
    if (score >= 0.7) return 'Critical';
    if (score >= 0.5) return 'High';
    if (score >= 0.3) return 'Moderate';
    return 'Low';
}

// API request helper
async function apiRequest(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(endpoint, options);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Real-time updates
function startRealtimeUpdates(intervalMs = 5000) {
    setInterval(async function() {
        try {
            const data = await apiRequest('/api/scores');
            updateDashboardStats(data);
        } catch (error) {
            console.error('Error fetching real-time updates:', error);
        }
    }, intervalMs);
}

// Update dashboard statistics
function updateDashboardStats(data) {
    const scores = data.scores || {};
    
    // Count stress levels
    const critical = Object.values(scores).filter(v => v.stress_score >= 0.7).length;
    const high = Object.values(scores).filter(v => v.stress_score >= 0.5 && v.stress_score < 0.7).length;
    
    // Update cards if they exist
    const criticalCard = document.querySelector('[data-stat="critical"]');
    const highCard = document.querySelector('[data-stat="high"]');
    
    if (criticalCard) criticalCard.querySelector('h2').textContent = critical;
    if (highCard) highCard.querySelector('h2').textContent = high;
}

// Auto-dismiss alerts
function autoDismissAlerts(timeout = 5000) {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, timeout);
    });
}

// Format date time
function formatDateTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// Highlight rows on table
function highlightRows() {
    const rows = document.querySelectorAll('table tbody tr');
    rows.forEach((row, index) => {
        row.style.animationDelay = (index * 0.05) + 's';
    });
}

// Export data as CSV
function exportToCSV(tableElement, filename = 'data.csv') {
    let csv = [];
    const rows = tableElement.querySelectorAll('tr');

    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        let csvRow = [];
        cols.forEach(col => {
            csvRow.push(col.innerText);
        });
        csv.push(csvRow.join(','));
    });

    downloadCSV(csv.join('\n'), filename);
}

// Download CSV
function downloadCSV(csv, filename) {
    const csvFile = new Blob([csv], { type: 'text/csv' });
    const downloadLink = document.createElement('a');
    downloadLink.href = URL.createObjectURL(csvFile);
    downloadLink.download = filename;
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

// Show loading spinner
function showLoading(element) {
    element.innerHTML = '<div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div>';
}

// Hide loading spinner
function hideLoading(element) {
    element.innerHTML = '';
}

// Success notification
function showSuccessNotification(message, duration = 3000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show';
    alertDiv.innerHTML = `
        <i class="fas fa-check-circle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('main');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, duration);
}

// Error notification
function showErrorNotification(message, duration = 5000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.innerHTML = `
        <i class="fas fa-times-circle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('main');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, duration);
}

// Initialize on page load
window.addEventListener('load', function() {
    autoDismissAlerts();
    highlightRows();
});

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl+R for reload
    if (event.ctrlKey && event.key === 'r') {
        event.preventDefault();
        location.reload();
    }
    
    // Ctrl+H for home
    if (event.ctrlKey && event.key === 'h') {
        event.preventDefault();
        window.location.href = '/';
    }
});

console.log('MSME Financial Stress Score Advisor - JavaScript Initialized');
