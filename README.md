# RPI XMLRPC Server
XMLRPC Server for remote GPIO control

Installation
--------------------------

1. #### downoad the require python packages

	>sudo apt-get update

	>sudo apt-get install python3-mysql.connector


2. #### Create the /srv folder
	
	>sudo mkdir /srv


3. #### Get the main code

	> cd /srv

	> sudo git clone git@gitlab.smo:automation/xmlrpc.git


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
