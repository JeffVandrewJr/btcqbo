from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired


class BTCCodeForm(FlaskForm):
    code = StringField('Pairing Code', validators=[DataRequired()])
    submit = SubmitField('Submit')


class KeysForm(FlaskForm):
    qb_id = StringField('Quickbooks Client ID', validators=[DataRequired()])
    qb_secret = StringField('Quickbooks Client Secret', validators=[DataRequired()])
    qb_sandbox = BooleanField('Quickbooks Sandbox')
    submit = SubmitField('Submit')


class MailForm(FlaskForm):
    mail_on = BooleanField('Mail On or Off')
    mail_user = StringField('Email Username', validators=[DataRequired()])
    mail_pswd = StringField('Email Password', validators=[DataRequired()])
    mail_host = StringField('Email Host', validators=[DataRequired()])
    mail_port = StringField('Email Port', validators=[DataRequired()])
    mail_from = StringField('Sender Email', validators=[DataRequired()])
    merchant = StringField('Merchant Name', validators=[DataRequired()])
    recipient = StringField('Test Recipient')
    submit = SubmitField('Submit')
