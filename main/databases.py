from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

currency_to_currency = Table('currency_to_currency',
                             Base.metadata,
                             Column('left_currency_id',
                                    ForeignKey('currencies.id'),
                                    primary_key=True),
                             Column('right_currency_id',
                                    ForeignKey('currencies.id'),
                                    primary_key=True))


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance

class Currency(Base):
    """
    Currency base
    """
    __tablename__ = "currencies"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    short_name = Column(String(3))
    right_currencies = relationship(
        "Currency",
        secondary=currency_to_currency,
        primaryjoin=id == currency_to_currency.c.left_currency_id,
        secondaryjoin=id == currency_to_currency.c.right_currency_id,
        backref="left_currencies")


class CurrencyRate(Base):
    """
    Currency rates base
    """
    __tablename__ = "rates"
    id = Column(Integer, primary_key=True)
    currency_from = Column(ForeignKey('currencies.id'))
    currency_to = Column(ForeignKey('currencies.id'))
    graph_id = Column(Integer)
