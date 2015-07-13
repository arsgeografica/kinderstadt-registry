from datetime import datetime, timedelta
from registry.models import Passport
from registry.extensions import db


def test_visits_are_ordered(app):
    """Visits are ordered by check_in"""
    with app.test_request_context():
        passport = Passport(surname='John', name='Doe', pass_id=111,
                            phone='123', age=7, address='Musterweg')
        when = datetime.now()
        passport.check_in(when - timedelta(minutes=10))
        passport.check_out(when - timedelta(minutes=9))
        passport.check_out(when - timedelta(minutes=6))  # Corrupt one
        passport.check_in(when - timedelta(minutes=5))
        passport.check_out(when - timedelta(minutes=4))
        passport.check_in(when - timedelta(minutes=3))
        passport.check_in(when - timedelta(minutes=2))
        passport.check_out(when - timedelta(minutes=0))

        db.session.expire_all()

        passport = Passport.get(111)

        for i in range(0, len(passport.visits) - 1):
            v1 = passport.visits[i]
            v2 = passport.visits[i + 1]
            assert v1.timestamp > v2.timestamp


def test_new_passport_is_inactive(app):
    """Passes with no transaction are not activated"""
    with app.test_request_context():
        passport = Passport(surname='John', name='Doe', pass_id=111,
                            phone='123', age=7, address='Musterweg')
        assert passport.is_active is False


def test_visit_activates_passport(app):
    """Visit activates Passport"""
    with app.test_request_context():
        passport = Passport(surname='John', name='Doe', pass_id=111,
                            phone='123', age=7, address='Musterweg')
        passport.check_in()
        assert passport.is_active is True


def test_check_in_creates_visit(app):
    """Checkin create visit"""
    with app.test_request_context():
        passport = Passport(surname='John', name='Doe', pass_id=111,
                            phone='123', age=7, address='Musterweg')
        passport.check_in()

        db.session.expire_all()

        assert Passport.get(111).visits[0].check_in


def test_check_out_closes_visit(app):
    """Checkin create visit"""
    with app.test_request_context():
        passport = Passport(surname='John', name='Doe', pass_id=111,
                            phone='123', age=7, address='Musterweg')
        passport.check_in()
        passport.check_out()

        db.session.expire_all()

        assert Passport.get(111).visits[0].check_out


def test_is_checked_in_property(app):
    """Check checked_in property works"""
    with app.test_request_context():
        passport = Passport(surname='John', name='Doe', pass_id=111,
                            phone='123', age=7, address='Musterweg')
        assert not passport.checked_in
        passport.check_in()
        assert passport.checked_in
        passport.check_out()
        assert not passport.checked_in


def test_passport_actives_passes_query(app):
    """Check that the Passport's active_passes query method works"""
    with app.test_request_context():
        p1 = Passport(surname='A', name='A', pass_id=111, phone='123', age=7,
                      address='Musterweg')
        p2 = Passport(surname='B', name='B', pass_id=222, phone='123', age=7,
                      address='Musterweg')
        p3 = Passport(surname='C', name='C', pass_id=333, phone='123', age=7,
                      address='Musterweg')

        assert Passport.active_passes().count() == 0
        p1.check_in()
        assert Passport.active_passes().count() == 1
        p2.check_in()
        assert Passport.active_passes().count() == 2
        p3.check_in()
        assert Passport.active_passes().count() == 3
        p1.check_out()
        assert Passport.active_passes().count() == 2
        p3.check_out()
        assert Passport.active_passes().count() == 1
        p2.check_out()
        assert Passport.active_passes().count() == 0
        p1.check_in()
        assert Passport.active_passes().count() == 1
