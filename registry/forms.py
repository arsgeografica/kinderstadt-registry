# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import HiddenField, IntegerField, StringField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from stdnum import luhn


CHECK_ALPHABET = '0123456789ABCDEFGHJKLMNPQRSTUVWXY'


def check(value):
    """
    Creates two-digit check value for given input value
    """

    def _check(value):
        return luhn.calc_check_digit(value, alphabet=CHECK_ALPHABET)

    a = _check(value)
    b = _check(str(value) + str(a))

    return a + b


def check_validator(pass_id, check_id):
    actual = check_id.lower()
    expected = check(pass_id).lower()
    if actual != expected:
        raise ValidationError(u'Ungültige Check-ID')


class QuickSelectForm(Form):
    pass_id = IntegerField(validators=[DataRequired(), NumberRange(min=1)])


class ActivateForm(Form):
    surname = StringField(validators=[DataRequired()])
    name = StringField(validators=[DataRequired()])
    pass_id = HiddenField(validators=[DataRequired()])
    check = StringField(validators=[DataRequired()])

    def validate_check(form, field):
        return check_validator(form.pass_id.data, form.check.data)


class TransactionForm(Form):
    pass_id = HiddenField(validators=[DataRequired()])
    check = StringField(validators=[DataRequired()])

    def validate_check(form, field):
        return check_validator(form.pass_id.data, form.check.data)


class ConfirmForm(Form):
    pass_id = HiddenField(validators=[DataRequired()])
    check = HiddenField(validators=[DataRequired()])
