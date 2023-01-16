from flask import Flask, render_template, url_for, request, redirect, flash
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user, UserMixin  

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'thisissec'

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "авторизируйтесь, чтобы получить доступ к недоступным странцам"

mail = Mail(app)

db = SQLAlchemy(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(20), nullable = False)
    password = db.Column(db.String(300), nullable = False)
        
class UserLogin(): # если написать db.Model то ломается, а если написать UserMixin и убрать 3 функции тоже ломается
    def fromDB(self, user_id, db):
        if (len(db.session.query(User).filter(User.id == user_id).all()) > 0):
            self.__user = db.session.query(User).filter(User.id == user_id).all()[0]
            return self
        else:
            print("пользователь не найден")
            return False
    def create(self, user):
        self.__user = user
        return self
    def is_authenticated(self):   
        return True
    def is_active(self):
        return True
    def if_anonymous(self):
        return False
    def get_id(self):
        return str(self.__user.id)
   

@login_manager.user_loader
def load_user(user_id):
   return UserLogin().fromDB(user_id, db)   

@app.route('/')
@login_required 
def index():
    return render_template("index.html")

@app.route('/create-account', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        tit = request.form['title']
        hashe = generate_password_hash(request.form['intro'])
        user = User(email = tit, password = hashe)
        if (len(db.session.query(User).filter(User.email == tit).all()) > 0):
            return "уже зарег"
        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/')
        except:
            return "mistake"
    else:
        return render_template("create-account.html")

@app.route('/profile')
@login_required
def profile():
    cust_id = current_user.get_id()
    return render_template("profile.html", cust_id = cust_id)
    

@app.route('/login', methods = ["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect('/profile')
    if (request.method == "POST"):
        tit = request.form['title1']
        passw = request.form['intro1']
        if ( len(db.session.query(User).filter(User.email == tit).all()) > 0 ):
            user = db.session.query(User).filter(User.email == tit).all()[0]
        else:
            return "mistake"
        if check_password_hash(user.password, passw):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remember') else False
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or '/profile')
        return "mistake"
    else:
        return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("you are logout")
    return redirect("/login")

if __name__ == '__main__':
    app.run()
