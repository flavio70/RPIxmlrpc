"""
.. module::DBClass
   :platform: Unix
   :synopsis:Class definition for DB Operations

.. moduleauthor:: Flavio Ippolito <flavio.ippolito@sm-optics.com>

"""
import os
import logging
import logging.config
import settings
import mysql.connector
from datetime import datetime
from ansicolors import *


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# init logging

logging.config.fileConfig(BASE_DIR + '/logging.conf')
logger = logging.getLogger('xmlServer')



class rpiDB(object):
	'''We use this class for managing MySQL DB access.

	:param str host: MySQl DB Host IP Address
	:param str name: MySql DB Name
	:param str _username: MySql DB User
	:param str _password: MySql DB user password

	'''
	def __init__(self):
		self.host = settings.DATABASE['HOST']
		self._username = settings.DATABASE['USER']
		self._password = settings.DATABASE['PASSWORD']
		self._port = settings.DATABASE['PORT']
		self.name = settings.DATABASE['NAME']

	def _connect(self):
		return mysql.connector.connect(user=self._username,password=self._password,host=self.host,database=self.name,port=self._port)



	def set_pin_status(self,rpi,pin,value,user='RPI',operation='Manual'):
                '''Set into DB the current pin information.

                :param str rpi: Raspberry IP address
                :param str pin: Raspberry pin number
                :param str value: pin status to be set
                :param user: User id for DB Operation 
                :type user: str or None
                :param operation: Operation type (Manual|Automatic)
                :type operation: str or None
                :returns: bool.
                :raises: Exception

                >>> DB1.set_pin_status('10.10.20.1','5','0')
                True

                '''
                try:
                        conn=self._connect()
                        cursor=conn.cursor()
                        querystr="insert into T_POWER_STATUS(select id_powerMngmt,'"+value+"',null,'"+user+"','"+operation+"',manual_status from T_POWER_MNGMT join T_POWER_STATUS on(id_powerMngmt=T_POWER_MNGMT_id_powerMngmt) join T_NET using(T_EQUIPMENT_id_equipment) where ip='"+rpi+"' and pin="+pin+" order by last_change desc limit 1);"
                        cursor.execute(querystr)
                        conn.commit()
                        conn.close()
                        logger.info('status %s for pin %s updated into DB. %s'%(value,pin,operation))
                        return True
                except Exception as inst:
                        logger.error(ANSI_fail('DBClass.set_pin_status\n%s'%str(inst)))
                        return False
                        conn.close()



	def get_pin_status(self,rpi,pin):
                '''Get from  DB the current pin information.

                :param str rpi: Raspberry IP address
                :param int pin: Raspberry pin number
                :returns: pin status
                :rtype: int
                :raises: Exception

                >>> DB1.get_pin_status('10.10.20.1',5)
                '0'

                '''

                try:
                        res=-1
                        conn=self._connect()
                        cursor=conn.cursor()
                        querystr="select power_status from T_POWER_STATUS join T_POWER_MNGMT on (T_POWER_MNGMT_id_powerMngmt=id_powerMngmt) join T_NET using(T_EQUIPMENT_id_equipment) where ip='"+rpi+"' and pin="+str(pin)+" order by last_change desc limit 1;"
                        cursor.execute(querystr)
                        queryres = cursor.fetchone()
                        res=queryres[0]
                        conn.close()
                        logger.info('Current DB status for pin %i : %i'%(pin,res))

                        return res

                except Exception as inst:
                        logger.error(ANSI_fail('DBClass.get_pin_status\n%s'%str(inst)))
                        conn.close()
                        return -1






	def check_pin_mode(self,rpi,pin,mode=0):
                '''check the actual pin mode from DB.

                :param str rpi: Raspberry IP address
                :param int pin: Raspberry pin number
                :param mode: pin mode to be checked(0,1) 0 for Automatic, 0 for Manual 
                :type mode: str or None
                :returns: bool.
                :raises: Exception

                >>> DB1.check_pin_mode('10.10.20.1','5',0)
                True

                '''


                res=False
                res_str='False'
                mode_str='Automatic'
                if mode != 0: mode_str='Manual'
                try:
                        conn=self._connect()
                        cursor=conn.cursor()
                        querystr="select manual_status from T_POWER_STATUS join T_POWER_MNGMT on (T_POWER_MNGMT_id_powerMngmt=id_powerMngmt) join T_NET using(T_EQUIPMENT_id_equipment) where ip='"+rpi+"' and pin="+str(pin)+" order by last_change desc limit 1;"
                        cursor.execute(querystr)
                        queryres = cursor.fetchone()
                        if len(queryres)==0:res=False
                        if queryres[0] == mode:
                                res=True
                                res_str='True'
                        conn.close()
                        logger.info('Checking pinmode %i(%s) for pin %i ... %s'%(mode,mode_str,pin,res_str))
                        return res
                except Exception as inst:
                        logger.error(ANSI_fail('DBClass.check_pin_mode\n%s'%str(inst)))
                        return False
                        conn.close()




	def get_events(self,rpi):
                '''Get from  DB the events list related to selected RPI.

                :param str rpi: Raspberry IP address
                :returns: list of events
                :rtype: list of dict
                :raises: Exception

                >>> DB1.get_events('10.10.20.1')
                [{'start_time': datetime.datetime(2017, 1, 31, 15, 10), 'stop_time': datetime.datetime(2017, 1, 31, 15, 15), 'id': 8, 'pin': 4, 'interval': 1440}]

                '''   

                res=[]
                try:
                        conn=self._connect()
                        cursor=conn.cursor()
                        querystr="select idT_POWER_SCHEDULE,pin,start_time,stop_time,T_POWER_SCHEDULE.interval,busy from T_POWER_SCHEDULE join T_POWER_MNGMT on (T_POWER_MNGMT_id_powerMngmt=id_powerMngmt) join T_NET using(T_EQUIPMENT_id_equipment) where ip='"+rpi+"';"
                        cursor.execute(querystr)
                        queryres = cursor.fetchall()
                        conn.close()
                        logger.info('Getting Event list for RPI %s ...\n'%rpi)
                        for row in queryres:
                            rdict={'id':row[0],'pin':row[1],'start_time':row[2],'stop_time':row[3],'interval':row[4],'busy':row[5]}
                            res.append(rdict)        
                            logger.info('Event %s'%rdict)
                        logger.info('...end of List\n')
                        return res
                except Exception as inst:
                        logger.error(ANSI_fail('DBClass.get_events\n%s'%str(inst)))
                        return res
                        conn.close()

                        

	def update_event(self,ev_id,start_time,stop_time,busy=0):
                '''Update event start & stop time.

                :param int ev_id: DB event id to be updated
                :param str start_time: (in the format '%Y-%m-%d %H:%M:%S')
                :param str stop_time: (in the formant: '%Y-%m-%d %H:%M:%S')
                :param int busy: (0,1) 1 in case
                :returns: bool
                :raises: Exception

                >>> DB1.update_event(3,'2016-10-12 17:00:00','2016-10-12 17:30:00' )
                True

                '''
                try:
                        conn=self._connect()
                        cursor=conn.cursor()
                        querystr="update T_POWER_SCHEDULE set `start_time`='"+start_time+"',`stop_time`='"+stop_time+"',`busy`='"+str(busy)+"' where `idT_POWER_SCHEDULE`="+str(ev_id)
                        cursor.execute(querystr)
                        conn.commit()
                        conn.close()
                        logger.info('event %i has been updated into DB. StartTime %s  StopTime %s'%(ev_id,start_time,stop_time))
                        return True


                except Exception as inst:
                        logger.error(ANSI_fail('DBClass.update_event\n%s'%str(inst)))
                        return False
                        conn.close()






	def delete_event(self,ev_id):
                '''Delete event from DB

                :param int ev_id: DB event id to be deleted
                :returns: bool
                :raises: Exception

                >>> DB1.delete_event(3)
                True

                '''


                try:
                        conn=self._connect()
                        cursor=conn.cursor()
                        querystr="DELETE FROM `T_POWER_SCHEDULE` where `idT_POWER_SCHEDULE`="+str(ev_id)
                        cursor.execute(querystr)
                        conn.commit()
                        conn.close()
                        logger.info('event %i has been removed from DB.'%ev_id)
                        return True


                except Exception as inst:
                        logger.error(ANSI_fail('DBClass.delete_event\n%s'%str(inst)))
                        return False
                        conn.close()



	def check_busy_events(self,rpi,pin,busy=1):
                '''Check presence into DB about events related to selected RPI.
                belonging to pin and havin busy value
                :param str rpi: Raspberry IP address
                :param str pin: Raspberry pin id
                :parm str busy: POWER_SCHEDULE busy param to be checked
                :returns: True/False
                :rtype: bool
                :raises: Exception

                >>> DB1.check_busy_events('10.10.20.1','2','1')
                
                '''   

                res=False
                try:
                        conn=self._connect()
                        cursor=conn.cursor()
                        querystr="select idT_POWER_SCHEDULE,pin,busy from T_POWER_SCHEDULE join T_POWER_MNGMT on (T_POWER_MNGMT_id_powerMngmt=id_powerMngmt) join T_NET using(T_EQUIPMENT_id_equipment) where ip='"+rpi+"' and pin = '"+str(pin)+"' and busy = '"+str(busy)+"';"
                        cursor.execute(querystr)
                        queryres = cursor.fetchall()
                        conn.close()
                        logger.info('Checking busy (%s) Events list for RPI %s\nbelonging to pin %s ...\n'%(str(busy),rpi,str(pin)))
                        if queryres:
                            res=True       
                            logger.info('... %i Events Found!!\n'%len(queryres))
                        else:
                            logger.info('... No Events Found!!\n')
                        return res
                except Exception as inst:
                        logger.error(ANSI_fail('DBClass.check_busy_events\n%s'%str(inst)))
                        return res
                        conn.close()



	def update_month_pin_counters(self,rpi,pin,update_time):
                '''update statistics for current rpi and selected pin
                :param str rpi: Raspberry IP address
                :param str pin: Raspberry pin id

                :param str update_time: time ticks to be added to current counters
                :returns: True/False
                :rtype: bool
                :raises: Exception

                >>> DB1.update_month_pin_stats('10.10.20.1','15','12','1')
                
                '''
                res=False
                try:
                        conn=self._connect()
                        cursor=conn.cursor()
                        querystr="insert into T_POWER_USAGE (select null,concat(year(now()),'-',month(now())) as time_frame,T_POWER_MNGMT_id_powerMngmt,0 from T_POWER_MNGMT join T_POWER_STATUS on(id_powerMngmt=T_POWER_MNGMT_id_powerMngmt) join T_NET using(T_EQUIPMENT_id_equipment) where ip='"+rpi+"' and pin="+str(pin)+" order by last_change desc limit 1) on duplicate key update hour_counter=hour_counter+"+str(update_time)
                        cursor.execute(querystr)
                        conn.commit()
                        conn.close()
                        logger.info('Updated counters for RPI %s pin %s by %s ticks.'%(rpi,str(pin),str(update_time)))
                        res=True
                        return res
                except Exception as inst:
                        logger.error(ANSI_fail('DBClass.update_month_pin_stats\n%s'%str(inst)))
                        return res
                        conn.close()
                
