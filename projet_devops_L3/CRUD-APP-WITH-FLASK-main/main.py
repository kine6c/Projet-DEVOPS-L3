from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Initialiser l'application
app = Flask(__name__)

# Configuration de l'application
app.config['SECRET_KEY'] = 'xxxxxxxxxxxxxx'
# Spécifier l'URI de la base de données SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_dev.db'
# Désactiver le suivi des modifications de session pour la performance
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialiser SQLAlchemy
db = SQLAlchemy(app)

# Définition du modèle de données (table users)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150))

# Fonction d'insertion d'utilisateur
@app.route('/insert', methods=['GET', 'POST'])
def insert():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')

        # Vérification si le nom d'utilisateur ou l'email existent déjà
        check_username = User.query.filter_by(username=username).first()
        check_email = User.query.filter_by(email=email).first()

        if check_username:
            flash('Username already used', category='error')
        elif check_email:
            flash('Email already used', category='error')
        elif len(email) < 3:
            flash('Email must be greater than 3 characters', category='error')
        elif len(username) < 2:
            flash('Username must be greater than 2 characters', category='error')
        else:
            # Créer un nouvel utilisateur
            new_user = User(email=email, username=username)
            db.session.add(new_user)
            db.session.commit()
            flash(f'User "{username}" created successfully!', category='success')
            return redirect(url_for("home"))
    return render_template("insert.html")

# Route d'accueil pour afficher tous les utilisateurs
@app.route('/')
def home():
    userlist = User.query.all()
    return render_template("home.html", userlist=userlist)

# Fonction pour mettre à jour un utilisateur
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    uto = User.query.get_or_404(id)
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')

        # Vérification si les informations sont valides
        if uto.email == email:
            flash('Email already used', category='error')
        elif len(email) < 3:
            flash('Email must be greater than 3 characters', category='error')
        elif len(username) < 2:
            flash('Username must be greater than 2 characters', category='error')
        else:
            uto.email = email
            uto.username = username
            db.session.commit()
            flash(f'User "{uto.username}" updated successfully!', category='success')
            return redirect(url_for("home"))
    return render_template("update.html", user=uto)

# Fonction pour supprimer un utilisateur
@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_user(id):
    utd = User.query.get_or_404(id)
    username = utd.username
    if utd:
        db.session.delete(utd)
        db.session.commit()
        flash(f'User "{username}" deleted', category='warning')
        return redirect(url_for("home"))

# Créer toutes les tables si elles n'existent pas encore, directement avant de démarrer l'application
if __name__ == '__main__':
    # Créer la base de données et les tables (si elles n'existent pas)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
