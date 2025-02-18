# Functions for Arduino Communication

import serial
import serial.tools.list_ports as port_list
import time

def findPorts(): #finds and returns devices ocnnected to serial port
	ports = list(port_list.comports())
	
	return ports


def openCOMs(params, selDev): #sets paramaters and opens serial port for device
	# inputs:
	#       params - list containing baudrate and port as strings (ex: params = ['115200', 'COM12']
	#       selDev - string indicating the type of serial port device (ex: selDev = 'Arduino')
	#dev = serial.Serial()
	dev.baudrate = int(params[0])
	dev.port = params[1]
	dev.timeout = 2
	dev.open()
	
	print(selDev + " is open!")
	#time.sleep(0.100)
	
	return dev

def changeSessionParams(ard, params, y):
        # params = ['Initial Training', 'Detection', '60', '10', 'Yes', '3']
        com = []
        for i, param in enumerate(params):
                if i == 0: #alternating ports parameter
                        if param == "Initial Training":
                                com = 'P42'
                        else:
                                com = 'P41'
                elif i == 1: #session type parameter (not used yet)
                        print(param)
                        com = []
                elif i == 2: #session length parameter (in minutes)
                        com = 'P1' + param

                elif i == 3: #response time parameter (in seconds)
                        com = 'P2' + param

                elif i == 4: #forced trials parameter
                        if param == "Yes":
                                com = 'P51'
                        else:
                                com = 'P50'
                elif i == 5: #consecutive error parameter
                        com = 'P3' + param
                if (len(com) > 0):
                        ard.write(com.encode('utf-8'))
                        while ard.in_waiting == 0:
                                pass
                        x = ard.read_until(expected=b'\r\n').decode("utf").rstrip()
                        print(x)
                        y.append(x)

def manualControl(ard, component, state, y):
        
        if component == "left-door":
                if state == "true":
                        com = 'D1'
                else:
                        com = 'D0'
                        
        elif component == "right-door":
                if state == "true":
                        com = 'd1'
                else:
                        com = 'd0'
                        
        elif component == "left-flush":
                com = 'L'
                
        elif component == "right-flush":
                com = 'R'
                
        elif component == "house-light":
                if state == "true":
                        com = 'H1'
                else:
                        com = 'H0'
                        
        elif component == "buzzer":
                if state == "true":
                        com = 'B1'
                else:
                        com = 'B0'
                        
        elif component == "test-sensors":
                if state == "true":
                        com = 'J'
                else:
                        com = 'K'
                        
        elif component == "start":
                com = 'b'
                
        elif component == "stop":
                com = 'Q'
                
        elif component == "pause":
                com = 'p'
                
        ard.write(com.encode('utf-8'))
        readArdData(ard,y)
                #while ard.in_waiting > 0:
                #        x = ard.readline().decode("utf").rstrip()
                #        print(x)
                #        y.append(x)
                                #response_flag = 1

def readArdData(ard,y):
        while ard.in_waiting == 0:
                pass
        x = ard.read_until(expected=b'\r\n').decode("utf").rstrip()
        print(x)
        y.append(x)
        
def waitForArduino(ard,y):
        #print("Entering Arduino Loop!")
        while ard.in_waiting == 0:
                pass
        
        while ard.in_waiting > 0:
                x = ard.read_until(expected=b'\r\n').decode("utf").rstrip()
                dat = x.split(',')
                print(dat[0])
                if dat[0] == "Connected":
                        print(dat[1])
                        y.append(dat[0])

##def waitForArduino(ard, y):
##
##        msg = ""
##        while msg.find("Connected") == -1:
##                while ard.in_waiting == 0:
##                        pass
##                msg = ard.read_until(expected=b'\r\n').decode("utf").rstrip()
##                x = msg.split(",")
##                if x[0] == "Connected":
##                        y.append(x[0])
			
def waitForGibson(gib, y):
        write_uint8(gib,0)
        msg = ""
        while msg.find("Connected") == -1:
                while gib.in_waiting == 0:
                        pass
                msg = gib.read_until(expected=b'\r\n').decode("utf").rstrip()
                print(msg)
                y.append(msg)
                        
def gibsonLoop(gib,y):
        #print("Entering Gibson Loop!")
        write_uint8(gib,1)
        while gib.in_waiting == 0:
                pass
        
        while gib.in_waiting > 0:
                x = gib.read_until(expected=b'\r\n').decode("utf").rstrip()
                print(x)
                y.append(x)
##        flag_1 = 0
##        while True:
##                if (gib.inWaiting() > 0):
##                        x = gib.readline().decode('utf-8')#decode("utf").rstrip()
##                        print(x)
##
##                        y.append(x)
'''			
The following functions are used for communication with the gibson stimulator:
        - 'write_uint8'  = writes parameter corresponding to MATLAB's 'uint8'
        - 'write_int16' = writes parameter corresponding to MATLAB's 'uint16'
        - 'currentConfig' = configures current for writing to gibson
        - 'changePulseNumber' = changes the number of pulses in stimulation pulse-train
        - 'changePulseWidth' = changes the pulse-width of stimulation pulse-train (us)
        - 'changeIPI' = changes the inter-phase interval (us)
        - 'changeFrequency' = changes frequency (Hz)
        - 'changeAmplitude' = changes amplitude of pulse-train (uA)
        - 'changeCV' = changes the coefficient of variation (aperiodicity) of pulse-train (can be 0, 0.1, 0.2,..., 1.0)
        - 'changeStimParams' = changes all stimulation parameters, primarily used for initial setup
        - 'stimulate' = sends command to deliver stimulation based on parameters set by the previous functions

To change stimulation parameters:
        1. the stimulation channel must first be selected
                -ex: write_uint8(gib, 0)
                -In the case here, only a single channel is used (channel 0) and is hard coded. This may be changed for future applications
        2. the parameter to be changed is selected
                -pulse number         -> 1, ex: write_uint8(gib, 1)
                -pulse width          -> 2, ex: write_uint8(gib, 2)
                -inter-phase interval -> 3, ex: write_uint8(gib, 3)
                -frequency            -> 4, ex: write_uint8(gib, 4)
                -amplitude requires sequence of three bytes
                                      -> 5, 6, 7
                -CV                   -> 8
        3. the corresponding parameter value is written
                -ex: if pulse width is selected -> write_uint8(gib, 250)
                -for number of pulses, write_int16 is used to allow for values above 255
        4. Complete example for changing pulse-width:
                write_uint8(gib, 0) #selects channel
                write_uint8(gib, 2) #selects pulse width
                write_uint8(gib, 250) #sets pulse-width to 250us
        5. Complete example for changing amplitude (assuming currentConfig has been called):
                write_uint8(gib, 0) #selects channel
        
        
'''

def readGibData(gib, r_max, y):
        # r_max is used to indicate number of reponses from device
        while gib.in_waiting == 0:
                pass
        i = 0
        while i < r_max: #gib.in_waiting > 0:
                x = gib.read_until(expected=b'\r\n').decode("utf").rstrip()
                print(x)
                y.append(x)
                i = i + 1
                
def readGib(gib, y):
        while gib.in_waiting == 0:
                pass
        x = gib.read_until(expected=b'\r\n').decode("utf").rstrip()
        print(x)
        y.append(x)
        
def write_uint8(gib, val):
#stackoverflow link for writing uint8:
#https://stackoverflow.com/questions/72614604/read-and-write-to-port-with-unit8-format

        gib.write((val).to_bytes(1, byteorder="big"))

def write_int16(gib, val):
#https://blenderartists.org/t/pyserial-how-to-send-numbers-larger-than-256/564195/6

        gib.write((val).to_bytes(2, byteorder="little"))#, signed="True")

def currentConfig(current):
        '''
        help from chatgpt to convert matlab script to python
        -matlab script 'currentconfig.m' located 'C:\Operant_Control\Gibson CV Stim\Matlab App\'
        0-800 for current <---> 0-4095 decimal 
        800 / 4095 = 5.11875 
        value = current * 5.11875 (round to positive int)
        convert to 12-bit binary
        '''
        dac_volt = format(int(round(current * 5.11875)), '012b')
    
        '''
        Correction factor required? Add here ------
    
        Take last 8-bits of dac_volt, convert to uint8 dec and assign to ab_byte
        '''
        ab_byte = int(dac_volt[4:12], 2).to_bytes(1, byteorder='big')
    
        # Take 1st 4-bits of dac_volt and add to back of dac_A configuration
        # Convert to uint8 dec and assign to a_byte
        dacAconfig = format(1, '04b')  # 1 = 0001
        a_byte = int(dacAconfig + dac_volt[0:4], 2).to_bytes(1, byteorder='big')
    
        # Take 1st 4-bits of dac_volt and add to back of dac_B configuration
        # Convert to uint8 dec and assign to b_byte
        dacBconfig = format(9, '04b')  # 9 = 1001
        b_byte = int(dacBconfig + dac_volt[0:4], 2).to_bytes(1, byteorder='big')
    
        return a_byte, b_byte, ab_byte

def changePulseNumber(gib, pnVal, y):
        write_uint8(gib, 0) 
        write_uint8(gib, 1)
        write_int16(gib, int(pnVal))
        readGibData(gib, 2, y)
        
def changePulseWidth(gib, pwVal, y):
        write_uint8(gib, 0) #channel (zero-indexed)
        write_uint8(gib, 2) #parameter index for pulse-width
        write_uint8(gib, int(pwVal))
        readGibData(gib, 2, y)

def changeIPI(gib, ipiVal, y):
        write_uint8(gib, 0)
        write_uint8(gib, 3)
        write_uint8(gib, int(ipiVal))
        readGibData(gib, 2, y)


def changeFrequency(gib, freqVal, y):
        write_uint8(gib, 0)
        write_uint8(gib, 4)
        write_uint8(gib, int(freqVal))
        readGibData(gib, 2, y)


def changeAmplitude(gib, ampVal, y):
        a_byte, b_byte, ab_byte = currentConfig(int(ampVal))
        a_int = int.from_bytes(a_byte, byteorder='big')
        b_int = int.from_bytes(b_byte, byteorder='big')
        ab_int = int.from_bytes(ab_byte, byteorder='big')
        write_uint8(gib, 0)
        write_uint8(gib, 5)
        write_uint8(gib, a_int)
        
        write_uint8(gib, 0)
        write_uint8(gib, 6)
        write_uint8(gib, b_int)
        
        write_uint8(gib, 0)
        write_uint8(gib, 7)
        write_uint8(gib, ab_int)
        readGibData(gib, 3, y)

def changeCV(gib, cvVal, y):
        write_uint8(gib, 0)
        write_uint8(gib, 8)
        write_uint8(gib, int(float(cvVal) * 10)) #cv is read as 0-10 so multiply by 10
        readGibData(gib, 2, y)
        
def changeStimParams(gib, params):
        for i, param in enumerate(params):
                print(param)
                if i == 0:
                        print(type(param))#changeAmplitude(gib, int(param))
                elif i == 1:
                        changeFrequency(gib, int(param))
                elif i == 2:
                        changeCV(gib, float(param))

def stimulate(gib):
        #write_uint8(gib,0 + 4) # '0' is the channel, stim command is channel + 4
        print('stim time')
                        
        

