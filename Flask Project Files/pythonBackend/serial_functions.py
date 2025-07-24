# Functions for Arduino Communication

import serial
import serial.tools.list_ports as port_list
import time
import random

def findPorts(): #finds and returns devices ocnnected to serial port
	ports = list(port_list.comports())
	
	return ports

def changeSessionParams(ard, params, y):
        """ changes all rrelevant session parameters for running 2AFC experiments
        # Inputs:
        #       ard    - serial port object for task arduino
        #       params - dict of paramaters to updated, ex: params = ['Initial Training', 'Detection', '60', '10', 'Yes', '3']
        #       y      - data stream variable for storing/sending display information to angular
        """
        print(params)
        com = []
        # sets session
        if params[0] == "Initial Training":
                ard.write('P42'.encode('utf-8'))
                
        else:
                ard.write('P41'.encode('utf-8'))
                
                if params[1] == "Detection":
                        ard.write('P80'.encode('utf-8'))
                        
                        ard.write(('P6' + params[7]).encode('utf-8'))
                        
                else:
                        ard.write('P81'.encode('utf-8'))
                        
                        ard.write(('P6' + params[7]).encode('utf-8'))
                        
                        ard.write(('P7' + params[8]).encode('utf-8'))
                        


        # sets session length
        ard.write(('P1' + params[2]).encode('utf-8'))
        

        # sets response time
        ard.write(('P2' + params[3]).encode('utf-8'))
        

        # sets forced trials
        if params[4] == "Yes":
                ard.write('P51'.encode('utf-8'))
                
        else:
                ard.write('P50'.encode('utf-8'))
                

        # set consecutive error
        ard.write(('P3' + params[5]).encode('utf-8'))
        readResponse(ard, y)

def readResponse(ard, y):
        while ard.in_waiting == 0: #do nothing until bytes are available to read
                pass
        #a = ard.read_until('\r\n')
        #print(a)
        while ard.in_waiting > 0: # read all bytes available
                x = ard.read_until(expected=b'\r\n').decode("utf").rstrip()
        #x = a.decode("utf").rstrip() # decode bytes to string
                print(x)
                data = x.split(',')
                y.append(data[0])

def changeAuditoryParams(ard, params, y):
        com = []

        #if



#def manualControlDic(ard,com):
com_lookup = {'left-door-true': 'D',
              'left-door-false': 'D',
              'right-door-true': 'd',
              'right-door-false': 'd',
              'left-flush-true': 'L',
              'left-flush-false': 'L',
              'right-flush-true': 'R',
              'right-flush-false': 'R',
              'house-light-true': 'H',
              'house-light-false':'H',
              'buzzer-true': 'B1',
              'buzzer-false': 'B0',
              'test-sensors-true': 'J',
              'test-sensors-false': 'K',
              'pause-true': 'p',
              'pause-false': 'u',
              'stop-N/A': 'Q'}

## manualControl replaced by above dictionary. Thought that all the if-statements were causing a lot of lag
# between converting the HTTP POST to serial command but it ended up being on the arduino program side.
def manualControl(ard, component, state, y):
        """ Commands sent to arduino to control various components in the operant chamber.
        # Manual control is only enable before a session is started and during pauses (or fored trials)
        # may do something like: comp = {'left-door':{'true':'D1','false':'D0'},'right-door':{'true':'d1','false':'d0'},'left-flush':'L','right-flush':'R'}
        # Inputs:
        #       ard       - serial port object for task arduino
        #       component - string indicating component to control (ex: "right-door")
        #       state     - string indicating button/switch state ("true", "false", or "NAN"
        """
        if component == "left-door": # open/close left door
                if state == "true":
                        com = 'D1'
                else:
                        com = 'D0'
                        
        elif component == "right-door": # open/close right door
                if state == "true":
                        com = 'd1'
                else:
                        com = 'd0'
                        
        elif component == "left-flush": # flushes/stop flushes left port
                com = 'L'
                
        elif component == "right-flush": # flushed/stop flushed right port
                com = 'R'
                
        elif component == "house-light": # turns houselight on/off
                if state == "true":
                        com = 'H1'
                else:
                        com = 'H0'
                        
        elif component == "buzzer": # plays short/long buzzer tone
                if state == "true":
                        com = 'B1' # short
                else:
                        com = 'B0' # long

        elif component == "tone": # plays high/low frequency tone
                if state == "true":
                        com = 'T1'
                        
        elif component == "test-sensors": # allows for testing of sensors and reward delivery
                if state == "true":
                        com = 'J' # initiates sensor testing
                else:
                        com = 'K' # ends sensor testing
                        
        elif component == "start": # starts session (isn't used here)
                com = 'b'
                
        elif component == "stop": # stops session
                com = 'Q'
                
        elif component == "pause": # pauses session
                if state == "true":
                        com = 'p' # pause
                else:
                        com = 'u' # unpause
                
        ard.write(com.encode('utf-8'))
        
def randomizeAmplitude(gib, stimParams, y):
        """ function for randomizing amplitude of stimulation
        # Inputs:
        #       gib        - serial port object for stimulator
        #       stimParams - dict of stimulation params (ex: line 76 in application.py
        #       y          - data stream variable for storing/sending display information to angular
        """
        if stimParams["amp_indx"] == len(stimParams["task_amps"]): #check if every amplitude in stimParams["task_amps"] has been used
                stimParams["amp_indx"] = 0 #reset index
                print("Amp_indx asaa: " + str(stimParams["amp_indx"]))
                stimParams["shuffled_amps"] = random.sample(
                        stimParams["task_amps"],
                        len(stimParams["task_amps"])) #reshuffle amplitudes
        y.append("amplitude index: " + str(stimParams["amp_indx"])) #update display in anglar
        stimParams["amplitude"] = stimParams["shuffled_amps"][stimParams["amp_indx"]]
        changeAmplitude(gib, stimParams["amplitude"], y)
        stimParams["amp_indx"] = stimParams["amp_indx"] + 1
        
                

def arduinoTask(ard, gib, y, sessionData, currentTrialData, stimParams):
        """serial port "listener" to perform specific actions depending on what arduino writes to port
        # Inputs:
        #       ard              - serial port object for task arduino
        #       gib              - serial port object for stimulator
        #       y                - data stream variable for storing/sending display information to angular
        #       sessionData      - dict to store relevant behavioral data during session
        #       currentTrialData - dict to update trial table in angular
        #       stimParams       - dict containing parameters of stimulation
        """
        break_flag = 0 # flag to break external while loop if present
        while ard.in_waiting == 0: #do nothing until bytes are available to read
                pass
        #a = ard.read_until('\r\n')
        #print(a)
        x = ard.read_until(expected=b'\r\n').decode("utf").rstrip()
        #x = a.decode("utf").rstrip() # decode bytes to string
        print(x)
        data = x.split(',')
        if data[0] == "Connected":
                print("Arduino " + data[0])
                print("Manual Control Enabled")
                y.append("Arduino " + data[0])
                y.append("Manual Control Enabled")
                break_flag = 1
        elif data[0] == "Start":
                print("Beginning Session")
                y.append("Beginning Session")
                
        elif data[0] == "Trial":
                print("Trial time: " + data[1])
                print("Trial Number: " + data[2])
                y.append("Trial Number: " + data[2]) 
                trial_time = int(data[1]) / 1000 # to seconds
                ## update data 
                currentTrialData["sess_time"] = str(round(trial_time / 60,2)) #to minutes
                currentTrialData["trial_n"] = data[2]
                currentTrialData["trial_type"] = "-"
                currentTrialData["stim_A"] = "-"
                currentTrialData["stim_fre"] = "-"
                currentTrialData["CV"] = "-"
                currentTrialData["trial_res"] = "-"
                sessionData["trial_time"].append(trial_time)
                sessionData["trial_number"].append(int(data[2]))
                
        elif data[0] == "Type":
                
                if data[1] == "2": #right trial, no stimulation for detection experiment
                        if stimParams["discrimination"]:
                                sessionData["tone_duration"].append(stimParams["tone_durationR"])
                                sessionData["amplitude"].append([])
                                sessionData["frequency"].append([])
                                sessionData["CV"].append([])
                        else:
                                sessionData["tone_duration"].append([])
                                sessionData["amplitude"].append([])
                                sessionData["frequency"].append([])
                                sessionData["CV"].append([])
                else: #left trial, stimulation if CV experiment is selected
                        
                        if stimParams["stim_enable"] == 1:
                                #if stimParams["randomize"] == 1:
                                #        randomizeAmplitude(gib, stimParams, y)
                                print("HERE")
                                print(stimParams["tone_durationL"])
                                currentTrialData["stim_A"] = str(stimParams["amplitude"])
                                currentTrialData["stim_fre"] = str(stimParams["frequency"])
                                currentTrialData["CV"] = str(stimParams["CV"])
                                sessionData["tone_duration"].append(stimParams["tone_durationL"])
                                sessionData["amplitude"].append(stimParams["amplitude"])
                                sessionData["frequency"].append(stimParams["frequency"])
                                sessionData["CV"].append(stimParams["CV"])
                        else:
                                sessionData["tone_duration"].append([])
                                sessionData["amplitude"].append([])
                                sessionData["frequency"].append([])
                                sessionData["CV"].append([])
                                
                datStr = ard.read_until(expected=b'\r\n').decode("utf").rstrip()
                y.append(datStr)
                currentTrialData["trial_type"] = data[1]
                currentTrialData["forced"] = data[2]
                sessionData["trial_type"].append(int(data[1]))
                sessionData["forced"].append(int(data[2]))
                sessionData["randomized"].append(stimParams["randomize"])
                sessionData["response"].append([])
                sessionData["response_time"].append([])
                sessionData["correct"].append([])
                sessionData["percent"].append([])
                
        elif data[0] == "Stim":
                if data[1] == "1": #left trial
                        if gib.is_open == 1: #stimParams["stimEnable"] == 1
                                stimulate(gib, stimParams, y)
                        print("Stim")
                        if stimParams["discrimination"]:
                                y.append("Left Stim")
                        else:
                                y.append("Stim")
                else:
                        print("No stim")
                        if stimParams["discrimination"]:
                                y.append("Right Stim")
                        else:
                                y.append("No stim")
                        
        elif data[0] == "Response":
                res_time = int(data[1]) / 1000
                if data[3] == "1":
                        datStr = "correct."
                elif data[3] == "0":
                        datStr = "incorrect."
                elif data[3] == "5":
                        #data[3] = "0"
                        datStr = "forced."
                print("Response Time: " + str(res_time) + "sec")
                
                if data[2] == "1":
                        datStr = "Left Port Response, " + datStr
                elif data[2] == "2":
                        datStr = "Right Port Response, " + datStr
                elif data[2] == "5":
                        datStr = "No response."
                        
                print(datStr)
                y.append(datStr)
                currentTrialData["trial_res"] = data[2]
                sessionData["response_time"][-1] = res_time
                sessionData["response"][-1] = int(data[2])
                sessionData["correct"][-1] = int(data[3])
                
                
        elif data[0] == "Percent":
                percent = float(data[1]) * 100
                currentTrialData["per_cor"] = str(percent)
                sessionData["percent"][-1] = percent
                y.append("Running percentage correct: " + str(percent) + "%")
                
        elif data[0] == "End":
                print("Session Ended")
                y.append("Session Ended")
                break_flag = 1
        elif data[0] == "Wait":
                print("Manual Control Enabled")
                y.append("Manual Control Enabled")
                #break_flag = 1
        elif data[0] == "Wait for Response":
                print("Waiting for response...")
                y.append("Waiting for response...")
        #elif data[0] == "Paused":
        #        print("Paused")
        #        y.append(data[0])
        else:
                y.append(data[0])
        return break_flag
                                                
'''			
The following functions are used for communication with the gibson stimulator:
        - 'waitForGibson' = establishes connection to stimulator
        - 'readGibData' = reads/clears data written by stimulator on serial port
        - 'convertToBytes' = configures command to stimulator to change parameters
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
        1. the stimulation channel must first be selected (ch)
                -In the case here, only a single channel is used (channel 0) and is hard coded. This may be changed for future applications
        2. the parameter to be changed is selected (val_ind)
                -pulse number         -> 1
                -pulse width          -> 2
                -inter-phase interval -> 3
                -frequency            -> 4
                -amplitude requires sequence of three bytes:
                                      -> 5, 6, 7
                -CV                   -> 8
        3. the corresponding parameter value is written (val)
                -ex: for pulse width -> 256
                -ex: for frequency   -> 50
        4. Function 'convertToBytes' takes the 3 aformentioned values and appropriately configures them for writing to serial port     
'''

def waitForGibson(gib, y):
        """ establishes connection to stimulator
         Inputs:
                gib - serial port object for stimulator
                y   - data stream variable for storing/sending display information to angular
        """
        gib.write((1).to_bytes(1, byteorder="big"))#write_uint8(gib,0)
        msg = ""
        while msg.find("Connected") == -1:
                while gib.in_waiting == 0:
                        pass
                msg = gib.read_until(expected=b'\r\n').decode("utf").rstrip()
                print(msg)
                y.append("Gibson " + msg)

def readGibData(gib, r_max, y):
        """ reads serial port of stimulator
         Inputs:
                gib   - serial port object for stimulator
                r_max - indicate number of reponses (lines) from device
                y     - data stream variable for storing/sending display information to angular
        """
        while gib.in_waiting == 0: # wait until bytes are on the serial port
                pass
        i = 0
        while i < r_max:
                x = gib.read_until(expected=b'\r\n').decode("utf").rstrip()
                print(x)
                y.append(x)
                i = i + 1
                
def convertToBytes(ch, val_ind, val):
        """ Converts channel (ch), parameter index (val_ind), and parameter value (val) to
            bytes and joins them together. 
         Inputs:
                 ch      - stimulation channel, zero-index (0-3, but 0 is only in use)
                 val_ind - value specifying the parameter to be changed
                 val     - value of parameter to change
        """
        CH = ch.to_bytes(1, byteorder="big")
        VAL_IND = val_ind.to_bytes(1, byteorder="big")
        if val_ind == 1: #pulse number can be greater than 255
                VAL = val.to_bytes(2, byteorder="little") #give pulse number 2 bytes
        else:
                VAL = val.to_bytes(1, byteorder="big")
        COM = b''.join([CH, VAL_IND, VAL])
        return COM

        
def currentConfig(current):
        '''
        -converted from matlab script 'currentconfig.m'
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
        """ changes pulse number value.
        # Inputs:
        #       gib   - serial port object for stimulator
        #       pnVal - number of pulses, string (ex: '300')
        #       y     - data stream variable for storing/sending display information to angular
        """
        COM = convertToBytes(0, 1, int(pnVal)) 
        gib.write(COM)
        readGibData(gib, 2, y)
        
def changePulseWidth(gib, pwVal, y):
        """ changes pulse width.
        # Inputs:
        #       gib   - serial port object for stimulator
        #       pwVal - pulse width in us, string (ex: '200')
        #       y     - data stream variable for storing/sending display information to angular
        """
        COM = convertToBytes(0, 2, int(pwVal))
        gib.write(COM)
        readGibData(gib, 2, y)

def changeIPI(gib, ipiVal, y):
        """ changes inter-phase interval.
        # Inputs:
        #       gib    - serial port object for stimulator
        #       ipiVal - inter-phase interval in us, string (ex: '50')
        #       y      - data stream variable for printing reads from serial port
        """
        COM = convertToBytes(0, 3, int(ipiVal))
        gib.write(COM)
        readGibData(gib, 2, y)


def changeFrequency(gib, freqVal, y):
        """ changes frequency.
        # Inputs:
        #       gib     - serial port object for stimulator
        #       freqVal - frequency in Hz, string (ex: '50')
        #       y       - data stream variable for storing/sending display information to angular
        """
        COM = convertToBytes(0, 4, int(freqVal))
        gib.write(COM)
        readGibData(gib, 2, y)


def changeAmplitude(gib, ampVal, y):
        """ changes amplitde.
        # Inputs:
        #       gib    - serial port object for stimulator
        #       ampVal - amplitude in uA, string (ex: '250')
        #       y      - data stream variable for storing/sending display information to angular
        """
        a_byte, b_byte, ab_byte = currentConfig(int(ampVal))
        a_int = int.from_bytes(a_byte, byteorder='big')
        b_int = int.from_bytes(b_byte, byteorder='big')
        ab_int = int.from_bytes(ab_byte, byteorder='big')

        aCOM = convertToBytes(0, 5, a_int)
        gib.write(aCOM)
        
        bCOM = convertToBytes(0, 6, b_int)
        gib.write(bCOM)
        
        abCOM = convertToBytes(0, 7, ab_int)
        gib.write(abCOM)
        readGibData(gib, 3, y)

def changeCV(gib, cvVal, y):
        """ changes CV value.
         Inputs:
                gib   - serial port object for stimulator
                cvVal - coeficient of variation value, string (ex: '0.8')
                y     - data stream variable for storing/sending display information to angular
        """
        COM = convertToBytes(0, 8, int(float(cvVal) * 10)) #cv is read as 0-10 so multiply by 10
        gib.write(COM)
        readGibData(gib, 2, y)
        
def changeStimParams(gib, params, stimParams, y):
        """ sequentially changes all stimulation parameters
         Inputs:
                gib        - serial port object for stimulator
                params     - list of parameters as strings sent from angular to be changed
                stimParams - dict containing parameters of stimulation
                y          - data stream variable for storing/sending display information to angular
        """
        ampStr = params[0]
        stimParams["amplitude"] = int(ampStr)
        stimParams["base_amp"] = int(ampStr)
        freqStr = params[1]
        stimParams["frequency"] = int(freqStr)
        pwStr = params[2]
        stimParams["pulse_width"] = int(pwStr)
        ipiStr = params[3]
        stimParams["ipi"] = int(ipiStr)
        pnStr = params[4]
        stimParams["pulse_num"] = int(pnStr)
        cvStr = params[5]
        stimParams["CV"] = float(cvStr)
        if stimParams["CV"] > 0:
                stimParams["periodic"] = 1
        else:
                stimParams["periodic"] = 0
        
        changeAmplitude(gib, ampStr, y)
        changeFrequency(gib, freqStr, y)
        changePulseWidth(gib, pwStr, y)
        changeIPI(gib, ipiStr, y)
        changePulseNumber(gib, pnStr, y)
        changeCV(gib, cvStr, y)

def stimulate(gib, stimParams, y):
        """ delivers stimulation based on set stimulation parameters
         Inputs:
                 gib        - serial port object for stimulator
                 stimParams - dict containing parameters of stimulation
                 y          - data stream variable for storing/sending display information to angular
        """
        gib.write((0 + 4).to_bytes(1, "big")) # '0' is the channel, stim command is channel + 4
        if stimParams["periodic"] == 0:
                readGibData(gib, 1, y)
        else:
                readGibData(gib, 2, y)
                        
        

