import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from databases import Base, Currency


class TestCurrency(unittest.TestCase):
    """
    Test Currency database
    """
    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    session = Session()

    def setUp(self):
        """
        """
        Base.metadata.create_all(self.engine)
        curr1 = Currency(1, "US Dollar", "USD", 12)
        curr2 = Currency(1, "Australian Dollar", "AUD", 11)
        curr1.connections.append(curr2)
        self.session.add(curr1)
        self.session.add(curr2)
        self.session.commit()

    def tearDown(self):
        Base.metadata.drop_all(self.engine)
