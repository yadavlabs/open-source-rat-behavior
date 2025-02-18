"""
	Flask RESTful API - Back-End Services to the Angular Application
	Authors: Scott Miller, Jacob Slack
	_/_/23
	
	This is the main file responsible for the RESTful API and its
		respective services. The two accompanying files 
		('serial_functions.py' and 'helper_functions.py') contain
		functions and more to support the services presented within
		the RESTful API.
	More information on how to open and run the virtual environment
		can be found in supporting documents in the provided GitHub.
		Comments found within the code will outline function and logic,
		not maintenance.
	
"""

# Native Python imports
from flask import Flask, request, Response
import flask
from flask_cors import CORS
import serial
import json
import random
import time

# Other Python file imports
import serial_functions as s #serial port communication functions for both arduino and stimulator
import helper_functions as h #additional helpers functions

"""
	Variable declarations:
	
	The following lines declare variables, objects, and dictionaries
		that provide structure for communication between the front-end
		and back-end applications. Alongside offering organization
		of commonly used values to handle the logic within each
		service.
"""

y = [] # The global variable that collects serial port print statements
start_flag = 0
# dictionary to store session data to export/save
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
# dictionary for updating Trial table in angular
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
# dictionary for storing session task parameters (defaults are defined in ...\Arduino Files\operant_task_control\operant_task_control.no)
sessionParams = {
        "experiment":"CV Experiment",
        "type":"Detection",
        "session_length":"60",
        "response_time":"10",
        "forced_trials":"Yes",
        "consecutive_error":"1"
        }
# dictionary to store default and running stimulation parameters
stimParams = { #uses integers and floats (not strings) to populate dict
        "frequency":[],  #frequency in Hz
        "amplitude":[],  #running amplitude in uA
        "CV":[],         #coefficient of variation of stimulation (0-1 with steps of 0.1)
        "pulse_width":[],#pulse-width in us
        "ipi":[],        #inter-pulse interval in us
        "pulse_num":[],  #number of pulses (only used in periodic case (i.e. CV = 0)
        "stim_enable":0, #indicates if experiment involves stimulation
        "periodic":0,    #indicates if stimulation is periodic (CV = 0) or aperiodic (CV > 0)
        "randomize":0,   #indicates if stimulation parameter should be randomized
        "base_amp":[],   #base/default amplitude set at beginning of session (if randomize=0, this amplitude is used for stimulation trials)
        "task_amps":list(range(25,275,25)), #amplitudes to be randomized and tested (this variable can be changed depending on the experiment)
        "shuffled_amps":[], #randomized amplitudes based on task_amps
        "amp_indx":0     #index to track which amplitudes have been tested in shuffled_amps
        }

ard = serial.Serial() # A serial port object responsible for communication with the Arduino
gib = serial.Serial() # A serial port object responsible for communication with the Gibson
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
	- 'enterLoop' = enters a forever loop that relays Arduino print statements to the variable "y".
	- 'updateParams' = updates the parameters/settings utilized by both devices.
"""
@app.post("/device_setup")
def ArduinoSetUpFunctions():
	# Declaration of global variables for use within the view function
	global y, ard, gib, sessionData, currentTrialData, stimParams, start_flag
	print('Task:', request.form["task"])
	"""
		This code is completed if the received HTTP request at this URL
			includes the specified task, which only originates from the
			"Find Ports" button on the UI.
	"""
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
		print(ardPorts)
		# The completed lists are returned to the Angular application
		return {"task":request.form["task"],"message":"success","output":{"Arduino":ardPorts,"Gibson":gibPorts}}
	
	
	"""
		This code is completed if the received HTTP request at this URL
			includes the specified task, which only originates from the
			"Connect <device>" buttons on the UI.
		Both the Gibson and Arduino will use this part of the view
			function to open the serial port, so some nested logic is
			used to separate both devices.
	"""
	if (request.form["task"] == "openCOMs"):
	
		try:
			# This code is completed if the "Connect Arduino" button was pressed
			if (request.form["device"] == "Arduino"): # Checks that it's the Arduino
				
				ard.baudrate = int(request.form["baudRate"]) # Extracts the baud rate from sent params
				ard.port = request.form["port"] # Extracts the COM port from sent params
				ard.timeout = 2 #read timeout in sec 
				ard.open() # Opens the serial port object
				time.sleep(1) # Implements a delay of 1 second for the system to catch up
 
            # This code is completed if the "Connect Gibson" button was pressed
			elif (request.form["device"] == "Gibson"): # Checks that it's the Gibson
				
				gib.baudrate = int(request.form["baudRate"]) # Extracts the baud rate from sent params
				gib.port = request.form["port"] # Extracts the COM port from sent params
				gib.timeout = 2
				gib.open() # Opens the serial port object
                                
			print(request.form["device"] + " is open!") # Partial indicator to the user that the device was opened
			return {"task":request.form["task"],"message":"success","output":request.form["device"]} # Returns the status message
						
		except:
			# This code is completed if the "try" statement cannot execute
			print("Failed") # Partial indicator to the user that the device was not opened
			return {"task":request.form["task"],"message":"failed","output":request.form["device"]} # Returns the status message
	
		
	"""
		This code is completed if the received HTTP request at this URL
			includes the specified task, which only originates from the
			"Disconnect <device>" buttons on the UI.
		Both the Gibson and Arduino will use this part of the view
			function to close the serial port, so some nested logic is
			used to separate both devices.
	"""
	if (request.form["task"] == "closeCOMs"):	
		try:
			if (request.form["device"] == "Arduino"): # Checks if the device is the Arduino
				while ard.in_waiting > 0:
						ard.readline()
				ard.close() # Closes the Arduino serial port
								
			elif (request.form["device"] == "Gibson"): # Checks if the device is the Gibson
				while gib.in_waiting > 0:
						gib.readline()
				gib.close() # Closes the Gibson serial port
			
			print(request.form["device"] + " is closed") # Partial indicator that the serial port is closed
			return {"task":request.form["task"],"message":"success","output":request.form["device"]} # Returns status message
			
		except:
			# This code is completed if the "try" statement cannot execute
			print("Failed to close the " + request.form["device"]) # Partial indicator that the serial port coundn't be closed
			return {"task":request.form["task"],"message":"failed","output":request.form["device"]} # Returns status message
	
	
	"""
		This code is completed if the received HTTP request at this URL
			includes the specified task, which is the last operation of
			the "Connect <device>" buttons on the UI.
		Both the Gibson and Arduino will use this part of the view
			function to close the serial port, so some nested logic is
			used to separate both devices.
	"""
	if (request.form["task"] == "enterLoop"):
		
		try: 
			if request.form["device"] == "Arduino": # Checks the device is the Arduino
				connected_flag = 0 #flag for establishing arduino connection
				while connected_flag == 0: #runs until arduino sends "Connected" followed by "Wait"
					connected_flag = s.arduinoTask(ard, gib, y, sessionData, currentTrialData, stimParams)
				
				
			elif request.form["device"] == "Gibson": # Checks the device is the Gibson
				print("Entering gibson loop")
				s.waitForGibson(gib, y) # waits for gibson to respond with "Connected"
                                
		except:
			print("Couldn't enter the Arduino loop, or leaving the Arduino loop.") # Partial indicator that an error was met
		return {"task":request.form["task"],"message":"In Loop","output":[]} # Returns status message
	
	
	"""
		This code is completed if the received HTTP request at this URL
			includes the specified task, which originates from both
			"Update <type> Parameters" buttons in the UI
		Both parameter types use this part of the view function, so
			nested logic is used to separate functionality.
	"""
	if (request.form["task"] == "updateParams"):
		#
		paramType = request.form["paramType"]
		#print(request.form["paramType"])
		params = request.form["params"].split(',')

		if paramType == "Session":
			if params[0] == "CV Experiment": #sets if experiment includes stimulation
				stimParams["stim_enable"] = 1
			else:
				stimParams["stim_enable"] = 0
                                
			s.changeSessionParams(ard,params,y) #updates arduno task parameters
			if start_flag == 0: #checks if experiment has start (i.e. start button has been pressed)
				while ard.in_waiting > 0: # reads responses to parameter changes until serial port is empty
					_ = s.arduinoTask(ard, gib, y, sessionData, currentTrialData, stimParams)

		elif paramType == "Stimulator":
			s.changeStimParams(gib, params, stimParams, y) #changes stimulation parameters

		return {"task":request.form["task"], "message":"return", "output":[]}

	if (request.form["task"] == "paramsImpExp"):

		return {"task":request.form["task"], "message":"return", "output":[]}
		

"""
View Function 3:
	- Handles writing to the COM ports of both devices.
"""
@app.route("/to_dev",methods=["POST"])
def WriteToCOMport():
	global ard, gib, y, currentTrialData, start_flag

	if (request.form["device"] == "Arduino"): #check if POST is associated with Arduino

		component = request.form["string"] #checks the button/switch that was pressed
		state = request.form["butState"] #checks state, "true" or "false" for switches or "N/A" for buttons

		
		if component == "start": #start button was pressed
			
			if stimParams["stim_enable"] == 1: #if experiment involves stimulation, perform initial randomization of stim params
				stimParams["shuffled_amps"] = random.sample(stimParams["task_amps"],len(stimParams["task_amps"]))
			while ard.in_waiting > 0: #clear any leftover serial port bytes
				ard.readline()
                                
			ard.write("b".encode('utf-8')) #write 'b' to start session
			start_flag = 1
			end_flag = 0
			while end_flag == 0: #run arduinoTask until end of session criteria are met (either end button press or session time met)
				end_flag = s.arduinoTask(ard, gib, y, sessionData, currentTrialData, stimParams)
			start_flag = 0
				
		elif component == "randomize": #check if randomize switch is on/off
			stimParams[component] = state
			if state == "true":
				stimParams[component] = 1 #randomize stim params
			else:
				stimParams[component] = 0 #stop randomizing stim params (set back to initially set params)
				s.changeAmplitude(gib, stimParams["base_amp"], y) #in this case, only amplitude was randomized
				stimParams["amplitude"] = stimParams["base_amp"]
		else: #button presses for manual controls

			com = s.com_lookup[component+"-"+state]
			print(com)
			ard.write(com.encode('utf-8'))
	
			#s.manualControl(ard, component, state, y) # write corresponding values to control components
			if start_flag == 0: #if experiment hasn't started, read from serial port (if experiment has started, arduinoTask is already running)
				_ = s.arduinoTask(ard, gib, y, sessionData, currentTrialData, stimParams)

	elif (request.form["device"] == "Gibson"):
		#print(request.form["string"])
		
		if request.form["string"] == "STIM": #Test stimulation button pressed
			s.stimulate(gib, stimParams, y) #stimulate using set stim params

	else:
		if request.form["string"] == "export": #export button pressed
			print(sessionData)
			h.saveSessionDataUI(sessionData, y) #saves session data

	return {"task":request.form["task"],"message":"success"}
		
	

"""
	View Function 4:
		- Handles the Server-Sent Events (SSEs)
		- Receives, from global variables, current trial data and
			strings printed from either serial port object, and yields
			the data to the stream.
		- The front-end has this url (http://127.0.0.1:5000/stream) 
			defined as an EventSource, and monitors the data emitted
			from this URL.
"""
@app.route("/stream")
def dataStream():
	
	def get_data():
		global y, currentTrialData
		trialData_lastPass = currentTrialData.copy() #have to make a copy
		
		"""
			Both conditions in the while loop create a dictionary that
				will be yielded to the data stream, processes the variables
				to prevent re-printing (y) or to prevent re-triggering
				(trialData_lastPass), and the yields the data in a
				specially constructed f-string.
		"""
		while True:			
			if y != []:
				dict_toSend = json.dumps({"item1":y, "item2":currentTrialData})
				del y[:]
				yield f"data: {dict_toSend}\nevent: message\n\n"

			if currentTrialData != trialData_lastPass:
				dict_toSend = json.dumps({"item2":currentTrialData})
				trialData_lastPass = currentTrialData.copy()
				yield f"data: {dict_toSend}\nevent: message\n\n"		

	"""
		The dataStream function returns a response, which is dependent
			on the nested function get_data(). This calls an infinite
			loop as the return function calls a new process each time.
		The data, serialized to a JSON object format, is yielded to
			the data stream as a response.
	"""
	return Response(get_data(), mimetype="text/event-stream")
	
