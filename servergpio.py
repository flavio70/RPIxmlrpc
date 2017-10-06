#!/usr/bin/env python3
from xmlrpc.server import SimpleXMLRPCServer
import json
import socket
import threading
from socketserver import ThreadingMixIn
import sys
import os
import fcntl
import struct
import time
from datetime import datetime
from datetime import timedelta
import logging
import logging.config
import RPi.GPIO as GPIO
from DBClass import rpiDB
from ansicolors import *

#polling time (sec.) used for event polling

POLLING_TIME=60
PIN_ON=GPIO.LOW
PIN_OFF=GPIO.HIGH

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# init DB instance for current host

hostDB=rpiDB()


# init logging

logging.config.fileConfig(BASE_DIR + '/logging.conf')
logger = logging.getLogger('xmlServer')


hostip=''
# init list with pin numbers
pinList = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
# init list with managed pin
managedPinList = []



def get_interface_ip(ifname):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15].encode('utf-8')))[20:24])



def get_lan_ip():
	ip = socket.gethostbyname(socket.gethostname())
	if ip.startswith("127."):
		interfaces = ["eth0","wlan0"]
		for ifname in interfaces:
			try:
				ip = get_interface_ip(ifname)
				break
			except IOError:
				pass
	return ip


def init_GPIO():
	# settings for GPIOs
	global pinList
	global managedPinList
	global hostip
	global hostDB
	logger.info(ANSI_info("Initializing GPIOs..."))
	logger.debug(ANSI_info("Initializing GPIOs..."))
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)


	# loop through pins and set mode to output and state
	# according to value stored into DB
 
	for i in pinList: 
		GPIO.setup(i, GPIO.OUT, initial=PIN_OFF)
		statusDB=hostDB.get_pin_status(hostip,i)

		if statusDB == -1:
                        GPIO.output(i, PIN_ON)

		if statusDB == 0:
                        GPIO.output(i, PIN_ON)
                        hostDB.set_pin_status(hostip,str(i),'0','RPI','Restore Rack Power status to ON after Power Management (RPI) REBOOT')
                        managedPinList.append(i)
		if statusDB == 1:
		        GPIO.output(i, PIN_OFF)
		        hostDB.set_pin_status(hostip,str(i),'1','RPI','Restore Rack Power status to OFF after Power Management (RPI) REBOOT')
		        managedPinList.append(i)
	logger.info(ANSI_info('Registered Pin List for current host: %s'%str(managedPinList)))
	logger.debug(ANSI_info('Registered Pin List for current host: %s'%str(managedPinList)))


def get_GPIO_status(pinArray):
        #return list containing status for each element in pinArray
        res=[]
        for i in pinArray:
                res.append(GPIO.input(i))
        logger.info('Current status for pinList %s = %s'%(str(pinArray),str(res)))
        logger.debug('Current status for pinList %s = %s'%(str(pinArray),str(res)))
        return res



def check_GPIO_status(pin,status):
        #check the status 1/0 of the selected pin
        r=GPIO.input(pin)
        if r == status:
                return True
        else:
                return False



def update_GPIO_counters(prePinStatusList):
        '''update DB conters ticks for managedPinList
        :param str prePinStatusList: list of status before waiting time
        '''
        global managedPinList
        logger.info(ANSI_info('Updating GPIO Counters for pin: %s...'%(str(managedPinList))))
        logger.info('Previous status for pinList %s = %s'%(str(managedPinList),str(prePinStatusList)))
        #get current status
        currentPinStatusList=get_GPIO_status(managedPinList)
        for i in range(0,len(managedPinList)-1):
                currentPin=managedPinList[i]
                prePinStatus=prePinStatusList[i]
                currentPinStatus=currentPinStatusList[i]
                logger.info('\tCurrent pin: %i. CurrentValue: %i, OldValue: %i'%(currentPin,currentPinStatus,prePinStatus))

                if prePinStatus == 1 and currentPinStatus == 0:
                        #pin passed from OFF to ON
                        #we have to update the off counters for this pin
                        logger.info('\tUpdating time ticks for Current pin: %i set to ON in this current polling time...'%(currentPin))
                        hostDB.update_month_pin_counters(hostip,managedPinList[i],POLLING_TIME)
                elif prePinStatus == 0 and currentPinStatus == 0:
                        #pin still ON from previous polling preiod
                        #we have to update the off counters for this pin
                        logger.info('\tUpdating time ticks for Current pin: %i Still ON in this current polling time...'%(currentPin))
                        hostDB.update_month_pin_counters(hostip,managedPinList[i],POLLING_TIME)
                else:logger.info('\tCurrent pin: %i set to OFF. Skipping time ticks update...'%(currentPin))
                        


class ServerFuncts: 

        def __init__(self):
                #make all of the string functions availabel through
                #string.func_name
                import string
                self.string = string

        def _listMethods(self):
                #implement this method so that system.listMethods
                #knows to advertise the string methods
                logger.info('serving listMethods funct ...')
                return ['checkServer','setGPIO']

        def checkServer(self):
                ''' check XMLRPC server service status
 
                :returns: string
                :rtype: json


                '''
                global hostip		
                logger.info ("serving checkServer funct...XMLRPC Server from %s" %hostip)		
                return json.dumps("XMLRPC Server from %s" %hostip)



        def setGPIO(self,gpio):
                '''set GPIO pin to status value and update DB.

                :param list gpio: list of Dictionary in the form: {'gpio':pinid,status:'ON|OFF','modifier':userid} 

                >>> setGPIO([{'gpio':5,'status':'ON','modifier':'ippolf'},{'gpio':6,'status':'OFF','modifier':'ippolf'}])
                '''

                global hostip
                for item in gpio:
                    status = str(item['status']).upper()
                    gpiopin = str(item['gpio'])
                    modifier = str(item['modifier'])
                    try:
                        if  status == 'ON':
                            GPIO.output(int(gpiopin), PIN_ON)
                            hostDB.set_pin_status(hostip,gpiopin,'0',modifier,'Change Rack Power Status to ON')
                        else:
                            GPIO.output(int(gpiopin), PIN_OFF)
                            hostDB.set_pin_status(hostip,gpiopin,'1',modifier,'Change Rack Power status to OFF')
                    except exception as inst:
                        logger.error(str(inst))
                        
                    logger.info ("serving setGPIO funct... Pin: %s , Status %s from user %s " % (gpiopin,status,modifier) )
                
                return json.dumps(gpio)




class ThreadedSimpleXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    """ handle requests in a separate thread."""


if __name__ == '__main__':

    hostip = get_lan_ip()
    #server = SimpleXMLRPCServer((hostip, 8080))
    server = ThreadedSimpleXMLRPCServer((hostip, 8080))
    server.register_function(pow)
    server.register_introspection_functions()
    server.register_instance(ServerFuncts(), allow_dotted_names=True)
    server.register_multicall_functions()

    init_GPIO()


    serverThread = threading.Thread(target = server.serve_forever)
    serverThread.daemon = True


    try:
        serverThread.start()
    except Exception as inst:
        logger.error(ANSI_fail(str(inst)))


    logger.info('Serving XML-RPC requests  on %s  port 8080...' %hostip)



    while True:
        logger.info(ANSI_info('################## Start new event polling cycle...#####################\n'))
    

        #getting event list 
        evl=hostDB.get_events(hostip)
        prePinStatus=get_GPIO_status(managedPinList)

        #managing found events
        logger.info('managing Found events...\n')
        for ev in evl:
            ev_id=int(ev['id'])
            ev_pin=int(ev['pin'])
            ev_interval=int(ev['interval'])
            now=datetime.now()
            to_be_served= False
            set_pin_on = False
            set_pin_off = False
            start_str='%s %s %s %s %s'%(ev['start_time'].year,ev['start_time'].month,ev['start_time'].day,ev['start_time'].hour,ev['start_time'].minute)
            stop_str='%s %s %s %s %s'%(ev['stop_time'].year,ev['stop_time'].month,ev['stop_time'].day,ev['stop_time'].hour,ev['stop_time'].minute)
            start_time=datetime.strptime(start_str,'%Y %m %d %H %M')
            stop_time=datetime.strptime(stop_str,'%Y %m %d %H %M')
            logger.info('Found Event id %i for pin %i.\n StartTime: %s StopTime %s'%(ev_id,ev_pin,start_time,stop_time))
            
            if now >= start_time:
                    #in this case we have to update the event start time in the DB
                    #start_time+interval
                    to_be_served = True
                    logger.info('current Time %s >= event startTime %s'%(now,start_time))
                    logger.info('Updating DB event StartTime...')
                    start_time=start_time+timedelta(minutes=ev_interval)
                    hostDB.update_event(ev_id,start_time.strftime('%Y-%m-%d %H:%M:%S'),stop_time.strftime('%Y-%m-%d %H:%M:%S'),1)
                    #now check if pin has been set in manual mode
                    logger.info('Checking pin %i status...'%ev_pin)
                    if not hostDB.check_pin_mode(hostip,ev_pin):
                            #pin set in auto mode
                            #we should set the pin OFF
                            set_pin_off = True
                    else:logger.info(ANSI_info('PIN %i set in manual Mode. Skipping PIN management...'%ev_pin))

            if now >= stop_time:
                    #in this case we have to update the event stop time in the DB
                    #stop_time+interval
                    to_be_served = True
                    logger.info('current Time %s >= event stopTime %s'%(now,start_time))
                    logger.info('Updating DB event StopTime...')
                    stop_time=stop_time+timedelta(minutes=ev_interval)
                    hostDB.update_event(ev_id,start_time.strftime('%Y-%m-%d %H:%M:%S'),stop_time.strftime('%Y-%m-%d %H:%M:%S'),0)
                    #now check if pin has been set in manual mode
                    logger.info('Checking pin %i status...'%ev_pin)
                    if not hostDB.check_pin_mode(hostip,ev_pin):
                            #pin set in auto mode
                            #we should set the pin ON 
                            set_pin_on = True
                    else:logger.info(ANSI_warning('PIN %i set in manual Mode. Skipping PIN management...'%ev_pin))


            if (set_pin_off and not set_pin_on):
                    #We have to set the pin OFF (just if is ON)
                    #we are at the begin of a scheduled event
                    if check_GPIO_status(ev_pin, PIN_ON):
                            #pin is ON
                            logger.info(ANSI_success('Pin %i is ON. Setting to OFF..'%ev_pin))
                            GPIO.output(ev_pin, PIN_OFF)
                            #set pin status into DB
                            hostDB.set_pin_status(hostip,str(ev_pin),'1','Scheduled','Change Rack Power Status to OFF')
                            #set pin mode to Auto? (no should be already done)
                            logger.info('Planned Event Start.pin %i set OFF because event %i\n'%(ev_pin,ev_id))
                    else:
                            logger.info(ANSI_warning('PIN %i already OFF. Skipping PIN management...'%ev_pin))



            if (not set_pin_off and set_pin_on):
                    #We have to set the pin ON(just if is OFF and not pending events)
                    #we are at the end of a scheduled event
                    if check_GPIO_status(ev_pin, PIN_OFF):
                            #pin is OFF
                            if hostDB.check_busy_events(hostip,ev_pin,1):
                                    #we have other events active on same pin
                                    logger.info(ANSI_warning('Keeping Pin %i OFF because other events pending\n'%ev_pin))
                            else:
                                    logger.info(ANSI_success('Pin %i is OFF. Setting to ON..'%ev_pin))
                                    GPIO.output(ev_pin, PIN_ON)
                                    #set pin status into DB
                                    hostDB.set_pin_status(hostip,str(ev_pin),'0','Scheduled','Change Rack Power Status to ON')
                                    #set pin mode to Auto? (no should be already done)
                                    logger.info('Planned Event Stop. pin %i set ON because event %i\n'%(ev_pin,ev_id))
     
                    else:logger.info(ANSI_warning('PIN %i already ON. Skipping PIN management...'%ev_pin))



            if (set_pin_on and set_pin_off):
                    #We have to set the pin ON(just if is OFF)
                    #but just in case the ev_interval is set to 0 (event not recurrent)
                    if (check_GPIO_status(ev_pin, PIN_OFF) and ev_interval == 0):
                            #pin is OFF
                            if hostDB.check_busy_events(hostip,ev_pin,1):
                                    #we have other events active on same pin
                                    logger.info(ANSI_warning('Keeping Pin %i OFF because other events pending\n'%ev_pin))
                                    if ev_interval == 0:#event not recurrent
                                            hostDB.delete_event(ev_id)
                            else:
                                    logger.info(ANSI_success('Pin %i is OFF. Setting to ON..'%ev_pin))
                                    GPIO.output(ev_pin, PIN_ON)
                                    #set pin status into DB
                                    hostDB.set_pin_status(hostip,str(ev_pin),'0','Scheduled','Change Rack Power Status to ON')
                                    #delete event from DB
                                    hostDB.delete_event(ev_id)
                                    #set pin mode to Auto? (no should be already done)
                                    logger.info('Planned Event Start. pin %i set ON because event %i\n'%(ev_pin,ev_id))
                    else:
                            logger.info(ANSI_warning('PIN %i already ON. Skipping PIN management...'%ev_pin))
                            if ev_interval == 0:#event not recurrent
                                    hostDB.delete_event(ev_id)



                    
            if not to_be_served:
                    logger.info('Event timing windows outside current time. Skipping...\n')

        logger.info(ANSI_info('...End of events'))
        logger.info(ANSI_info('...waiting for %i seconds...'%POLLING_TIME))
        time.sleep(POLLING_TIME)
        logger.info(ANSI_info('...polling cycle finished!\n'))
        update_GPIO_counters(prePinStatus)


