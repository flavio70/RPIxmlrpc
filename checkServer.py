#!/usr/bin/env python3
import xmlrpc.client
import time 
s=xmlrpc.client.ServerProxy('http://151.98.64.32:8080')
print('checking server connection...')
print('... %s Returned'%s.checkServer())

aryon=[]
aryoff=[]
pinList = [2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,17,18]

for i in pinList:
	aryon.append({'gpio':i,'status':'ON','modifier':'xtest'})
	aryoff.append({'gpio':i,'status':'OFF','modifier':'xtest'})

print('checking full on/off cycle')
for count in range(1,10):
	print('Iteration %i'%count)
	s.setGPIO(aryon)
	time.sleep(2)
	s.setGPIO(aryoff)
	time.sleep(2)

print('checking pin by pin on/off cycle')
for count in range(1,10):
	print('Iteration %i'%count)
	for item in pinList:
		s.setGPIO([{'gpio':item,'status':'ON','modifier':'xtest'}])
		time.sleep(1)
	for item in pinList:
		s.setGPIO([{'gpio':item,'status':'OFF','modifier':'xtest'}])
		time.sleep(1)

print('checking pin by pin on/off cycle')
for count in range(1,10):
	print('Iteration %i'%count)
	for item in pinList:
		s.setGPIO([{'gpio':item,'status':'ON','modifier':'xtest'}])
		time.sleep(1)
		s.setGPIO([{'gpio':item,'status':'OFF','modifier':'xtest'}])
		time.sleep(1)	
