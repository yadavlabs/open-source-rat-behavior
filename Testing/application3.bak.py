# These imports are important for back-end functionality
from flask import Flask, request, Response
import flask
from flask_cors import CORS
import serial
import serial_functions as s #serial port communication functions for both arduino and stimulator
import json

# These imports were used temporarily for SSE practice. Can be removed.
from datetime import datetime
import time

y = [] # The global variable that collects Arduino (and maybe Gibson) print statements
ard = serial.Serial()
gib = serial.Serial()
#yg = []
#gib_con_flag = 0; #gibson doesn't restart after port is closed, so need a check here when reopening coms to not write to port (mainly for debugging)

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
	#global y, ard, gib
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
                                #ard = serial.Serial()
                                ard.baudrate = 115200 #int(params[0])
                                ard.port = params[1]
                                ard.timeout = 2
                                ard.open()
                                time.sleep(1)
                                #ard = s.openCOMs(params, request.form["device"]) # Opens the serial port
			elif (request.form["device"] == "Gibson"):
                                #global gib
                                #gib = serial.Serial()
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
                                print("here")
                                s.waitForArduino(ard, y) #s.arduinoLoop(ard,y)
                        elif request.form["device"] == "Gibson":
                                print("Entering gibson loop")
                                s.waitForGibson(gib, y)#s.gibsonLoop(gib,y)
                                
                except:
                        print("Couldn't enter the Arduino loop, or leaving the Arduino loop.")
		
                return {"task":request.form["task"],"message":"In Loop","output":[]}
	
	elif (request.form["task"] == "updateParams"):

                paramType = request.form["paramType"]
                print(request.form["paramType"])
                params = request.form["params"].split(',')
		#for i,param in enumerate(params):
                #        print(str(i)+" "+str(param))
		
                """
                        What's being sent is the parameters for the session and stimulator,
                                as I have them share a function to reduce redundancy.
                        You'll need to incorporate logic here to keep them separate. Easiest
                                way to do that is to use 'request.form["paramType"]', as
                                that can only be "Stimulator" or "Session".
                """
                if paramType == "Session":
                        
                        s.changeSessionParams(ard,params,y)

                elif paramType == "Stimulator":
                        print(params[0])
                        print(params[1])
                        if params[0] == "0":
                                s.changePulseNumber(gib, params[1], y)
                        elif params[0] == "1":
                                s.changePulseWidth(gib, params[1], y)
                        elif params[0] == "2":
                                s.changeIPI(gib, params[1], y)
                        elif params[0] == "3":
                                s.changeFrequency(gib, params[1], y)
                        elif params[0] == "4":
                                s.changeAmplitude(gib, params[1], y)
                        elif params[0] == "5":
                                s.changeCV(gib, params[1], y)
                        elif params[0] == "6":
                                print(gib)
                                gib.get_settings()
                                print(gib.readline().decode('utf-8'))
                        elif params[0] == "7":
                                print(ard)
                                ard.get_settings()
                        elif params[0] == "8":
                                s.write_uint8(gib, 0)
                                s.write_uint8(gib, 4)
                                s.write_uint8(gib, int(params[1]))
                                s.readGibData(gib, 2, y)
                        elif params[0] == "9":
                                print(gib.is_open)
                                print(gib.in_waiting)
                                print(gib.out_waiting)
                        else:
                                print("INVALAICD")
                                 
                        #s.changeStimParams(gib, params)
                        #s.changeAmplitude(gib, int(params[0]))
                        #print(params[1])
                        #s.changeFrequency(gib, int(params[1]), y)
                        #s.changeCV(gib, float(params[2]))
                        #s.changeFrequency(gib, int(params[1]))
                        
                        
                return {"task":request.form["task"], "message":"return", "output":[]}
		


@app.route("/to_ard",methods=["POST"])
def WriteToCOMport():
	#global y
	try:
                #global y
                if (request.form["device"] == "Arduino"):
                        component = request.form["string"]
                        state = request.form["butState"]
                        
                        print(component)
                        print(state)
                        s.manualControl(ard, component, state, y)
                        #ard.write(request.form["string"].encode("utf-8"))
                        
                elif (request.form["device"] == "Gibson"):
                        #gib.write(request.form["string"])
                        print(request.form["string"]) # This is Gibson_string from Angular
                        if request.form["string"] == "STIM":
                                print(gib.readline().decode('utf-8'))
                        
                        """
                                THIS IS WHERE YOU WILL WRITE TO THE GIBSON HOWEVER IT IS DONE
                                        THE CONTENT CAN COME FROM "string" FROM THE HTTP
                                        POST REQUEST
                        """
                        
                return {"task":request.form["task"],"message":"success"}
	
	except:
		print("Failed to write to Arduino")
		return {"task":request.form["task"], "message":"failed"}
	
		
	


@app.route("/stream")
def dataStream():
	
	def get_data():
		#global y
		while True:
			
			#global y
			#global yg
			
			"""
			dict_toSend = json.dumps({"minute":datetime.now().minute,"second":datetime.now().second})
			time.sleep(1)
			yield f"data: {dict_toSend}\nevent: message\n\n"
			"""
			
			
			if y != []:
				dict_toSend = json.dumps({"item1":y})
				del y[:]
				
				yield f"data: {dict_toSend}\nevent: message\n\n"
				
			'''elif yg != []:
                                dict_toSend = json.dumps({"item1":yg})
                                del yg[:]

                                yield f"data: {dict_toSend}\nevent: message\n\n"'''
			

	return Response(get_data(), mimetype="text/event-stream")
	
