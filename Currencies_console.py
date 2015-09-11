'''
Created on Jan 7, 2015

@author: grimel
'''
'''
Created on Jan 5, 2015

@author: grimel
'''
#coding utf blah-blah-blah

from bs4 import BeautifulSoup as bs
from urllib.request import urlopen, Request
from urllib import request
from time import sleep, strftime
import re, sys
from decimal import getcontext, Decimal
from urllib.error import URLError
from colorama import Fore, Back, Style, init
from PyQt4 import QtCore, QtGui
from os.path import isfile
EUR_RUB = "http://www.investing.com/currencies/eur-rub"
USD_RUB = "http://www.investing.com/currencies/usd-rub"
BRENT = "http://www.investing.com/commodities/brent-oil"

#last_last - css selector
class Economic():
    
    def __init__(self, site):
        self.headers = {"User-Agent":"Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}
        self.site = site
        self.pattern = "/(\w+)"
        self.name = re.findall(self.pattern, site)[2].upper()
        self.prev = None
        self.curr = None
        self.change = None
    
    def get_value(self):
        request = Request(self.site, HEADERS=self.headers)
        getcontext().prec = 2
        self.curr = Decimal(bs(urlopen(request)).find(id='last_last').text)
    
    def changed(self):
        if not self.prev or self.prev == self.curr:
            sys.stdout.write(Back.BLUE)
            self.change = "="
        elif self.curr > self.prev:
            sys.stdout.write(Back.GREEN)
            self.change = "↑"
        else: 
            sys.stdout.write(Back.RED)
            self.change = "↓"
        self.prev = self.curr
            
    def show(self):
        sys.stdout.write("{}-{:7.3f} {} ".format(self.name, self.curr, self.change))

#for qt app
    def save(self):
        settings = QtCore.QSettings("data.ini", QtCore.QSettings.IniFormat)
        settings.setValue(self.name, self.curr)
    
    def load(self):
        if isfile("data.ini"):
            settings = QtCore.QSettings("data.ini", QtCore.QSettings.IniFormat)
            self.curr = settings.value(self.name)
        else:
            self.curr = 0.00
#for qt app
 
    def do(self):
        self.get_value()
        self.changed()
        self.show()
#GUI PART
    
    def do_gui(self):
        self.get_value()
        return self.curr

def siteOn():
    try:
        response=urlopen('http://investing.com',timeout=1)
        return True
    except URLError as err: pass
    return False


class SysTrayIcon(QtGui.QSystemTrayIcon):
    
    def __init__(self, icon, parent=None):
        super(SysTrayIcon, self).__init__()
        self.dic = dict()
        self.menu = QtGui.QMenu(parent)
        self.exitAction = QtGui.QAction(self)
        self.dollarAction = QtGui.QAction(self)
        self.dollarAction.setText("0.00")
        self.exitAction.setText("Exit")
        self.exitAction.triggered.connect(sys.exit)
        self.menu.addAction(self.exitAction)
        self.menu.addAction(self.dollarAction)
        self.setContextMenu(self.menu)
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.loop)
        self.timer.start(10000)
    
    def loop(self):
        a = Economic(EUR_RUB)
        text = str(a.do_gui()) + " " + strftime("%H"+":"+"%M"+":"+"%S")
        self.dollarAction.setText(text)
    
def main():
    init()
    a = [Economic(i) for i in (EUR_RUB, USD_RUB, BRENT)]
    for i in range(10):
        if siteOn:
            for c in a:
                c.do()
            sys.stdout.write('\r')
            sys.stdout.flush()
            sleep(5)
        else:
            sys.stdout.write('Site is off')
            continue
def test():
    app = QtGui.QApplication(sys.argv)
    style = app.style()
    icon = QtGui.QIcon(style.standardPixmap(QtGui.QStyle.SP_FileIcon))
    trayIcon = SysTrayIcon(icon)
    trayIcon.show()
        
    sys.exit(app.exec_())
if __name__ == '__main__':
    #main()
    test()

'''
from pyvirtualdisplay import Display
from selenium import webdriver

display = Display(visible=0, size=(800, 600))
display.start()
print(display.is_started)
browser = webdriver.Firefox()
browser.get_value(site)
xpath = '//*[@id="last_last"]'
curr = browser.find_element_by_css_selector('#last_last')
print (curr.text)
browser.quit()

display.stop()
'''