from logging import getLogger
from flask import abort, flash, redirect, render_template, request, url_for
from registry.forms import ActivateForm, ConfirmForm, QuickSelectForm, \
                           TransactionForm, check
from registry.models import Passport


CHECKIN_MESSAGE = 'Pass %d wurde eingecheckt.'
CHECKOUT_MESSAGE = 'Pass %d wurde ausgecheckt.'


def home():
    form = QuickSelectForm(request.form)
    if 'POST' == request.method:
        if form.validate_on_submit():
            pass_id = form.pass_id.data
            if Passport.get(pass_id):
                return redirect(url_for('desk.passport', pass_id=pass_id))
            else:
                return redirect(url_for('desk.activate', pass_id=pass_id))

    return render_template('desk/home.html', form=form,
                           active_passes=Passport.active_passes())


def current():
    passes = Passport.active_passes().all()
    return render_template('desk/current.html', passes=passes)


def activate(pass_id):
    if Passport.get(pass_id):
        abort(404)

    form = ActivateForm(request.values)
    status_code = 200
    if 'POST' == request.method:
        if form.validate_on_submit():
            Passport.create(form.surname.data, form.name.data, pass_id)
            return redirect(url_for('desk.passport', pass_id=pass_id))
        else:
            status_code = 406
    return render_template('desk/activate.html', form=form, pass_id=pass_id), \
        status_code


def passport(pass_id):
    passport = Passport.get(pass_id)
    if not passport:
        abort(404)

    form = TransactionForm(request.values, obj=passport)
    if 'POST' == request.method:
        if form.validate_on_submit():
            logger = getLogger(__name__)
            checked_in = checked_out = False
            if request.form.get('checkin') is not None:
                if passport.checked_in:
                    return redirect(url_for('desk.confirm_transaction',
                                            pass_id=pass_id, action='checkin'))
                passport.check_in()
                logger.debug('Checked in pass id %d', passport.pass_id)
                checked_in = True
                flash(CHECKIN_MESSAGE % pass_id, 'checkin')
            elif request.form.get('checkout') is not None:
                if not passport.checked_in:
                    return redirect(url_for('desk.confirm_transaction',
                                            pass_id=pass_id,
                                            action='checkout'))
                passport.check_out()
                logger.debug('Checked out pass id %d', passport.pass_id)
                checked_out = True
                flash(CHECKOUT_MESSAGE % pass_id, 'checkout')
            assert checked_in or checked_out
            return redirect(url_for('desk.home'))
    return render_template('desk/passport.html', passport=passport, form=form)


def confirm_transaction(pass_id, action):
    assert action in ('checkin', 'checkout')
    passport = Passport.get(pass_id)
    if not passport:
        abort(404)
    if action == ('checkout' if passport.checked_in else 'checkin'):
        abort(406)

    form = ConfirmForm(obj=dict(pass_id=pass_id, check=check(pass_id)))
    if request.method == 'POST' and form.validate_on_submit():
        if action == 'checkin':
            passport.check_in()
            flash(CHECKIN_MESSAGE % pass_id, 'checkout')
        else:
            passport.check_out()
            flash(CHECKOUT_MESSAGE % pass_id, 'checkout')
        return redirect(url_for('desk.home'))
    return render_template('desk/confirm_transaction.html', form=form)
