from flask import abort, redirect, render_template, request, url_for
from registry.forms import ActivateForm, QuickSelectForm
from registry.models import Passport


def home():
    form = QuickSelectForm(request.form)
    if 'POST' == request.method:
        if form.validate_on_submit():
            pass_id = form.pass_id.data
            if Passport.get(pass_id):
                return redirect(url_for('desk.passport', pass_id=pass_id))
            else:
                return redirect(url_for('desk.activate', pass_id=pass_id))

    return render_template('desk/home.html', form=form)


def activate(pass_id):
    if Passport.get(pass_id):
        abort(404)

    form = ActivateForm(request.form)
    if 'POST' == request.method:
        if form.validate_on_submit():
            Passport.create(form.surname.data, form.name.data, pass_id)
            return redirect(url_for('desk.passport', pass_id=pass_id))
    return render_template('desk/activate.html', form=form, pass_id=pass_id)


def passport(pass_id):
    passport = Passport.get(pass_id)
    if not passport:
        abort(404)

    return render_template('desk/passport.html', passport=passport)


def transaction(passport_id):
    return render_template('desk/transaction_confirm.html')
