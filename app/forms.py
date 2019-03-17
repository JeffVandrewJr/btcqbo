from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired


class BTCCodeForm(FlaskForm):
    code = StringField('Pairing Code', validators=[DataRequired()])
    forward_url = StringField('IPN Forwarding URL (only for Deposit Mode)')
    submit = SubmitField('Submit')


class KeysForm(FlaskForm):
    qb_id = StringField('Quickbooks Client ID', validators=[DataRequired()])
    qb_secret = StringField('Quickbooks Client Secret', validators=[DataRequired()])
    qb_sandbox = BooleanField('Quickbooks Sandbox')
    submit = SubmitField('Submit')


class MailForm(FlaskForm):
    mail_on = BooleanField('Mail On or Off')
    mail_user = StringField('Email Username', validators=[DataRequired()])
    mail_pswd = PasswordField('Email Password', validators=[DataRequired()])
    mail_host = StringField('Email Host', validators=[DataRequired()])
    mail_port = StringField('Email Port', validators=[DataRequired()])
    mail_from = StringField('Sender Email', validators=[DataRequired()])
    merchant = StringField('Merchant Name', validators=[DataRequired()])
    mail_custom = TextAreaField('Enter a custom message for email receipts (optional):')
    recipient = StringField('Test Recipient')
    submit = SubmitField('Submit')
