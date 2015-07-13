from registry.models import Passport, Visit
from registry.extensions import db


def test_sweep_closes_visits(app):
    """Visits are ordered by check_in"""
    with app.test_request_context():
        passport = Passport(surname='John', name='Doe', pass_id=111)
        db.session.add(passport)
        db.session.commit()
        passport.check_in()
        passport.check_out()

        passport = Passport.create('John', 'Doe', 112)
        passport.check_in()

        passport = Passport.create('John', 'Doe', 113)
        passport.check_in()
        passport.check_out()

        passport = Passport.create('John', 'Doe', 114)
        passport.check_in()

        Visit.sweep()

        assert Visit.query.filter(Visit.sweeped == None).count() == 2
        assert Visit.query.filter(
            Visit.sweeped != None, Visit.check_out != None).count() == 2
