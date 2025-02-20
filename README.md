# Session Hijacking Demonstration

Je vais modifier le code pour remplacer le formulaire POST par une page avec du JavaScript qui modifie le cookie côté
client directement dans le navigateur, puis redirige vers la page `/secret`. Cela simule encore mieux une attaque
réaliste où un attaquant utilise un script ou les outils de développement pour injecter un cookie volé.

Voici le code mis à jour :

```python
from flask import Flask, request, render_template_string, session, redirect, url_for
import secrets

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
```

### Explications des Changements :

1. **Suppression du POST** :
    - L’endpoint `/hijack` ne gère plus POST. Il renvoie simplement une page HTML avec un script JavaScript pour GET.

2. **Page de Hijacking avec JavaScript** :
    - La variable `HIJACK_PAGE` contient maintenant :
        - Un champ `<input>` pour entrer le `session_id`.
        - Un bouton qui appelle la fonction `hijackSession()` au clic.
        - Un élément `<p>` pour afficher les erreurs.
    - Le script JavaScript :
        - Récupère la valeur du champ avec `document.getElementById('session_id').value`.
        - Vérifie qu’elle n’est pas vide (`trim()` enlève les espaces inutiles).
        - Définit le cookie avec `document.cookie = `session=${encodeURIComponent(sessionId)}; path=/`` (le `path=/`
          garantit que le cookie est disponible pour toutes les routes).
        - Redirige vers `/secret` avec `window.location.href`.

3. **Côté Client** :
    - Tout se passe dans le navigateur. Le serveur ne fait que servir la page ; c’est le JavaScript qui modifie le
      cookie et déclenche la redirection.

### Étapes pour Tester :

1. **Lancer le serveur** :
   ```bash
   python nom_du_fichier.py
   ```

2. **Connexion Légitime** :
    - Va à `http://localhost:5000/`, connecte-toi avec `alice` / `password123`.
    - Note le **Session ID** affiché (ex: `.eJwl...`).

3. **Hijacking** :
    - Ouvre un **nouveau navigateur** ou une **fenêtre anonyme** (pour partir d’une session vierge).
    - Va à `http://localhost:5000/hijack`.
    - Colle le `session_id` dans le champ texte.
    - Clique sur "Hijacker la session".
    - Le JavaScript modifiera le cookie dans ton navigateur et te redirigera vers `http://localhost:5000/secret`.

4. **Résultat Attendu** :
    - Tu verras la page `/secret` avec "Secret spécial pour alice", prouvant que le cookie volé a été utilisé pour
      hijacker la session.

### Pourquoi Cela Fonctionne :

- Le JavaScript modifie le cookie `session` côté client, ce qui est exactement ce qu’un attaquant pourrait faire avec
  les outils de développement du navigateur (ex: modifier un cookie dans l’onglet "Application") ou via un script
  malveillant (XSS).
- Lors de la redirection vers `/secret`, Flask reçoit ce cookie dans l’en-tête de la requête, le valide, et restaure la
  session associée.

### Dépannage :

- **Erreur 401** : Si tu obtiens "Vous devez être connecté" après redirection, vérifie que le `session_id` est copié
  intégralement (point initial inclus, pas d’espaces). Ouvre les outils de développement (F12) > onglet "
  Application" > "Cookies" pour confirmer que `session` est bien défini.
- **Pas de redirection** : Si rien ne se passe, assure-toi que JavaScript est activé et vérifie la console du navigateur
  pour d’éventuelles erreurs.

### Réalisme :

- Cette approche est très proche d’une attaque réelle où un attaquant injecterait un cookie via un script ou
  manuellement dans son navigateur pour usurper une session.

Si tu veux ajouter des fonctionnalités (ex: vérifier le cookie avant redirection) ou explorer autre chose, fais-moi
signe !