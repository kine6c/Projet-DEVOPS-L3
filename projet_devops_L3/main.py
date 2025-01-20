from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)

# Modèle de base de données
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), nullable=False)

    def __init__(self, email, username):
        self.email = email
        self.username = username

# Fonction d'initialisation de la base de données
def init_db():
    with app.app_context():
        db.create_all()

@app.route('/')
def home():
    userlist = User.query.all()
    return render_template("home.html", userlist=userlist)

@app.route('/insert', methods=['GET', 'POST'])
def insert():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')

        check_username = User.query.filter_by(username=username).first()
        check_email = User.query.filter_by(email=email).first()
        if check_username is not None:
            flash('Username already used', category='error')
        elif check_email is not None:
            flash('Email already used', category='error')
        elif len(email) < 3:
            flash('Email must be more than 4 characters', category='error')
        elif len(username) < 2:
            flash('Username must be more than 2 characters', category='error')
        else:
            new_user = User(email=email, username=username)
            db.session.add(new_user)
            db.session.commit()
            flash(f'User "{username}" created', category='success')
            return redirect(url_for("home"))
    return render_template("insert.html")

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    uto = User.query.get_or_404(id)
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')

        if email == uto.email:
            flash('No changes detected for the email', category='error')
        elif len(email) < 3:
            flash('Email must be more than 4 characters', category='error')
        elif len(username) < 2:
            flash('Username must be more than 2 characters', category='error')
        else:
            uto.email = email
            uto.username = username
            db.session.commit()
            flash(f'User "{uto.username}" updated', category='success')
            return redirect(url_for("home"))
    return render_template("update.html", user=uto)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_user(id):
    utd = User.query.get_or_404(id)
    username = utd.username
    db.session.delete(utd)
    db.session.commit()
    flash(f'User "{username}" deleted', category='warning')
    return redirect(url_for("home"))

if __name__ == '__main__':
    # Initialiser la base de données
    init_db()
    app.run(debug=True)
