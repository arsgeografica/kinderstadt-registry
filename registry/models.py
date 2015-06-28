import logging
from sqlalchemy import ForeignKey
from sqlalchemy.sql import desc, text
from sqlalchemy.sql.expression import func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import DateTime, Integer, String
from registry.extensions import db
from datetime import datetime
from uuid import uuid4


class Passport(db.Model):

    """DB representation of a single passport."""

    __tablename__ = 'passport'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    pass_id = Column(Integer, nullable=False, unique=True)
    name = Column(String(length=128), nullable=False)
    surname = Column(String(length=128), nullable=False)

    visits = relationship('Visit', backref=backref('passport'),
                          order_by='desc(Visit.timestamp)')

    @classmethod
    def create(cls, surname, name, pass_id):
        """Factory method to save a passport to the database.

        :param surname: Surname to store
        :param name: Name to store
        :param pass_id: Pass ID to store
        :returns: Passport object
        """
        p = cls()
        p.surname = surname
        p.name = name
        p.pass_id = pass_id

        db.session.add(p)
        db.session.commit()

        return p

    @property
    def is_active(self):
        """Property indicating whether the passport has any visits at all"""
        return len(self.visits) > 0

    @property
    def checked_in(self):
        return len(self.visits) > 0 and not self.visits[0].check_out

    def check_in(self, when=None):
        """Check in passport, creating a new visit

        :param when: timestamp to use for checkin, defaults to datetime.now()
        """
        visit = Visit()
        visit.passport = self
        visit.check_in = when if when else datetime.now()

        db.session.add(visit)
        db.session.commit()

        return visit

    def check_out(self, when=None):
        """Check out passport.

        This either closes the last visit or creates a new visit with only
        an checkout time.

        :param when: timestamp to use for checkout, defaults to datetime.now()
        """
        if len(self.visits) and not self.visits[0].check_out:
            current_visit = self.visits[0]
        else:
            current_visit = Visit()
            current_visit.passport = self

        current_visit.check_out = when if when else datetime.now()

        db.session.commit()

        return current_visit

    @classmethod
    def get(cls, pass_id):
        try:
            return cls.query.filter(cls.pass_id == pass_id).one()
        except:
            msg = 'Non-unique query result for pass_id "%d"' % pass_id
            logger = logging.getLogger(__name__)
            logger.exception(msg)

    @classmethod
    def active_passes(cls):
        last_visits = db.session.query(
            Visit,
            func.row_number().over(
                partition_by=Visit.passport_id,
                order_by=desc(Visit.timestamp)).label('row_number')) \
            .subquery('lv')
        open_visits = db.session.query(Visit) \
                        .select_entity_from(last_visits) \
                        .filter(last_visits.c.row_number == 1) \
                        .filter(last_visits.c.check_out == None) \
                        .subquery()

        open_passports = db.session.query(Passport).join(open_visits)

        return open_passports


class Visit(db.Model):

    """DB representation of a single visit."""

    __tablename__ = 'visit'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    passport_id = Column(UUID(as_uuid=True), ForeignKey('passport.id'),
                         index=True)
    check_in = Column(DateTime(timezone=False), index=True)
    check_out = Column(DateTime(timezone=False), index=True)

    @hybrid_property
    def timestamp(self):
        """Property giving timestamp for last visit check in or check out"""
        return self.check_out if self.check_out else self.check_in

    @timestamp.expression
    def timestamp(cls):
        return text('GREATEST(%s, %s)' % (cls.check_in, cls.check_out))

    @property
    def is_open(self):
        """Shorthand property to check if visit is still open"""
        return self.check_out is None
