from flask import url_for
from registry.models import Passport
from registry.forms import check


def test_transaction_confirm_stops_with_406_if_no_default(app):
    client = app.test_client()
    with app.test_request_context():
        passport = Passport.create('John', 'Doe', 111)

        def confirm(pass_id, action):
            return client.get(url_for('desk.confirm_transaction',
                                      pass_id=pass_id, action=action))

        passport.check_in()
        r = confirm(passport.pass_id, 'checkout')
        assert r.status_code == 406


def test_non_default_transaction_needs_confirmation(app):
    client = app.test_client()
    with app.test_request_context():
        passport = Passport.create('John', 'Doe', 111)

        def transaction(pass_id, action):
            data = dict(pass_id=pass_id, check=check(pass_id))
            data[action] = True
            return client.post(url_for('desk.passport', pass_id=pass_id),
                               data=data)

        def confirm(pass_id, action):
            data = dict(pass_id=pass_id, check=check(pass_id))
            return client.post(url_for('desk.confirm_transaction',
                                       pass_id=pass_id, action=action),
                               data=data)

        # First checkin
        r = transaction(passport.pass_id, 'checkin')
        assert r.status_code == 302
        assert r.headers.get('Location') == url_for('desk.home',
                                                    _external=True)

        # Second checkin, must be confirmed
        r = transaction(passport.pass_id, 'checkin')
        assert r.status_code == 302
        assert r.headers.get('Location') == url_for('desk.confirm_transaction',
                                                    pass_id=passport.pass_id,
                                                    action='checkin',
                                                    _external=True)
        # Confirm
        r = confirm(passport.pass_id, 'checkin')
        assert r.status_code == 302
        assert r.headers.get('Location') == url_for('desk.home',
                                                    _external=True)

        # Checkout, back to normal
        r = transaction(passport.pass_id, 'checkout')
        assert r.status_code == 302
        assert r.headers.get('Location') == url_for('desk.home',
                                                    _external=True)

        # Checkout again, must be confirmed
        r = transaction(passport.pass_id, 'checkout')
        assert r.status_code == 302
        assert r.headers.get('Location') == url_for('desk.confirm_transaction',
                                                    pass_id=passport.pass_id,
                                                    action='checkout',
                                                    _external=True)
        # Confirm
        r = confirm(passport.pass_id, 'checkout')
        assert r.status_code == 302
        assert r.headers.get('Location') == url_for('desk.home',
                                                    _external=True)
