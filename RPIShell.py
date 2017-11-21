#!/usr/bin/env python3

import cmd, sys, os
import xmlrpc.client
import socket
import fcntl
import struct
import re
from DBClass import rpiDB
from ansicolors import *
from settings import frmkLog
import RPi.GPIO as GPIO

PIN_ON=GPIO.HIGH
PIN_OFF=GPIO.LOW

hostip=''

# init DB instance for current host

hostDB=rpiDB()


# init logging

currLog=frmkLog()
logger = currLog.getLogger(os.path.basename(__file__))


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



class RPIShell(cmd.Cmd):
    global DBConnFlag
    prompt = ANSI_success('RPI Shell>>')
    global hostip
    hostip = get_lan_ip()

    def emptyline(self):
        pass
    def preloop(self):
        # settings for GPIOs
        global pinList
        global managedPinList
        global managedPinListStatus
        global hostip
        global hostDB
        global DBConnFlag
        print('\nchecking DB Connectivity...\n')
        

        # loop through pins and set mode to output and state
        # according to value stored into DB

        
        if hostDB.check():
            self.intro = ANSI_info('Welcome to the RPI shell.   Type help or ? to list commands.\n')

            for i in pinList: 

                statusDB=hostDB.get_pin_status(hostip,i)
                if statusDB == -2:
                                        
                        DBConnFlag=False
                        managedPinList = []
                        break
                else:
                        DBConnFlag=True
                        if statusDB == 0:
                                managedPinList.append(i)
                                managedPinListStatus.append('ON')
                        if statusDB == 1:
                                managedPinList.append(i)
                                managedPinListStatus.append('OFF')
        else:
            DBConnFlag=False
            self.intro = ANSI_info('Welcome to the RPI shell.   Type help or ? to list commands.\n')+ANSI_warning('Warning!! DB Connectivity not available\nonly PIN commands available')





    # ----- basic RPI commands -----
  

    def do_setIOpin(self, arg):
        'set GPIO pin to ON/OFF status'
        global hostip
        try:
            if not re.match('[0-9]+',parse(arg)[0]):
                    print('Bad input pin format (Must be an integer)')
                    return
            if not re.match('ON|OFF',parse(arg)[1]):
                    print('Bad input status format (Must be ON|OFF)')
                    return
            
            #s=xmlrpc.client.ServerProxy('http://%s:8080'%hostip)
            #s.setGPIO([{'gpio':parse(arg)[0],'status':parse(arg)[1],'modifier':'RPIShell'}])
            print('Setting pin %s to %s ...'%(parse(arg)[0],parse(arg)[1]))
            if parse(arg)[1] == 'ON':
                    status = PIN_ON
            else:
                    status = PIN_OFF
            GPIO.output(int(parse(arg)[0]), status)
            print('Current status for pin %s : %i'%(parse(arg)[0],GPIO.input(int(parse(arg)[0]))))
        except Exception as excp:
            print ('%s'%str(excp))
            logger.error('%s'%str(excp))


    def do_getIOpin(self, arg):
        'get GPIO pin status'
        global hostip
        try:
            if not re.match('[0-9]+',parse(arg)[0]):
                    print('Bad input pin format (Must be an integer)')
                    return
            print('Current status for pin %s : %i'%(parse(arg)[0],GPIO.input(int(parse(arg)[0]))))
        except Exception as excp:
            print ('%s'%str(excp))
            logger.error('%s'%str(excp))

  

    def do_getPinStatusFromDB(self, arg):
        'Get pin status using MySQL information'
        global managedPinList
        global managedPinListStatus
        global DBConnFlag
        if DBConnFlag:
                print(ANSI_info('Local managed pin list: %s status %s'%(str(managedPinList),str(managedPinListStatus))))
        else:
                print(ANSI_warning('Sorry! connection to DB has not been set!!'))

    def do_bye(self, arg):
        'Stop recording, close the RPI window, and exit:  BYE'
        print('Thank you for using RPI Shell, goodbye!!')
        return True



def parse(arg):
    'Convert a series of zero or more numbers to an argument tuple'
    return tuple(map(str, arg.split()))











if __name__ == '__main__':
    # init list with pin numbers
    pinList = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
    # setting GPIO mode
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    for i in pinList:GPIO.setup(i, GPIO.OUT)
    # init list with managed pin
    managedPinList = []
    managedPinListStatus = []
    RPIShell().cmdloop()
