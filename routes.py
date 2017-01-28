from flask import Flask, render_template, request, redirect, url_for, session
from models import db, User, LocationPoint
from forms import Signup, Login, Location

app = Flask(__name__)
#note that 'user' and 'password' aren't required...look into this
config = { 'host': 'localhost',
            'database': 'flaskpractice',
            'port': '5001'}
DATABASE_URI = "postgresql://@127.0.0.1:{}/{}".format(config['port'], config['database'])
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
#for removing repl warnings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)

app.secret_key = "secret_key"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if 'email' in session:
        return redirect(url_for('home'))
    form = Signup()

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('signup.html', form=form)
        else:
            new_user = User(form.first_name.data, form.last_name.data,
                            form.email.data, form.password.data)
            db.session.add(new_user)
            db.session.commit()

            session['email'] = new_user.email
            return redirect(url_for('home'))
    elif request.method == 'GET':
        return render_template("signup.html", form=form)
@app.route("/login", methods=['GET','POST'])
def login():
        if 'email' in session:
            return redirect(url_for('home'))
        form = Login()

        if request.method == 'POST':
            if form.validate() == False:
                return render_template('login.html', form=form)
            else:
                email = form.email.data
                password = form.password.data

                user = User.query.filter_by(email=email).first()

                if user is not None and user.check_password(password):
                    session['email'] = form.email.data
                    return redirect(url_for('home'))
                else:
                    return redirect(url_for('login'))
        elif request.method == 'GET':
            return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route("/home", methods=['GET','POST'])
def home():
    if 'email' not in session:
        return redirect(url_for('login'))

    form = Location()
    mall = []
    coord = (47.6062, -122.3321)
    if request.method == "POST":
        if form.validate() == False:
            return render_template('home.html', form=form)
        else:
            loc = form.location.data
            place = LocationPoint()
            coord = place.loc_lat_long(loc)
            mall = place.query(loc)
            return render_template('home.html', form=form, coord=coord, mall=mall)

    elif request.method == "GET":
        return render_template("home.html", form=form, coord=coord, mall=mall)

    return render_template("home.html")


if __name__=="__main__":
    app.run(debug=True)
