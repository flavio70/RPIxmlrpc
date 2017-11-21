"""
XMLRPC setting file for XMLRPC GPIO Server project
"""

import os
import json
import logging
import logging.config


PKG_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = PKG_DIR


DATABASE = {
	'NAME':'KATE',
	'USER':'smosql',
	'PASSWORD': 'sm@ptics',
	'PORT':'3306',
	'HOST':'151.98.52.73'
	}


class _logConst():

    #LOG_DIR = BASE_DIR + '/logs'
    LOG_DIR = '/var/log/GPIO'
    LOG_SETTINGS = BASE_DIR + '/logging.json'
    ERROR_LOG = LOG_DIR +'/xmlserver_errors.log'
    MAIN_LOG = LOG_DIR +'/xmlserver.log'

class frmkLog():
    
    def __init__(self):
        c=_logConst()
        print('\nXMLRPC Server Check package base dir: %s\n'%PKG_DIR)
        with open(c.LOG_SETTINGS,"r",encoding="utf-8") as fd:
            D = json.load(fd)
            D.setdefault('version',1)
            logging.config.dictConfig(D)

    def getLogger(self,name):
        
        return logging.getLogger(name)
