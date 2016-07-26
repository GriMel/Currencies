from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        return instance


class Currency(Base):
    """
    Currency base
    """
    __tablename__ = "currencies"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    short_name = Column(String(3))


class CurrencyRate(Base):
    """
    Currency rates base
    """
    __tablename__ = "currency_rates"
    id = Column(Integer, primary_key=True)
    currency_from = Column(ForeignKey('currencies.id'))
    currency_to = Column(ForeignKey('currencies.id'))
    graph_id = Column(Integer)
    url = Column(String)
    default = Column(Boolean, default=False)
    favored = Column(Boolean, default=True)


class Commodity(Base):
    """
    Commodity base
    """
    __tablename__ = "commodities"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)
    graph_id = Column(Integer)
    default = Column(Boolean, default=False)
    favored = Column(Boolean, default=False)
