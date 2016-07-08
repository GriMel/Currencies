from unittest import TestCase
from main import *


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


if __name__ == '__main__':
    unittest.main(warnings='ignore')
