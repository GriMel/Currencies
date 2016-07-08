from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

currency_to_currency = Table('currency_to_currency',
                             Base.metadata,
                             Column('left_currency_id',
                                    ForeignKey('currencies.id'),
                                    primary_key=True),
                             Column('right_currency_id',
                                    ForeignKey('currencies.id'),
                                    primary_key=True))


class Currency(Base):
    """
    Currency base
    """
    __tablename__ = "currencies"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    short_name = Column(String(3))
    region_id = Column(ForeignKey('regions.id'))
    right_currencies = relationship(
        "Currency",
        secondary=currency_to_currency,
        primaryjoin=id == currency_to_currency.c.left_currency_id,
        secondaryjoin=id == currency_to_currency.c.right_currency_id,
        backref="left_currencies")


class Region(Base):
    """
    Region base
    """
    __tablename__ = "regions"
    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    name = Column(String)
