from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class BTCCodeForm(FlaskForm):
    code = StringField('Pairing Code', validators=[DataRequired()])
    submit = SubmitField('Submit')
