"""Module for user specific stuff like forms and classes"""
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class SignupForm(FlaskForm):
    email = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField("Sign In")


class User(UserMixin):
    def __init__(self, username, password):
        super(User, self).__init__()
        self.id = username
        self.password = password
        self.is_admin = False


class UserDatabase:
    def __init__(self):
        self.users = dict()     # dict from username to User

    def add_user(self, username, password):
        """

        :return: Returns true if user was created successfully
        """

        if username in self.users:
            return None

        else:
            user = User(username, password)
            self.users[username] = user
            return user
