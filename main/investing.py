# -*- coding: utf-8 -*-
# !/usr/bin/env

import requests
import re
import dryscrape
from bs4 import BeautifulSoup as bs
from time import sleep
from itertools import product, chain
from logger import setLogger
from databases import Base, engine, Currency, get_or_create
from sqlalchemy.orm import sessionmaker

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


def getCombinations(iterable):
    """
    Changed version of recipe's powerset for product
    """
    s = list(iterable)
    return chain.from_iterable(product(s, repeat=r) for r in range(len(s)+1))


def find_common(string1, string2, splitter):
    """
    Returns common value from two strings
    """
    string = splitter
    match = ""
    index = 0
    # method #1
    while string in string2:
        match = string
        index += 1
        string = " ".join(string1.split(splitter)[:index])
    # method #2
    if not(string2.startswith(match) or string2.endswith(match)):
        set1 = set(string1.split(splitter))
        set2 = set(string2.split(splitter))
        common_words = set1.intersection(set2)
        combinations = getCombinations(common_words)
        for comb in combinations:
            string = " ".join(comb)
            if string2.startswith(string) or string2.endswith(string):
                match = string
    return match


def get_currency_name_old(short_name):
    """
    Returns currency name from short name
    """
    url = "http://www.xe.com/currency/{}"
    response = requests.get(url.format(short_name), headers=HEADERS).content
    soup = bs(response, "lxml")
    return soup.h1.string.split(" - ")[1]


def get_names_from_rate(rate):
    """
    """
    url = "http://www.investing.com/currencies/{}"
    value = re.sub("/", "-", rate)
    response = requests.get(url.format(value), headers=HEADERS).content
    soup = bs(response, "lxml")
    name1 = soup.select('div.right > div > span')[5].text
    name2 = soup.select('div.right > div > span')[7].text
    return name1, name2


def list_of_soups(url, end):
    """
    """
    for currency_id in range(1, end):
        try:
            response = requests.get(url=url.format(currency_id),
                                    headers=HEADERS)
            soup = bs(response.text, "lxml")
            if not soup('a'):
                raise
            yield currency_id, soup
        except:
            print("Exception triggered")


def collect_curr_soups():
    """
    """
    url = 'http://www.investing.com/currencies/Service/currency?currency_ID={0}'
    array = []
    logger = setLogger(name="collector")
    for currency_id, soup in list_of_soups(url, 200):
        cur_rates = [row['title'] for row in soup('a')][:2]
        logger.debug(cur_rates)
        currency_name = find_common(*cur_rates, splitter=' ')
        short_names = [row.text for row in soup('a')[:2]]
        logger.debug(short_names)
        logger.debug(currency_id)
        currency_short_name = find_common(*short_names, splitter='/')
        array.append({'currency_id': currency_id,
                      'currency_name': currency_name,
                      'currency_short_name': currency_short_name,
                      'soup': soup})
    return array


def get_second_currency(currency_rate, currency1):
    """
    Extracts currency name from currency rate
    Example:
        currency_rate:='Panamanian Balboa Australian Dollar'
        currency1:='Australian Dollar'
    We need to extract 'Panamian Balboa'
    """
    if currency_rate.startswith(currency1):
        currency2 = currency_rate.lstrip(currency1)
    else:
        currency2 = currency_rate.rstrip(currency1)
    return currency2


def get_second_short_name(currency_rate_short, short_name1):
    """
    """
    if currency_rate_short.startswith(short_name1):
        short_name2 = currency_rate_short.lstrip(short_name1)
    else:
        short_name2 = currency_rate_short.rstrip(short_name1)
    return short_name2


def create_final_table(array):
    """
    """
    currency_names = [currency['currency_name']
                      for currency in array]
    currency_short_names = [currency['currency_short_name']
                            for currency in array]
    for currency in array:
        currency_name = currency['currency_name']
        currency_short_name = currency['currency_short_name']
        currency_id = currency['currency_id']
        soup = currency['soup']
        for ul in soup('ul'):
            region_name = ul.span.string
            for a in ul('a'):
                curr_rate_name = a['title']
                currency2_name = get_second_currency(cur_rate_name, currency_name)
                currency2_id = "a"


def collect_short_names(limit):
    """
    """
    array = []
    logger = setLogger(name="short_names")
    url = 'http://www.investing.com/currencies/Service/currency?currency_ID={0}'
    for currency_id, soup in list_of_soups(url, 200):
        for row in soup('a'):
            short_name = row.text
            if short_name.startswith("/") or short_name.endswith("/"):
                continue
            array.append(row.text)
            logger.debug("%s %s" %(row.text, currency_id))
    return array


def collect_names(array):
    """
    """
    logger = setLogger(name="hast_table")
    hash_table = {}
    for index, short_name in enumerate(array):
        short1, short2 = short_name.split("/")
        if short1 not in hash_table or short2 not in hash_table:
            name1, name2 = get_names_from_rate(short_name)
        if short1 not in hash_table:
            hash_table[short1] = name1
            logger.debug("%s %s hashed [%s]" % (short1, name1, index))
        if short2 not in hash_table:
            hash_table[short2] = name2
            logger.debug("%s %s hashed [%s]" % (short2, name2, index))
    return hash_table


def fill_table(array, hash_table):
    """
    Create SQLAlchemy table
    """
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    for row in array:
        short1, short2 = row.split("/")
        name1, name2 = hash_table[short1], hash_table[short2]
        curr1 = get_or_create(session, Currency, name=name1, short_name=short1)
        curr2 = get_or_create(session, Currency, name=name2, short_name=short2)
        curr1.right_currencies.append(curr2)
        session.add(curr1)
        session.add(curr2)
    session.commit()


class GraphIDScraper():
    """
    Special class for handling dryscrape's session and
    retrieve a bunch of ids with the same session.
    """
    URL = "http://www.investing.com/webmaster-tools/technical-charts"

    def __init__(self):
        """
        Set url and initialize session
        """
        self.session = None
        self.logger = setLogging("id_scraper")
        self.init_session()

    def init_session(self):
        """
        """
        loaded = False
        self.session = dryscrape.Session()
        self.logger.debug("Dryscrape session initialized")
        while not loaded:
            try:
                self.session.visit(self.URL)
                loaded = True
            except:
                pass
        approve = self.session.xpath('//input[@id="terms_and_conds"]')[0]
        approve.left_click()
        self.logger("Site visited")

    def get_graph_id(self, currency_1, currency2):
        """
        Return graph_id for every pair of currencies
        """
        input_field = self.session.xpath('//input[@id="searchTextWmtTvc"]')[0]
        text = currency_1.short_name + currency2.short_name
        input_field.set(text)
        self.logger.debug("Set {} for input field".format(text))

        # Wait until popup is shown
        sleep(1)
        element = self.session.xpath('//td[@class="first symbolName"]')[0]
        element.click()
        self.logger.debug("Selected element from popup")

        submit = self.session.xpath('//a[@id="the_submit_button"]')[0]
        submit.left_click()
        self.logger.debug("HTML generated")

        # Start retrieving id
        txt = session.xpath('//textarea[@id="output"]')[0]
        soup = bs(txt.value(), "lxml")
        src = soup.find('iframe', False)['src']
        element_id = src.split('&')[0].split('=')[-1]
        return 2



def main():
    """
    Main module for processing GUI
    """
    # url = 'http://www.investing.com/currencies/Service/currency?region_ID={0}&currency_ID={1}
    '''
    for ul in soup('ul'):
        region = {'region_name': ul.span.string}
        if region not in regions:
            regions.append(region)
        for a in ul('a'):
            cur_rate_link = a['href']
            cur_rate_short = a['title']
            cur_rate_full = a.text
    '''

if __name__ == "__main__":

    main()
