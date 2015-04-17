#! python
#-*-coding:utf-8-*-
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen, Request
from urllib.error import URLError
from decimal import getcontext, Decimal
from time import strftime, sleep, time
from lxml import etree
from pyvirtualdisplay import Display
from selenium import webdriver

from PyQt4 import QtGui, QtCore
#from colorama import Fore, Back, Style, init
#from os.path import isfile

import sys
import re
import webbrowser
from urllib.parse import urlparse
import sqlite3
from os import path
#-------------default lines in systray-----------------------
MAS = ["http://www.investing.com/currencies/eur-rub",       #eur-rub
       "http://www.investing.com/currencies/usd-rub",       #usd-rub
       "http://www.investing.com/commodities/brent-oil"]    #brent
#-------------icons for system tray--------------------------
DOWN = "src/down.png"
UP = "src/up.png"
EQUAL = "src/equal.png"
EXIT = "src/exit.png"
MENU = "src/exchange.png"
#-------------time for update 30 seconds * 1000 milliseconds-
UPDATE_TIME = 30000 
#-------------FOR PARSING INVESTING.COM----------------------
URL_COMMO = "http://www.investing.com/commodities/"
URL_CURR = "http://www.investing.com/currencies/"
headers = {"User-Agent":"Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}
#-------------SQL resources-------
BASE = 'test.db'
SCHEMA = 'schema.sql'

def site_on():
    try:
        response=urlopen('http://investing.com',timeout=1)
        return True
    except URLError as err: pass
    return False

class Investing():
    
    def __init__(self, l=None):
        self.main_list = l
        
    def browser_start(self):
        self.display = Display(visible=0, size=(800, 600))
        print("Starting virtual display...")
        self.display.start()
        print("Display is ON")
        self.browser = webdriver.Firefox()
        print("Virtual browser is ran")
        self.browser.get(URL_CURR)
    
    def browser_stop(self):
        self.browser.close()
        self.display.stop()
        print("Browser has been stopped")
        
    def browser_click(self, id):
        element = self.browser.find_element_by_id(id)
        element.click()
        
    def parse_init(self, url):
        print('url, ', url)
        request = Request(url, headers=headers)
        s = urlopen(request)
        sitePath = s.read()
        parser = etree.HTMLParser()
        self.tree = etree.fromstring(sitePath, parser)
        self.last_id = 1
        self.continent_id = 1
        self.currency_id = 1
        print("Parser is ready")
        
    def parse_curr(self, soup):
        tableClass = "inlineblock alignTop curExpCol"
        titleClass = "curTitle inlineblock bold"
        lengths = []
        titles = []
        lists = []
        
        #getting count for every zone
        for i in soup.findAll("span", {"class":tableClass}):
            for ul in i.findAll('ul'):
                lengths.append(len(ul.findAll('li')))
        
        #getting names of every zone
        for i in soup.findAll("span", {"class":titleClass}):
            titles.append(i.text)
        
        #getting Rate USD/ASD, href, and  Full Name - Austrian Dollars
        for i in soup.findAll("span", {"class" : tableClass}):
            for j in i.select('li > a'):
                print(j)
                href = j.get('href')
                title = j.get('title')
                text = j.text
                dr = {'title' : title, 'href' : href, 'name' : text}
                lists.append(dr)
        
        #create dictionary
        #    {"id" : 1,
        #     "title" : "America",
        #     "content":[{'title':"USD/ASD", 'href' : "http://...", 'name':text},
        #                {'title':"USD/RUB", 'href' : "http://..", 'name':text}]}
        #
        #
        l = self.create_curr_list(titles, lengths, lists)
        return l
        
    def create_curr_list(self, titles, lengths, lists):
        last_id = self.last_id
        rates_list = []
        i = 0
        try:
            for zone in titles:
                print(zone)
                zone_list = []
                num = titles.index(zone)
                j = lengths[num]
                id = last_id + num
                
                for c in range(i, i + j):
                    zone_list.append(lists[c])
                    print(lists[c])
                rates_list.append({"id" : id,"text":zone, "content" : zone_list})
                i += j
        except:
            print("|")
        
        self.last_id = id +1
        assert rates_list    
        return rates_list
    
    def show_curr_list(self, l):
        for elem in l:
            print("id - {}, zone - {}".format(elem.get("id"), elem.get("text")))
            for curr in elem.get('content'):
                print("text : \"{}\", title : \"{}\", href : \"{}\"".format(curr.get('name'), curr.get('title'), curr.get('href')))
    def parse_continents_hor(self):
        self.main_list = []
        for elem in self.tree.xpath('//*[@id="filterBoxExpTabsTop"]'):
            #/html/body/div[7]/section/div[4]/div[1]/ul
            for i in elem:
                text = i.getchildren()[0].text
                elem_id = i.attrib['id']
                self.browser_click(elem_id)
                continent_id = self.continent_id
                self.main_list.append({'id':continent_id, 'name':text, 'content':self.parse_currencies_ver()})
                self.continent_id+=1
                
    def parse_currencies_ver(self):
        currs_list = []
        parser = etree.HTMLParser()
        sitePath = self.browser.page_source
        tree = etree.fromstring(sitePath, parser)
        for elem in tree.xpath('//*[@id="filterBoxTable"]'):
            #//*[@id="filterBoxTable"]
            #/html/body/div[7]/section/div[4]/div[3]/div/div[1]
            for i in elem:
                text = i.getchildren()[1].text
                elem_id = i.attrib['id']
                self.browser_click(elem_id)
                soup = bs(self.browser.page_source)
                currency_id = self.currency_id
                currs_list.append({'id':currency_id, 'name':text, 'content':self.parse_curr(soup)}) #'US Dollar' : []
                self.currency_id +=1 
        return currs_list
    
    def show(self):
        for continent in self.main_list:
            print("id:{}, {}".format(continent.get('id'), continent.get('name')))
            for currency in continent.get('content'):
                print("id:{}, {}".format(currency.get('id'), currency.get('name')))
                rates = currency.get('content')
                self.show_curr_list(rates)         
                
class DataBase():
    
    def __init__(self, name):
        self.name = name
    
    def db_create(self, schema):
        self.schema = schema
        dbIsNew = not path.exists(self.name)
        self.conn = sqlite3.connect(self.name)
        if dbIsNew:
            print("Creating schema")
            with open(self.schema) as f:
                schema = f.read()
            self.conn.executescript(schema)
            print("Schema created")
        else:
            print("Schema already exists")
            print(self.name)
        self.conn.commit()
    
    def add(self, db):
        self.db = db
        with sqlite3.connect(self.name) as conn:
            cur = conn.cursor()
            
            for continent in self.db:
                cur.execute('INSERT INTO Continents VALUES(?,?)',
                            (continent.get('id'), continent.get('name')))
                #print("id:{}, {}".format(continent.get('id'), continent.get('name')))
                currencies = continent.get('content')
                for currency in currencies:
                    cur.execute('INSERT INTO Currencies VALUES(?,?,?)',
                                 (currency.get('id'), currency.get('name'), continent.get('id')))
                    print("id:{}, {}".format(currency.get('id'), currency.get('name')))
                    zones = currency.get('content')
                    for zone in zones:
                        print(zone.get('id'), " zone id")
                        cur.execute('INSERT INTO Zones VALUES (?,?,?,?)',
                                    (zone.get('id'), zone.get('name'), continent.get('id'), currency.get('id')))
                        rates = zone.get('content')
                        for rate in rates:
                            print(rate)
                            print(rate.get('id'))
                            cur.execute('INSERT INTO Rates VALUES (?,?,?,?,?,?,?)',
                                         (rate.get('id'), rate.get('name'), rate.get('title'), rate.get('href'), continent.get('id'), currency.get('id'), zone.get('id')))
            conn.commit()
            print("made commit")
    def db_load(self):
        self.db = []
        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()
            continents = cursor.execute("SELECT * FROM Continents").fetchall()
            rates = cursor.execute("SELECT * FROM Rates").fetchall()
            for continent in continents:
                co_id, co_n = continent[0], continent[1]
                self.db.append({'id' : co_id, "text": co_n, "content":[]})
                currencies = cursor.execute("SELECT * FROM Currencies WHERE ContinentId = ?", (co_id,)).fetchall()
                for currency in currencies:
                    cur_id, cur_n = currency[0], currency[1]
                    self.db[-1]['content'].append({'id':cur_id, 'name':cur_n, 'content':[]})
                    zones = cursor.execute("SELECT * FROM Zones WHERE ContinentId = :co_id AND CurrencyId = :cur_id", {'co_id':co_id, 'cur_id':cur_id}).fetchall()
                    for zone in zones:
                        z_id, z_n = zone[0], zone[1]
                        self.db[-1]['content'][-1]['content'].append({'id':z_id, 'name':z_n, 'content':[]})
                        rates = cursor.execute("SELECT * FROM Rates WHERE ContinentId = :co_id AND CurrencyId = :cur_id AND ZoneId = :z_id", {'co_id':co_id, 'cur_id':cur_id, 'z_id':z_id})
                        for rate in rates:
                            r_id, r_n, r_t, r_href = rate[0], rate[1], rate[2], rate[3]
                            self.db[-1]['content'][-1]['content'][-1]['content'].append({'id':r_id, 'name' : r_n,'title':r_t, 'href':r_href})
            #currencies = cursor.execute("SELECT * FROM Currencies")
            #zones = cursor.execute("SELECT * FROM Zones")
            #rates = cursor.execute("SELECT * FROM Rates")
            #print(continents)
        assert self.db, "Database is empty"
        return self.db
    
    def db_show(self):
        pass
    
#last_last - css selector
class Economic():
    
    def __init__(self, site):
        
        self.headers = {"User-Agent":"Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}
        self.site = site
        self.name = self.get_name()
        self.prev = None
        self.curr = None
        self.currange = None
        self.change = None
    
    def get_name(self):
        '''
        pattern = "/(\w+)"
        name = re.findall(pattern, self.site)[2].upper()
        '''
        name = urlparse(self.site).path.split('/')[2].strip('-oil')
        return name.upper()
    
    def get_value(self):
        request = Request(self.site, headers=self.headers)
        getcontext().prec = 2
        self.curr = Decimal(bs(urlopen(request)).find(id='last_last').text)
        
    def changed(self):
        if not self.prev or self.prev == self.curr:
            self.change = "="
        elif self.curr > self.prev:
            self.change = "↑"
        else: 
            self.change = "↓"
        self.prev = self.curr
    
    def return_string(self):
        try:
            self.get_value()
            self.changed()
        except:
            return None
        return "{:7.3f}   {}".format(self.curr, self.name)

class Picker(QtGui.QWidget):
    
    def __init__(self):
        pass
          
class SysTrayIcon(QtGui.QSystemTrayIcon):
    
    def __init__(self, icon, parent=None):
        super(SysTrayIcon, self).__init__()
        self.setIcon(icon)
        self.menu = QtGui.QMenu(parent)
        self.init_list()
        self.menu.addSeparator()
        
        self.time = QtGui.QAction(self)
        self.time.triggered.connect(self.loop)
        self.menu.addAction(self.time)
        self.menu.addSeparator()
        
        self.exitAction = QtGui.QWidgetAction(self)
        self.exitAction.setIcon(QtGui.QIcon(EXIT))
        self.exitAction.setIconText("Exit")
        self.exitAction.triggered.connect(self.closeEvent)
        self.menu.addAction(self.exitAction)
        self.setContextMenu(self.menu)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.loop)
        self.loop()
        self.activated.connect(self.handle_click)
        
    def handle_click(self, reason):
        
        if reason == QtGui.QSystemTrayIcon.MiddleClick:
            self.closeEvent()
        elif reason == QtGui.QSystemTrayIcon.Trigger:
            
            y = self.geometry().top() - 120
            x = self.geometry().left() - 130
    
            pos = QtCore.QPoint(x, y)
            self.contextMenu().move(pos)
            self.contextMenu().show()
            
    def init_list(self):
        self.a = [Economic(i) for i in MAS]
        site = [i for i in MAS]
        for _, s in zip(self.a, site):
            action = QtGui.QAction(self)
            action.setObjectName(s)
            action.triggered.connect(self.open_site)
            self.menu.addAction(action)
            
    def loop(self):
        if self.timer.isActive(): self.timer.stop()
        for c, w in zip(self.a, self.menu.actions()):
            value = c.return_string()
            if not value: continue
            w.setText(value)
            if c.change == "=":
                #w.setIcon(QtGui.QIcon.fromTheme("face-smirk"))
                w.setIcon(QtGui.QIcon(EQUAL))
            elif c.change == "↑":
                w.setIcon(QtGui.QIcon(UP))
            else:
                w.setIcon(QtGui.QIcon(DOWN))
        self.time.setText(strftime("%H"+":"+"%M"+":"+"%S"))
        self.timer.start(UPDATE_TIME)
        
    def open_site(self):
        webbrowser.open(self.sender().objectName())
        
    def closeEvent(self):
        q = QtGui.QWidget()
        q.setWindowIcon(QtGui.QIcon(EXIT))
        reply = QtGui.QMessageBox.question(q, 'Message', 'Are you sure to quit?', QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            QtGui.QApplication.quit()

def test_show():
    i = Investing()
    titles = ['America', 'Europe', 'Asia']
    lengths = [1,2,3]
    last_id = 1
    lists = [{'title' : "USD/ASD", 'href' : "http://inv.com/usd-asd", 'name' : "US dollar-Aus dollar"},
             {'title' : "USD/EUR", 'href' : "http://inv.com/usd-eur", 'name' : "US dollar-Euro"},
             {'title' : "GBP/EUR", 'href' : "http://inv.com/gbp-eur", 'name' : "Pound - Euro"},
             {'title' : "CHY/EUR", 'href' : "http://inv.com/chy-eur", 'name' : "Chinese Yen - Euro"},
             {'title' : "CHY/USD", 'href' : "http://inv.com/chy-usd", 'name' : "Chinese Yen - US dollar"},
             {'title' : "CHY/GBP", 'href' : "http://inv.com/chy-gbp", 'name' : "Chinese Yen - Pound"}]
    l = i.create_curr_list(titles, lengths, lists, last_id)
    i.show_curr_list(l)
    
def test_db():
    test_db = [{"id" : 1,
                "text":"Majors",
                "content":[
                           {"id":1, 
                            "text":"European Euro", 
                            "content":[
                                       {"id":1,
                                        "text":"Pacific",
                                        "content":[{"text": "AUD/UAH", 
                                                    "title" : "Australian Dollar Ukrainian Hryvnia",
                                                    "href" : "http://www.investing.com/currencies/aud-uah"},
                                                   {"text" : "USD/UAH", 
                                                    "title" : "US Dollar Ukrainian Hryvnia",
                                                    "href" : "http://www.investing.com/currencies/usd-uah"}]},
                                        {"id":2,
                                        "text":"Central America",
                                        "content":[{"text" : "UAH/RUB", 
                                                    "title" : "Ukrainian Hryvnia Russian Ruble", 
                                                    "href" : "http://www.investing.com/currencies/uah-rub"},
                                                   {"text":"DKK/UAH",
                                                    "title" : "Danish Krone Ukrainian Hryvnia",
                                                    "href" : "http://www.investing.com/currencies/dkk-uah"}]}]},
                           {"id":2,
                            "text":"US Dollar",
                            "content":[
                                       {"id":3,
                                        "text":"South America",
                                        "content":[{"text" : "TRY/OMR",
                                                    "title" : "Turkish Lira Omani Rial",
                                                    "href" : "http://www.investing.com/currencies/try-omr"},
                                                   {"text" : "TRY/BHD",
                                                    "title" : "Turkish Lira Baharain Dinar",
                                                    "href" : "http://www.investing.com/currencies/try-bhd"}]}]}]}]
    
    d = DataBase(BASE,test_db)
    d.db_create(SCHEMA)
    d.add(test_db)
    
    
def main():
    app = QtGui.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    #style = app.style()
    icon = QtGui.QIcon(MENU)
    trayIcon = SysTrayIcon(icon)
    trayIcon.show()
    trayIcon.showMessage("Биржа",strftime("%H"+":"+"%M"+":"+"%S"), 1000)
    sys.exit(app.exec_())

def parse_add_show():
    i = Investing()
    i.browser_start()
    i.parse_init(URL_CURR)
    try:
        i.parse_continents_hor()
    except:
        i.browser_stop()
        print("Parsing went wrong")
        sys.exit()
    finally:
        print("PARSER FINISHED")
        sleep(3)
        
    try:
        d = DataBase(BASE)
        d.db_create(SCHEMA)
        d.add(i.main_list)
    except:
        print("Creating database went wrong")
        sys.exit()
    finally:
        print("DATABASE CREATED")
        sleep(3)
        
    l = d.db_load()
    i = Investing(l)
    i.show()
    print("DONE")
    
def parse():
    start = time()
    i = Investing()
    i.browser_start()
    i.parse_init(URL_CURR)
    try:
        i.parse_continents_hor()
        i.show()
    except:
        i.browser_stop()
        print("Something WENT WRONG")
    
    d = DataBase(BASE, i.main_list)
    d.db_create()
    d.add()
    
    print(time()-start, " seconds passed for execution")
    
def test_pars():
    url = "http://www.investing.com/currencies/"
    request = Request(url, headers=headers)
    s = urlopen(request)
    sitePath = s.read()
    parser = etree.HTMLParser()
    tree = etree.fromstring(sitePath, parser)
    for elem in tree.xpath('//*[@id="filterBoxExpTabsTop"]'):
        for i in elem:
            text = i.getchildren()[0].text
            elem_id = i.attrib['id']
            print(text, id)
    print("DOne")
    #//*[@id="filterBoxExpTabsTop"]
    
def test_load():
    d = DataBase(BASE)
    d.db_load()
    l = d.db_load()
    i = Investing(l)
    i.show()

if __name__ == "__main__":
    #test()
    #main()
    #parse()
    test_load()
    #test_pars()
    #test_db()