# Starting fresh
# J. Slack edits 8/4/23
# -adding gibson stimulator functionality

from flask import Flask, request, Response
import flask
from flask_cors import CORS
import ard_functions as a
import json

from datetime import datetime
import time



y = []

app = Flask(__name__)
CORS(app)

@app.route("/")
def welcomeScreen():
	return "Welcome"
	
	

@app.post("/ard_setup")
def ArduinoSetUpFunctions():
	
	if (request.form["task"] == "findPorts"):
		ports = a.findPorts()
		
		to_output = []
	
		for port in ports:
			print(port)	
			if ("Arduino" in str(port)):
				temp1 = str(port).split(" ")
				to_output.append({"value":str(port),"viewValue":temp1[0]})
				
			elif ("Stellaris" in str(port)):
                                temp1 = str(port).split(" ")
                                to_output.append({"value":str(port),"viewValue":temp1[0]})
                                
	
		return {"task":request.form["task"],"message":"success","output":to_output}
	
	elif (request.form["task"] == "openCOMs"):
		#print("Opening serial coms!")
		#print(request.form["message"])
		
		sent_str = request.form["message"]
		ardParams = sent_str.split(",")
		print(ardParams)
		
		try:
			global ard
			ard = a.openCOMs(ardParams)
			
			global y
			
			a.arduinoLoop(ard,y)
			
		except:
			print("Failed")
		
		"""
			Want to add an "output" that states when the Arduino is ready and finished restarting.
				Will need to add a print line in the Arduino code, and will need to create a function
				that will trap itself in a loop until it receives this message from the Arduino.
			This way the user will know that the Arduino is connected.
		"""
		
		return {"task":request.form["task"],"message":"success","output":[]}
		
	elif (request.form["task"] == "closeCOMs"):
		ard.close()
		print("Arduino is closed")
		
		return {"task":request.form["task"],"message":"success","output":[]}
		


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
			
			
			dict_toSend = json.dumps({"minute":datetime.now().minute,"second":datetime.now().second})
			time.sleep(1)
			yield f"data: {dict_toSend}\nevent: message\n\n"
			
			
			"""
			if y != []:
				dict_toSend = json.dumps({"item1":y})
				del y[:]
				
				yield f"data: {dict_toSend}\nevent: message\n\n"
			"""

	return Response(get_data(), mimetype="text/event-stream")
	
