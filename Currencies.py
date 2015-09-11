#! python
#-*-coding:utf-8-*-

from bs4 import BeautifulSoup as bs
from urllib.request import urlopen, Request
from urllib.error import URLError
from decimal import getcontext, Decimal
from time import strftime, sleep
from lxml import etree
from pyvirtualdisplay import Display
from selenium import webdriver


from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSignal


import sys
import webbrowser
from urllib.parse import urlparse
import sqlite3
from os import path

DEBUG = True

MAS = [{'href':"http://www.investing.com/currencies/eur-rub",
             'title':"Euro Russian Ruble", 
             'name':"EUR/RUB"},
            {'href':"http://www.investing.com/currencies/usd-rub",
             'title':'US Dollar Russian Ruble',
             'name':"USD/RUB"},
            {'href':"http://www.investing.com/commodities/brent-oil",
             'title':'brent-oil',
             'name':'Brent-Oil'}]
#-------------icons ----------------------------------------
DOWN = "src/down.png"
UP = "src/up.png"
EQUAL = "src/equal.png"
EXIT = "src/exit.png"
SYS_TRAY = "src/exchange.png"
CHOOSER_ICON = "src/chooser.png"
#-------------time for update 30 seconds * 1000
UPDATE_TIME = 30000 
#-------------FOR PARSING INVESTING.COM----------------------
URL_COMMO = "http://www.investing.com/commodities/"
URL_CURR = "http://www.investing.com/currencies/"
HEADERS = {"User-Agent":"Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}
#-------------SQL resources-------
BASE = 'test.db'
SCHEMA = 'schema.sql'
BASE_RATES = 'rates.db'
SCHEMA_RATES = 'schema_rates.sql'

def siteOn ():
    try:
        request = Request(URL_CURR, headers=HEADERS)
        _=urlopen(request)
        return True
    except URLError: pass
    return False

def createRequest(url):
    request = Request(url, headers=HEADERS)
    s = urlopen(request)
    return s 


class Investing():
    '''class for parsing site to one array'''
    def __init__(self, l=None):
        self.main_list = l
        
    def browserStart(self):
        '''start display and browser'''
        self.display = Display(visible=0, size=(800, 600))  #virtual display
        self.display.start()                                #start virtual display
        self.browser = webdriver.Firefox()                  #start browser
        self.browser.get(URL_CURR)                          #go to URL_CURR
    
    def browserStop(self):
        '''close display and browser'''
        self.browser.close()
        self.display.stop()
        
    def browserClick(self, el_id):
        '''handle click'''                                  
        element = self.browser.find_element_by_id(el_id)    
        element.click()                                     #click and open new page
        
    def parserInit(self, url):
        '''init parser'''
        s = createRequest(url)
        pageContent = s.read()
        parser = etree.HTMLParser()
        self.tree = etree.fromstring(pageContent, parser)
        self.last_id = 1
        self.continent_id = 1
        self.currency_id = 1
    
    def createRatesList(self, titles, lengths, lists):
        '''creating rates list for every currency'''
        last_id = self.last_id
        rates_list = []
        i = 0
        try:
            for index, zone_name in enumerate(titles):      #for every zone we have a structure
                if DEBUG: print(zone_name)                  #Zone_name
                zone_list = []                              #Currency1
                j = lengths[index]                          #Currency2
                zone_id = last_id + index                   #CurrencyN
                                                            #
                for c in range(i, i+j):                     #titles store titles of zone
                    zone_list.append(lists[c])              #lengths store count of currencies
                    if DEBUG: print(lists[c])               #lists store information about rates
                rates_list.append({'id':zone_id,            #for every zone we create zone_name and zone_list
                                   'name':zone_name,        #
                                   'content':zone_list})    #
                i += j
        except:
            print(sys.exc_info())
            
        self.last_id = zone_id +1
        assert rates_list    
        return rates_list
         
    def parseCurr(self, soup):
        '''parsing every currency for zone/rates'''
        tableClass = "inlineblock alignTop curExpCol"
        titleClass = "curTitle inlineblock bold"
        lengths = []
        titles = []
        lists = []
        
            #name of every zone
        for t in soup.findAll("span", {"class":titleClass}):
            assert t.text, "title is Empty"
            titles.append(t.text)
        
        for i in soup.findAll("span", {"class":tableClass}):
            #rate for every zone
            for ul in i.findAll('ul'):
                lengths.append(len(ul.findAll('li')))
            
            #rate title: USD/AUD, href: "http://..", title:US Dollar Austrian Dollar
            for j in i.select('li > a'):
                href = j.get('href')
                title = j.get('title')
                name = j.text
                assert isinstance(name, str), 'name is not str'
                assert href, 'href is Empty'
                assert title, 'title is Empty'
                dr = {'title' : title,
                      'href' : href,
                      'name' : name}
                lists.append(dr)
                
        l = self.createRatesList(titles, lengths, lists)
        return l
                
    def parseCurrVer(self):
        '''parsing currencies in vertical line'''
        verTab = '//*[@id="filterBoxTable"]' #/html/body/div[7]/section/div[4]/div[3]/div/div[1]
        currs_list = []
        parser = etree.HTMLParser()
        pageContent = self.browser.page_source
        tree = etree.fromstring(pageContent, parser)
        for elem in tree.xpath(verTab):
            for i in elem:
                name = i.getchildren()[1].text
                elem_id = i.attrib['id']
                self.browserClick(elem_id)
                soup = bs(self.browser.page_source)
                currency_id = self.currency_id
                currs_list.append({'id':currency_id, 'name':name, 'content':self.parseCurr(soup)}) #'US Dollar' : []
                self.currency_id +=1 
        return currs_list
    
    def parseMain(self):
        '''parsing continents line (horizontal line) - main parser'''
        horTab = '//*[@id="filterBoxExpTabsTop"]' #/html/body/div[7]/section/div[4]/div[1]/ul
        self.main_list = []
        for elem in self.tree.xpath(horTab):
            for i in elem:
                name = i.getchildren()[0].text
                elem_id = i.attrib['id']
                self.browserClick(elem_id)
                continent_id = self.continent_id
                self.main_list.append({'id':continent_id, 
                                       'name':name, 
                                       'content':self.parseCurrVer()})
                self.continent_id+=1    
    
    def show(self):
        '''test - show created list'''
        for continent in self.main_list:
            print("'id':{}, 'name' : {}".format(continent.get('id'),
                                                continent.get('name')))
            for currency in continent.get('content'):
                print("'id':{}, 'name' {}".format(currency.get('id'),
                                                  currency.get('name')))
                zones = currency.get('content')
                for zone in zones:
                    print("'id': {}, 'name': {}".format(zone.get('id'),
                                                        zone.get('name')))
                    rates = zone.get('content')
                    for rate in rates:
                        print("'id': {}, 'title': {}, 'name' : {}, 'href' : {}".format(rate.get('id'), 
                                                                                       rate.get('title'), 
                                                                                       rate.get('name'), 
                                                                                       rate.get('href')))         
                
class DataBase():
    
    def __init__(self, name):
        '''empty base with name'''
        self.name = name
    
    def create(self, schema):
        '''create empty base with schema'''
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
    
    def clean(self):
        
        with sqlite3.connect(self.name) as conn:
            conn.execute("DELETE FROM Continents")
            conn.execute("DELETE FROM Zones")
            conn.execute("DELETE FROM Currencies")
            conn.execute("DELETE FROM Rates")
            conn.commit()
        
    def add(self, db):
        '''add list from Investing to database'''
        assert db, 'empty list given'
        self.db = db
        with sqlite3.connect(self.name) as conn:
            cur = conn.cursor()
            for continent in self.db:
                cur.execute('INSERT INTO Continents VALUES(?,?)', (continent.get('id'),
                                                                   continent.get('name')))
                currencies = continent.get('content')
                for currency in currencies:
                    cur.execute('INSERT INTO Currencies VALUES(?,?,?)', (currency.get('id'),
                                                                         currency.get('name'),
                                                                         continent.get('id')))
                    zones = currency.get('content')
                    for zone in zones:
                        cur.execute('INSERT INTO Zones VALUES (?,?,?,?)', (zone.get('id'),
                                                                           zone.get('name'),
                                                                           continent.get('id'),
                                                                           currency.get('id')))
                        rates = zone.get('content')
                        for rate in rates:
                            cur.execute('INSERT INTO Rates VALUES (?,?,?,?,?,?,?)', (rate.get('id'),
                                                                                     rate.get('name'),
                                                                                     rate.get('title'),
                                                                                     rate.get('href'),
                                                                                     continent.get('id'),
                                                                                     currency.get('id'),
                                                                                     zone.get('id')))
            conn.commit()

    def load(self):
        '''load from existing database to list'''
        self.db = []
        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()
            continents = cursor.execute("SELECT * FROM Continents").fetchall()
            for continent in continents:
                co_id, co_n = continent[0], continent[1]
                self.db.append({'id' : co_id,
                                'name': co_n,
                                'content':[]})
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
        assert self.db, "Database is empty"
        return self.db
  
#last_last - css selector

class Economic():
    
    def __init__(self, l):
        self.name = l['name']
        self.title = l['title']
        self.href = l['href']
        self.previous = None
        self.current = None
        self.change = None
        self.value = self._string()
        
               
    def _get_current(self):
        '''get current value'''
        
        request = Request(self.href, headers=HEADERS)
        getcontext().prec = 2
        value = bs(urlopen(request)).find(id='last_last').text
        self.current = Decimal(value)
        self.current = self.current
        
    def _string(self):
        '''value for action'''
        
        #check for connection
        try:
            self._get_current()
            self._changed()
        except:
            return "No connection"      
        return "{:7.3f}    {}".format(self.current, self.name)
    
    def _changed(self):
        '''check if chandged'''
        if not self.previous or self.previous == self.current:
            self.change = "="
        elif self.current > self.previous:
            self.change = "↑"
        else:
            self.change = "↓"
        self.previous = self.current

class Chooser(QtGui.QDialog):#
    '''Widget - analogue to currency page view '''
    p = pyqtSignal()                                #IMPORTANT - not inside constructor 
    
    def __init__(self, db, parent=None):
        super(Chooser, self).__init__()
        self.db = db
        
        self.picked = None
        self.setupUI()
        self.retranslateUI()
    
    def setupUI(self):
        self.setObjectName("Chooser")
        self.tabWidget = QtGui.QTabWidget(self)
        
        for hor, continent in enumerate(self.db):
            tab = QtGui.QScrollArea()
            con_widget = QtGui.QWidget()
            tab.setWidget(con_widget)
            con_name = continent['name']
            tbox_widget = QtGui.QToolBox()
                        
            currencies = continent.get('content')
            for ver, currency in enumerate(currencies):
                cur_name = currency.get('name')
                cur_widget = QtGui.QWidget()
                tbox_widget.addItem(cur_widget, cur_name)
                zones = currency['content']
                grid_layout = self.fillGrid(hor, ver, zones)
            tbox_widget.setFixedHeight(tbox_widget.sizeHint().height())
            tbox_widget.setFixedWidth(tbox_widget.sizeHint().width())
            tbox_widget.currentChanged.connect(self.updateGrid)
            
            hor_layout = QtGui.QHBoxLayout(con_widget)
            
            ver_layout1 = QtGui.QVBoxLayout()
            ver_layout1.addWidget(tbox_widget)
            ver_layout1.addStretch(1)
            
            ver_layout2 = QtGui.QVBoxLayout()
            ver_layout2.addLayout(grid_layout)
            ver_layout2.addStretch(1)
            
            hor_layout.addLayout(ver_layout1)
            hor_layout.addLayout(ver_layout2)
            tab.setWidgetResizable(True)
            self.tabWidget.addTab(tab, con_name)
            
        self.tabWidget.adjustSize()
        self.lay = QtGui.QVBoxLayout()
        self.up_but = QtGui.QPushButton("Update")
        self.up_but.clicked.connect(self.updateDataBase)
        self.lay.addWidget(self.tabWidget)
        self.lay.addWidget(self.up_but)
        self.setLayout(self.lay)
        
    def updateGrid(self):
        '''update grid of currencies with zone titles'''
        widget = self.tabWidget.currentWidget().widget()
        hor = self.tabWidget.currentIndex()
        ver = self.sender().currentIndex()
        db = self.db
        zones = db[hor]['content'][ver]['content']
        grid_new = self.fillGrid(hor, ver, zones)
        
        v_layout = widget.layout().itemAt(1)
        grid_old = v_layout.itemAt(0)
        stretch = v_layout.itemAt(1)
        
        while grid_old.count():
            item = grid_old.takeAt(0)
            widget = item.widget()
            widget.deleteLater()
        
        v_layout.removeItem(grid_old)
        v_layout.removeItem(stretch)
        v_layout.addLayout(grid_new)
        v_layout.addStretch(1)
        
    def fillGrid(self, hor, ver, zones):
        '''creating grid'''
        grid_new = QtGui.QGridLayout()
        row = 0
        col = 0
        for zone in zones:
            name = zone['name']
            lbl = QtGui.QLabel(name)
            grid_new.addWidget(lbl, row, col, 1, 1)
            rates = zone['content']
            for rate in rates:
                row += 1
                r_name = rate['name']
                r_href = rate['href']
                r_title = rate['title']
                btn = QtGui.QPushButton(r_name)
                btn.setToolTip(r_title)
                btn.setObjectName(r_href)
                btn.clicked.connect(self.addRate)
                grid_new.addWidget(btn, row, col, 1, 1)
            row = 0
            col +=1
        
        return grid_new
    
    def addRate(self):
        '''action when clicked button'''
        name = self.sender().text()
        title = self.sender().toolTip()
        href = self.sender().objectName()
        
        if DEBUG: print("{}-name. {}-title, {}-href".format(name, title, href))
        self.picked =  Economic({'href':href, 'title':title, 'name':name})
        self.p.emit()
            
    def updateDataBase(self):
        if not siteOn():
            _ = QtGui.QMessageBox.information(self, 'Message', 'No internet connection', QtGui.QMessageBox.Ok)
            return
            
        reply = QtGui.QMessageBox.question(self, 'Message', 'Base is empty. Update? (takes 5-10 mins)', 
                                           QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, 
                                           QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            uc = UpdateChooser()
            self.close()
            uc.exec_()
        
    def retranslateUI(self):
        self.setWindowIcon(QtGui.QIcon(CHOOSER_ICON))
        self.setWindowTitle(self.tr("List of rates"))

class WorkThread(QtCore.QThread):
    
    punched = QtCore.pyqtSignal(str)
    signal_done = QtCore.pyqtSignal(list)
    
    def __init__(self):
        super(WorkThread, self).__init__()
        self.working = True
    def __del__(self):
        self.wait()
        
    def run(self):
        i = Investing()
        self.punched.emit("Created parser")
        sleep(1)
        i.browserStart()
        self.punched.emit("Initiated browser")
        sleep(1)
        i.parserInit(URL_CURR)
        self.punched.emit("...")
        sleep(1)
        self.punched.emit("Parser working")
        i.parseMain()
        i.browserStop() 
        self.punched.emit("Parser finished working")
        sleep(1)
        if DEBUG: print("Parser finished")
        print(BASE)
        d = DataBase(BASE)
        d.clean()
        self.punched.emit("Database cleaned")
        sleep(1)
        d.add(i.main_list)
        self.punched.emit("Created sql base")
        sleep(1)
        self.signal_done.emit(d.db)
        

class UpdateChooser(QtGui.QDialog):
    
    def __init__(self):
        super(UpdateChooser, self).__init__()
        self.initUI()
        self.retranslateUI()
        self.task = WorkThread()
        #self.task.signal_done.connect(self.close)
        #self.task.signal_done.connect(self.task.terminate)
        self.task.signal_done.connect(self.recreateChooser)
        self.startTask()
        
    def initUI(self):
        layout = QtGui.QVBoxLayout()
        self.label = QtGui.QLabel()
        self.progressBar = QtGui.QProgressBar()
        self.progressBar.setRange(0, 0)
        layout.addWidget(self.label)
        layout.addWidget(self.progressBar)
        self.setLayout(layout)
        
    def retranslateUI(self):
        self.label.setText(self.tr("Retrieving data. This can take up for 5-10 minutes"))
        
    def startTask(self):
        self.task.punched.connect(self.onProgress)
        self.task.start()
        
    def onProgress(self, i):
        self.label.setText(i)
    
    def recreateChooser(self, i):
        '''updating Chooser'''
        self.close()
        self.task.terminate()
        c = Chooser(i)
        c.exec_()
        
class SysTrayIcon(QtGui.QSystemTrayIcon):
    '''system tray class'''
    def __init__(self, parent=None):
        super(SysTrayIcon, self).__init__()
        self.a = []
        self.title = ""
        self.initUI()
        self.retranslateUI()
        self.initActions()
        self.initList()
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.loop)
        self.loop()

    def initUI(self):
        '''initializing UI of system tray'''
        #trayIcon.showMessage("Биржа", strftime("%H"+":"+"%M"+":"+"%S"), 1000)
        self.menu = QtGui.QMenu()
        self.menu.addSeparator()
        self.time = QtGui.QAction(self)
        self.update = QtGui.QAction(self)
        self.default = QtGui.QAction(self)
        self.menu.addAction(self.time)
        self.menu.addSeparator()
        self.menu.addAction(self.default)
        self.menu.addAction(self.update)
        self.menu.addSeparator()
        self.exitAction = QtGui.QWidgetAction(self)
        self.menu.addAction(self.exitAction)
        self.setContextMenu(self.menu)

    def retranslateUI(self):
        self.setIcon(QtGui.QIcon(SYS_TRAY))
        self.update.setIconText("Add currency")
        self.default.setIconText("Default")
        self.exitAction.setIconText(self.tr("Exit"))
        self.title = self.tr("Exchange")
        
    def initActions(self):
        self.activated.connect(self.handleClick)
        self.time.triggered.connect(self.loop)
        self.update.triggered.connect(self.add_currency)
        self.default.triggered.connect(self.setDefaultTray)
        self.exitAction.triggered.connect(self.closeEvent)
        
    def setDefaultTray(self):
        '''set default 3 rates'''
        for i in self.a:
            self.menu.removeAction(self.menu.actions()[0])
            if DEBUG: print(i, " deleted")
        self.initList(True)
        self.loop()
        
    def handleClick(self, reason):
        '''correct right click in Windows'''
        if reason == QtGui.QSystemTrayIcon.MiddleClick:
            self.closeEvent()
        elif reason == QtGui.QSystemTrayIcon.Trigger:
            
            y = self.geometry().top() - 120
            x = self.geometry().left() - 130
    
            pos = QtCore.QPoint(x, y)
            self.contextMenu().move(pos)
            self.contextMenu().show()
        
    def addAction(self, i):
        if DEBUG: print("New rate added to systray")
        self.a.append(i)
        action = QtGui.QAction(self)
        action.setObjectName(i.href)
        action.setText(i.value)
        action.setToolTip(i.title)
        action.triggered.connect(self.openLink)
        menu = QtGui.QMenu()
        sub_action = QtGui.QAction(action)
        sub_action.setText(self.tr("Delete"))
        sub_action.triggered.connect(self.deleteAction)
        menu.addAction(sub_action)
        action.setMenu(menu)
        if DEBUG: print(len(self.menu.actions()))
        last = len(self.a)-1
        old = self.menu.actions()[last]
        self.menu.insertAction(old, action)
        self.loop()
    
    def deleteAction(self):
        print(self.sender().parent())
        self.menu.removeAction(self.sender().parent())
        for i in self.a:
            if i.name in self.sender().parent().text():
                self.a.remove(i)
            print(len(self.a))
    
    def loadDefault(self):
        with sqlite3.connect('rates.db') as conn:
            conn.execute("DROP TABLE IF EXISTS Rates")
            conn.commit()
        self.a = [Economic(i) for i in MAS]
        
    def loadNotDefault(self):
        with sqlite3.connect(BASE_RATES) as conn:
            titles = conn.execute("SELECT Title FROM Rates").fetchall()
            hrefs  = conn.execute("SELECT Href FROM Rates").fetchall()
            names  = conn.execute("SELECT Name FROM Rates").fetchall()
                        
        for t, h, n in zip(titles, hrefs, names):
            mas = {"href":h[0], "title":t[0], "name":n[0]}
            self.a.append(Economic(mas))
            
        print("Loaded not default")
    
    def saveNewRates(self):
        with sqlite3.connect(BASE_RATES) as conn:
            with open(SCHEMA_RATES) as f:
                schema = f.read()
            conn.executescript(schema)
            conn.commit()
            for i in self.a:
                conn.execute("INSERT INTO Rates(Title, Href, Name) VALUES(?, ?, ?)", (i.title, i.href, i.name))
            conn.commit()
        print("Saved new rates")
    
    def initList(self, default=False):
        if default:
            self.loadDefault()
        else:
            try:
                print("Try")
                self.loadNotDefault()
            except:
                print("Fuck you!")
                self.loadDefault()
            
        for i in self.a:
            print(i)
            action = QtGui.QAction(self)
            action.setObjectName(i.href)
            action.setText(i.value)
            action.setToolTip(i.title)
            action.triggered.connect(self.openLink)
            #self.menu.addAction(action)
            old = self.menu.actions()[0]
            self.menu.insertAction(old, action)
    
    def loop(self):
        '''infinite loop until app closed'''
        if self.timer.isActive(): self.timer.stop()                 #preventing earlier timer
        for c, w in zip(self.a, self.menu.actions()):
            print(w.text())
            value = c._string()
            if not value: continue
            w.setText(value)
            if c.change == "=":
                w.setIcon(QtGui.QIcon(EQUAL))   #w.setIcon(QtGui.QIcon.fromTheme("face-smirk"))
            elif c.change == "↑":
                w.setIcon(QtGui.QIcon(UP))
            else:
                w.setIcon(QtGui.QIcon(DOWN))
        self.time.setText(strftime("%H"+":"+"%M"+":"+"%S"))
        self.timer.start(UPDATE_TIME)
        
    def add_currency(self):
        d = DataBase(BASE)
        l = d.load()
        self.c = Chooser(l)
        self.c.p.connect(lambda:self.addAction(self.c.picked))
        self.c.show()
        
    def openLink(self):
        webbrowser.open(self.sender().objectName())
         
    def closeEvent(self):
        '''make sure if really wanna quit'''
        q = QtGui.QWidget()
        q.setWindowIcon(QtGui.QIcon(EXIT))
        msg = QtGui.QMessageBox()
        msg.setText("Message")
        msg.setWindowIcon(QtGui.QIcon(EXIT))
        checkbox = QtGui.QCheckBox("Save new rates")
        checkbox.blockSignals(True)
        
        msg.addButton(QtGui.QMessageBox.Yes)
        msg.addButton(QtGui.QMessageBox.No)
        msg.setDefaultButton(QtGui.QMessageBox.No)
        msg.addButton(checkbox, QtGui.QMessageBox.ResetRole)
        new = len(self.a) > 3
        m = ExitWindow(new)
        m.saved.connect(self.saveNewRates)
        m.exec_()
        
        '''
        reply = QtGui.QMessageBox.question(q, 'Message', 'Are you sure to quit?', QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            QtGui.QApplication.quit()
            if len(self.a) > 3:
                    self.saveNewRates()
        '''
        
class ExitWindow(QtGui.QDialog):
    saved = QtCore.pyqtSignal()
    def __init__(self, new):
        super(ExitWindow, self).__init__()
        self.new = new
        self.initUI()
        self.retranslateUI()
        self.initActions()
    
    def initUI(self):
        layout = QtGui.QVBoxLayout()
        but_lay = QtGui.QHBoxLayout()
        self.label = QtGui.QLabel()
        self.checkbox = QtGui.QCheckBox()
        self.yes = QtGui.QPushButton()
        self.no = QtGui.QPushButton()
        but_lay.addWidget(self.yes)
        but_lay.addWidget(self.no)
        layout.addWidget(self.label)
        if self.new:
            layout.addWidget(self.checkbox)
        layout.addLayout(but_lay)
        self.setLayout(layout)
    
    
    def retranslateUI(self):
        self.setWindowIcon(QtGui.QIcon(EXIT))
        self.setWindowTitle(self.tr("Quit"))
        self.label.setText(self.tr("Are you sure to quit?"))
        self.checkbox.setText(self.tr("Save new rates"))
        self.yes.setText(self.tr("Yes"))
        self.no.setText(self.tr("No"))
        
    
    def exit(self):
        if self.checkbox.isChecked():
            self.saved.emit()
        QtGui.QApplication.quit()
        
    def initActions(self):
        self.yes.clicked.connect(self.exit)
        self.no.clicked.connect(self.close)

def main():
    app = QtGui.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)    #don't close systray after closing any window
    trayIcon = SysTrayIcon()
    trayIcon.show()
    trayIcon.showMessage(trayIcon.title, strftime("%H"+":"+"%M"+":"+"%S"), 1000)
    sys.exit(app.exec_())

    
if __name__ == "__main__":
    main()