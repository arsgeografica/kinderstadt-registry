from flask.ext.wtf import Form
from wtforms import IntegerField, StringField
from wtforms.validators import DataRequired, NumberRange


class QuickSelectForm(Form):
    pass_id = IntegerField(validators=[DataRequired(), NumberRange(min=1)])


class ActivateForm(Form):
    surname = StringField(validators=[DataRequired()])
    name = StringField(validators=[DataRequired()])
