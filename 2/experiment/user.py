# -*- coding: utf-8 -*-

"""Module for user specific stuff like forms and classes"""
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, RadioField
from wtforms.validators import DataRequired


class SignupForm(FlaskForm):
    pseudonim = StringField('pseudonim', validators=[DataRequired()])
    wiek = IntegerField('wiek', validators=[DataRequired()])
    sex = RadioField(u'płeć', choices=[('man',u'mężczyzna'),('woman','kobieta')], validators=[DataRequired()])
    submit = SubmitField("Rozpocznij")


class User(UserMixin):
    def __init__(self, username, password, is_admin):
        super(User, self).__init__()
        self.id = username
        self.password = password
        self.is_admin = is_admin
