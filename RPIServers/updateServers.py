#!/usr/bin/env python3

import os
import sys
import time
import ctypes
import logging
import logging.config
from ansicolors import *
from pexpect import pxssh


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR + '/..')


from RPIServers import rpiConst


userID=rpiConst.USER['id']
userPWD=rpiConst.USER['pwd']

# init logging

logging.config.fileConfig(BASE_DIR + '/logging.conf')
logger = logging.getLogger('rpiServer')

def Mbox(title, text, style):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)



if __name__ == '__main__':
        logger.info(ANSI_info('Updating GIT Repositories...'))
        for rpi in rpiConst.SERVER_LIST:
                logger.info('RPI-%s : %s'%(str(rpi['id']),str(rpi['ip'])))
                try:
                        s=pxssh.pxssh()
                        if not s.login(str(rpi['ip']),userID,userPWD):
                                logger.error('SSH Session failed on login')
                                logger.error(str(s))
                        else:
                                logger.info('SSH Session established')
                                s.sendline('cd /srv/RPIxmlrpc')
                                while not s.prompt():time.sleep(1)
                                s.sendline('sudo chown -R %s docs'%userID)
                                while not s.prompt():time.sleep(1)
                                s.sendline('sudo chgrp -R %s docs'%userID)
                                while not s.prompt():time.sleep(1)
                                logger.info('Updating GIT Repo...')
                                s.sendline('git pull')
                                while not s.prompt():time.sleep(1)
                                
                                logger.info(s.before.decode("utf-8"))
                                logger.info('Done!!')
                                #logger.info('Restarting servergpio service...')
                                #s.sendline('sudo service servergpio restart')
                                #while not s.prompt():time.sleep(1)
                                logger.info('Done!!')
                                
                                s.logout()
                        
                except Exception as xxx:
                        logger.error(str(xxx))
                        logger.error(ANSI_fail('RPI-%s : %s'%(str(rpi['id']),str(rpi['ip']))))
                        

        logger.info(ANSI_info('...Done!!'))

