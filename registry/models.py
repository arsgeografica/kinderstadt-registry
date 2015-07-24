import logging
from flask import current_app
from flask.ext.sqlalchemy import BaseQuery
from sqlalchemy import ForeignKey
from sqlalchemy.sql import desc, text
from sqlalchemy.sql.expression import func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.types import Boolean, DateTime, Integer, String, Text
from sqlalchemy_utils.types import TSVectorType
from sqlalchemy_searchable import SearchQueryMixin
from registry.extensions import db
from datetime import datetime
from uuid import uuid4


class PassportQuery(BaseQuery, SearchQueryMixin):
    pass


class Passport(db.Model):

    """DB representation of a single passport."""

    __tablename__ = 'passport'
    query_class = PassportQuery

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    pass_id = Column(Integer, nullable=False, unique=True)
    name = Column(String(length=128), nullable=False)
    surname = Column(String(length=128), nullable=False)
    age = Column(Integer, nullable=False)
    address = Column(Text())
    phone = Column(String(length=128), nullable=False)
    email = Column(String(length=128))
    notes = Column(Text())
    flags = Column(MutableDict.as_mutable(JSONB))
    infos_wanted = Column(Boolean, default=False)
    photos_allowed = Column(Boolean, default=False)
    lexemes = Column(TSVectorType('surname', 'name', regconfig='german'),
                     nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey('group.id'))

    visits = relationship('Visit', backref=backref('passport'),
                          order_by='desc(Visit.timestamp)')

    def __to_dict__(self):
        return dict(
            id=str(self.id),
            pass_id=self.pass_id,
            name=self.name,
            surname=self.surname,
            age=self.age,
            address=self.address,
            phone=self.phone,
            email=self.email,
            notes=self.notes,
            flags=self.flags,
            infos_wanted=self.infos_wanted,
            photos_allowed=self.photos_allowed,
            group_id=str(self.group_id))

    @property
    def is_active(self):
        """Property indicating whether the passport has any visits at all"""
        return len(self.visits) > 0

    @property
    def checked_in(self):
        return len(self.visits) > 0 and not self.visits[0].check_out

    def check_in(self, when=None, commit=True):
        """Check in passport, creating a new visit

        :param when: timestamp to use for checkin, defaults to datetime.now()
        """
        visit = Visit()
        visit.passport = self
        visit.check_in = when if when else datetime.now()

        db.session.add(visit)
        if commit:
            db.session.commit()

        return visit

    def check_out(self, when=None, commit=True):
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

        if commit:
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

    def __repr__(self):
        return u'<Passport (%r)>' % self.pass_id


class Visit(db.Model):

    """DB representation of a single visit."""

    __tablename__ = 'visit'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    passport_id = Column(UUID(as_uuid=True), ForeignKey('passport.id'),
                         index=True)
    check_in = Column(DateTime(timezone=False), index=True)
    check_out = Column(DateTime(timezone=False), index=True)
    sweeped = Column(Boolean, nullable=True)

    def __to_dict__(self):
        return dict(
            id=str(self.id),
            passport_id=str(self.passport_id),
            check_in=self.check_in.isoformat() if self.check_in else None,
            check_out=self.check_out.isoformat() if self.check_out else None,
            sweeped=self.sweeped)

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

    @classmethod
    def sweep(cls):
        Visit.query \
            .filter(Visit.check_out == None) \
            .update({Visit.sweeped: True, Visit.check_out: datetime.now()})
        db.session.flush()
        db.session.commit()

    @classmethod
    def binned(cls, bin_size=None):
        if not bin_size:
            bin_size = current_app.config['CHART_BIN_SIZE']

        sql = """
        WITH checks AS (
            SELECT
                True AS is_check_in,
                ts_round(check_in, %(bin_size)s) AS ts
            FROM
                visit
            WHERE
                check_in IS NOT NULL
            UNION ALL
            SELECT
                False AS is_check_in,
                ts_round(check_out + interval '%(bin_size)s seconds', %(bin_size)s) AS ts
            FROM
                visit
            WHERE
                check_out IS NOT NULL
        )
        SELECT
            ts,
            is_check_in,
            count(*)
        FROM
            checks
        GROUP BY is_check_in, ts
        ORDER BY ts ASC
        """
        result = db.engine.execute(sql, bin_size=bin_size)
        return result.fetchall()


class Group(db.Model):
    __tablename__ = 'group'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(length=128), nullable=False, unique=True)
    flags = Column(JSONB)
    passports = relationship(Passport, backref='group')

    def __to_dict__(self):
        return dict(
            id=str(self.id),
            name=self.name,
            flags=self.flags)


def commit_model(cls, *args, **kwargs):
    model = cls(*args, **kwargs)
    db.session.add(model)
    db.session.commit()
    return model
