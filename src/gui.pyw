#!/usr/bin/env python
###

###

from __future__ import print_function
from __future__ import unicode_literals
#from future_builtins import *

import sys
from smsthread import SmsThread
from googlevoice.util import LoginError
from PyQt4 import QtCore# (Qt, SIGNAL, QUrl)
from PyQt4.QtGui import (QApplication, QDialog,
        QGridLayout, QMessageBox)
from PyQt4 import QtWebKit
import fileio

class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        
        self.sms_thread = SmsThread()
        
        self.my_html = fileio.read_html("chat.html")
        
        self.browser = QtWebKit.QWebView()
        self.browser.setHtml(self.my_html)

        QtCore.QObject.connect(self.browser.page().mainFrame(), 
                               QtCore.SIGNAL("contentsSizeChanged(QSize)"), 
                               self.scroll_to_bottom)
        QtCore.QObject.connect(self.sms_thread, 
                               QtCore.SIGNAL("finished_parsing(PyQt_PyObject)"), 
                               self.updateUi)
        
        layout = QGridLayout()
        layout.addWidget(self.browser, 0, 0)
        self.setLayout(layout)           

        self.setWindowTitle("Text Messages")
        
    def start_fetching(self):
        try:
            self.sms_thread.set_credentials()
            self.sms_thread.start()
            QtCore.QTimer.singleShot(15000, form.start_fetching)
        except LoginError, e:
            QMessageBox.warning(self, "Login Error",
                                "Error logging in: " + unicode(e))
            
    def scroll_to_bottom(self, size):    
        self.browser.page().mainFrame().scroll(size.width(), size.height())
        
    def refresh_sms(self):
        self.sms_thread.update_sms()
        self.updateUi()

    def updateUi(self, all_msgs):
        for msg in all_msgs:
            self.my_html += ("<div class='bubbledRight'>{0}<br/>"
                            " {1}</div>".format(msg['from'], msg['text']))
        self.browser.setHtml(self.my_html)
 


if __name__ == '__main__':    
    app = QApplication(sys.argv)
    form = Form()
    QtCore.QTimer.singleShot(0, form.start_fetching)
    form.show()
    form.raise_()
    form.activateWindow()
    app.exec_()

