# Starting fresh
# These imports are important for back-end functionality
from flask import Flask, request, Response
import flask
from flask_cors import CORS
import ard_functions as a
import json

from datetime import datetime
import time



y = [] # The global variable that collects Arduino (and maybe Gibson) print statements

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
	
	if (request.form["task"] == "findPorts"):
		ports = a.findPorts()
		
		to_output = []
	
		for port in ports:
			
			if (request.form["message"] == "Arduino"):
							
				if ("Arduino" in str(port)):
					temp1 = str(port).split(" ")
					to_output.append({"value":str(port),"viewValue":temp1[0]})
			
			if (request.form["message"] == "Gibson"):
				
				if ("Stellaris" in str(port)):
					temp2 = str(port).split(" ")
					to_output.append({"value":str(port),"viewValue":temp2[0]})
			
	
		return {"task":request.form["task"],"message":"success","output":to_output}
	
	elif (request.form["task"] == "openCOMs"):
		#print("Opening serial coms!")
		#print(request.form["message"])
		
		sent_str = request.form["message"] 
		tot_params = sent_str.split(",")
		
		print(tot_params)
		
		# Can now pull off the appropriate parameters from this array (tot_params)
		# For example:
		ardParams = tot_params[0:2]
		print(ardParams)
				
		try:
			global ard
			global y
			
			ard = a.openCOMs(ardParams)
			
			return {"task":request.form["task"],"message":"success","output":[]}
						
		except:
			print("Failed")
			
			return {"task":request.form["task"],"message":"failed","output":[]}
		
		
	elif (request.form["task"] == "closeCOMs"):
				
		try:		
			ard.close()
			print("Arduino is closed")
		
			return {"task":request.form["task"],"message":"success","output":[]}
			
		except:
			print("Failed to close the Arduino")
			
			return {"task":request.form["task"],"message":"failed","output":[]}
	
	elif (request.form["task"] == "enterLoop"):
		try:
			
			global y
			
			a.arduinoLoop(ard,y)
			
		except:
			print("Couldn't enter the Arduino loop, or leaving the Arduino loop.")
		
		return {"task":request.form["task"],"message":"In Loop","output":[]}
		


@app.route("/to_ard",methods=["POST"])
def ArduinoButtons():
	
	if (request.method == "POST"):
		try:
			ard.write(request.form["character"].encode("utf-8"))
		except:
			print("Failed to write to Arduino")
	
		return {"task":request.form["task"],"message":"success"}
	


@app.route("/stream")
def dataStream():
	
	def get_data():
		
		while True:
			
			global y
			
			"""
				THIS IS CURRENTLY UNCOMMENTED TO OUTPUT SOMETHING TO THE
					EVENT STREAM EVERY SECOND WITHOUT AN ARDUINO, MAKE
					SURE TO COMMENT OUT LINES 135 to 137 AND UNCOMMENT
					LINES 140 to 146 TO SEND ARDUINO STRINGS TO THE DATA
					STREAM.
			"""
			
			#dict_toSend = json.dumps({"minute":datetime.now().minute,"second":datetime.now().second})
			#time.sleep(1)
			#yield f"data: {dict_toSend}\nevent: message\n\n"
			
			
			
			if y != []:
				dict_toSend = json.dumps({"item1":y})
				del y[:]
				
				yield f"data: {dict_toSend}\nevent: message\n\n"
			

	return Response(get_data(), mimetype="text/event-stream")
	
