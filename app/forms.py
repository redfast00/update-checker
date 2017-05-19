from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField, validators
from app import models, scraper
from flask_login import current_user
import re

def validate_domain_name(domain):
    return re.match(r'^[a-zA-Z\d-]{1,63}(\.[a-zA-Z\d-]{1,63})+$', domain)

class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[validators.Length(min=4, max=120)])
    email = StringField('email', validators=[validators.Length(min=6, max=255)])
    password = PasswordField('password', validators=[
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('confirm')

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        # check if we already have this username
        if models.User.query.filter_by(nickname=self.username.data).first():
            self.username.errors.append("Username already used")
            return False
        # don't check email
        return True


class LoginForm(FlaskForm):
    username =  StringField('username', validators=[
        validators.DataRequired(),
        validators.Length(min=4, max=120)
    ])
    password = PasswordField('password', validators=[validators.DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        user = models.User.query.filter_by(nickname=self.username.data).first()
        if user is None:
            self.username.errors.append('Unknown username')
            return False
        if not user.verify_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False
        self.user = user
        return True

class RemoveDomainForm(FlaskForm):
    to_remove = StringField('to_remove', validators=[validators.DataRequired()])
    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        if not validate_domain_name(self.to_remove.data):
            self.to_remove.errors.append('Invalid package name')
            return False
        app = models.AndroidApp.query.filter_by(android_id=self.to_remove.data).first()
        if app is None or current_user not in app.subscribers:
            self.to_remove.errors.append('You are not subscribed to this app')
            return False
        self.app = app
        return True

class AddDomainForm(FlaskForm):
    domain = StringField('domain', validators=[validators.DataRequired()])
    submit = SubmitField('submit')
    app = None
    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        # check that domain is a valid package name
        if not validate_domain_name(self.domain.data):
            self.domain.errors.append('Invalid package name')
            return False
        # check if the domain is already in the database
        app = models.AndroidApp.query.filter_by(android_id=self.domain.data).first()
        if app is not None:
            if current_user in app.subscribers:
                self.domain.errors.append('You are already subscribed to this app')
                return False
            else:
                self.app = app
                return True
        # app isn't in database yet, check if it exists
        result = scraper.get_information(self.domain.data)
        if result is None:
            self.domain.errors.append('Package is not in Google Play Store (yet)')
            return False
        return True

