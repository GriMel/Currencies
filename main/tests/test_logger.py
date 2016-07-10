import logging
from log_conf import setLogger
from testfixtures import LogCapture, Comparison as C, compare
from unittest import TestCase
from os import remove


class TestLogger(TestCase):
    """
    Main test for testing logging
    """
    TEST_FILE = "test.out"

    def setUp(self):
        """
        """
        self.logger = setLogger(name='main',
                                log_file=self.TEST_FILE)
        self.level = self.logger.level
        self.log_capture = LogCapture()

    def tearDown(self):
        """
        Remove test logging file
        """
        remove(self.TEST_FILE)
        self.logger.level = self.level
        del(self.log_capture)

    def test_basic_configuration(self):
        """
        Everything is configured properly
        """
        compare([
            C('logging.StreamHandler',
              formatter=C('logging.Formatter',
                          _fmt='%(message)s',
                          strict=False),
              level=logging.INFO,
              strict=False),
            C('logging.FileHandler',
              formatter=C('logging.Formatter',
                          _fmt='%(asctime)s :: %(name)s - %(message)s',
                          strict=False),
              level=logging.DEBUG,
              strict=False)], self.logger.handlers)
