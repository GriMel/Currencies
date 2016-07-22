# -*- coding: utf-8 -*-
# !/usr/bin/env

import grequests
import requests
from bs4 import BeautifulSoup as bs
from lxml import html
from logger import setLogger
from databases import Base, Currency, get_or_create
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1;' +
                  ' WOW64; rv:28.0) Gecko/20100101 Firefox/28.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest'
}


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
        return element_id


def get_responses(url, limit):
    """
    """
    rs = (grequests.get(url.format(i),
                        headers=HEADERS) for i in range(limit))
    responses = grequests.map(rs)
    return responses


def collect_soups(responses):
    """
    """
    soups = []
    for response in responses:
        soups.append(bs(response.content, "lxml"))
    return soups


def collect_short_rate_names(soups):
    """
    """
    short_rate_names = []
    for soup in soups:
        if not soup('a'):
            continue
        for row in soup('a'):
            name = row.text
            # Investing sometimes returns '/RUB' or 'USD/'
            if name.startswith("/") or name.endswith("/"):
                continue
            short_rate_names.append(name)
    return short_rate_names


def prepare_for_parse(short_rate_names):
    """
    Given an array of currency pairs returns
    array of unique pairs
    """
    unique_short_rate_names = []
    to_parse = []
    for row in short_rate_names:
        append = False
        first, second = row.split("/")
        if first not in unique_short_rate_names:
            unique_short_rate_names.append(first)
            append = True
        if second not in unique_short_rate_names:
            unique_short_rate_names.append(second)
            append = True
        if append:
            to_parse.append(row)
    return to_parse


def get_short_rate_name_responses(short_rate_names):
    """
    """
    url = "http://www.investing.com/currencies/{}"
    values = [short_name.replace("/", "-") for short_name in short_rate_names]
    rs = (grequests.get(url.format(value), headers=HEADERS)
          for value in values)
    responses = grequests.map(rs)
    return responses


def return_proper_name(tree, bad_name, other_name):
    """
    Check if name, retrieved from tree doesn't end up with '...'
    Otherwise retrieves it from tree
    """
    title = tree.cssselect('h1')[0].text.split(" - ")[1]
    part_name = bad_name.rstrip(" ...")
    other_name = other_name.rstrip(" ...")
    parts = title.split(part_name)
    name = ""
    if not parts[0]:
        other_index = parts[1].find(other_name)
        name = part_name + " " + parts[1][:other_index].strip(" ")
    else:
        name = part_name + " " + parts[1].strip(" ")
    return name


def return_page_tree(currency_rate):
    """
    Return tree of currency rate's page
    :currency_rate - AUD/USD
    """
    url = "http://www.investing.com/currencies/{}"
    value = currency_rate.replace("/", "-")
    response = requests.get(url.format(value), headers=HEADERS)
    return html.fromstring(response.content)


def create_hash_table(responses, short_names):
    """
    """
    hash_table = {}
    for response, short_name in zip(responses, short_names):
        tree = html.fromstring(response.content)
        name1 = tree.cssselect('div.right > div > span')[5].text
        name2 = tree.cssselect('div.right > div > span')[7].text
        if name1.endswith("..."):
            name1 = return_proper_name(tree, name1, name2)
        if name2.endswith("..."):
            name2 = return_proper_name(tree, name2, name1)
        short_name1 = short_name.split("/")[0]
        short_name2 = short_name.split("/")[1]
        hash_table[short_name1] = name1
        hash_table[short_name2] = name2
        print("{} - {}".format(name1, short_name1))
        print("{} - {}".format(name2, short_name2))
    return hash_table


def create_table(tablename, short_names, hash_table):
    """
    Create SQLAlchemy table
    """
    table_engine = 'sqlite:///{}.sqlite3'
    engine = create_engine(table_engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    for row in short_names:
        short1, short2 = row.split("/")
        name1, name2 = hash_table[short1], hash_table[short2]
        curr1 = get_or_create(session, Currency, name=name1, short_name=short1)
        curr2 = get_or_create(session, Currency, name=name2, short_name=short2)
        curr1.right_currencies.append(curr2)
        session.add(curr1)
    session.commit()


def main():
    """
    """
    pass

if __name__ == "__main__":
    main()
