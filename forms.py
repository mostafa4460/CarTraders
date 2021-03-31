from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, FileField
from wtforms.validators import DataRequired, Email, Length, InputRequired, Optional, EqualTo

class UserEditForm(FlaskForm):
    """Form for editing users."""

    def validate_location(form, field):
        if "," not in field.data:
            field.errors = ['Please only input your CITY & STATE separated by a comma.']

    first_name = StringField('First Name', validators=[DataRequired(), Length(max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=10)])
    location = StringField('Location (City, State)', validators=[DataRequired(), validate_location])

class UserAddForm(UserEditForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired(), Length(max=20)])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=6),
        EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm Password')

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired(), Length(max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

class AddTradeForm(FlaskForm):
    """Add New Trade form."""

    trading = StringField('Trading', validators=[DataRequired()])
    trading_for = StringField('Trading For', validators=[DataRequired()])
    additional_cash = IntegerField('Asking $', validators=[Optional()])
    offering_cash = IntegerField('Offering $', validators=[Optional()])
    img = StringField('Image')
    description = TextAreaField('Description')