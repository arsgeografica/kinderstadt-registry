# -*- encoding: utf-8 -*-

import datetime
from logging import getLogger
from flask import abort, current_app, flash, jsonify, redirect, \
                  render_template, request, url_for
from registry.extensions import db
from registry.forms import ConfirmForm, QuickSelectForm, SweepForm
from registry.forms import check, passport_form_factory, \
    transaction_form_factory
from registry.models import Passport, Visit


CHECKIN_MESSAGE = 'Pass %d wurde eingecheckt.'
CHECKOUT_MESSAGE = 'Pass %d wurde ausgecheckt.'


def home():
    form = QuickSelectForm(request.form)
    if 'POST' == request.method:
        if form.validate():
            pass_id = form.pass_id.data
            if Passport.get(pass_id):
                return redirect(url_for('passport.passport', pass_id=pass_id))
            else:
                return redirect(url_for('passport.activate', pass_id=pass_id))

    return render_template('passport/home.html', form=form,
                           active_passes=Passport.active_passes())


def query():
    if request.json is None:
        abort(400)

    query = request.json.get('query', None)
    if query is None:
        abort(400)

    passports = Passport.query.search(query) \
        .order_by(Passport.surname, Passport.name) \
        .limit(10).all()
    return jsonify(data=[{
        'pass_id': p.pass_id,
        'full_name': '%s %s' % (p.surname, p.name),
        'checked_in': p.checked_in
    } for p in passports])


def current():
    passes = Passport.active_passes().all()
    return render_template('passport/current.html', passes=passes)


def sweep():
    form = SweepForm(request.values)
    active_count = Passport.active_passes().count()
    status_code = 200
    if 'POST' == request.method:
        if form.validate():
            Visit.sweep()
            flash('Es wurden %d Pässe ausgecheckt' % active_count, 'success')
            return redirect(url_for('home'))
        status_code = 406
    return render_template('passport/sweep.html',
                           form=form, active_count=active_count), status_code


def activate(pass_id):
    if Passport.get(pass_id):
        abort(404)

    form = passport_form_factory(request.values, Passport(pass_id=pass_id),
                                 current_app.config['FLAGS'],
                                 current_app.config['START_DATE'],
                                 current_app.config['END_DATE'])

    status_code = 200
    if 'POST' == request.method:
        if form.validate():
            passport = Passport()
            passport.flags = {}
            form.populate_obj(passport)
            db.session.add(passport)
            db.session.commit()
            return redirect(url_for('passport.passport', pass_id=pass_id))
        else:
            status_code = 406
    return render_template('passport/activate.html',
                           form=form, pass_id=pass_id), status_code


def passport(pass_id):
    passport = Passport.get(pass_id)
    if not passport:
        abort(404)

    today = datetime.date.today().isoformat()
    passport_flags = passport.flags if passport.flags else {}

    active_flags = [(k, current_app.config['FLAGS'][k])
                    for k, d in passport_flags.items() if today in d]
    flag_filter = 'can_checkout' if passport.checked_in else 'can_checkin'
    flags = dict([(k, f['label']) for (k, f) in active_flags
                 if f.get(flag_filter) == False])

    form = transaction_form_factory(request.values, passport, flags)
    status_code = 200
    if 'POST' == request.method:
        if form.validate():
            logger = getLogger(__name__)
            checked_in = checked_out = False
            if request.form.get('checkin') is not None:
                if passport.checked_in:
                    return redirect(url_for('passport.confirm_transaction',
                                            pass_id=pass_id, action='checkin'))
                passport.check_in()
                logger.debug('Checked in pass id %d', passport.pass_id)
                checked_in = True
                flash(CHECKIN_MESSAGE % pass_id, 'success')
            elif request.form.get('checkout') is not None:
                if not passport.checked_in:
                    return redirect(url_for('passport.confirm_transaction',
                                            pass_id=pass_id,
                                            action='checkout'))
                passport.check_out()
                logger.debug('Checked out pass id %d', passport.pass_id)
                checked_out = True
                flash(CHECKOUT_MESSAGE % pass_id, 'success')
            assert checked_in or checked_out
            return redirect(url_for('passport.home'))
        status_code = 406
    return render_template('passport/passport.html',
                           passport=passport, form=form), status_code


def confirm_transaction(pass_id, action):
    assert action in ('checkin', 'checkout')
    passport = Passport.get(pass_id)
    if not passport:
        abort(404)
    if action == ('checkout' if passport.checked_in else 'checkin'):
        abort(406)

    form = ConfirmForm(obj=Passport(pass_id=pass_id),
                       data=dict(check=check(pass_id)))
    if request.method == 'POST' and form.validate():
        if action == 'checkin':
            passport.check_in()
            flash(CHECKIN_MESSAGE % pass_id, 'success')
        else:
            passport.check_out()
            flash(CHECKOUT_MESSAGE % pass_id, 'success')
        return redirect(url_for('passport.home'))
    return render_template('passport/confirm_transaction.html', form=form,
                           passport=passport)


def edit(pass_id):
    passport = Passport.get(pass_id)
    if not passport:
        abort(404)

    form = passport_form_factory(request.values, passport,
                                 current_app.config['FLAGS'],
                                 current_app.config['START_DATE'],
                                 current_app.config['END_DATE'],
                                 checked=False)
    status_code = 200
    if 'POST' == request.method:
        if form.validate():
            form.populate_obj(passport)
            db.session.commit()
            flash('Die Passdaten wurden aktualisert.', 'success')
            return redirect(url_for('passport.passport', pass_id=pass_id))
        else:
            status_code = 406
    return render_template('passport/edit.html', form=form, pass_id=pass_id,
                           flags=current_app.config['FLAGS'].keys()), \
        status_code
