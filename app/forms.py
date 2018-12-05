from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired


class BTCCodeForm(FlaskForm):
    code = StringField('Pairing Code', validators=[DataRequired()])
    submit = SubmitField('Submit')


class PasswordForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class KeysForm(FlaskForm):
    qb_id = StringField('Quickbooks Client ID', validators=[DataRequired()])
    qb_secret = StringField('Quickbooks Client Secret', validators=[DataRequired()])
    qb_sandbox = BooleanField('Quickbooks Sandbox')
    submit = SubmitField('Submit')
