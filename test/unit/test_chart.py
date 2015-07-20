from datetime import datetime, timedelta, tzinfo
from registry.models import Passport, Visit
from registry.extensions import db


class TZ(tzinfo):

    def utcoffset(self, dt):
        return timedelta(hours=1)

    def tzname(self, dt):
        return "tz"

    def dst(self, dt):
        return timedelta(0)

tz = TZ()


def test_chart_calculates_right_amount(app):
    """chart query calculates correct aggregates"""
    _ = {'pass_id_counter': 0}

    def create_pass():
        _['pass_id_counter'] = _['pass_id_counter'] + 1
        passport = Passport(surname='John', name='Doe',
                            pass_id=_['pass_id_counter'], phone='123', age=7,
                            address='Musterweg')
        db.session.add(passport)
        db.session.commit()
        return passport

    with app.test_request_context():
        passes = [create_pass() for i in range(6)]
        start_ts = datetime(2015, 1, 1, 9, tzinfo=tz)
        cp0 = start_ts.isoformat()
        # IN = 3, OUT = 0
        passes[0].check_in(start_ts + timedelta(minutes=1))
        passes[1].check_in(start_ts + timedelta(minutes=2))
        passes[2].check_in(start_ts + timedelta(minutes=4))
        cp1 = (start_ts + timedelta(minutes=5)).isoformat()
        # IN = 2,  OUT = 0
        passes[3].check_in(start_ts + timedelta(minutes=6))
        passes[4].check_in(start_ts + timedelta(minutes=7))
        passes[0].check_out(start_ts + timedelta(minutes=8))
        cp2 = (start_ts + timedelta(minutes=10)).isoformat()
        # IN = 0, OUT = 1
        passes[1].check_out(start_ts + timedelta(minutes=11))
        passes[2].check_out(start_ts + timedelta(minutes=12))
        passes[3].check_out(start_ts + timedelta(minutes=13))
        passes[4].check_out(start_ts + timedelta(minutes=14))
        cp3 = (start_ts + timedelta(minutes=15)).isoformat()
        # IN = 0, OUT = 4

        bins = Visit.binned(bin_size=5*60)
        chart = {}
        for bin in bins:
            print(bin)
            ts = bin.ts.isoformat()
            if ts not in chart:
                chart[ts] = {'checkin': 0, 'checkout': 0}
            mode = 'checkin' if bin.is_check_in else 'checkout'
            chart[ts][mode] = bin.count
        print(chart)
        # From 0 to 5: 3 in, 0 out
        assert chart[cp0]['checkin'] == 3
        assert chart[cp0]['checkout'] == 0
        # From 5 to 10: 2 in, 0 out
        assert chart[cp1]['checkin'] == 2
        assert chart[cp1]['checkout'] == 0
        # From 10 to 15: 0 in, 1 out
        assert chart[cp2]['checkin'] == 0
        assert chart[cp2]['checkout'] == 1
        # From 15: 0 in, 4 out
        assert chart[cp3]['checkin'] == 0
        assert chart[cp3]['checkout'] == 4
