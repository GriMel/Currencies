# -*- coding: utf-8 -*-
# !/usr/bin/env

import requests
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSignal

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1;' +
                  ' WOW64; rv:28.0) Gecko/20100101 Firefox/28.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest'
}


def checkRegions():
    """
    Check if something new appeared
    Have an ideal list and compare to it
    """
    url = "http://www.investing.com/currencies/Service/region?region_ID={}&currency_ID=false"
    regions = {
        "Majors": "majors",
        "Asia/Pasific": 4,
        "Americas": 1,
        "Africa": 8,
        "Middle East": 7,
        "Europe": 6
        }


def main():
    """
    Main module for processing GUI
    """
    url = 'http://www.investing.com/currencies/Service/currency?region_ID={0}&currency_ID={1}'
    region_id = 4
    currency_id = 93
    response = requests.get(url=url.format(region_id, currency_id),
                            headers=HEADERS)

if __name__ == "__main__":

    main()
