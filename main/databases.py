from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

association_table = Table('connections', Base.metadata,
    Column('currency_id', Integer, ForeignKey('currency.id')),
    Column('connnection_id', Integer, ForeignKey('right.id'))
)


class Currency(Base):
    """
    Currency base
    """
    __tablename__ = "currencies"
    id = Column(Integer, primary_key=True)
