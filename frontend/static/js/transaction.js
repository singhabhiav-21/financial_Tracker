// Transaction page JavaScript
const API_URL = 'http://localhost:8000';
const currentUserId = parseInt(sessionStorage.getItem('user_id'));

// Redirect to login if not authenticated
if (!currentUserId) {
    alert('Please log in first');
    window.location.href = '/';
}

// ==================== PAGE LOAD ====================
document.addEventListener('DOMContentLoaded', () => {
    loadTransactions();

    // Attach form handler
    const form = document.getElementById('addTransactionForm');
    if (form) {
        form.addEventListener('submit', addTransaction);
    }

    // Attach delete confirm form handler
    const deleteForm = document.getElementById('deleteTransactionForm');
    if (deleteForm) {
        deleteForm.addEventListener('submit', confirmDeleteTransaction);
    }
});

// ==================== MODAL FUNCTIONS ====================
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        // Reset form if exists
        const form = modal.querySelector('form');
        if (form) form.reset();
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}

// ==================== TOAST NOTIFICATIONS ====================
function showMessage(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ==================== LOAD TRANSACTIONS ====================
async function loadTransactions() {
    try {
        const res = await fetch(`${API_URL}/transactions?user_id=${currentUserId}`);
        const transactions = res.ok ? await res.json() : [];

        const list = document.getElementById('transactions-list');
        if (!list) return;

        if (transactions.length === 0) {
            list.innerHTML = '<p style="text-align: center; color: #666; padding: 40px;">No transactions found. Add your first transaction!</p>';
            return;
        }

        // Group by date
        const grouped = {};
        transactions.forEach(t => {
            const date = t.transaction_date || 'No date';
            if (!grouped[date]) grouped[date] = [];
            grouped[date].push(t);
        });

        let html = '';
        Object.keys(grouped).sort().reverse().forEach(date => {
            html += `<div class="transaction-date-group">
                <h3 class="transaction-date-header">${formatDate(date)}</h3>`;

            grouped[date].forEach(t => {
                const isPositive = parseFloat(t.amount) > 0;
                html += `
                    <div class="transaction-card">
                        <div class="transaction-main">
                            <div class="transaction-info">
                                <div class="transaction-name">${escapeHtml(t.name)}</div>
                                ${t.description ? `<div class="transaction-desc">${escapeHtml(t.description)}</div>` : ''}
                            </div>
                            <div class="transaction-amount ${isPositive ? 'positive' : 'negative'}">
                                ${isPositive ? '+' : ''}$${Math.abs(parseFloat(t.amount)).toFixed(2)}
                            </div>
                        </div>
                        <div class="transaction-actions">
                            <button class="btn-edit" onclick="editTransaction(${t.transaction_id})" title="Edit">
                                ✏️ Edit
                            </button>
                            <button class="btn-delete" onclick="openDeleteModal(${t.transaction_id}, '${escapeHtml(t.name).replace(/'/g, "\\'")}', ${t.amount})" title="Delete">
                                🗑️ Delete
                            </button>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
        });

        list.innerHTML = html;
    } catch (error) {
        console.error('Error loading transactions:', error);
        showMessage('Failed to load transactions', 'error');
    }
}

// ==================== ADD TRANSACTION ====================
async function addTransaction(e) {
    e.preventDefault();

    const transactionData = {
        user_id: currentUserId,
        category_id: parseInt(document.getElementById('transaction-category').value),
        name: document.getElementById('transaction-name').value.trim(),
        amount: parseFloat(document.getElementById('transaction-amount').value),
        description: document.getElementById('transaction-description').value.trim() || null,
        transaction_date: document.getElementById('transaction-date').value || null
    };

    // Validation
    if (!transactionData.name) {
        showMessage('Please enter a transaction name', 'error');
        return;
    }

    if (isNaN(transactionData.amount) || transactionData.amount === 0) {
        showMessage('Please enter a valid amount', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/transactions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(transactionData)
        });

        if (response.ok) {
            showMessage('Transaction added successfully!');
            closeModal('addTransaction');
            loadTransactions();
            e.target.reset();
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Failed to add transaction', 'error');
        }
    } catch (error) {
        console.error('Error adding transaction:', error);
        showMessage('Connection error. Please try again.', 'error');
    }
}

// ==================== DELETE TRANSACTION ====================
let transactionToDelete = null;

function openDeleteModal(transactionId, transactionName, amount) {
    transactionToDelete = transactionId;

    const isPositive = parseFloat(amount) > 0;
    const formattedAmount = `${isPositive ? '+' : ''}${Math.abs(parseFloat(amount)).toFixed(2)}`;

    // Update modal content
    const infoDiv = document.getElementById('transaction-to-delete-info');
    if (infoDiv) {
        infoDiv.innerHTML = `
            <div style="margin-bottom: 10px;">
                <strong style="font-size: 16px;">${transactionName}</strong>
            </div>
            <div style="color: ${isPositive ? '#10b981' : '#ef4444'}; font-size: 18px; font-weight: 700;">
                ${formattedAmount}
            </div>
        `;
    }

    openModal('deleteTransactionModal');
}

function closeDeleteModal() {
    transactionToDelete = null;
    closeModal('deleteTransactionModal');
}

async function confirmDeleteTransaction(e) {
    e.preventDefault();

    if (!transactionToDelete) return;

    try {
        const response = await fetch(`${API_URL}/transactions/${transactionToDelete}?user_id=${currentUserId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showMessage('Transaction deleted successfully!');
            closeDeleteModal();
            loadTransactions();
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Failed to delete transaction', 'error');
        }
    } catch (error) {
        console.error('Error deleting transaction:', error);
        showMessage('Connection error. Please try again.', 'error');
    }
}

// ==================== EDIT TRANSACTION (PLACEHOLDER) ====================
function editTransaction(id) {
    showMessage('Edit feature coming soon!', 'info');
    // TODO: Implement edit modal similar to accounts
}

// ==================== UTILITY FUNCTIONS ====================
function formatDate(dateStr) {
    if (dateStr === 'No date') return 'No Date';

    const date = new Date(dateStr);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
        return 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
        return 'Yesterday';
    } else {
        return date.toLocaleDateString('en-US', {
            weekday: 'short',
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function logout() {
    sessionStorage.removeItem('user_id');
    sessionStorage.removeItem('email');
    window.location.href = '/';
}