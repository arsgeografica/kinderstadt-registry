from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.types import Boolean, DateTime, Integer, String
from registry.extensions import db


class Passport(db.Model):
    """DB representation of a single passport."""

    __tablename__ = 'passport'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=128), nullable=False)
    surname = Column(String(length=128), nullable=False)
    deactivated = Column(Boolean)


class Transaction(db.Model):
    """DB representation of a single transaction."""

    __tablename__ = 'transaction'

    id = Column(Integer, primary_key=True)
    passport_id = Column(Integer, ForeignKey('passport.id'))
    timestamp = Column(DateTime(timezone=False))
    action = Column(ENUM('IN', 'OUT', name='transaction_action'))

    passport = relationship('Passport', backref=backref('transactions'),
                            order_by=timestamp)
