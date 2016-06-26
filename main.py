# -*- coding: utf-8 -*-
# !/usr/bin/env

import requests
import re
from bs4 import BeautifulSoup as bs
from time import sleep
from itertools import product

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


def findCommon(string1, string2):
    """
    Function to retrieve the current processing currency
    """
    set1 = set(string1.split(' '))
    set2 = set(string2.split(' '))
    common_words = set1.intersection(set2)
    count_of_words = len(common_words)
    # Idea
    # ('A', 'B')
    # product generates ('A', 'A'), ('B', 'B')
    # By calling set(combination) we leave only unique combinations
    combinations = [combination for combination in
                    product(common_words, repeat=count_of_words)
                    if len(set(combination)) == count_of_words]
    # Retrieve the currency by checking exact
    # string in string1
    for comb in combinations:
        string = " ".join(comb)
        if re.search(string, string1):
            return string


def main():
    """
    Main module for processing GUI
    """
    # url = 'http://www.investing.com/currencies/Service/currency?region_ID={0}&currency_ID={1}'
    url2 = 'http://www.investing.com/currencies/Service/currency?currency_ID={0}'
    array = []
    regions = []
    for currency_id in range(1, 3):
        subarray = []
        try:
            response = requests.get(url=url2.format(currency_id),
                                    headers=HEADERS)
            soup = bs(response.text, "lxml")
            string1, string2 = soup('a')[:2]
            currency_name = findCommon(string1, string2)
            for ul in soup('ul'):
                items = [{'link': a['href'],
                          'title': a['title'],
                          'name': a.text} for a in ul('a')]
                region_name = ul.span_string
                region = {'region_name': region_name,
                          'currencies': []}

                for a in ul('a'):
                    link = a['href']
                    title = a['title']
                    name = a.text
                subarray.append({'region': region,
                                 'items': items
                                 })
        except:
            pass
        array.append({'currency_id': currency_id,
                      'currency_name': currency_name,
                      'items': subarray})


if __name__ == "__main__":

    main()
