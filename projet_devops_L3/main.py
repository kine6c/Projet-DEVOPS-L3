from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

# Initialisation de l'application
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'xxxxxxxxxxxxxx'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:votre_nouveau_mot_de_passe@localhost:3306/flask_dev'
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Le dossier où les images seront stockées
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Initialisation de la base de données
db = SQLAlchemy(app)

# Modèle de la base de données
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150))
    photo = db.Column(db.String(150))  # Nouvelle colonne pour la photo

    def __init__(self, email, username, photo=None):
        self.email = email
        self.username = username
        self.photo = photo

# Vérification de l'extension du fichier
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Route pour la page d'accueil
@app.route('/')
def home():
    userlist = User.query.all()
    return render_template("home.html", userlist=userlist)

# Fonction pour ajouter un utilisateur
@app.route('/insert', methods=['GET', 'POST'])
def insert(): 
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        photo = request.files.get('photo')

        # Vérification des utilisateurs existants
        check_username = User.query.filter_by(username=username).first()
        check_email = User.query.filter_by(email=email).first()

        if check_username:
            flash('Username already used', category='error') 
        elif check_email:
            flash('Email already used', category='error') 
        elif len(email) < 3:
            flash('Email should be at least 3 characters', category='error')
        elif len(username) < 2:
            flash('Username should be at least 2 characters', category='error')
        else:
            # Gestion de la photo
            photo_filename = None
            if photo and allowed_file(photo.filename):
                photo_filename = secure_filename(photo.filename)
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
            
            new_user = User(email=email, username=username, photo=photo_filename)
            db.session.add(new_user)
            db.session.commit()
            flash('User: "' + username + '" Created', category='success')
            return redirect(url_for('home'))
    return render_template("insert.html")

# Fonction pour mettre à jour un utilisateur
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    uto = User.query.get_or_404(id)
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        photo = request.files.get('photo')

        # Vérification des changements
        if uto.email == email and uto.username == username and not photo:
            flash('No changes made.', category='warning')
        else:
            # Mise à jour des informations utilisateur
            if uto.email != email:
                uto.email = email
            if uto.username != username:
                uto.username = username
            
            # Gestion de la photo
            if photo and allowed_file(photo.filename):
                # Supprimer l'ancienne photo si elle existe
                if uto.photo:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], uto.photo))
                
                # Sauvegarder la nouvelle photo
                photo_filename = secure_filename(photo.filename)
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
                uto.photo = photo_filename
            
            db.session.commit()
            flash(f'User: "{uto.username}" Updated', category='success')
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

# Lancer l'application Flask
if __name__ == '__main__':
    app.run(debug=True)
