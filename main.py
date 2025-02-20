import secrets

from flask import Flask, request, render_template_string, session, redirect, url_for

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Clé secrète pour signer les sessions

# Simulation d'une base de données utilisateurs
users = {
    "alice": "password123"
}

# Page HTML de base avec login
LOGIN_PAGE = """
    <h1>Connexion</h1>
    <form method="POST">
        Utilisateur: <input type="text" name="username"><br>
        Mot de passe: <input type="password" name="password"><br>
        <input type="submit" value="Se connecter">
    </form>
    {% if error %}
        <p style="color: red">{{ error }}</p>
    {% endif %}
"""

# Page d'accueil après connexion
HOME_PAGE = """
    <h1>Bienvenue {{ username }}</h1>
    <p>Votre Session ID: {{ session_id }}</p>
    <a href="/secret">Voir votre secret</a><br>
    <a href="/logout">Déconnexion</a>
"""

# Page du secret
SECRET_PAGE = """
    <h1>Votre Secret</h1>
    <p>Secret: {{ secret }}</p>
    <a href="/">Retour</a>
"""

# Page de hijacking avec JavaScript
HIJACK_PAGE = """
    <h1>Session Hijacking</h1>
    <p>Entrez le Session ID volé :</p>
    <input type="text" id="session_id" style="width: 300px;" placeholder="Collez le Session ID ici"><br><br>
    <button onclick="hijackSession()">Hijacker la session</button>
    <p id="error" style="color: red;"></p>

    <script>
        function hijackSession() {
            const sessionId = document.getElementById('session_id').value.trim();
            if (!sessionId) {
                document.getElementById('error').innerText = 'Veuillez entrer un Session ID';
                return;
            }

            // Modifier le cookie côté client
            document.cookie = `session=${encodeURIComponent(sessionId)}; path=/`;

            // Rediriger vers la page secret
            window.location.href = '/secret';
        }
    </script>
"""


@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return render_template_string(HOME_PAGE,
                                      username=session['username'],
                                      session_id=request.cookies.get('session'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('login'))

        return render_template_string(LOGIN_PAGE, error="Mauvais identifiants")

    return render_template_string(LOGIN_PAGE)


@app.route('/secret')
def secret():
    if 'username' not in session:
        return "Vous devez être connecté", 401

    secret = f"Secret spécial pour {session['username']}"
    return render_template_string(SECRET_PAGE, secret=secret)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


# Endpoint pour le hijacking avec JavaScript
@app.route('/hijack')
def hijack():
    return render_template_string(HIJACK_PAGE)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
