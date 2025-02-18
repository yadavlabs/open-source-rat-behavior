# These imports are important for back-end functionality
from flask import Flask, request, Response
import flask
from flask_cors import CORS
import serial
import serial_functions as s #serial port communication functions for both arduino and stimulator
import helper_functions as h #additional helpers functions 
import json
import random

# These imports were used temporarily for SSE practice. Can be removed.
from datetime import datetime
import time

y = [] # The global variable that collects Arduino (and maybe Gibson) print statements
start_flag = 0
sessionData = { #uses integers and/or floats (not strings) to populate dict
        "trial_time":[],
        "trial_number":[],
        "trial_type":[],
        "forced":[],
        "response":[],
        "response_time":[],
        "correct":[],
        "percent":[],
        "randomized":[],
        "amplitude":[],
        "frequency":[],
        "CV":[]}
currentTrialData = {
        "sess_time":"-",
        "trial_n":"-",
        "trial_type":"-",
        "forced":"-",
        "stim_A":"-",
        "stim_fre":"-",
        "CV":"-",
        "trial_res":"-",
        "per_cor":"-"
        }
sessionParams = {
        "experiment":"CV Experiment",
        "type":"Detection",
        "session_length":"60",
        "response_time":"10",
        "forced_trials":"Yes",
        "consecutive_error":"1"
        }
stimParams = { #uses integers and floats (not strings) to populate dict
        "frequency":[],
        "amplitude":[],
        "CV":[],
        "pulse_width":[],
        "ipi":[],
        "pulse_num":[],
        "stim_enable":0,
        "periodic":0,
        "randomize":0,
        "base_amp":[],
        "task_amps":list(range(25,275,25)),
        "shuffled_amps":[],
        "amp_indx":0
        }

ard = serial.Serial()
gib = serial.Serial()
app = Flask(__name__) # This creates the application as a Flask object
CORS(app) # Implements CORS protocol to the application

"""
View Function 1:
	- Simple welcome screen for if the website is opened.
	- No other functionality.
"""
@app.route("/")
def welcomeScreen():
	return "Welcome"
	
"""
View Function 2:
	- Handles Gibson and Arduino device set-up and tear-down procedures.
	- 'findPorts' = returns a list of Gibson and Arduino ports to Angular.
	- 'openCOMs' = creates Arduino or Gibson serial objects for communication.
	- 'closeCOMs' = closes Arduino or Gibson serial objects.
	- 'enterLoop' = enters a forever loop that relays Arduino print statements to the variable "y"
"""
@app.post("/device_setup")
def ArduinoSetUpFunctions():
	global y, ard, gib, sessionData, currentTrialData, stimParams, start_flag
	if (request.form["task"] == "findPorts"):
		ports = s.findPorts() # Gathers the list of connected ports and COM ports
		ardPorts = [] # Empty list of Arduino ports
		gibPorts = [] # Empty list of Gibson ports
	
		for port in ports:
			if (request.form["device"] == "Arduino"): # Checks for Arduino device
				if ("Arduino" in str(port)): # Checks if Arduino is in the name of the port
					temp1 = str(port).split(" ")
					ardPorts.append({"value":str(port),"viewValue":temp1[0]}) # Adds it to the list of Arduino ports
			
			if (request.form["device"] == "Gibson"): # Checks for Gibson device
				if ("Stellaris" in str(port)): # Checks if the Gibson is the name of the port
					temp2 = str(port).split(" ")
					gibPorts.append({"value":str(port),"viewValue":temp2[0]}) # Adds it to the list of Gibson ports
			
		return {"task":request.form["task"],"message":"success","output":{"Arduino":ardPorts,"Gibson":gibPorts}}
	
	elif (request.form["task"] == "openCOMs"):
		
		params = [request.form["baudRate"], request.form["port"]] # Parameters sent from Angular
		
		try:
			# Global variables to be accessed in other functions...
			#global ard # ...the to-be Arduino serial object...
			#global sessionData
			#global gib # ...the to-be Gibson serial object...
			#global y # ...the to-be variable for data logging.
			


			if (request.form["device"] == "Arduino"): # Checks device
                                #global ard
                                
                                ard.baudrate = int(params[0])
                                ard.port = params[1]
                                ard.timeout = 2
                                ard.open()
                                time.sleep(1)
                                #ard = s.openCOMs(params, request.form["device"]) # Opens the serial port
			elif (request.form["device"] == "Gibson"):
                                #global gib
                                
                                gib.baudrate = int(params[0])
                                gib.port = params[1]
                                gib.timeout = 2
                                gib.open()
                                
                                #gib = s.openCOMs(params, request.form["device"])
			print(request.form["device"] + "is open!")
			return {"task":request.form["task"],"message":"success","output":request.form["device"]}
						
		except:
			print("Failed") # If the "try" statement experiences an error
			
			return {"task":request.form["task"],"message":"failed","output":request.form["device"]}
		
		
	elif (request.form["task"] == "closeCOMs"):
				
		try:
			if (request.form["device"] == "Arduino"):
                                
				ard.close()
			elif (request.form["device"] == "Gibson"):
                                
				gib.close()
			
			print(request.form["device"] + " is closed")
			
			return {"task":request.form["task"],"message":"success","output":request.form["device"]}
			
		except:
			print("Failed to close the " + request.form["device"])
			
			return {"task":request.form["task"],"message":"failed","output":request.form["device"]}
	
	elif (request.form["task"] == "enterLoop"):
                #s.waitForArduino()
                try: 
                        
                        if request.form["device"] == "Arduino":
                                connected_flag = 0
                                while connected_flag == 0:
                                        connected_flag = s.arduinoTask(ard, gib, y, sessionData, currentTrialData, stimParams)
                                print("here")
                        elif request.form["device"] == "Gibson":
                                print("Entering gibson loop")
                                s.waitForGibson(gib, y)
                                
                except:
                        print("Couldn't enter the Arduino loop, or leaving the Arduino loop.")
		
                return {"task":request.form["task"],"message":"In Loop","output":[]}
	
	elif (request.form["task"] == "updateParams"):

                paramType = request.form["paramType"]
                print(request.form["paramType"])
                params = request.form["params"].split(',')
		
                """
                        What's being sent is the parameters for the session and stimulator,
                                as I have them share a function to reduce redundancy.
                        You'll need to incorporate logic here to keep them separate. Easiest
                                way to do that is to use 'request.form["paramType"]', as
                                that can only be "Stimulator" or "Session".
                """
                if paramType == "Session":
                        if params[0] == "CV Experiment": #check if session involves stimulation
                                stimParams["stim_enable"] = 1
                        else:
                                stimParams["stim_enable"] = 0
                                
                        s.changeSessionParams(ard,params,y)
                        if start_flag == 0:
                                while ard.in_waiting > 0:
                                        _ = s.arduinoTask(ard, gib, y, sessionData, currentTrialData, stimParams)

                elif paramType == "Stimulator":
                        s.changeStimParams(gib, params, stimParams, y)
                        
                                 
                        
                        
                return {"task":request.form["task"], "message":"return", "output":[]}
		


@app.route("/to_ard",methods=["POST"])
def WriteToCOMport():
        global ard, gib, y, currentTrialData, start_flag
##	try:
        if (request.form["device"] == "Arduino"):
                component = request.form["string"]
                state = request.form["butState"]

                print(component)
                print(state)
                if component == "start":
                        if stimParams["stim_enable"] == 1:
                                stimParams["shuffled_amps"] = random.sample(stimParams["task_amps"],len(stimParams["task_amps"]))
                        while ard.in_waiting > 0:
                                ard.readline()
                                
                        ard.write("b".encode('utf-8')) #write 'b' to start session
                        start_flag = 1
                        end_flag = 0
                        while end_flag == 0:
                                end_flag = s.arduinoTask(ard, gib, y, sessionData, currentTrialData, stimParams)
                if component == "randomize":
                        stimParams[component] = state
                        if state == "true":
                                stimParams[component] = 1
                        else:
                                stimParams[component] = 0
                                s.changeAmplitude(gib, stimParams["base_amp"], y)
                                stimParams["amplitude"] = stimParams["base_amp"]
                else:
                        s.manualControl(ard, component, state, y)
                        if start_flag == 0:
                                _ = s.arduinoTask(ard, gib, y, sessionData, currentTrialData, stimParams)
        #ard.write(request.form["string"].encode("utf-8"))

        elif (request.form["device"] == "Gibson"):
        #gib.write(request.form["string"])
                print(request.form["string"]) # This is Gibson_string from Angular in "run-trial.components.ts"
                if request.form["string"] == "STIM":
                        s.stimulate(gib, stimParams, y)#gib.write((4).to_bytes(1, "big"))
                        #s.readGibData(gib, 2, y)#print(gib.readline().decode('utf-8'))
        else:
                if request.form["string"] == "export":
                        print(sessionData)
                        #h.saveSessionData(sessionData, y)
                        h.saveSessionDataUI(sessionData, y)

        """
        THIS IS WHERE YOU WILL WRITE TO THE GIBSON HOWEVER IT IS DONE
                THE CONTENT CAN COME FROM "string" FROM THE HTTP
                POST REQUEST
        """

        return {"task":request.form["task"],"message":"success"}
	
##	except:
##		print("Failed to write to Arduino")
##		return {"task":request.form["task"], "message":"failed"}
	
		
	


@app.route("/stream")
def dataStream():
        def get_data():
                global y, currenTrialData
                trialData_lastPass = currentTrialData.copy() #have to make a copy
                while True:

			
                        """
                        dict_toSend = json.dumps({"minute":datetime.now().minute,"second":datetime.now().second})
                        time.sleep(1)
                        yield f"data: {dict_toSend}\nevent: message\n\n"
                        """
			
			
                        if y != []:
                                dict_toSend = json.dumps({"item1":y, "item2":currentTrialData})
                                del y[:]

                                yield f"data: {dict_toSend}\nevent: message\n\n"

                        if currentTrialData != trialData_lastPass:
                                dict_toSend = json.dumps({"item2":currentTrialData})
                                trialData_lastPass = currentTrialData.copy()

                                yield f"data: {dict_toSend}\nevent: message\n\n"
			

        return Response(get_data(), mimetype="text/event-stream")
	
