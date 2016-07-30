# -*- coding: utf-8 -*-
# !/usr/bin/env

import dryscrape
import grequests
import requests
import treq
import json
from time import sleep
from bs4 import BeautifulSoup as bs
from lxml import html
from logger import setLogger
from databases import Base, Currency, CurrencyRate, Commodity, get_or_create
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from twisted.internet import defer, task, reactor

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
        self.init_session()

    def init_session(self):
        """
        """
        loaded = False
        self.session = dryscrape.Session()
        while not loaded:
            try:
                self.session.visit(self.URL)
                loaded = True
            except:
                pass
        # Sometimes there can appear overlapping area
        try:
            overlap = self.session.xpath('//html/body/div[6]/div[2]/div[1]/a')[0]
            overlap.click()
        except:
            pass
        approve = self.session.xpath('//input[@id="terms_and_conds"]')[0]
        approve.left_click()

    def get_graph_id(self, currency_1_name, currency2_name):
        """
        Return graph_id for every pair of currencies
        """
        input_field = self.session.xpath('//input[@id="searchTextWmtTvc"]')[0]
        text = currency_1_name + currency2_name
        input_field.set(text)

        # Wait until popup is shown
        sleep(1)
        got_popup = False
        while not got_popup:
            try:
                element = self.session.xpath('//td[@class="first symbolName"]')[0]
                element.click()
                got_popup = True
            except IndexError:
                sleep(1)

        submit = self.session.xpath('//a[@id="the_submit_button"]')[0]
        submit.left_click()

        # Start retrieving id
        txt = self.session.xpath('//textarea[@id="output"]')[0]
        soup = bs(txt.value(), "lxml")
        src = soup.find('iframe', False)['src']
        element_id = src.split('&')[0].split('=')[-1]
        return element_id


def get_responses(limit):
    """
    """
    url =\
        "http://www.investing.com/currencies/Service/currency?currency_ID={0}"
    rs = (grequests.get(url.format(i),
                        headers=HEADERS) for i in range(limit))
    responses = grequests.map(rs)
    return responses


def collect_soups(responses):
    """
    """
    soups = []
    for response in responses:
        soup = (bs(response.content, "lxml"))
        if not soup('a'):
            continue
        soups.append(soup)
    return soups


def collect_short_rate_names(soups):
    """
    """
    short_rate_names = []
    for soup in soups:
        for row in soup('a'):
            name = row.text
            # Investing sometimes returns '/RUB' or 'USD/'
            if name.startswith("/") or name.endswith("/"):
                continue
            if name not in short_rate_names:
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


def get_short_rate_names_responses(short_rate_names):
    """
    """
    url = "http://www.investing.com/currencies/{}"
    values = [short_name.replace("/", "-") for short_name in short_rate_names]
    rs = (grequests.get(url.format(value), headers=HEADERS)
          for value in values)
    responses = grequests.map(rs)
    return responses


def collect_short_rate_names_trees(responses):
    """
    """
    trees = []
    for response in responses:
        trees.append(html.fromstring(response.content))
    return trees


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


def create_hash_table(trees, short_names):
    """
    """
    hash_table = {}
    for tree, short_name in zip(trees, short_names):
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


def get_graph_id(item):
    """
    """
    value = "".join(item.split("/"))
    url = "http://tvc.forexprostools.com/"\
          "8ffb9c48396938f5fac698799da1cef9/"\
          "1469440167/1/1/7/search?limit=30&"\
          "query={}&type=&exchange="

    response = requests.get(url.format(value), headers=HEADERS).json()[0]
    return response['ticker']


def get_graph_ids(short_rate_names):
    """
    """
    url = "http://tvc.forexprostools.com/"\
          "8ffb9c48396938f5fac698799da1cef9/"\
          "1469440167/1/1/7/search?limit=30&"\
          "query={}&type=&exchange="
    graph_ids = []
    values = ["".join(short.split("/")) for short in short_rate_names]
    responses = []
    left = values[:250]
    while len(left) != 0:
        rs = (grequests.get(url.format(value), headers=HEADERS) for value in left)
        responses.extend(grequests.map(rs))
        print("Proceeded")
        sleep(1)
        values = values[250:]
        left = values[:250]
    for response in responses:
        graph_ids.append(response.json()[0]['ticker'])
    return graph_ids


def create_currencies_tables(tablename, short_names, hash_table):
    """
    Create SQLAlchemy table
    """
    table_engine = 'sqlite:///{}.sqlite3'.format(tablename)
    engine = create_engine(table_engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    for row in short_names:
        short1, short2 = row.split("/")
        name1, name2 = hash_table[short1], hash_table[short2]
        curr1 = get_or_create(session,
                              Currency,
                              name=name1,
                              short_name=short1)
        curr2 = get_or_create(session,
                              Currency,
                              name=name2,
                              short_name=short2)
        url = "http:/investing.com/currencies/{}-{}".format(
            short1.lower(), short2.lower())
        cur_rate = get_or_create(session,
                                 CurrencyRate,
                                 currency_from=curr1.id,
                                 currency_to=curr2.id,
                                 url=url)
    session.commit()


def save_graph_id(response, session, curr1, curr2):
    """
    """
    curr1_row = session.query(Currency).\
        filter(Currency.short_name == curr1).\
        first()
    curr2_row = session.query(Currency).\
        filter(Currency.short_name == curr2).\
        first()
    curr_rate_row = session.query(CurrencyRate).\
        filter(CurrencyRate.currency_from == curr1_row.id).\
        filter(CurrencyRate.currency_to == curr2_row.id).first()
    string = response.decode('utf-8')
    try:
        dictionary = json.loads(string)[0]
        curr_rate_row.graph_id = int(dictionary['ticker'])
    except:
        session.delete(curr_rate_row)


def query(session, curr1, curr2):
    """
    """
    text = curr1 + curr2
    url = 'http://tvc.forexprostools.com/'\
          '8ffb9c48396938f5fac698799da1cef9/'\
          '1469440167/1/1/7/search?limit=30&'\
          'query={}&type=&exchange='.format(text)
    get = treq.get(url, headers=HEADERS)
    get.addCallback(treq.content)
    get.addCallback(save_graph_id, session, curr1, curr2)
    return get


def parallel(session, iterable, count):
    """
    """
    values = [i.split("/") for i in iterable]
    coop = task.Cooperator()
    work = (query(session, curr1, curr2) for curr1, curr2 in values)
    return defer.DeferredList(coop.coiterate(work) for i in range(count))


def graph_id_parser(reactor, curr_short_rate_names):
    """
    """
    table_engine = 'sqlite:///userdb.sqlite3'
    engine = create_engine(table_engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    finished = parallel(session, curr_short_rate_names, 1000)
    finished.addCallback(print)
    session.commit()
    return finished


def main():
    """
    """
    logger = setLogger()
    currencies_responses = get_responses(200)
    logger.debug("Got responses")
    currencies_soups = collect_soups(currencies_responses)
    logger.debug("Got soups")
    curr_short_rate_names = collect_short_rate_names(currencies_soups)
    logger.debug("Collected short rate names")
    short_rate_names_to_parse = prepare_for_parse(curr_short_rate_names)
    logger.debug("Got short rate names to parse")
    short_rate_names_responses = get_short_rate_names_responses(
        short_rate_names_to_parse)
    logger.debug("Got short rate names responses")
    short_rate_names_trees = collect_short_rate_names_trees(
        short_rate_names_responses)
    logger.debug("Collected short rate names trees")
    hash_table = create_hash_table(short_rate_names_trees,
                                   short_rate_names_to_parse)
    logger.debug("Created hash_table")
    create_currencies_tables('userdb',
                             curr_short_rate_names,
                             hash_table,
                             )
    logger.debug("Created currencies table")
    task.react(graph_id_parser, (curr_short_rate_names,))

if __name__ == "__main__":
    main()
