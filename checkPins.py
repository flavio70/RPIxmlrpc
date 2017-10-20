#!/usr/bin/env python3
#from xmlrpc.server import SimpleXMLRPCServer
#import json
#import socket
#import threading
#from socketserver import ThreadingMixIn
#import sys
import os
#import fcntl
#import struct
import time
#from datetime import datetime
#from datetime import timedelta
import logging
import logging.config
import RPi.GPIO as GPIO
#from DBClass import rpiDB


PIN_ON=GPIO.HIGH
PIN_OFF=GPIO.LOW

#polling time (sec.) used for event polling

POLLING_TIME=2
POLLING_TIME_ALL=5

BASE_DIR = os.path.dirname(os.path.abspath(__file__))



# init logging

logging.config.fileConfig(BASE_DIR + '/logging.conf')
logger = logging.getLogger('xmlServer')


# init list with pin numbers
pinList = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]



def init_GPIO():
	# settings for GPIOs
	
	logger.info("Initializing GPIOs...")
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)


	# loop through pins and set mode to output and state

 
	for i in pinList: 
		GPIO.setup(i, GPIO.OUT, initial=PIN_OFF)
	logger.info("...Initialized!!")
	time.sleep(5)




if __name__ == '__main__':

    

    init_GPIO()

    logger.info('Testing GPIO Functionality...')



    for i in pinList:
            logger.info('\tChecking Pin %i ON for %i secs...'%(i,POLLING_TIME))
            GPIO.setup(i, GPIO.OUT, initial=PIN_ON)
            time.sleep(POLLING_TIME)
            GPIO.setup(i, GPIO.OUT, initial=PIN_OFF)
            logger.info('\t...Done!!!\n')
            time.sleep(1)
            
    time.sleep(2)
    logger.info('\tChecking ALL Pin ON for %i secs...'%(POLLING_TIME_ALL))
    for i in pinList:
            GPIO.setup(i, GPIO.OUT, initial=PIN_ON)        
    time.sleep(POLLING_TIME_ALL)
    logger.info('\tSetting ALL Pin OFF ...')
    for i in pinList:
            GPIO.setup(i, GPIO.OUT, initial=PIN_OFF)

    
    logger.info('End of Execution')

