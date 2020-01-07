from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from wtforms.validators import Email, EqualTo
from app.models import Users, get_user
#re is imported to use regular expressions to validate the rollno in 
#registration form.
import re


class LoginForm(FlaskForm):
    username = StringField("Username", validators = [DataRequired() ])
    password = PasswordField("Password", validators = [DataRequired() ])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    rollno = StringField("Rollno", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Repeat Password", validators=[DataRequired()
        ,EqualTo("password")])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = get_user(username=username.data)
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        user = get_user(email=email.data)
        if user is not None:
            raise ValidationError("Please use a different email address.")
    # I need to learn regular expressions(REGEX)
    # It will make the following stuff very simple and efficient.
    def validate_rollno(self, rollno):
        user = get_user(rollno=rollno.data)
        if user is not None:
            raise ValidationError("A user with this rollno already exists.")
       
        """The below expression checks that the rollno entered is a valid
        rollno given to us by our college. I am using a regex that matches
        the rollno format for my college.
        
        If you are reusing this code (very unlikely as I don't think this code
        would even be read by someone else than me.) you need to remove the
        code section below or use your custom regex."""

        result=re.fullmatch("(18|19)[Ii][Tt][0-9]{4}", rollno.data)
        if result is None:
            raise ValidationError("Please provide the correct rollno.")
        
