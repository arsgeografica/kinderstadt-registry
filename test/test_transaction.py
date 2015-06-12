import pytest
from datetime import datetime, timedelta
from registry.models import Passport, DeactivatedException


def test_visits_are_ordered(app):
    """Visits are ordered by check_in"""
    with app.test_request_context():
        p1 = Passport.create('John', 'Doe', 111)
        when = datetime.now()
        p1.check_in(when - timedelta(minutes=10))
        p1.check_out(when - timedelta(minutes=9))
        p1.check_in(when - timedelta(minutes=8))
        p1.check_out(when - timedelta(minutes=7))
        p1.check_out(when - timedelta(minutes=6))  # Corrupt one
        p1.check_in(when - timedelta(minutes=5))
        p1.check_out(when - timedelta(minutes=4))

        p2 = Passport.query.get(p1.id)

        for i in range(0, len(p2.visits) - 1):
            v1 = p2.visits[i]
            v2 = p2.visits[i + 1]

            assert v1.timestamp < v2.timestamp


def test_new_passport_is_inactive(app):
    """Passes with no transaction are not activated"""
    with app.test_request_context():
        passport = Passport.create('John', 'Doe', 111)
        assert passport.is_active is False


def test_visit_activates_passport(app):
    """Visit activates Passport"""
    with app.test_request_context():
        passport = Passport.create('John', 'Doe', 111)
        passport.check_in()
        assert passport.is_active is True


def test_deactivated_pass_cannot_check_in(app):
    """Deactivated pass cannot be checked in"""
    with app.test_request_context():
        passport = Passport.create('Bad John', 'Doe', 111)
        passport.deactivate()
        with pytest.raises(DeactivatedException):
            passport.check_in()
