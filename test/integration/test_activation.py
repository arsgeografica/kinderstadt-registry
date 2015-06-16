from flask import url_for
from registry.models import Passport


def test_passport_must_be_activated_first(app):
    client = app.test_client()
    with app.test_request_context():
        post_url = url_for('desk.home')
        expected_url = url_for('desk.activate', pass_id=111, _external=True)

        r = client.post(post_url, data=dict(pass_id=111))

        assert r.status_code == 302
        assert r.headers.get('Location') == expected_url


def test_activation_can_only_be_called_once(app):
    client = app.test_client()
    with app.test_request_context():
        Passport.create('John', 'Doe', 111)

        r = client.get(url_for('desk.activate', pass_id=111))

        assert r.status_code == 404


def test_activated_passport_gets_transaction(app):
    client = app.test_client()
    with app.test_request_context():
        Passport.create('John', 'Doe', 111)

        post_url = url_for('desk.home')
        expected_url = url_for('desk.passport', pass_id=111, _external=True)

        r = client.post(post_url, data=dict(pass_id=111))

        assert r.status_code == 302
        assert r.headers.get('Location') == expected_url
