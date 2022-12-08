from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


# from flask_ckeditor import CKEditorField

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    city = StringField("City", validators=[DataRequired()])
    submit = SubmitField("REGISTER")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("LOG IN")


class CafeForm(FlaskForm):
    name = StringField("Cafe Name", validators=[DataRequired()])
    map_url = StringField("Map url", validators=[DataRequired()])
    img_url = StringField("Img url", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    wifi = SelectField("Is there a wifi?", choices=['Yes', 'No'], validators=[DataRequired()])
    toilet = SelectField('Has enough toilet?', choices=['Yes', 'No'],
                         validators=[DataRequired()])
    sockets = SelectField("Is it easy to find power sockets?", choices=['Yes', 'No'],
                          validators=[DataRequired()])
    seats = SelectField("Are tables and chairs comfortable for work?",
                        choices=['0-10', '10-20', "20-30", "30-40", "50+"],
                        validators=[DataRequired()])
    calls = SelectField("Can you comfortably make audio/video calls?", choices=['Yes', 'No'],
                        validators=[DataRequired()])
    price = StringField("Coffee Price", validators=[DataRequired()])

    submit = SubmitField("Add")


class ReviewForm(FlaskForm):
    review_text = CKEditorField("Review", validators=[DataRequired()])
    submit = SubmitField("Send review")
