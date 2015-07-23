from registry.models import Passport, Visit
from registry.extensions import db


def test_sweep_closes_visits(app):
    """Visits are ordered by check_in"""
    with app.test_request_context():
        passport = Passport(surname='John', name='Doe', pass_id=111,
                            phone='123', age=7, address='Musterweg')
        db.session.add(passport)
        db.session.commit()
        passport.check_in()
        passport.check_out()

        passport = Passport(surname='John', name='Doe', pass_id=112,
                            phone='123', age=7, address='Musterweg')
        passport.check_in()

        passport = Passport(surname='John', name='Doe', pass_id=113,
                            phone='123', age=7, address='Musterweg')
        passport.check_in()
        passport.check_out()

        passport = Passport(surname='John', name='Doe', pass_id=114,
                            phone='123', age=7, address='Musterweg')
        passport.check_in()

        Visit.sweep()

        assert Visit.query.filter(Visit.sweeped == None).count() == 2
        assert Visit.query.filter(
            Visit.sweeped != None, Visit.check_out != None).count() == 2
