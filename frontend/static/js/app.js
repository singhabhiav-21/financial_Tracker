// Update this to match your FastAPI server URL
const API_URL = 'http://localhost:8000';

function showForm(formType) {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const toggleBtns = document.querySelectorAll('.toggle-btn');

    toggleBtns.forEach(btn => btn.classList.remove('active'));

    if (formType === 'login') {
        loginForm.classList.add('active');
        registerForm.classList.remove('active');
        toggleBtns[0].classList.add('active');
    } else {
        registerForm.classList.add('active');
        loginForm.classList.remove('active');

        toggleBtns[1].classList.add('active');
    }

    // Clear messages
    document.getElementById('login-message').style.display = 'none';
    document.getElementById('register-message').style.display = 'none';
}

async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const btn = document.getElementById('login-btn');
    const messageDiv = document.getElementById('login-message');

    btn.disabled = true;
    btn.textContent = 'Logging in...';
    messageDiv.style.display = 'none';

    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('login-message', 'Login successful! Redirecting to dashboard...', 'success');

            // Store user_id and email for later use
            sessionStorage.setItem('user_id', data.user_id);
            sessionStorage.setItem('email', email);

            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
        } else {
            showMessage('login-message', data.detail || 'Login failed', 'error');
        }
    } catch (error) {
        showMessage('login-message', 'Connection error. Please try again.', 'error');
        console.error('Error:', error);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Login';
    }
}

async function handleRegister(e) {
    e.preventDefault();

    const name = document.getElementById('register-name').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const btn = document.getElementById('register-btn');
    const messageDiv = document.getElementById('register-message');

    btn.disabled = true;
    btn.textContent = 'Registering...';
    messageDiv.style.display = 'none';

    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('register-message', 'Registration successful! Please login.', 'success');

            // Clear form
            document.getElementById('register-name').value = '';
            document.getElementById('register-email').value = '';
            document.getElementById('register-password').value = '';

            // Switch to login form after 2 seconds
            setTimeout(() => {
                showForm('login');
            }, 2000);
        } else {
            showMessage('register-message', data.detail || 'Registration failed', 'error');
        }
    } catch (error) {
        showMessage('register-message', 'Connection error. Please try again.', 'error');
        console.error('Error:', error);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Register';
    }
}

function showMessage(elementId, text, type) {
    const messageDiv = document.getElementById(elementId);
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = 'block';
}

// Check if user is already logged in on page load
document.addEventListener('DOMContentLoaded', () => {
    const userId = sessionStorage.getItem('user_id');
    if (userId && window.location.pathname === '/') {
        // User is already logged in and on login page, redirect to dashboard
        window.location.href = '/dashboard';
    }
});