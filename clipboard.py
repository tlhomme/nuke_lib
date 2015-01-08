#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2014-04-03 14:44
@summary: small utility to have copy paste between users in nuke
@author: olavenant
"""

import nuke
import os 
from PySide import QtGui
import smtplib
import getpass
from email.mime.text import MIMEText

XCHANGE_PATH = '/s/prods/lap/_tmp/clipboard_comp/'

def setupMyFolder():
    path = XCHANGE_PATH+'%s/clipboard.nk'%getpass.getuser()
    dirpath = os.path.dirname(path)
    if not os.path.exists(dirpath):
        try:
            os.makedirs(dirpath)
        except Exception, e:
            print e

def sendMail(sender, dest, subject, body):
    frommail = sender
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = frommail
    msg['To'] = dest
    s = smtplib.SMTP('aspmx.l.google.com')
    destList = [dest]
    if "," in dest:
        destList = dest.split(",")
    s.sendmail(frommail, destList, msg.as_string())
    s.quit()


def pasteClipboard():
    '''
    @summary: 
    @param :
    @result: 
    '''
    path = XCHANGE_PATH+'%s/clipboard.nk'%getpass.getuser()
    nuke.nodePaste(path)

def createClipboard(file):
    '''
    @summary: 
    @param file:
    @result: 
    '''
    nodes = nuke.selectedNodes()
    if nodes != None:
        nuke.nodeCopy("%clipboard%")
        nuke.nodeCopy( file )
    else:
        nuke.message('Selecte nodes')

def copyClipboard():
    '''
    @summary: 
    @param :
    @result: 
    '''
    # create file clipboad.nk
    path = XCHANGE_PATH
    list = os.listdir(path)
    list.sort()
    names = ' '.join(list)

    clipboardPanel = nuke.Panel('Clipboard')
    clipboardPanel.addEnumerationPulldown('Name', names)
    ret = clipboardPanel.show()
    if ret:
        file = path + "/" + clipboardPanel.value('Name') + "/" + "clipboard.nk"

        createClipboard(file)
        print "Clipboard to "+ clipboardPanel.value('Name')

        # send a message
        sender = '%s@mikrosimage.eu' %getpass.getuser()
        receiver = '%s@mikrosimage.eu' %clipboardPanel.value('Name')
        message = """Hello dear,
    %s send you a clipboard in nuke.
    You can paste it by pressing ctrl+shift+v inside nuke.
                                                            Cheers."""%getpass.getuser()
        # sendMail(sender,receiver, "Nuke Clipboard", message)
