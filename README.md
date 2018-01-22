# RPI XMLRPC Server
XMLRPC Server for remote GPIO control

Installation
--------------------------

1. #### downoad the require python packages

	>sudo apt-get update

	>sudo apt-get install python3-mysql.connector python3-pexpect


2. #### Create the /srv folder
	
	>sudo mkdir /srv


3. #### Get the main code

	> cd /srv

	> sudo git clone https://github.com/flavio70/xmlrpc.git


Configuration
--------------------------




- configure the reference to your mysqlDB (KATE DB)  by editing /srv/xmlrpc/settings.py file

	>NAME

	>USER

	>PASSWORD

	>PORT

	>HOST



- Create the log directory

	>sudo mkdir /var/log/GPIO

	>sudo chmod 777 -R /var/log/GPIO


- Copy the initialization service file

	>sudo cp /srv/xmlrpc/initd /etc/init.d/servergpio

	>sudo chmod +x /etc/init.d/servergpio


- Enable the service

	>sudo systemctl enable servergpio

- Start the service

	>sudo service servergpio start
	

Usage
--------------------------

The server runs on RPI Power Management chassis and works together with KATE/PowerManagement application (WEB UI)
and an instance of MYSQL DB with (KATE DB).
Is able to perform two kinds of services

- Manual services

    The user asks to switch ON/OFF racks declared as manual into DB (using WEB UI)
    The server acts istantly the request over the correspondig GPIO pin and updates the DB

- Automatic services

    Every polling time (default is 60 secs) the Server ask the pin status and programmed scheduler to DB.
    The server acts the conseguent actions, switching ON/OFF the correspondig GPIO pin and updates the DB

For both services, scheduler events and pin status can be set into DB using the WEB UI
Log trace of every operation will be saved into rotational log file:

    /var/log/GPIO/xmlserver.log

    
