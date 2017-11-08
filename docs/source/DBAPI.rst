DB Access APIs Documentation
****************************


DB Schema Configuration
=======================

- **T_LOCATION Entries**::

	be sure all locations you need to control are present 
	id_location|site|room|row|rack|pos (where pos = 0)


- **T_EQUIPMENT Entries**::

	be sure all RPI are registered into this table using location rack=0 and pos=0 


- **T_POWER_MNGMT Entries**::

	You need one entry for each pin you need to control i.e.
	id_powerMngmt|T_EQUIPMENT_id_equipment|pin|T_LOCATION_id_location|owner
	     1       |   10003                | 2 |      100069          | user1

	T_EQUIPMENT_id_equipment --> reference to RPI id into T_EQUIPMENT table
	T_LOCATION_id_location   --> reference to location we need to control



- **T_POWER_STATUS Entries**::

	You need one initial entry for each pT_POWER_MNGMT entry i.e.
	T_POWER_MNGMT_id_powerMngmt|power_status|last_change          |modifier|remarks                  |manual_status
	     1                     |     1      | 2017-10-19 15:40:00 | ADMIN  |Rack Added to RPI COntrol|     0

	T_POWER_MNGMT_id_powerMngmt --> reference to T_POWER_MNGMT entry


- **Other Tables entries**::

	When running the service also update entries in the following DB tables:

	T_POWER_SCHEDULE
	T_POWER_USAGE
        T_POWER_USAGE_WEEK
	T_RPI_KEEP_ALIVE



Remote Operations
=================



.. automodule :: DBClass
   :members:
