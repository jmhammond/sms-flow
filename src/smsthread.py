#!/usr/bin/env python
###
# Sms module from 
# pygooglevoice
###

import BeautifulSoup
from googlevoice import Voice
from googlevoice import util
from PyQt4.QtCore import (QThread, SIGNAL) 

class SmsThread(QThread):
        
    def set_credentials(self, email=None, passwd=None):
        """
        set_credentials -- establish the login credentials for Google Voice
        If unspecified, pygooglevoice reverts to looking for ~/.gvoice 
        """
        self.voice = Voice()
        self.email = email
        self.passwd = passwd
        self.callback = None

    def run(self):
        """
        run -- called when the thread starts. We process the text messages 
        and notify any listeners when we're done with 
        the Qt signal finished_parsing(PyQt_PyObject) 
        """
        self.voice.login(self.email, self.passwd)
        self.already_read_ids = list()
        self.update_sms()  
        self.emit(SIGNAL("finished_parsing(PyQt_PyObject)"), self.all_msgs)

    def extract_sms(self, htmlsms):
        """
        extractsms  --  extract SMS messages from BeautifulSoup tree 
        of Google Voice SMS HTML.

        Output is a list of dictionaries, one per message.
        """
        msgitems = []                                        
     
        tree = BeautifulSoup.BeautifulSoup(htmlsms)         
        conversations = tree.findAll("div",attrs={"id" : True},recursive=False)
        for conversation in conversations :
            # For each conversation, extract each row, which is one SMS message.
            rows = conversation.findAll(attrs={"class" : "gc-message-sms-row"})
            for row in rows :                                # for all rows
                #    For each row, which is one message, extract all the fields.
                msgitem = {"id" : conversation["id"]} 
                spans = row.findAll("span",attrs={"class" : True}, 
                                    recursive=False)
                for span in spans :    
                    cl = span["class"].replace('gc-message-sms-', '')
                    msgitem[cl] = (" ".join(span.findAll(text=True))).strip()   
                msgitems.append(msgitem)            
        return msgitems

    def update_sms(self):
        try:
            self.voice.sms()
            every_message = self.extract_sms(self.voice.sms.html)
            self.all_msgs = list()
            
            for msg in every_message:
                aKey = str(msg['id']) + str(msg['from']) + str(msg['time'])
                if aKey not in self.already_read_ids:
                    self.already_read_ids.append(aKey)
                    self.all_msgs.append(msg)
        except util.ParsingError, e:
            self.all_msgs.append({'from':"", 'time':'12:12', 
                                  'text':e, 'id':'12345'})
