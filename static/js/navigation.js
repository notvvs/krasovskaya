// Navigation and authentication utilities for SoilAnalyzer

// Parse JWT token
function parseJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(
            atob(base64)
                .split('')
                .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
                .join('')
        );
        return JSON.parse(jsonPayload);
    } catch (e) {
        return null;
    }
}

// Get user data from token
function getUserFromToken() {
    const token = localStorage.getItem('access_token');
    if (!token) return null;

    const payload = parseJwt(token);
    if (!payload) return null;

    return {
        email: payload.sub,
        userId: payload.user_id
    };
}

// Check if user is authenticated (for protected pages)
function checkAuthRequired() {
    const protectedPaths = ['/dashboard', '/analyze', '/history', '/profile'];
    const currentPath = window.location.pathname;

    if (protectedPaths.includes(currentPath)) {
        const token = localStorage.getItem('access_token');
        if (!token) {
            window.location.href = '/login';
            return false;
        }
    }
    return true;
}

// Logout function
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
}

// Initialize auth check on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAuthRequired();
});
