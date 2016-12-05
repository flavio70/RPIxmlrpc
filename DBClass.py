"""
Class definition for DB Operations


CLASS DataBase

  Properties
     - host
     - username
     - password
     - name

  Methods
     - __init__
     - _connect(self)


"""
import os
import logging
import logging.config
import settings
import mysql.connector
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# init logging

logging.config.fileConfig(BASE_DIR + '/logging.conf')
logger = logging.getLogger('xmlServer')



class rpiDB(object):
	def __init__(self):
		self.host = settings.DATABASE['HOST']
		self._username = settings.DATABASE['USER']
		self._password = settings.DATABASE['PASSWORD']
		self._port = settings.DATABASE['PORT']
		self.name = settings.DATABASE['NAME']

	def _connect(self):
		return mysql.connector.connect(user=self._username,password=self._password,host=self.host,database=self.name,port=self._port)



	def set_pin_status(self,rpi,pin,value,user='RPI',operation='Manual'):
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
                        logger.error('DBClass.set_pin_status\n%s'%str(inst))
                        return False
                        conn.close()



	def get_pin_status(self,rpi,pin):
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
                        logger.error('DBClass.get_pin_status\n%s'%str(inst))
                        conn.close()
                        return -1






	def check_pin_mode(self,rpi,pin,mode=0):
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
                        logger.error('DBClass.check_pin_mode\n%s'%str(inst))
                        return False
                        conn.close()




	def get_events(self,rpi):
                res=[]
                try:
                        conn=self._connect()
                        cursor=conn.cursor()
                        querystr="select idT_POWER_SCHEDULE,pin,start_time,stop_time,T_POWER_SCHEDULE.interval from T_POWER_SCHEDULE join T_POWER_MNGMT on (T_POWER_MNGMT_id_powerMngmt=id_powerMngmt) join T_NET using(T_EQUIPMENT_id_equipment) where ip='"+rpi+"';"
                        cursor.execute(querystr)
                        queryres = cursor.fetchall()
                        conn.close()
                        logger.info('Getting Event list for RPI %s ...\n'%rpi)
                        for row in queryres:
                            rdict={'id':row[0],'pin':row[1],'start_time':row[2],'stop_time':row[3],'interval':row[4]}
                            res.append(rdict)        
                            logger.info('Event %s'%rdict)
                        logger.info('...end of List\n')
                        return res
                except Exception as inst:
                        logger.error('DBClass.get_events\n%s'%str(inst))
                        return res
                        conn.close()

	def update_event(self,ev_id,start_time,stop_time):
                try:
                        conn=self._connect()
                        cursor=conn.cursor()
                        querystr="update T_POWER_SCHEDULE set `start_time`='"+start_time+"',`stop_time`='"+stop_time+"' where `idT_POWER_SCHEDULE`="+str(ev_id)
                        cursor.execute(querystr)
                        conn.commit()
                        conn.close()
                        logger.info('event %i has been updated into DB. StartTime %s  StopTime %s'%(ev_id,start_time,stop_time))
                        return True


                except Exception as inst:
                        logger.error('DBClass.update_event\n%s'%str(inst))
                        return False
                        conn.close()






	def delete_event(self,ev_id):
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
                        logger.error('DBClass.delete_event\n%s'%str(inst))
                        return False
                        conn.close()



