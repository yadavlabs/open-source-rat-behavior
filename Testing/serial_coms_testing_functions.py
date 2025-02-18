# testing arduino and gibson communication
# Author: J. Slack 8/7/23

import serial
import serial.tools.list_ports as port_list


def findPorts():
    ports = list(port_list.components())

    return ports

def openCOMS(ardParams):

    ard = serial.Serial()
    ard.timeout = 2.0
    ard.baudrate = int(ardPArams[0])
    ard.port = ardParams[1]
    ard.open()
    print("Attempting Connection...")
    line = ard.readline()
    print(line)

    return ard

#def arduinoL
