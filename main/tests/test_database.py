import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from databases import Base, Currency, Region


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
        self.region = Region(number=1, name="Asia")
        self.curr1 = Currency(name="US Dollar",
                              short_name="USD",
                              region_id=self.region.id)
        self.curr2 = Currency(name="Australian Dollar",
                              short_name="AUD",
                              region_id=self.region.id)
        self.curr1.right_currencies.append(self.curr2)
        self.session.add(self.curr1)
        self.session.add(self.curr2)
        self.session.commit()

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def test_query_currency(self):
        expected = [self.curr1, self.curr2]
        result = self.session.query(Currency).all()
        self.assertEqual(result, expected)
