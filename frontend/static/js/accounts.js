// ==================== CONFIGURATION ====================
const API_URL = 'http://localhost:8000';
let currentUserId = null;

// ==================== AUTH CHECK ====================
function checkAuth() {
    currentUserId = parseInt(sessionStorage.getItem('user_id'));
    console.log('Auth check - User ID:', currentUserId);

    if (!currentUserId && window.location.pathname !== '/' && !window.location.pathname.includes('index.html')) {
        alert('Please log in first');
        window.location.href = '/';
        return false;
    }
    return true;
}

// ==================== MODAL FUNCTIONS ====================
function openModal(id) {
    console.log(`Opening modal: ${id}`);
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = 'block';
        const form = modal.querySelector('form');
        if (form) form.reset();
    } else {
        console.error(`Modal with id "${id}" not found`);
    }
}

function closeModal(id) {
    console.log(`Closing modal: ${id}`);
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = 'none';
    }
}

window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
};

// ==================== UTILITY FUNCTIONS ====================
function showMessage(message, type = 'success') {
    console.log(`${type.toUpperCase()}: ${message}`);

    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icon = type === 'error' ? '❌' : '✅';

    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <span class="toast-message">${message}</span>
        <span class="toast-close" onclick="this.parentElement.remove()">×</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 3000);
}

function logout() {
    sessionStorage.removeItem('user_id');
    sessionStorage.removeItem('email');
    window.location.href = '/';
}

const currencySymbols = {
    'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'CNY': '¥', 'INR': '₹',
    'AUD': 'A$', 'CAD': 'C$', 'CHF': 'Fr', 'SEK': 'kr', 'NOK': 'kr', 'DKK': 'kr',
    'RUB': '₽', 'BRL': 'R$', 'ZAR': 'R', 'KRW': '₩', 'MXN': '$', 'SGD': 'S$',
    'HKD': 'HK$', 'NZD': 'NZ$', 'TRY': '₺', 'AED': 'د.إ', 'SAR': '﷼', 'PLN': 'zł',
    'THB': '฿', 'MYR': 'RM', 'IDR': 'Rp', 'PHP': '₱', 'CZK': 'Kč', 'ILS': '₪',
    'CLP': '$', 'PKR': '₨', 'EGP': 'E£', 'BTC': '₿', 'ETH': 'Ξ'
};

function getCurrencySymbol(currencyCode) {
    return currencySymbols[currencyCode?.toUpperCase()] || currencyCode || '$';
}

function formatCurrency(amount, currencyCode) {
    const symbol = getCurrencySymbol(currencyCode);
    const formattedAmount = parseFloat(amount || 0).toFixed(2);
    const suffixCurrencies = ['SEK', 'NOK', 'DKK', 'CZK', 'PLN'];
    if (suffixCurrencies.includes(currencyCode?.toUpperCase())) {
        return `${formattedAmount} ${symbol}`;
    }
    return `${symbol}${formattedAmount}`;
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return date.toLocaleDateString('en-US', options);
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ==================== ACCOUNTS FUNCTIONS ====================
async function loadAccounts() {
    if (!currentUserId) {
        console.error('No user ID available');
        return;
    }

    try {
        console.log(`Loading accounts for user ${currentUserId}`);
        const res = await fetch(`${API_URL}/accounts?user_id=${currentUserId}`);

        if (!res.ok) {
            throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        }

        const accounts = await res.json();
        console.log('Accounts loaded:', accounts);

        const list = document.getElementById('accounts-list');
        if (!list) {
            console.error('accounts-list element not found');
            return;
        }

        if (accounts.length === 0) {
            list.innerHTML = '<div class="empty-state"><p>No accounts found. Add one to get started!</p></div>';
            return;
        }

        list.innerHTML = accounts.map(a => `
            <div class="account-card">
                <div class="account-header">
                    <strong>${escapeHtml(a.account_name)}</strong>
                    <span class="account-balance">${formatCurrency(a.account_balance, a.currency)}</span>
                </div>
                <div class="account-details">
                    <div class="detail-row">
                        <span class="detail-label">Account Type:</span>
                        <span class="detail-value">${escapeHtml(a.account_type)}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Currency:</span>
                        <span class="detail-value">${escapeHtml(a.currency)} (${getCurrencySymbol(a.currency)})</span>
                    </div>
                    ${a.platform_name ? `
                    <div class="detail-row">
                        <span class="detail-label">Platform:</span>
                        <span class="detail-value">${escapeHtml(a.platform_name)}</span>
                    </div>
                    ` : ''}
                    <div class="detail-row">
                        <span class="detail-label">Created:</span>
                        <span class="detail-value">${formatDate(a.created_at)}</span>
                    </div>
                </div>
                <div class="account-actions">
                    <button class="btn btn-danger btn-sm" onclick="deleteAccount(${a.account_id}, '${escapeHtml(a.account_name)}', ${a.account_balance})">
                        Delete Account
                    </button>
                </div>
            </div>
        `).join('');

    } catch (error) {
        console.error('Error loading accounts:', error);
        const list = document.getElementById('accounts-list');
        if (list) {
            list.innerHTML = '<div class="error-state"><p>Failed to load accounts. Please refresh the page.</p></div>';
        }
        showMessage(`Failed to load accounts: ${error.message}`, 'error');
    }
}

async function handleAddAccount(e) {
    e.preventDefault();
    console.log('=== ADD ACCOUNT FORM SUBMITTED ===');

    if (!currentUserId) {
        showMessage('User not logged in', 'error');
        return;
    }

    const name = document.getElementById('account-name').value.trim();
    const type = document.getElementById('account-type').value;
    const balance = parseFloat(document.getElementById('account-balance').value);
    const currency = document.getElementById('account-currency').value.trim();
    const platform = document.getElementById('account-platform').value.trim();

    console.log('Form values:', { name, type, balance, currency, platform });

    if (!name) {
        showMessage('Please enter an account name', 'error');
        return;
    }
    if (!type) {
        showMessage('Please select an account type', 'error');
        return;
    }
    if (isNaN(balance) || balance < 0) {
        showMessage('Please enter a valid balance (0 or greater)', 'error');
        return;
    }
    if (balance > 10000000) {
        showMessage('Balance cannot exceed 10,000,000', 'error');
        return;
    }
    if (!currency) {
        showMessage('Please enter a currency', 'error');
        return;
    }

    const accountData = {
        user_id: currentUserId,
        name: name,
        type: type,
        balance: balance,
        currency: currency,
        platform_name: platform || null
    };

    console.log('Sending account data:', accountData);

    try {
        const response = await fetch(`${API_URL}/accounts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(accountData)
        });

        const result = await response.json();
        console.log('Response:', response.status, result);

        if (response.ok) {
            showMessage('Account added successfully!');
            closeModal('addAccount');
            e.target.reset();
            document.getElementById('account-currency').value = 'USD';
            await loadAccounts();
        } else {
            showMessage(result.detail || 'Failed to add account', 'error');
        }
    } catch (error) {
        console.error('Error adding account:', error);
        showMessage('Connection error. Please check your internet and try again.', 'error');
    }
}

// ==================== DELETE ACCOUNT FUNCTIONS ====================
let accountToDelete = null;

function deleteAccount(accountId, accountName, accountBalance) {
    console.log(`Initiating delete for account ${accountId}`);
    accountToDelete = accountId;

    const infoDiv = document.getElementById('account-to-delete-info');
    if (infoDiv) {
        infoDiv.innerHTML = `
            <strong style="color: #1a202c; font-size: 16px; display: block; margin-bottom: 8px;">
                📊 ${escapeHtml(accountName)}
            </strong>
            <span style="color: #666; font-size: 14px; display: block; margin-bottom: 4px;">
                💰 Balance: $${parseFloat(accountBalance || 0).toFixed(2)}
            </span>
            <span style="color: #999; font-size: 13px;">
                🆔 Account ID: ${accountId}
            </span>
        `;
    }

    const passwordField = document.getElementById('delete-password');
    if (passwordField) {
        passwordField.value = '';
    }

    openModal('deleteConfirmModal');
}

function closeDeleteModal() {
    accountToDelete = null;
    closeModal('deleteConfirmModal');

    const passwordField = document.getElementById('delete-password');
    if (passwordField) {
        passwordField.value = '';
    }
}

async function handleDeleteAccount(e) {
    e.preventDefault();

    if (!accountToDelete) {
        showMessage('No account selected for deletion', 'error');
        return;
    }

    const password = document.getElementById('delete-password').value;

    if (!password) {
        showMessage('Please enter your password', 'error');
        return;
    }

    console.log(`Confirming delete for account ${accountToDelete}`);

    const deleteBtn = e.target.querySelector('.btn-danger');
    const originalText = deleteBtn.innerHTML;
    deleteBtn.disabled = true;
    deleteBtn.innerHTML = '⏳ Deleting...';

    try {
        const response = await fetch(`${API_URL}/accounts/${accountToDelete}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ password: password })
        });

        const result = await response.json();
        console.log('Delete response:', response.status, result);

        if (response.ok) {
            showMessage('Account deleted successfully!');
            closeDeleteModal();
            await loadAccounts();
        } else {
            showMessage(result.detail || 'Failed to delete account. Check your password.', 'error');
        }
    } catch (error) {
        console.error('Error deleting account:', error);
        showMessage('Connection error. Please try again.', 'error');
    } finally {
        deleteBtn.disabled = false;
        deleteBtn.innerHTML = originalText;
    }
}

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== ACCOUNTS PAGE INITIALIZED ===');
    console.log('API URL:', API_URL);

    if (!checkAuth()) {
        return;
    }

    console.log('Current User ID:', currentUserId);

    const addForm = document.getElementById('addAccountForm');
    if (addForm) {
        addForm.addEventListener('submit', handleAddAccount);
        console.log('✅ Add form submit handler attached');
    } else {
        console.error('❌ Add form not found!');
    }

    const deleteForm = document.getElementById('deleteAccountForm');
    if (deleteForm) {
        deleteForm.addEventListener('submit', handleDeleteAccount);
        console.log('✅ Delete form submit handler attached');
    } else {
        console.error('❌ Delete form not found!');
    }

    loadAccounts();
});

// ==================== GLOBAL EXPORTS ====================
window.openModal = openModal;
window.closeModal = closeModal;
window.logout = logout;
window.deleteAccount = deleteAccount;
window.loadAccounts = loadAccounts;
window.closeDeleteModal = closeDeleteModal;

console.log('accounts.js loaded successfully');