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

MAS = ["http://www.investing.com/currencies/eur-rub",       #eur-rub
       "http://www.investing.com/currencies/usd-rub",       #usd-rub
       "http://www.investing.com/commodities/brent-oil"]    #brent

DOWN = "src/down.png"
UP = "src/up.png"
EQUAL = "src/equal.png"
EXIT = "src/exit.png"
MENU = "src/exchange.png"
UPDATE_TIME = 30000 # 30 seconds * 1000 milliseconds
#-------------FOR PARSING INVESTING.COM--------------
URL_COMMO = "http://www.investing.com/commodities/"
URL_CURR = "http://www.investing.com/currencies/"
headers = {"User-Agent":"Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}

BASE_NAME = 'test.db'

def site_on():
    try:
        response=urlopen('http://investing.com',timeout=1)
        return True
    except URLError as err: pass
    return False

class Investing():
    
    def __init__(self):
        self.last_id = 1
        
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
        request = Request(url, headers=headers)
        s = urlopen(request)
        sitePath = s.read()
        parser = etree.HTMLParser()
        self.tree = etree.fromstring(sitePath, parser)
        
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
                href = j.get('href')
                title = j.get('title')
                text = j.text
                dr = {'title' : title, 'href' : href, 'text' : text}
                lists.append(dr)
        
        #create dictionary
        #    {"id" : 1,
        #     "title" : "America",
        #     "content":[{'title':"USD/ASD", 'href' : "http://...", 'text':text},
        #                {'title':"USD/RUB", 'href' : "http://..", 'text':text}]}
        #
        #
        l = self.create_curr_list(titles, lengths, lists, last_id)
        return l
        
    def create_curr_list(self, titles, lengths, lists, last_id):
        rates_list = []
        i = 0
        try:
            for zone in titles:
                zone_list = []
                num = titles.index(zone)
                j = lengths[num]
                id = last_id + num
                
                assert i < j
                for c in range(i, i + j):
                    zone_list.append(lists[c])
                rates_list.append({"id" : id,"zone":zone, "content" : zone_list})
                i = j
        except:
            print("Done")
        
        assert rates_list    
        return rates_list
    
    def show_curr_list(self, l):
        for elem in l:
            print("id - {}, zone - {}".format(elem.get("id"), elem.get("zone")))
            for curr in elem.get('content'):
                print("text - {}, title - {}, link = {}".format(curr.get('text'), curr.get('title'), curr.get('href')))
            
    def parse_continents_hor(self):
        self.main_list = []
        for elem in self.tree.xpath('/html/body/div[7]/section/div[4]/div[1]/ul'):
            for i in elem:
                text = i.getchildren()[0].text
                id = i.attrib['id']
                self.browser_click(id)
                print(text, ' horizontal')
                self.main_list.append({'text':text, 'content':self.parse_currencies_ver()})
    
    def parse_currencies_ver(self):
        currs_list = []
        parser = etree.HTMLParser()
        sitePath = self.browser.page_source
        tree = etree.fromstring(sitePath, parser)
        for elem in tree.xpath('/html/body/div[7]/section/div[4]/div[3]/div/div[1]'):
            for i in elem:
                text = i.getchildren()[1].text
                id = i.attrib['id']
                self.browser_click(id)
                soup = bs(self.browser.page_source)
                print(text, 'vertical')
                currs_list.append({'text':text, 'content':self.parse_curr(soup)}) #'US Dollar' : [] 
        return currs_list
    
    def show(self):
        for continent in self.main_list:
            print(continent.get('text'))
            for currency in continent.get('content'):
                print(currency.get('text'))
                rates = currency.get('content')
                self.show_curr_list(rates)         
                
class DataBase():
    
    def __init__(self, name, schema):
        self.name = name
        self.schema = schema
    
    def create_db(self):
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
    
    def add(self, dic):
        pass
    
    def show(self):
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
    
    def collect_com_and_curr(self):
        comm_url = "http://www.investing.com/commodities/"
        curr_xpath = "/html/body/div[7]/section/div[4]/div[3]/div/div[1]/a[2]/i"
        pass
        
    def closeEvent(self):
        q = QtGui.QWidget()
        q.setWindowIcon(QtGui.QIcon(EXIT))
        reply = QtGui.QMessageBox.question(q, 'Message', 'Are you sure to quit?', QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            QtGui.QApplication.quit()
def test():
    i = Investing()
    titles = ['America', 'Europe', 'Asia']
    lengths = [1,2,3]
    last_id = 1
    lists = [{'title' : "USD/ASD", 'href' : "http://inv.com/usd-asd", 'text' : "US dollar-Aus dollar"},
             {'title' : "USD/EUR", 'href' : "http://inv.com/usd-eur", 'text' : "US dollar-Euro"},
             {'title' : "GBP/EUR", 'href' : "http://inv.com/gbp-eur", 'text' : "Pound - Euro"},
             {'title' : "CHY/EUR", 'href' : "http://inv.com/chy-eur", 'text' : "Chinese Yen - Euro"},
             {'title' : "CHY/USD", 'href' : "http://inv.com/chy-usd", 'text' : "Chinese Yen - US dollar"},
             {'title' : "CHY/GBP", 'href' : "http://inv.com/chy-gbp", 'text' : "Chinese Yen - Pound"}]
    l = i.create_curr_list(titles, lengths, lists, last_id)
    i.show_curr_list(l)
    
def main():
    app = QtGui.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    #style = app.style()
    icon = QtGui.QIcon(MENU)
    trayIcon = SysTrayIcon(icon)
    trayIcon.show()
    trayIcon.showMessage("Биржа",strftime("%H"+":"+"%M"+":"+"%S"), 1000)
    sys.exit(app.exec_())

def parse():
    start = time()
    i = Investing()
    i.browser_start()
    i.parse_init(URL_CURR)
    i.parse_continents_hor()
    i.show()
    print(time()-start, " seconds passed for execution")
        
if __name__ == "__main__":
    #test()
    #main()
    parse()