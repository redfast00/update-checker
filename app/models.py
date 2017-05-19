from app import db, app
from passlib.hash import bcrypt
import string
import random

user_app_association = db.Table('subscriptions', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('android_app_id', db.Integer, db.ForeignKey('android_app.id'))
)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(120), unique=True)
    passwordhash = db.Column(db.String(60))
    email = db.Column(db.String(255))
    feed_uid = db.Column(db.String(app.config["FEED_UID_LEN"]), unique=True)
    subscribed_on = db.relationship("AndroidApp",
        secondary=user_app_association,
        back_populates="subscribers")
    def __init__(self):
        super(User, self ).__init__()
        self.set_feed_uid()

    def set_feed_uid(self):
        chars = string.ascii_letters + string.digits
        size = app.config["FEED_UID_LEN"]
        self.feed_uid = ''.join(random.choice(chars) for _ in range(size))
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User %r>' % (self.nickname)

    def verify_password(self, guess):
        return bcrypt.verify(guess, self.passwordhash)

    def set_password(self, password):
        self.passwordhash = bcrypt.hash(password)


class AndroidApp(db.Model):
    __tablename__ = 'android_app'
    id = db.Column(db.Integer, primary_key=True)
    android_id =  db.Column(db.String(), index=True, unique=True)

    updates = db.relationship("AndroidAppUpdate", back_populates="android_app")
    subscribers = db.relationship("User",
        secondary=user_app_association,
        back_populates="subscribed_on")

    def __init__(self, android_id):
        self.android_id = android_id

class AndroidAppUpdate(db.Model):
    __tablename__ = 'android_app_update'
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String())
    date_updated = db.Column(db.Date)
    timestamp = db.Column(db.DateTime)

    android_app_id = db.Column(db.Integer, db.ForeignKey('android_app.id'))
    android_app = db.relationship("AndroidApp", back_populates="updates")

    @property
    def android_id(self):
        return self.android_app.android_id

    def __repr__(self):
        return '<AndroidAppUpdate %r, %r>' % (self.version, self.timestamp)
