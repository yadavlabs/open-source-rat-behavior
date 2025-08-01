
# experiment_handlers.py

''' This section corresponds to the Auditory detection/discrimination experiment '''

session_params_auditory = {
        "session_type": "Initial Training",
		"experiment_type": "Detection",
        "session_length": "60",
        "response_time": "10",
        "forced_trials": "Yes",
        "consecutive_error": "3"
}
stim_params_auditory = {
	"tone_durationL": "500",
	"tone_durationR": "100",
    "randomize": "0"
}
current_trial_data_auditory = {
        "sess_time":"-",
        "trial_n":"-",
        "trial_type":"-",
        "forced":"-",
        "tone_duration":"-",
        "trial_res":"-",
        "per_cor":"-"
}
# dictionary to store auditory session data to export/save
session_data_auditory = { #uses integers and/or floats (not strings) to populate dict
        "trial_time":[],
        "trial_number":[],
        "trial_type":[],
        "forced":[],
        "response":[],
        "response_time":[],
        "correct":[],
        "percent":[],
		"tone_duration":[],
        "randomized":[]
}
column_names_auditory = [
    'Time (sec)',
    'Trial',
    'Type',
    'Forced',
    'Response',
    'Response Time (sec)',
    'Correct',
    'Percent (%)',
    'Tone Duration (msec)',
    'Randomized'
]

def handle_data_auditory(self, line):
    """serial port "listener" to perform specific actions depending on what arduino writes to port
        # Inputs:
        #       ard              - serial port object for task arduino
        #       gib              - serial port object for stimulator
        #       y                - data stream variable for storing/sending display information to angular
        #       sessionData      - dict to store relevant behavioral data during session
        #       currentTrialData - dict to update trial table in angular
        #       stimParams       - dict containing parameters of stimulation
        """

    data = line.split(',')
    if data[0] == "Connected":
        print("[Arduino] Connected")
        print("[Arduino] Manual Control Enabled")
        self.serial_queue.put("Arduino " + data[0])
        self.serial_queue.put("Manual Control Enabled")
        self.serial_connected_event.set()

    elif data[0] == "Start":
        print("[Arduino] Beginning Session")
        self.serial_queue.put("Beginning Session")
            
    elif data[0] == "Trial":
        print("[Arduino] Trial time: " + data[1] + ", Trial Number: " + data[2])
        print("[Arduino] Trial Number: " + data[2])
        self.serial_queue.put("Trial Number: " + data[2]) 
        trial_time = int(data[1]) / 1000 # to seconds
        trial_number = data[2]
        ## update data 
        self.current_trial_data["sess_time"] = str(round(trial_time / 60,2))
        self.current_trial_data["trial_n"] = trial_number
        self.current_trial_data["trial_type"] = "-"
        self.current_trial_data["forced"] = "-"
        self.current_trial_data["tone_duration"] = "-"
        self.current_trial_data["trial_res"] = "-"
        #"sess_time"] = str(round(trial_time / 60,2)) #to minutes
        #self.current_trial_data["trial_n"] = data[2]
        #self.current_trial_data["trial_type"] = "-"
        #currentTrialData["stim_A"] = "-"
        #currentTrialData["stim_fre"] = "-"
        #currentTrialData["CV"] = "-"
        #currentTrialData["trial_res"] = "-"
        self.session_data["trial_time"].append(trial_time)
        self.session_data["trial_number"].append(int(data[2]))
                
    elif data[0] == "Type":
            
        if data[1] == "2": #right trial, no stimulation for detection experiment
            if self.session_params["experiment_type"] == "Discrimination" and self.session_params["session_type"] != "Initial Training":
                self.session_data["tone_duration"].append(self.stim_params["tone_durationR"])
                #self.session_data["amplitude"].append([])
                #self.session_data["frequency"].append([])
                #self.session_data["CV"].append([])
            else:
                self.session_data["tone_duration"].append([])
                #self.session_data["amplitude"].append([])
                #self.session_data["frequency"].append([])
                #self.session_data["CV"].append([])
        else: #left trial, stimulation if CV experiment is selected
                
            if self.session_params["session_type"] != "Initial Training": #self.stim_params["stim_enable"] == 1:
                #if stimParams["randomize"] == 1:
                #        randomizeAmplitude(gib, stimParams, y)
                #print("HERE")
                #print(stimParams["tone_durationL"])
                self.current_trial_data["tone_duration"] = self.stim_params["tone_durationL"]
                #currentTrialData["stim_fre"] = str(stimParams["frequency"])
                #currentTrialData["CV"] = str(stimParams["CV"])
                self.session_data["tone_duration"].append(self.stim_params["tone_durationL"])
                #self.session_data["amplitude"].append(stimParams["amplitude"])
                #self.session_data["frequency"].append(stimParams["frequency"])
                #self.session_data["CV"].append(stimParams["CV"])
            else:
                self.session_data["tone_duration"].append([])
                #self.session_data["amplitude"].append([])
                #self.session_data["frequency"].append([])
                #self.session_data["CV"].append([])
                            
        #datStr = ard.read_until(expected=b'\r\n').decode("utf").rstrip()
        #y.append(datStr)
        self.current_trial_data["trial_type"] = data[1]
        self.current_trial_data["forced"] = data[2]
        print(self.current_trial_data)
        self.session_data["trial_type"].append(int(data[1]))
        self.session_data["forced"].append(int(data[2]))
        self.session_data["randomized"].append(self.stim_params["randomize"])
        self.session_data["response"].append([])
        self.session_data["response_time"].append([])
        self.session_data["correct"].append([])
        self.session_data["percent"].append([])
            
    elif data[0] == "Stim":
        if data[1] == "1": #left trial
            if self.session_params["session_type"] == "Initial Training":
                self.serial_queue.put("No stim.")
            elif self.session_params["experiment_type"] == "Discrimination":
                self.serial_queue.put("Left port stim")
            else:
                self.serial_queue.put("Stim")
        else:
            print("No stim")
            if self.session_params["session_type"] == "Initial Training" or self.session_params["experiment_type"] == "Detection":
                self.serial_queue.put("No stim")
            else:
                self.serial_queue.put("Right port stim")
                
                    
    elif data[0] == "Response":
        res_time = int(data[1]) / 1000
        if data[3] == "1":
            datStr = "correct."
        elif data[3] == "0":
            datStr = "incorrect."
        elif data[3] == "5":
            #data[3] = "0"
            datStr = "forced."
        print("[Arduino] Response Time: " + str(res_time) + "sec")
        
        if data[2] == "1":
            datStr = "Left Port Response, " + datStr
        elif data[2] == "2":
            datStr = "Right Port Response, " + datStr
        elif data[2] == "5":
            datStr = "No response."
                
        print("[Arduino] " + datStr)
        self.serial_queue.put(datStr)
        self.current_trial_data["trial_res"] = data[2]
        self.session_data["response_time"][-1] = res_time
        self.session_data["response"][-1] = int(data[2])
        self.session_data["correct"][-1] = int(data[3])
            
            
    elif data[0] == "Percent":
        
        percent = float(data[1]) * 100
        self.current_trial_data["per_cor"] = str(percent)
        self.session_data["percent"][-1] = percent
        self.serial_queue.put("Running percentage correct: " + str(percent) + "%")
            
    elif data[0] == "End":
        print("[Arduino] Session Ended")
        self.serial_queue.put("Session Ended")
        
    elif data[0] == "Wait":
        print("[Arduino] Manual Control Enabled")
        self.serial_queue.put("Manual Control Enabled")
        #break_flag = 1
    elif data[0] == "Wait for Response":
        print("[Arduino] Waiting for response...")
        self.serial_queue.put("Waiting for response...")
    #elif data[0] == "Paused":
    #        print("Paused")
    #        y.append(data[0])
    elif data[0] == "GET":
        #print(data[0] + "," + data[1] + "," + data[2])
        #print(data[2])
        if data[1] in self.session_params:
            previous_val = self.session_params[data[1]]
            setting_type = "Session Setting"
        elif data[1] in self.stim_params:
            previous_val = self.stim_params[data[1]]
            setting_type = "Stimulation Parameter"
        else:
            print("[Arduino] Warning: Parameter '" + data[1] + "' not found")
            return
        
        print("[Arduino] Verifying " + setting_type + ": '" + data[1] + "' is '" + previous_val + "'...")
        if previous_val != data[2]:
            print("[Arduino] Updating: '" + data[1] + "'... ")
            param = {data[1]: data[2]} # format as dictionary
            self.serial_queue.put("GET," + data[1] + "," + data[2])
            self.update_params(param)
        else:
            print("[Arduino] Parameter '" + data[1] + "' OK")
            #print("[Arduino] " + setting_type + "OK: '" + data[1] + "' == " + previous_val)
            #print("[Arduino] " + setting_type + "'" + param + "' OK: " + data[2])


            '''
            print("[Arduino] Verifying Session Setting: '" + data[1] + "'...")
            #print(self.session_params[data[1]])
            #print(self.session_data[data[1]])
            if self.session_params[data[1]] != data[2]:

                print("[Arduino] Updating: '" + data[1] + "'... ")
                print("[Arduino]  value: " + self.session_params[data[1]])
                print("[Arduino] New value: " + data[2])
                param = {data[1]: data[2]}
                self.update_params(param)
            else:
                print("[Arduino] Parameter '" + param + "' OK: " + data[2])

        elif data[1] in self.stim_params:
            print("[Arduino] Verifying Stimulataion Parameter: '" + data[1] + "'...")
            if self.stim_params[data[1]] != data[2]:
                print("[Arduino] Updating: '" + data[1] + "'... ")
                print("[Arduino] Old value: " + self.stim_params[data[1]])
                print("[Arduino] New value: " + data[2])
                param = {data[1]: data[2]}
                self.update_params(param)
            else:
                print("[Arduino] OK")
                '''

    elif data[0] == "SET":
        if len(data) == 4:
            msg = "Updated parameter: '" + data[1] + "' set to " + data[2] + data[3]
        else:
            msg = "Updated parameter: '" + data[1] + "' set to " + data[2]
        print("[Arduino] " + msg)
        self.serial_queue.put(msg)
        
    else:
        print("[Arduino] " + data[0])
        self.serial_queue.put(data[0])
