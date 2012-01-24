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
        QGridLayout, QMessageBox, QSound)
from PyQt4 import QtWebKit
import fileio
import qrc_resources

import logging

class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        
        self.sms_thread = SmsThread()
        self.sms_thread.set_credentials()
        
        self.alert = QSound("../resources/pixiedust.wav")
        
        self.my_html = fileio.read_html("../resources/chat.html")
        
        self.browser = QtWebKit.QWebView()
        self.browser.setHtml(self.my_html) 
        self.link_js_to_python
        
        QtCore.QObject.connect(self.browser.page().mainFrame(), 
                               QtCore.SIGNAL("contentsSizeChanged(QSize)"), 
                               self.scroll_to_bottom)
        QtCore.QObject.connect(self.sms_thread, 
                               QtCore.SIGNAL("finished_parsing(PyQt_PyObject)"), 
                               self.updateUi)
        QtCore.QObject.connect(self.browser.page().mainFrame(),
                               QtCore.SIGNAL("javaScriptWindowObjectCleared()"),
                               self.link_js_to_python)
        
        layout = QGridLayout()
        layout.addWidget(self.browser, 0, 0)
        self.setLayout(layout)           

        self.setWindowTitle("Text Messages")
        
        logging.basicConfig(filename='sms-flow.log',level=logging.DEBUG)
        logging.info('App is Launched.')
        
    def start_fetching(self):
        try:
            self.sms_thread.start()
            QtCore.QTimer.singleShot(15000, self.start_fetching)
        except LoginError, e:
            QMessageBox.warning(self, "Login Error",
                                "Error logging in: " + unicode(e))
            
        
    def refresh_sms(self):
        self.sms_thread.update_sms()
        self.updateUi()

    def updateUi(self, all_msgs):
        if not all_msgs:
            return
        self.alert.play()
        
        logging.debug('Received a text. Here\'s all messages')
        logging.debug(all_msgs)        
        
        logging.debug('==============')
        for msg in all_msgs:
            logging.debug(msg)
        logging.debug('==============')
        logging.debug('=====End of Messages=====')
        
        for msg in all_msgs:
            self.my_html += ("<div class='bubble'><p class='from'>{0}</p>"
                            "<p class='text'>{1}</p></div>".format(msg['from'], 
                                                                   msg['text']))
        self.browser.setHtml(self.my_html)
 
    def link_js_to_python(self):
        self.browser.page().mainFrame().addToJavaScriptWindowObject("pyObj", 
                                                                    self) 

    ## Slots

    @QtCore.pyqtSlot(str)
    def a_method(self):
        QMessageBox.information(None, "Info", "HEy! What is up???")  

    def scroll_to_bottom(self, size):    
        self.browser.page().mainFrame().scroll(size.width(), size.height())


    

if __name__ == '__main__':    
    app = QApplication(sys.argv)
    form = Form()
    QtCore.QTimer.singleShot(0, form.start_fetching)
    form.show()
    form.raise_()
    form.activateWindow()
    app.exec_()

