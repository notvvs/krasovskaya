// API базовый URL
const API_URL = '/api/v1/users';

// Утилиты для работы с токенами
const TokenManager = {
    setAccessToken(token) {
        localStorage.setItem('access_token', token);
    },

    getAccessToken() {
        return localStorage.getItem('access_token');
    },

    removeAccessToken() {
        localStorage.removeItem('access_token');
    },

    isAuthenticated() {
        return !!this.getAccessToken();
    }
};

// Утилиты для отображения сообщений
function showMessage(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    const container = document.querySelector('.container');
    const firstChild = container.firstChild;
    container.insertBefore(alertDiv, firstChild);

    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Утилиты для управления кнопками
function setButtonLoading(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        button.dataset.originalText = button.textContent;
        button.innerHTML = '<div class="loader"></div>';
        button.querySelector('.loader').style.display = 'block';
    } else {
        button.disabled = false;
        button.textContent = button.dataset.originalText;
    }
}

// API функции
async function makeRequest(endpoint, method = 'GET', data = null, includeAuth = false) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include' // Для работы с cookies
    };

    if (includeAuth) {
        const token = TokenManager.getAccessToken();
        if (token) {
            options.headers['Authorization'] = `Bearer ${token}`;
        }
    }

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_URL}${endpoint}`, options);
        const responseData = await response.json();

        if (!response.ok) {
            throw new Error(responseData.detail || 'Произошла ошибка');
        }

        return responseData;
    } catch (error) {
        throw error;
    }
}

// Регистрация
async function register(username, email, password) {
    return await makeRequest('/register', 'POST', { username, email, password });
}

// Вход
async function login(email, password) {
    return await makeRequest('/login', 'POST', { email, password });
}

// Верификация
async function verify(email, verifyCode) {
    return await makeRequest('/verify', 'POST', { email, verify_code: verifyCode });
}

// Повторная отправка кода
async function resendCode(email) {
    return await makeRequest('/resend-code', 'POST', { email });
}

// Обновление токена
async function refreshToken() {
    return await makeRequest('/refresh', 'POST');
}

// Проверка авторизации при загрузке страницы dashboard
function checkAuth() {
    const currentPath = window.location.pathname;

    if (currentPath === '/dashboard') {
        if (!TokenManager.isAuthenticated()) {
            window.location.href = '/login';
        }
    }

    if ((currentPath === '/login' || currentPath === '/register' || currentPath === '/') && TokenManager.isAuthenticated()) {
        window.location.href = '/dashboard';
    }
}

// Выход
function logout() {
    TokenManager.removeAccessToken();
    window.location.href = '/login';
}

// Автоматическое обновление токена
let tokenRefreshInterval;

function startTokenRefresh() {
    // Обновляем токен каждые 14 минут (access token живет 15 минут)
    tokenRefreshInterval = setInterval(async () => {
        try {
            const data = await refreshToken();
            TokenManager.setAccessToken(data.access_token);
            console.log('Token refreshed successfully');
        } catch (error) {
            console.error('Failed to refresh token:', error);
            logout();
        }
    }, 14 * 60 * 1000);
}

function stopTokenRefresh() {
    if (tokenRefreshInterval) {
        clearInterval(tokenRefreshInterval);
    }
}

// Проверка авторизации при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();

    if (TokenManager.isAuthenticated() && window.location.pathname === '/dashboard') {
        startTokenRefresh();
    }
});