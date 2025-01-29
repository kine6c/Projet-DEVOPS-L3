from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from datetime import datetime 
from flask import make_response


# Initialiser l'application Flask
app = Flask(__name__)

# Configuration de l'application
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialiser SQLAlchemy
db = SQLAlchemy(app)

# Initialiser Flask-Migrate
migrate = Migrate(app, db)

# Modèle User
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), default='user', nullable=True)
    password = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime,nullable=True, default=datetime.now)

    def __init__(self, email, username,  password, role):
        super().__init__()
        self.email=email
        self.password=generate_password_hash(password)
        self.username=username
        self.role=role

# Décorateur pour vérifier si l'utilisateur est connecté
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to be logged in to access this page.', category='error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Route pour afficher les utilisateurs
@app.route('/')
@login_required
def home():
    try:
        users = User.query.all()
        return render_template("home.html", users=users)

    except Exception as e:
        print("ERROR", e)
        users = []
        return render_template("home.html", users=users)

# Route pour insérer un nouvel utilisateur
@app.route('/insert', methods=['GET', 'POST'])
@login_required
def insert():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        created_at = datetime.now()
        role = request.form.get('role', 'user')  # Rôle par défaut

        if not email or not username or not password:
            flash('All fields are required.', category='error')
        else:
            check_username = User.query.filter_by(username=username).first()
            check_email = User.query.filter_by(email=email).first()

            if check_username or check_email:
                flash('Email or username already exists.', category='error')
            else:
                new_user = User(email=email, username=username,  password=password, role=role)
                try:
                    db.session.add(new_user)
                    db.session.commit()
                    flash(f'User "{username}" created successfully!', category='success')
                    return redirect(url_for("home"))
                except IntegrityError:
                    db.session.rollback()
                    flash('Failed to create user. Please try again.', category='error')

    return render_template("insert.html")

# RECHERCHE
@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    query = request.args.get('query', '')  # Term de recherche
    role = request.args.get('role', '')  # Rôle sélectionné
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    page = request.args.get('page', 1, type=int)  # Pagination

    # Initialisation de la requête pour obtenir les utilisateurs
    results = User.query

    # Filtrage par terme de recherche (email ou username)
    if query:
        results = results.filter(
            (User.username.ilike(f'%{query}%')) | 
            (User.email.ilike(f'%{query}%'))
        )

    # Filtrage par rôle
    if role:
        results = results.filter(User.role == role)

    # Filtrage par date (start_date et end_date)
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            results = results.filter(User.created_at >= start_date_obj)
        except ValueError:
            flash("Invalid start date format. Please use YYYY-MM-DD.", category='error')

    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            results = results.filter(User.created_at <= end_date_obj)
        except ValueError:
            flash("Invalid end date format. Please use YYYY-MM-DD.", category='error')

    # Pagination
    results = results.paginate(page=page, per_page=10, error_out=False)

    return render_template('search.html', query=query, results=results, role=role, start_date=start_date, end_date=end_date)

# Route pour mettre à jour un utilisateur
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        role = request.form.get('role', 'user')

        if not email or not username:
            flash('Email and username are required.', category='error')
        else:
            check_email = User.query.filter(User.email == email, User.id != id).first()
            check_username = User.query.filter(User.username == username, User.id != id).first()

            if check_email:
                flash('Email is already used by another user.', category='error')
            elif check_username:
                flash('Username is already used by another user.', category='error')
            else:
                user.email = email
                user.username = username
                user.role = role
                db.session.commit()
                flash(f'User "{username}" updated successfully!', category='success')
                return redirect(url_for("home"))

    return render_template("update.html", user=user)


# Route pour l'inscription
@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        role = "User"
        confirm_password = request.form.get('confirm_password')

        # Validation des champs
        if not email or not username or not password or not confirm_password:
            flash('All fields are required.', category='error')
        elif password != confirm_password:
            flash('Passwords do not match.', category='error')
        else:
            # Vérifiez si l'utilisateur existe déjà
            check_user = User.query.filter_by(email=email).first()
            if check_user:
                flash('Email already exists. Please use a different one.', category='error')
            else:
                # Créez un nouvel utilisateur
                new_user = User(email=email, username=username,role=role, password=password)
                try:
                    db.session.add(new_user)
                    db.session.commit()
                    flash('Account created successfully! You can now log in.', category='success')
                    return redirect(url_for('login'))
                except IntegrityError:
                    db.session.rollback()
                    flash('An error occurred. Please try again.', category='error')

    return render_template("inscription.html")

# Route pour la connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('You have been logged in!', category='success')
            return redirect(url_for('home'))
        else:
            flash('Invalid login credentials. Please try again.', category='error')

    return render_template("login.html")

# Route pour la déconnexion
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', category='info')
    return redirect(url_for('login'))

# Point d'entrée de l'application
if __name__ == '__main__':
    app.run(debug=True, port=8000)
