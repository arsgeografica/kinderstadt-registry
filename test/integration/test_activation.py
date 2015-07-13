# -*- coding: utf-8 -*-
import pytest
from flask import url_for
from registry.models import Passport
from registry.extensions import db


@pytest.fixture
def user(request):
    return {
        'pass_id': 111,
        'check': 'u5',
        'surname': 'Heiko',
        'name': 'Bär'
    }


PASS_REQUIREMENTS = {
    None: False,
    'pass_id': True,
    'check': True,
    'surname': True,
    'name': True
}


@pytest.fixture(params=PASS_REQUIREMENTS.items())
def requirement(request):
    return request.param


def test_passport_must_be_activated_first(app):
    client = app.test_client()
    with app.test_request_context():
        post_url = url_for('passport.home')
        expected_url = url_for('passport.activate', pass_id=111,
                               _external=True)

        r = client.post(post_url, data=dict(pass_id=111))

        assert r.status_code == 302
        assert r.headers.get('Location') == expected_url


def test_activation_can_only_be_called_once(app):
    client = app.test_client()
    with app.test_request_context():
        db.session.add(Passport(surname='John', name='Doe', pass_id=111))
        db.session.commit()

        r = client.get(url_for('passport.activate', pass_id=111))

        assert r.status_code == 404


def test_activated_passport_gets_transaction(app):
    client = app.test_client()
    with app.test_request_context():
        db.session.add(Passport(surname='John', name='Doe', pass_id=111))
        db.session.commit()

        post_url = url_for('passport.home')
        expected_url = url_for('passport.passport', pass_id=111,
                               _external=True)

        r = client.post(post_url, data=dict(pass_id=111))

        assert r.status_code == 302
        assert r.headers.get('Location') == expected_url


def test_activation_requirements(app, user, requirement):
    key, required = requirement
    pass_id = user['pass_id']
    client = app.test_client()
    with app.test_request_context():
        post_url = url_for('passport.activate', pass_id=pass_id)
        if required:
            expected_url = url_for('passport.activate', pass_id=pass_id,
                                   _external=True)
            expected_status_code = 406
        else:
            expected_url = url_for('passport.passport', pass_id=pass_id,
                                   _external=True)
            expected_status_code = 302

        user.pop(key, None)
        r = client.post(post_url, data=user)

        assert r.status_code == expected_status_code
        if not required:
            assert r.headers.get('Location') == expected_url
