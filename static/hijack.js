function hijackSession() {
    const sessionId = document.getElementById('session_id').value.trim();
    if (!sessionId) {
        document.getElementById('error').innerText = 'Veuillez entrer un Session ID';
        return;
    }
    document.cookie = `session=${encodeURIComponent(sessionId)}; path=/`;
    window.location.href = '/secret';
}
