#! python
#-*-coding:utf-8-*-
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen, Request
from urllib.error import URLError
from decimal import getcontext, Decimal
from colorama import Fore, Back, Style, init
from time import strftime
from PyQt4 import QtGui, QtCore
from os.path import isfile
import sys
import re
import webbrowser

MAS = ["http://www.investing.com/currencies/eur-rub",       #eur-rub
       "http://www.investing.com/currencies/usd-rub",       #usd-rub
       "http://www.investing.com/commodities/brent-oil"]    #brent

DOWN = "src/down.png"
UP = "src/up.png"
EQUAL = "src/equal.png"
EXIT = "src/exit.png"
MENU = "src/exchange.png"
UPDATE_TIME = 30000 # 30 seconds * 1000 milliseconds

def site_on():
    try:
        response=urlopen('http://investing.com',timeout=1)
        return True
    except URLError as err: pass
    return False

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
        pattern = "/(\w+)"
        name = re.findall(pattern, self.site)[2].upper()
        return name
    
    def get(self):
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
            self.get()
            self.changed()
        except:
            return None
        return "{:7.3f}   {}".format(self.curr, self.name)

class MainMenu (QtGui.QWidget):
    
    def __init__(self):
        super(MainMenu, self).__init__()
        self.button = QtGui.QPushButton(self)
        self.setGeometry(300, 300, 250, 150)
        
class SysTrayIcon(QtGui.QSystemTrayIcon):
    
    def __init__(self, icon, parent=None):
        super(SysTrayIcon, self).__init__()
        self.setIcon(icon)
        self.menu = QtGui.QMenu(parent)
        self.init_list()
        self.menu.addSeparator()
        
        self.time = QtGui.QAction(self)
        self.time.triggered.connect(self.loop)
        self.time.setText("Update")
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
        self.activated.connect(self.dor)
    
    def dor(self, reason):
        if reason == QtGui.QSystemTrayIcon.MiddleClick:
            self.closeEvent()
        
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
        sys.exit()
        
def main():
    app = QtGui.QApplication(sys.argv)
    style = app.style()
    icon = QtGui.QIcon(MENU)
    trayIcon = SysTrayIcon(icon)
    trayIcon.show()
    trayIcon.showMessage("Биржа", "Нажмите Update", 1000)
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()