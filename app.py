import secrets

from flask import Flask, request, render_template, session, redirect, url_for

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Clé secrète pour signer les sessions

# Simulation d'une base de données utilisateurs
users = {
    "alice": "password123"
}


@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return render_template('home.html',
                               username=session['username'],
                               session_id=request.cookies.get('session'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('login'))

        return render_template('login.html', error="Mauvais identifiants")

    return render_template('login.html')


@app.route('/secret')
def secret():
    if 'username' not in session:
        return "Vous devez être connecté", 401

    secret = f"Secret spécial pour {session['username']}"
    return render_template('secret.html', secret=secret)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


# Endpoint pour le hijacking avec JavaScript
@app.route('/hijack')
def hijack():
    return render_template('hijack.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
