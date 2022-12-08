from flask import Flask, render_template, redirect, url_for, flash, abort
# from flask_ckeditor import CKEditor
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from forms import CafeForm, RegisterForm, LoginForm, ReviewForm
from flask_login import LoginManager, login_user, UserMixin, login_required, current_user, logout_user
from sqlalchemy.orm import relationship
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_gravatar import Gravatar

app = Flask(__name__)
app.config['SECRET_KEY'] = "SECRET_KEY"
ckeditor = CKEditor(app)
Bootstrap(app)
# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///cafes.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
gravatar = Gravatar(app,
                    size=110,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))

    all_cafe = relationship("Cafes", back_populates="author")
    reviews = relationship("Review", back_populates="review_author")


class Cafes(db.Model):
    __tablename__ = "cafe"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="all_cafe")

    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    has_sockets = db.Column(db.String(250), nullable=False)
    has_toilets = db.Column(db.String(250), nullable=False)
    has_wifi = db.Column(db.String(250), nullable=False)
    can_take_calls = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    coffee_price = db.Column(db.String(250), nullable=False)

    reviews = relationship("Review", back_populates="parent_cafes")


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    review_author = relationship("User", back_populates="reviews")

    cafe_id = db.Column(db.Integer, db.ForeignKey("cafe.id"))
    parent_cafes = relationship("Cafes", back_populates="reviews")

    text = db.Column(db.Text, nullable=False)


# advanced decoration
def admin_only(f):
    @wraps(f)
    def wrapper_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return wrapper_function


@app.route('/')
def get_all_cafes():
    cafes = Cafes.query.all()
    return render_template("index.html", all_cafes=cafes, current_user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("You've already signed up try to log in.")
            return redirect(url_for('login'))
        new_user = User()
        new_user.email = form.email.data
        new_user.name = form.name.data
        new_user.city = form.city.data
        hashed_password = generate_password_hash(password=form.password.data, method='pbkdf2:sha256', salt_length=8)
        new_user.password = hashed_password
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('get_all_cafes'))

    return render_template('register.html', form=form, current_user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("That email is not exist.")
        elif not check_password_hash(user.password, password):
            flash("Password is wrong.")
        else:
            login_user(user)
            return redirect(url_for('get_all_cafes'))
    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_cafes'))


@app.route('/cafe/<int:cafe_id>', methods=['GET', 'POST'])
def show_cafe(cafe_id):
    requested_cafe = Cafes.query.get(cafe_id)
    form = ReviewForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login to review")
            return redirect(url_for('login'))
        new_review = Review(
            text=form.review_text.data,
            review_author=current_user,
            parent_cafes=requested_cafe)
        db.session.add(new_review)
        db.session.commit()
    return render_template("post.html", cafe=requested_cafe, current_user=current_user, form=form)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_new_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        if Cafes.query.filter_by(name=form.name.data).first():
            flash("This place already exist.")
            return redirect(url_for('add_new_post'))
        new_cafe = Cafes(
            name=form.name.data,
            author=current_user,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.location.data,
            has_sockets=form.sockets.data,
            has_toilets=form.toilet.data,
            has_wifi=form.wifi.data,
            can_take_calls=form.calls.data,
            seats=form.seats.data,
            coffee_price=form.price.data
        )
        db.session.add(new_cafe)
        db.session.commit()
        flash("Place successfully added.")
        return redirect(url_for('get_all_cafes'))
    return render_template("make-post.html", form=form, current_user=current_user)


@app.route('/edit-cafe/<int:cafe_id>', methods=['GET', 'POST'])
@login_required
def edit_cafe(cafe_id):
    cafe = Cafes.query.get(cafe_id)
    form = CafeForm()
    if form.validate_on_submit():
        cafe.name = form.name.data
        cafe.map_url = form.map_url.data
        cafe.img_url = form.img_url.data
        cafe.location = form.location.data
        cafe.has_sockets = form.sockets.data
        cafe.has_toilets = form.toilet.data
        cafe.has_wifi = form.wifi.data
        cafe.can_take_calls = form.calls.data
        cafe.seats = form.seats.data
        cafe.coffee_price = form.price.data
        db.session.commit()
        return redirect(url_for('show_cafe', cafe_id=cafe_id))
    return render_template("make-post.html", form=form, current_user=current_user)


@app.route("/delete/<int:cafe_id>")
@admin_only
def delete_cafe(cafe_id):
    post_delete = Cafes.query.get(cafe_id)
    db.session.delete(post_delete)
    db.session.commit()
    return redirect(url_for('get_all_cafes'))


if __name__ == "__main__":
    app.run(host='192.168.1.33', port=5000, debug=True)
