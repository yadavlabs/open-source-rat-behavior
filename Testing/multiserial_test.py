import pyMultiSerial as p


ard = p.MultiSerial()
ard.baudrate = 9600
ard.timeout = 2

def port_connection_found_callback(portno, serial):
    print("Port Found: "+portno)

ard.port_connection_found_callback = port_connection_found_callback

def port_read_callback(portno, serial, text):
    print ("Received '"+text+"' from port "+portno)
    pass

ard.port_read_callback = port_read_callback

def port_disconnection_callback(portno):
    print("Port "+portno+" disconnected")

ard.port_disconnection_callback = port_disconnection_callback
ard.Start()
