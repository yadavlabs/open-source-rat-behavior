# Functions for Arduino Communication

import serial
import serial.tools.list_ports as port_list
import asyncio

def findPorts():
	ports = list(port_list.comports())
	
	return ports


def openCOMs(ardParams):
	
	ard = serial.Serial()
	ard.baudrate = int(ardParams[0])
	ard.port = ardParams[1]
	ard.open()
	print("Arduino is open!")
	print(ardParams)
	
	return ard
	

def arduinoLoop(ard,y):
	print("Entering Arduino Loop!")
	
	flag_1 = 0
	
	while True:
		if (ard.inWaiting() > 0):
			
			x = ard.readline().decode("utf").rstrip()
				
			print(x)

			y.append(x)
			
