# -*- utf-8 -*-
########################################
# PSF license aggrement for logmsg.py
# Developed by Ivan Rybko
# Logmsg
########################################

from singleton import Singleton
import logging

@Singleton
class Logmsg:
    def __init__(self, name):
        if isinstance(name, str):
            self.lname = name
            self.lpath = self.lname + ".log"

    def logmsg(self, message):
        # create file handler which logs even debug messages
        logger = logging.getLogger(self.lname)
        logger.setLevel(logging.DEBUG)
        # create file handler which logs even debug info messages
        loghandler = logging.FileHandler(self.lpath)
        loghandler.setLevel(logging.DEBUG)
        # add format
        frmt = logging.Formatter('{asctime} {name} {levelname:8s} {message}',style='{')
        loghandler.setFormatter(frmt)
        logger.addHandler(loghandler)
        # add message
        logger.debug(message)
        logging.info(message)

    def __call__(self, message):
        self.logmsg(message)

def uselog(*args):
    step1 = args[0]
    step2 = args[1]
    log = Logmsg(step1)
    log(step2)

logs = {
    "static":     Logmsg("staticserver"),
    "dynamic":    Logmsg("dynamicserver"),
    "httpserver": Logmsg("httpserver"),
    "smtpserver": Logmsg("smtpserver"),
    "wsgiserver": Logmsg("wsgiserver"),
    "wsgiapp":    Logmsg("wsgiapp"),
    "imapclient": Logmsg("imapclient"),
    "smtpclient": Logmsg("smtpclient"),
    "httpclient": Logmsg("httpclient"),
    "dbrequest":  Logmsg("dbrequest") 
    }


