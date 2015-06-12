from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import Boolean, DateTime, Integer, String
from registry.extensions import db
from datetime import datetime
from uuid import uuid4


class DeactivatedException(Exception):
    pass


class Passport(db.Model):

    """DB representation of a single passport."""

    __tablename__ = 'passport'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    pass_id = Column(Integer, nullable=False, unique=True)
    name = Column(String(length=128), nullable=False)
    surname = Column(String(length=128), nullable=False)
    deactivated = Column(Boolean)

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

    def check_in(self, when=None):
        """Check in passport, creating a new visit

        :param when: timestamp to use for checkin, defaults to datetime.now()
        """
        if self.deactivated:
            raise DeactivatedException

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
        if len(self.visits):
            current_visit = self.visits[-1]
        else:
            current_visit = Visit()
            current_visit.passport = self

        current_visit.check_out = when if when else datetime.now()

    def deactivate(self):
        """Mark passport as deactivated, prohibiting new visits"""
        self.deactivated = True
        db.session.commit()


class Visit(db.Model):

    """DB representation of a single visit."""

    __tablename__ = 'visit'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    passport_id = Column(UUID(as_uuid=True), ForeignKey('passport.id'),
                         index=True)
    check_in = Column(DateTime(timezone=False), index=True)
    check_out = Column(DateTime(timezone=False), index=True)

    passport = relationship('Passport', backref=backref('visits'))

    @property
    def timestamp(self):
        """Property giving timestamp for last visit check in or check out"""
        return self.check_out if self.check_out else self.check_in

    @property
    def is_open(self):
        """Shorthand property to check if visit is still open"""
        return self.check_out is None
