// Global variables
let currentUserId = null;
let reportToDelete = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Get user ID from localStorage or session
    currentUserId = getUserId();

    if (!currentUserId) {
        alert('Please login first');
        window.location.href = '/';
        return;
    }

    // Set max date for month input to current month
    const monthInput = document.getElementById('reportMonth');
    const today = new Date();
    const maxMonth = today.toISOString().substring(0, 7);
    monthInput.max = maxMonth;
    monthInput.value = maxMonth;

    // Load reports on page load
    loadReports();

    // Setup form submission
    document.getElementById('generateReportForm').addEventListener('submit', handleGenerateReport);
});

// Get user ID from storage
function getUserId() {
    const userId = localStorage.getItem('user_id') || sessionStorage.getItem('user_id');
    return userId ? parseInt(userId) : null;
}

// Load all reports for user
async function loadReports() {
    const loadingState = document.getElementById('loadingState');
    const emptyState = document.getElementById('emptyState');
    const reportsTable = document.getElementById('reportsTable');

    loadingState.style.display = 'block';
    emptyState.style.display = 'none';
    reportsTable.style.display = 'none';

    try {
        const response = await fetch(`/api/reports?user_id=${currentUserId}`);

        if (!response.ok) {
            throw new Error('Failed to load reports');
        }

        const data = await response.json();

        loadingState.style.display = 'none';

        if (!data.reports || data.reports.length === 0) {
            emptyState.style.display = 'block';
            updateStatistics([]);
            return;
        }

        // Display reports in audit trail format
        displayReportsAudit(data.reports);
        updateStatistics(data.reports);
        reportsTable.style.display = 'block';

    } catch (error) {
        console.error('Error loading reports:', error);
        loadingState.style.display = 'none';
        showMessage('Failed to load reports. Please try again.', 'error');
    }
}

// Display reports in audit trail table
function displayReportsAudit(reports) {
    const tbody = document.getElementById('reportsTableBody');
    tbody.innerHTML = '';

    reports.forEach((report, index) => {
        const row = document.createElement('tr');

        // Determine row background for alternating pattern
        if (index % 2 === 0) {
            row.style.background = '#ffffff';
        }

        row.innerHTML = `                                
            <td>
                <span class="period-badge">${formatMonth(report.report_month)}</span>
            </td>
            <td>
                <span class="spending-amount">SEK ${formatNumber(report.total_spending)}</span>
            </td>
            <td>
                <span class="transaction-count">
                     ${report.transaction_count}
                </span>
            </td>
            <td style="color: #6b7280; font-size: 13px;">
                ${formatDateFull(report.generated_at)}
            </td>          
            <td>
                <div class="action-btns">
                    <button class="btn-action btn-download" onclick="downloadReport('${report.report_month}')">
                        Download
                    </button>                   
                    <button class="btn-action btn-delete" onclick="showDeleteModal(${report.report_id})">
                        Delete
                    </button>
                </div>
            </td>
        `;

        tbody.appendChild(row);
    });
}

// Update statistics cards
function updateStatistics(reports) {
    const totalReports = reports.length;
    const totalSpending = reports.reduce((sum, r) => sum + parseFloat(r.total_spending || 0), 0);
    const totalTransactions = reports.reduce((sum, r) => sum + parseInt(r.transaction_count || 0), 0);
    const avgTransactions = totalReports > 0 ? Math.round(totalTransactions / totalReports) : 0;
    const latestMonth = totalReports > 0 ? formatMonth(reports[0].report_month) : '-';

    document.getElementById('totalReports').textContent = totalReports;
    document.getElementById('totalSpending').textContent = `SEK ${formatNumber(totalSpending)}`;
    document.getElementById('latestMonth').textContent = latestMonth;
    document.getElementById('avgTransactions').textContent = avgTransactions;
}

// Handle report generation
async function handleGenerateReport(e) {
    e.preventDefault();

    const monthInput = document.getElementById('reportMonth');
    const month = monthInput.value;
    const generateBtn = document.getElementById('generateBtn');
    const btnText = generateBtn.querySelector('.btn-text');
    const loader = generateBtn.querySelector('.loader');

    if (!month) {
        showMessage('Please select a month', 'error');
        return;
    }

    // Disable button and show loader
    generateBtn.disabled = true;
    btnText.style.display = 'none';
    loader.style.display = 'block';

    try {
        const response = await fetch('/api/reports/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: currentUserId,
                month: month
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to generate report');
        }

        showMessage(`✓ Report generated successfully for ${formatMonth(month)}!`, 'success');

        await downloadReport(month);

        // Reload reports after 1.5 seconds
        setTimeout(() => {
            loadReports();
        }, 1500);

    } catch (error) {
        console.error('Error generating report:', error);
        showMessage('✗ ' + (error.message || 'Failed to generate report'), 'error');
    } finally {
        // Re-enable button
        generateBtn.disabled = false;
        btnText.style.display = 'inline';
        loader.style.display = 'none';
    }
}

// Download report PDF
async function downloadReport(month) {
    try {
        showMessage(`Downloading report for ${formatMonth(month)}...`, 'success');

        const response = await fetch(`/api/reports/download?user_id=${currentUserId}&month=${month}`);

        if (!response.ok) {
            throw new Error('Failed to download report');
        }

        // Create blob from response
        const blob = await response.blob();

        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `financial_report_${month}.pdf`;
        document.body.appendChild(a);
        a.click();

        // Cleanup
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showMessage(`✓ Report downloaded successfully!`, 'success');

    } catch (error) {
        console.error('Error downloading report:', error);
        showMessage('✗ Failed to download report', 'error');
    }
}


// Show delete confirmation modal
function showDeleteModal(reportId) {
    reportToDelete = reportId;
    const modal = document.getElementById('deleteModal');
    modal.classList.add('active');

    // Setup confirm button
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    confirmBtn.onclick = () => deleteReport(reportId);
}

// Close delete modal
function closeDeleteModal() {
    const modal = document.getElementById('deleteModal');
    modal.classList.remove('active');
    reportToDelete = null;
}

// Delete report
async function deleteReport(reportId) {
    try {
        const response = await fetch(`/api/reports/${reportId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: currentUserId
            })
        });

        if (!response.ok) {
            throw new Error('Failed to delete report');
        }

        showMessage('✓ Report deleted successfully from audit trail!', 'success');
        closeDeleteModal();

        // Reload reports after 1 second
        setTimeout(() => {
            loadReports();
        }, 1000);

    } catch (error) {
        console.error('Error deleting report:', error);
        showMessage('✗ Failed to delete report', 'error');
    }
}

// Show message
function showMessage(text, type) {
    const messageEl = document.getElementById('generateMessage');
    messageEl.textContent = text;
    messageEl.className = `message ${type}`;
    messageEl.style.display = 'block';

    // Auto-hide after 5 seconds
    setTimeout(() => {
        messageEl.style.display = 'none';
    }, 5000);
}

// Format month (YYYY-MM to "Month YYYY")
function formatMonth(month) {
    if (!month) return '-';
    const [year, monthNum] = month.split('-');
    const date = new Date(year, monthNum - 1);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long' });
}

// Format date with full details
function formatDateFull(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });
}

// Format number with thousand separators
function formatNumber(num) {
    if (!num) return '0.00';
    return parseFloat(num).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('deleteModal');
    if (event.target.classList.contains('modal-overlay')) {
        closeDeleteModal();
    }
}