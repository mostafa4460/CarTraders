"""SQLAlchemy models for CarTraders."""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)

class Trade(db.Model):
    """An individual trade."""

    __tablename__ = "trades"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(70),
        nullable=False
    )

    description = db.Column(db.Text)

    trading_for = db.Column(
        db.String(50),
        default="Open to trades"
    )

    asking_cash = db.Column(db.Integer)

    offering_cash = db.Column(db.Integer)

    available = db.Column(
        db.Boolean,
        default=True
    )

    img_url = db.Column(
        db.Text,
        default='/static/images/default-car.png'
    )

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow(),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    user = db.relationship("User", backref="trades")

class User(UserMixin, db.Model):
    """User in the system."""

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(20),
        nullable=False,
        unique=True
    )

    password = db.Column(
        db.Text,
        nullable=False
    )

    first_name = db.Column(
        db.String(20),
        nullable=False
    )

    last_name = db.Column(
        db.String(20),
        nullable=False
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    phone = db.Column(
        db.String(10),
        nullable=False,
        unique=True
    )

    city = db.Column(
        db.Text,
        nullable=False
    )

    state = db.Column(
        db.Text,
        nullable=False
    )

    cover_pic = db.Column(
        db.Text,
        default = 'static/images/default_cover.jpg'
    )

    profile_pic = db.Column(
        db.Text,
        default = 'static/images/default_profile.jpg'
    )

    @classmethod
    def signup(cls, username, password, first_name, last_name, email, phone, city, state):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pw = bcrypt.generate_password_hash(password, rounds=14).decode('UTF-8')
        
        user = User(
            username = username,
            password = hashed_pw,
            first_name = first_name,
            last_name = last_name,
            email = email,
            phone = phone,
            city = city,
            state = state
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Authenticates a username and password to an existing user in the system
        - Checks if a user with the given username exists
        - If so, check that the user's hashed password and passed in password match
        - Return user object if true, False if not
        """

        user = cls.query.filter_by(username=username).first()
        if user:
            if bcrypt.check_password_hash(user.password, password):
                return user
        return False

    def __repr__(self):
        """Returns a better string representation of a user"""
        return f'<User {self.id} {self.username}>'