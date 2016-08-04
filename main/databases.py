from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
Base = declarative_base()


def init_session(tablename):
    """
    """
    table_engine = 'sqlite:///{}.sqlite3'.format(tablename)
    engine = create_engine(table_engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.flush()
        return instance

class Region(Base):
    """
    Region base - Europe, North America
    """
    __tablename__ = "regions"
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Country(Base):
    """
    Country base - Italy, France
    """
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    region = Column(ForeignKey('regions.id'))


class Currency(Base):
    """
    Currency base
    """
    __tablename__ = "currencies"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    short_name = Column(String(3))
    country = Column(ForeignKey('countries.id'))


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
