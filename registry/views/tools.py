from flask import render_template, request
from registry.forms import CheckIdForm, check


def index():
    return render_template('tools/index.html')


def check_id():
    check_id = None
    form = CheckIdForm(request.values, csrf_enabled=False)
    if form.validate():
        pass_id = form.pass_id.data
        check_id = check(pass_id)
    return render_template('tools/check-id.html', form=form, check_id=check_id)
