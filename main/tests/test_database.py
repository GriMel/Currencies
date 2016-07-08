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
    TEST_CURR_1 = Currency(1, "US Dollar", "USD", 12)
    TEST_CURR_2 = Currency(1, "Australian Dollar", "AUD", 11)

    def setUp(self):
        """
        """
        Base.metadata.create_all(self.engine)
        curr1 = self.TEST_CURR_1
        curr2 = self.TEST_CURR_2
        curr1.connections.append(curr2)
        self.session.add(curr1)
        self.session.add(curr2)
        self.session.commit()

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def test_query_currency(self):
        expected = [self.TEST_CURR_1, self.TEST_CURR_2]
        result = self.session.query(Currency).all()
        self.assertEqual(result, expected)
