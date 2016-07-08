from PyQt4 import QtCore, QtGui
import webbrowser

class Chooser(QtGui.QWidget):

	def __init__(self, db, parent=None):
		super(Chooser, self).__init__()
		self.db = db
		self.setupUI()
		self.translateUI()

	def setupUI(self):
		self.setObjectName("Chooser")
		self.tabWidget = QtGui.QTabWidget(self)
		self.tabWidget.setGeometry(QtCore.QRect(10, 20, 417, 393))
		self.tabWidget.setStatusTip("")
		self.tabWidget.setObjectName("tabWidget")
		
		self.con_tabs = []
        self.hor_lays = []
        self.tboxes = []
        self.grids = []
        for continent in self.db:
        	name = continent.get('name')
        	con_widget = QtGui.QWidget(name)
        	self.tabWidget.setTabText(self.tabWidget.indexOf(con_widget), name)
        	hor_layout = QtGui.QHBoxLayout(con_widget)
        	tbox = QtGui.QToolBox()
			tbox.currentChanged.connect(self.update_grid)

        	currencies = continent.get('content')
        	grids_temp = []
        	for currency in currencies:
        		name = currency.get('name')
        		cur_widget = QtGui.QWidget(name)
        		tbox.addItem(cur_widget, name)
        		#tbox.setItemText(tbox.indexOf(cur_widget), name)
        		
        		rates = currency['content']:
        		row = 0
        		col = 0
        		grid = QtGui.QGridLayout()
        		for zone in zones:
        			name = zone['name']
        			lbl = QtGui.QLabel(name)
        			grid.addWidget(lbl, col, row, 1, 1)
        			for rate in rates
        				row += 1
        				name = rate['name']
        				btn = QtGui.QPushButton(name)
        				grid.addWidget(btn, col, row, 1, 1)
    				row = 0
    				col +=1
    			grids_temp.append(grid)
    		self.grids.append(grids_temp)
    		self.con_tabs.append(con_widget)
    		self.tabWidget.addTab(con_widget)
			hor_layout.addWidget(tbox)
			hor_layout.addLayout(grid)
			self.tboxes.append(tbox)
			self.hor_lays.append(hor_layout)
		self.tabWidget.setCurrentIndex(0)


    def fillGrid(self, l, index):
    	col = 0
    	row = 0
    	for zone in l:
    		name = zone.get('name')
    		rates = zone.get('content')
    		label = QtGui.QLabel(name)
    		self.grids[index].addWidget(label, row, col, 1, 1)
    		for rate in rates:
    			name = rate.get('name')
    			title = rate.get('title')
    			href = rate.get('href')
    			button = QtGui.QPushButton(title)
    			button.setObjectName(href)
    			button.setStatusTip(name)
    			button.clicked.connect(self.go_site)
    			self.grids[index].addWidget(button, row, col, 1, 1)
    			row += 1
    		col += 1
    
    def flushGrid(self, index):
    	while self.grids[index].count():
    		item = self.grids[index].takeAt(0)
    		widget = item.widget()
    		widget.deleteLater()

    def go_site(self):
    	webbrowser.open(self.sender().objectName())

	def translateUI(self):
		pass

	def update_rates(self):
		cur_name = self.sender().text()
		con_id = self.tabWidget.currentIndex()
		cur_id = self.sender().currentIndex()
		#first clear
		while self.grids[con_id].count():
			item = self.grids[con_id].takeAt(0)
			widget = item.widget()
			widget.deleteLater()
		zones = self.db[con_id]['content'][cur_id]['content']


test_db = [{'id' : 1,
                'name':"Majors",
                'content':[
                           {'id':1, 
                            'name':"European Euro", 
                            'content':[
                                       {'id':1,
                                        'name':"Pacific",
                                        'content':[{'name': "AUD/UAH", 
                                                    'title' : "Australian Dollar Ukrainian Hryvnia",
                                                    'href' : "http://www.investing.com/currencies/aud-uah"},
                                                   {'name' : "USD/UAH", 
                                                    'title' : "US Dollar Ukrainian Hryvnia",
                                                    'href' : "http://www.investing.com/currencies/usd-uah"}]},
                                        {'id':2,
                                        'name':"Central America",
                                        'content':[{'name' : "UAH/RUB", 
                                                    'title' : "Ukrainian Hryvnia Russian Ruble", 
                                                    'href' : "http://www.investing.com/currencies/uah-rub"},
                                                   {'name':"DKK/UAH",
                                                    'title' : "Danish Krone Ukrainian Hryvnia",
                                                    'href' : "http://www.investing.com/currencies/dkk-uah"}]}]},
                           {'id':2,
                            'name':"US Dollar",
                            'content':[
                                       {'id':3,
                                        'name':"South America",
                                        'content':[{'name' : "TRY/OMR",
                                                    'title' : "Turkish Lira Omani Rial",
                                                    'href' : "http://www.investing.com/currencies/try-omr"},
                                                   {'name' : "TRY/BHD",
                                                    'title' : "Turkish Lira Baharain Dinar",
                                                    'href' : "http://www.investing.com/currencies/try-bhd"}]}]}]}]
    

def main():
	app = QtGui.QApplication(sys.argv)
	p = Chooser(test_db)
	p.setupUI()
	p.show()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()