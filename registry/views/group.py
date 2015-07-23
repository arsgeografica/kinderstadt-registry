# -*- encoding: utf8 -*-
from flask import flash, redirect, render_template, request, url_for
from flask.ext.wtf import Form
from sqlalchemy.exc import IntegrityError
from registry.models import Group, Passport
from registry.forms import GroupForm
from registry.extensions import db
from registry.utils import pass_spec_builder, pass_spec_parser
from registry.fields import MultiPassportField


def index():
    groups = Group.query.order_by(Group.name).all()
    return render_template('group/index.html', groups=groups)


def edit(group_id=None):
    if group_id is None:
        group = Group()
    else:
        group = Group.query.get_or_404(group_id)

    passport_ids = pass_spec_builder([p.pass_id for p in group.passports])

    form = GroupForm(request.values, obj=group,
                     data=dict(passport_ids=passport_ids.replace(',', ', ')))
    status_code = 200
    if 'POST' == request.method:
        _pass_ids = pass_spec_parser(form.passport_ids.data)
        passports = Passport.query.filter(
            Passport.pass_id.in_(_pass_ids)).all()
        error = False
        error_msg = 'Pass <em>%d</em> gehört zu einer anderen Gruppe.'
        for passport in passports:
            if passport.group and passport.group != group:
                error = True
                flash(error_msg % passport.pass_id, 'danger')

        if form.validate() and not error:
            form.populate_obj(group)
            group.passports = passports
            try:
                db.session.add(group)
                db.session.commit()
                flash('Die Gruppe %s wurde gespeichert' % group.name,
                      'success')
                return redirect(url_for('group.index'))
            except IntegrityError:
                db.session.rollback()
                form.name.errors.append('Dieser Name ist bereits vergeben.')
        status_code = 406
    return render_template('group/edit.html',
                           form=form, group=group), status_code


def check_in(group_id):
    return transaction(group_id, 'check_in')


def check_out(group_id):
    return transaction(group_id, 'check_out')


def transaction(group_id, action):
    group = Group.query.get_or_404(group_id)
    passport_field = MultiPassportField(group.passports)

    class F(Form):
        pass
    setattr(F, 'passports', passport_field)

    form = F(request.values)
    status_code = 200
    if 'POST' == request.method:
        if form.validate():
            count = 0
            for passport in group.passports:
                if passport.pass_id not in form.passports.data:
                    continue
                if 'check_in' == action:
                    passport.check_in(commit=False)
                else:
                    passport.check_out(commit=False)
                count = count + 1
            db.session.commit()
            action = 'eingecheckt' if action == 'check_in' else 'ausgecheckt'
            flash('Es wurden %d Pässe %s' % (count, action), 'success')
            return redirect(url_for('home'))
        status_code = 406
    return render_template('group/transaction.html',
                           form=form, action=action), status_code
