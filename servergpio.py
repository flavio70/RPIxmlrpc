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
import subprocess
from datetime import datetime
from datetime import timedelta
import logging
import logging.config
import RPi.GPIO as GPIO
from DBClass import rpiDB
from ansicolors import *
from settings import frmkLog

#polling time (sec.) used for event polling

POLLING_TIME=60
PIN_ON=GPIO.HIGH
PIN_OFF=GPIO.LOW

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR + '/..')

# init DB instance for current host

hostDB=rpiDB()
DBConnFlag=True

# init logging

currLog=frmkLog()
logger = currLog.getLogger(os.path.basename(__file__))

#logging.config.fileConfig(BASE_DIR + '/logging.conf')
#logger = logging.getLogger('xmlServer')


hostip=''
# init list with pin numbers
pinList = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
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
	global DBConnFlag
	logger.info(ANSI_info("Initializing GPIOs..."))
	logger.debug(ANSI_info("Initializing GPIOs..."))
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)


	# loop through pins and set mode to output and state
	# according to value stored into DB
 
	for i in pinList: 
		GPIO.setup(i, GPIO.OUT, initial=PIN_ON)
		statusDB=hostDB.get_pin_status(hostip,i)
		if statusDB == -2:
                        #GPIO.output(i, PIN_ON)
                        DBConnFlag=False
                        logger.error('DB Connection Not available')
		else:
                        DBConnFlag=True

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
        for i in range(0,len(managedPinList)):
                currentPin=managedPinList[i]
                prePinStatus=prePinStatusList[i]
                currentPinStatus=currentPinStatusList[i]
                logger.info('\tCurrent pin: %i. CurrentValue: %i, OldValue: %i'%(currentPin,currentPinStatus,prePinStatus))

                if prePinStatus == PIN_OFF and currentPinStatus == PIN_ON:
                        #pin passed from OFF to ON
                        #we have to update the off counters for this pin
                        logger.info('\tUpdating time ticks for Current pin: %i set to ON in this current polling time...'%(currentPin))
                        hostDB.update_month_pin_counters(hostip,managedPinList[i],POLLING_TIME)
                        #hostDB.update_week_pin_counters(hostip,managedPinList[i],POLLING_TIME)
                elif prePinStatus == PIN_ON and currentPinStatus == PIN_ON:
                        #pin still ON from previous polling period
                        #we have to update the off counters for this pin
                        logger.info('\tUpdating time ticks for Current pin: %i Still ON in this current polling time...'%(currentPin))
                        hostDB.update_month_pin_counters(hostip,managedPinList[i],POLLING_TIME)
                        #hostDB.update_week_pin_counters(hostip,managedPinList[i],POLLING_TIME)
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
                return ['checkServer','setGPIO','getGPIOStatus','getTemperature']

        def checkServer(self):
                ''' check XMLRPC server service status
 
                :returns: string
                :rtype: json


                '''
                global hostip		
                logger.info ("serving checkServer funct...XMLRPC Server from %s" %hostip)		
                return json.dumps("XMLRPC Server from %s" %hostip)

        def getTemperature(self):
                ''' check XMLRPC server RPI Internal temp
 
                :returns: string
                :rtype: json


                '''
                global hostip		
                logger.info ("serving getTemperature funct...XMLRPC Server from %s" %hostip)
                proc = subprocess.Popen(['/opt/vc/bin/vcgencmd measure_temp'],stdout=subprocess.PIPE, shell=True)
                (out,err) = proc.communicate()
                if not err:

                        temp=str(out.decode('utf-8')).replace("'C","").replace('temp=','').replace('\n','')
                        logger.info("serving getTemperature funct... temp: %s 'C"%temp)
                        return json.dumps(temp)
                else:
                        logger.error('serving getTemperature funct error: \n%s'%str(err))
                        return json.dumps("ERROR")







        def getGPIOStatus(self):
                ''' get current PIN Status
                :returns: string
                :rtype: json


                '''
                global managedPinList
                logger.info ("serving getGPIOStatus XMLRPC funct...")
                #get current status
                currentPinStatusList=get_GPIO_status(managedPinList)
                #for i in range(0,len(managedPinList)):
                #        currentPin=managedPinList[i]
                #        prePinStatus=prePinStatusList[i]
                #        currentPinStatus=currentPinStatusList[i]
                return json.dumps(currentPinStatusList)


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
        if not DBConnFlag:
                logger.info(ANSI_warning('DB was not available when start...Trying to reinit...'))
                init_GPIO()
                
        logger.info(ANSI_info('################## Start new event polling cycle...#####################\n'))

        #update keep Alive table 
        hostDB.update_keep_alive(hostip)    

        #getting event list 
        evl=hostDB.get_events(hostip)
        prePinStatus=get_GPIO_status(managedPinList)

        #managing found events
        logger.info('managing Found events...\n')
        for ev in evl:
            ev_id=int(ev['id'])
            ev_pin=int(ev['pin'])
            ev_interval=int(ev['interval'])
            if int(ev['enabled']) == 0:
                    ev_enabled = False
                    ev_busy = 0
                    ev_enabled_str = 'event Disabled by User'
            else:
                    ev_enabled = True
                    ev_enabled_str = ''
                    ev_busy = 1
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
                    hostDB.update_event(ev_id,start_time.strftime('%Y-%m-%d %H:%M:%S'),stop_time.strftime('%Y-%m-%d %H:%M:%S'),ev_busy)
                    #now check if pin has been set in manual mode
                    logger.info('Checking pin %i status...'%ev_pin)
                    if hostDB.check_pin_mode(hostip,ev_pin):
                            pin_manual = True
                            pin_manualstr = 'Set to Manual mode'
                    else:
                            pin_manual = False
                            pin_manualstr = 'Set to Automatic mode'
                            
                    if (not pin_manual) and ev_enabled:
                            #pin set in auto mode and event enabled by user
                            #we should set the pin OFF
                            set_pin_off = True
                    else:logger.info(ANSI_warning('PIN %i %s %s. Skipping PIN management...'%(ev_pin,pin_manualstr,ev_enabled_str)))

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
                    if hostDB.check_pin_mode(hostip,ev_pin):
                            pin_manual = True
                            pin_manualstr = 'Set to Manual mode'
                    else:
                            pin_manual = False
                            pin_manualstr = 'Set to Automatic mode'
                    
                    if (not pin_manual) and ev_enabled:
                            #pin set in auto mode
                            #we should set the pin ON 
                            set_pin_on = True
                    else:logger.info(ANSI_warning('PIN %i %s %s. Skipping PIN management...'%(ev_pin,pin_manualstr,ev_enabled_str)))



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


