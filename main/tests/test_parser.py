from unittest import TestCase
import dryscrape
from investing import *


class TestParser(TestCase):
    """
    Class for testing parsing results
    """

    def test_find_common_currency_name(self):
        """
        findCommon should return proper currency name
        """
        string1 = "Australian Dollar Ukrainian Hryvna"
        string2 = "US Dollar Australian Dollar"
        string3 = "Australian Dollar US Dollar"
        proper_common = "Australian Dollar"
        current_common = findCommon(string1, string2, string2, splitter=' ')
        self.assertEqual(proper_common, current_common)

    def test_get_second_currency_name(self):
        """
        Should extract proper currency from currency rate
        """
        currency_rate = "Australian Dollar US Dollar"
        currency1 = "US Dollar"
        proper_currency2 = "Australian Dollar"
        currency2 = get_second_currency(currency_rate, currency1)
        self.assertEqual(currency2, proper_currency2)


class TestDryScrape(self):
    """
    Class for testing dryscrape
    """
    URL = "http://www.investing.com/webmaster-tools/technical-charts"

    def __init__(self, *args, **kwargs):
        super(TestDryScrape, self).__init__(*args, **kwargs)
        self.session = dryscrape.Session
        self.init_session()

    def init_session(self):
        """
        """
        loaded = False
        while not loaded:
            try:
                self.session.visit(self.URL)
                loaded = True
            except:
                pass

    def test_dryscrape_success(self):
        """
        Dryscrape should finally return valid information
        """
        pass


if __name__ == '__main__':
    unittest.main(warnings='ignore')
