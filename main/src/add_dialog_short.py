# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'add_dialog_short.ui'
#
# Created: Fri Apr 17 21:44:48 2015
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(759, 635)
        self.tabWidget = QtGui.QTabWidget(Form)
        self.tabWidget.setGeometry(QtCore.QRect(10, 20, 721, 311))
        self.tabWidget.setStatusTip(_fromUtf8(""))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.continent_1 = QtGui.QWidget()
        self.continent_1.setObjectName(_fromUtf8("continent_1"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.continent_1)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.toolBox = QtGui.QToolBox(self.continent_1)
        self.toolBox.setObjectName(_fromUtf8("toolBox"))
        self.currency_1 = QtGui.QWidget()
        self.currency_1.setGeometry(QtCore.QRect(0, 0, 89, 167))
        self.currency_1.setObjectName(_fromUtf8("currency_1"))
        self.toolBox.addItem(self.currency_1, _fromUtf8("1"))
        self.currency_2 = QtGui.QWidget()
        self.currency_2.setGeometry(QtCore.QRect(0, 0, 89, 167))
        self.currency_2.setObjectName(_fromUtf8("currency_2"))
        self.toolBox.addItem(self.currency_2, _fromUtf8(""))
        self.currency_3 = QtGui.QWidget()
        self.currency_3.setGeometry(QtCore.QRect(0, 0, 89, 167))
        self.currency_3.setObjectName(_fromUtf8("currency_3"))
        self.toolBox.addItem(self.currency_3, _fromUtf8(""))
        self.toolBox.currentChanged.connect(self.ad)
        self.horizontalLayout_3.addWidget(self.toolBox)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.zone8 = QtGui.QLabel(self.continent_1)
        self.zone8.setObjectName(_fromUtf8("zone8"))
        self.gridLayout.addWidget(self.zone8, 0, 7, 1, 1)
        self.zone6 = QtGui.QLabel(self.continent_1)
        self.zone6.setObjectName(_fromUtf8("zone6"))
        self.gridLayout.addWidget(self.zone6, 0, 5, 1, 1)
        self.zone5 = QtGui.QLabel(self.continent_1)
        self.zone5.setObjectName(_fromUtf8("zone5"))
        self.gridLayout.addWidget(self.zone5, 0, 4, 1, 1)
        self.rate_1 = QtGui.QPushButton(self.continent_1)
        self.rate_1.setObjectName(_fromUtf8("rate_1"))
        self.gridLayout.addWidget(self.rate_1, 1, 0, 1, 1)
        self.rate_2 = QtGui.QPushButton(self.continent_1)
        self.rate_2.setObjectName(_fromUtf8("rate_2"))
        self.gridLayout.addWidget(self.rate_2, 2, 0, 1, 1)
        self.zone1 = QtGui.QLabel(self.continent_1)
        self.zone1.setObjectName(_fromUtf8("zone1"))
        self.gridLayout.addWidget(self.zone1, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.zone7 = QtGui.QLabel(self.continent_1)
        self.zone7.setObjectName(_fromUtf8("zone7"))
        self.gridLayout.addWidget(self.zone7, 0, 6, 1, 1)
        self.zone3 = QtGui.QLabel(self.continent_1)
        self.zone3.setObjectName(_fromUtf8("zone3"))
        self.gridLayout.addWidget(self.zone3, 0, 2, 1, 1)
        self.rate_4 = QtGui.QPushButton(self.continent_1)
        self.rate_4.setObjectName(_fromUtf8("rate_4"))
        self.gridLayout.addWidget(self.rate_4, 4, 0, 1, 1)
        self.zone4 = QtGui.QLabel(self.continent_1)
        self.zone4.setObjectName(_fromUtf8("zone4"))
        self.gridLayout.addWidget(self.zone4, 0, 3, 1, 1)
        self.zone2 = QtGui.QLabel(self.continent_1)
        self.zone2.setObjectName(_fromUtf8("zone2"))
        self.gridLayout.addWidget(self.zone2, 0, 1, 1, 1)
        self.rate_3 = QtGui.QPushButton(self.continent_1)
        self.rate_3.setObjectName(_fromUtf8("rate_3"))
        self.rate_3.clicked.connect(self.rem)
        self.gridLayout.addWidget(self.rate_3, 3, 0, 1, 1)
        self.rate_5 = QtGui.QPushButton(self.continent_1)
        self.rate_5.setObjectName(_fromUtf8("rate_5"))
        self.gridLayout.addWidget(self.rate_5, 5, 0, 1, 1)
        self.horizontalLayout_3.addLayout(self.gridLayout)
        self.tabWidget.addTab(self.continent_1, _fromUtf8(""))
        self.continent_2 = QtGui.QWidget()
        self.continent_2.setObjectName(_fromUtf8("continent_2"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.continent_2)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.tabWidget.addTab(self.continent_2, _fromUtf8(""))

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        self.toolBox.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(Form)
        
    def de(self):
        layout = self.gridLayout
        item = layout.takeAt(0)
        widget = item.widget()
        widget.deleteLater()

    def ad(self):
        print(self.tabWidget.currentIndex())
        layout = self.gridLayout
        but = QtGui.QPushButton("NEW")
        layout.addWidget(but, 8,10)

    def rem(self):
        while self.gridLayout.count():
            item = self.gridLayout.takeAt(0)
            widget = item.widget()
            widget.deleteLater()


    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        #self.toolBox.setItemText(self.toolBox.indexOf(self.currency_1), _translate("Form", "Page 1", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.currency_2), _translate("Form", "Page 2", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.currency_3), _translate("Form", "Page 3", None))
        self.zone8.setText(_translate("Form", "TextLabel", None))
        self.zone6.setText(_translate("Form", "TextLabel", None))
        self.zone5.setText(_translate("Form", "TextLabel", None))
        self.rate_1.setText(_translate("Form", "PushButton", None))
        self.rate_2.setText(_translate("Form", "PushButton", None))
        self.zone1.setText(_translate("Form", "TextLabel", None))
        self.zone7.setText(_translate("Form", "TextLabel", None))
        self.zone3.setText(_translate("Form", "TextLabel", None))
        self.rate_4.setText(_translate("Form", "PushButton", None))
        self.zone4.setText(_translate("Form", "TextLabel", None))
        self.zone2.setText(_translate("Form", "TextLabel", None))
        self.rate_3.setText(_translate("Form", "PushButton", None))
        self.rate_5.setText(_translate("Form", "PushButton", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.continent_1), _translate("Form", "Tab 1", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.continent_2), _translate("Form", "Tab 2", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

