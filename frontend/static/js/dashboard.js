// ==================== CONFIGURATION ====================
const API_URL = 'http://localhost:8000';
let currentUserId = null;
let accounts = [];
let transactions = [];

// ==================== CURRENCY UTILITIES ====================
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

// ==================== AUTH CHECK ====================
function checkAuth() {
    currentUserId = parseInt(sessionStorage.getItem('user_id'));
    console.log('Dashboard - User ID:', currentUserId);

    if (!currentUserId) {
        alert('Please log in first');
        window.location.href = '/';
        return false;
    }
    return true;
}

// ==================== DASHBOARD FUNCTIONS ====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== DASHBOARD PAGE INITIALIZED ===');
    
    if (!checkAuth()) {
        return;
    }
    
    loadDashboard();
});

async function loadDashboard() {
    console.log('Loading dashboard data...');
    await Promise.all([loadAccounts(), loadTransactions()]);
    updateStats();
    renderRecentTransactions();
}

async function loadAccounts() {
    try {
        const res = await fetch(`${API_URL}/accounts?user_id=${currentUserId}`);
        accounts = res.ok ? await res.json() : [];
        console.log('Accounts loaded:', accounts.length);
    } catch (error) {
        console.error('Error loading accounts:', error);
        accounts = [];
    }
}

async function loadTransactions() {
    try {
        const res = await fetch(`${API_URL}/transactions?user_id=${currentUserId}`);
        transactions = res.ok ? await res.json() : [];
        console.log('Transactions loaded:', transactions.length);
    } catch (error) {
        console.error('Error loading transactions:', error);
        transactions = [];
    }
}

function updateStats() {
    // Group balances by currency
    const balancesByCurrency = {};
    
    accounts.forEach(acc => {
        const currency = acc.currency || 'USD';
        if (!balancesByCurrency[currency]) {
            balancesByCurrency[currency] = 0;
        }
        balancesByCurrency[currency] += parseFloat(acc.account_balance || 0);
    });

    // Display total balance
    const totalBalanceDiv = document.getElementById('total-balance');
    if (!totalBalanceDiv) return;

    if (Object.keys(balancesByCurrency).length === 0) {
        totalBalanceDiv.textContent = '$0.00';
    } else if (Object.keys(balancesByCurrency).length === 1) {
        // Single currency - show normally
        const currency = Object.keys(balancesByCurrency)[0];
        totalBalanceDiv.textContent = formatCurrency(balancesByCurrency[currency], currency);
    } else {
        // Multiple currencies - show all
        totalBalanceDiv.innerHTML = Object.entries(balancesByCurrency)
            .map(([curr, amt]) => `<div style="font-size: 18px; margin: 2px 0;">${formatCurrency(amt, curr)}</div>`)
            .join('');
    }

    // Get primary currency (from first account or default to USD)
    const primaryCurrency = accounts[0]?.currency || 'USD';

    // Calculate income (positive amounts)
    const totalIncome = transactions
        .filter(t => t.amount > 0)
        .reduce((sum, t) => sum + parseFloat(t.amount), 0);
    
    const incomeDiv = document.getElementById('total-income');
    if (incomeDiv) {
        incomeDiv.textContent = formatCurrency(totalIncome, primaryCurrency);
    }

    // Calculate expenses (negative amounts)
    const totalExpenses = transactions
        .filter(t => t.amount < 0)
        .reduce((sum, t) => sum + Math.abs(parseFloat(t.amount)), 0);
    
    const expensesDiv = document.getElementById('total-expenses');
    if (expensesDiv) {
        expensesDiv.textContent = formatCurrency(totalExpenses, primaryCurrency);
    }

    // Total accounts
    const accountsDiv = document.getElementById('total-accounts');
    if (accountsDiv) {
        accountsDiv.textContent = accounts.length;
    }

    console.log('Stats updated:', {
        balances: balancesByCurrency,
        income: totalIncome,
        expenses: totalExpenses,
        accounts: accounts.length
    });
}

function renderRecentTransactions() {
    const div = document.getElementById('recent-transactions');
    if (!div) return;

    if (transactions.length === 0) {
        div.innerHTML = '<div class="empty-state"><p style="color: #9ca3af; text-align: center; padding: 20px;">No recent transactions</p></div>';
        return;
    }

    // Get primary currency for display
    const primaryCurrency = accounts[0]?.currency || 'USD';

    // Show last 5 transactions
    div.innerHTML = transactions
        .slice(0, 5)
        .map(t => `
            <div class="transaction-item" style="display: flex; justify-content: space-between; padding: 12px 16px; border-bottom: 1px solid #e5e7eb;">
                <div>
                    <strong style="color: #111827;">${escapeHtml(t.name)}</strong>
                    <br>
                    <small style="color: #6b7280;">${formatDate(t.transaction_date)}</small>
                </div>
                <span class="${t.amount > 0 ? 'positive' : 'negative'}" style="font-weight: 600; font-size: 16px;">
                    ${t.amount > 0 ? '+' : ''}${formatCurrency(Math.abs(t.amount), primaryCurrency)}
                </span>
            </div>
        `).join('');
}

// ==================== UTILITY FUNCTIONS ====================
function logout() {
    sessionStorage.removeItem('user_id');
    sessionStorage.removeItem('email');
    window.location.href = '/';
}

// ==================== GLOBAL EXPORTS ====================
window.logout = logout;
window.loadDashboard = loadDashboard;

console.log('dashboard.js loaded successfully');