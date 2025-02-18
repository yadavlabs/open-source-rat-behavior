import serial
import serial.tools.list_ports as port_list



'''def openCOMS(ardParams):

    ard = serial.Serial()
    ard.timeout = 2.0
    ard.baudrate = int(ardParams[0])
    ard.port = ardParams[1]
    ard.open()
    print("Attempting Connection...")
    line = ard.readline()
    print(line)

    return ard

ports = list(port_list.comports())

for port in ports:
    print(port)

ardParams = ['9600', 'COM6']

ard = openCOMS(ardParams)

ard.close()
'''
ard.write(b's60')
if (ard.inWaiting() > 0):
    print(ard.readline().decode('utf-8'))
          
print('here')
