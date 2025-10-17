import serial
import serial.tools.list_ports as port_list
import time
import random
import threading
from queue import Queue


#ard = None #serial.Serial() # A serial port object responsible for communication with the Arduino
#serial_thread = None # Thread for serial communication
#serial_queue = Queue() # Queue for serial data
#serial_stop_event = threading.Event() # Event to stop the serial thread
#serial_connected_event = threading.Event() # Event to signal that the serial port is connected

# dictionary of commands for manually controlling operant chamber components and starting/stopping/pausing experiment
COMMAND_MAP = {
    "left-door": lambda state: f"D{int(state == 'true')}",
    "right-door": lambda state: f"d{int(state == 'true')}",
    "left-flush": lambda state: f"L{int(state == 'true')}",
    "right-flush": lambda state: f"R{int(state == 'true')}",
    "house-light": lambda state: f"H{int(state == 'true')}",
    "buzzer": lambda state: f"B{int(state == 'true')}",
    "test-sensors": lambda state: f"{'J' if state == 'true' else 'K'}",
    "pause": lambda state: f"{'p' if state == 'true' else 'u'}",
    "stop": lambda state: "Q",
    "start": lambda state: "b"
}

# dictionary of "GET" commands for returning parameters currently set on the Arduino
GET_PARAM_MAP = {
    "session_length": "G1",
    "response_time": "G2",
    "consecutive_error": "G3",
    "session_type": "G4",
    "forced_trials": "G5",
    "experiment_type": "G6",
    "tone_durationL": "G7",
    "tone_durationR": "G8"
}

# dictionary of "SET" commands for setting/changing parameters on the Arduino
SET_PARAM_MAP = {
    "session_length": lambda new_val: f"P1{new_val}",
    "response_time": lambda new_val: f"P2{new_val}",
    "consecutive_error": lambda new_val: f"P3{new_val}",
    "session_type": lambda new_val: f"P4{int(new_val == 'Initial Training')+1}",
    "forced_trials": lambda new_val: f"P5{int(new_val == 'Yes')}",
    "experiment_type": lambda new_val: f"P6{int(new_val == 'Discrimination')}",
    "tone_durationL": lambda new_val: f"P7{new_val}",
    "tone_durationR": lambda new_val: f"P8{new_val}"
}

#finds and returns devices ocnnected to serial port
def findPorts(): 
	ports = list(port_list.comports())
	
	return ports


class ArduinoManager:
    def __init__(self):
        self.ard = None # serial port object
        self.serial_thread = None # thread for serial communication
        self.serial_queue = Queue() # queue for serial data to be placed
        self.serial_stop_event = threading.Event() # event to stop serial thread
        self.serial_connected_event = threading.Event() # event to signal that the arduino is connected
        self._handle_data = lambda line: None # default, function for handling received data from the arduino 
        self.session_params = {} # dictionary of session parameters
        self.stim_params = {} # dictionary of stimulation parameters
        self.current_trial_data = {} # dictionary of current trial data
        self.session_data = {} # dictionary of session data
        self.column_names = [] # list of column names for exporting session data
        #print(f"Active threads before thread finishes: {threading.active_count()}")
        active_threads = threading.enumerate()
        for thread in active_threads:
            if thread.name != "MainThread":
                print(f"Thread Name: {thread.name}, is alive: {thread.is_alive()}")
                thread.join()
    
    # set properties specific to experiment, found in experiment_handlers.py
    def initialize_experiment(self, session_params, stim_params, current_trial_data, session_data, column_names):
        self.session_params = session_params
        self.stim_params = stim_params
        self.current_trial_data = current_trial_data
        self.session_data = session_data
        self.column_names = column_names

    # listener thread for reading incoming serial port data
    def _serial_listener(self):
        print("[THREAD] Serial listener started.")
        while not self.serial_stop_event.is_set():
            try:
                if self.ard.is_open and self.ard.in_waiting:
                    
                    line = self.ard.read_until(expected=b'\r\n').decode("utf").rstrip() #readline().decode('utf-8').strip()
                    #print(line)
                    if line:
                        self._handle_data(line)
                        #self.serial_queue.put(line)

            except serial.SerialException as e:
                    print(f"Serial error: {e}")
                    #self.serial_stop_event.set()
            time.sleep(0.1)  # Sleep to prevent busy waiting
        print("[THREAD] Serial listener stopped.")

    # connect to arduino and start listener
    def connect(self, port="COM6", baudrate=9600):
        if self.ard and self.ard.is_open:
            return "Arduino already connected."
        try:
            self.ard = serial.Serial(port, baudrate, timeout=2)  # Initialize the serial port object
            self.serial_stop_event.clear()  # Clear the stop event
            self.serial_connected_event.clear()
            self.serial_thread = threading.Thread(target=self._serial_listener, daemon=True)  # Create a thread for serial communication
            self.serial_thread.start()  # Start the serial thread
            return "Establishing connection"
        except Exception as e:
            return f"Error connecting to Arduino: {e}"
    
    # disconnect from arduino and stop listener
    def disconnect(self):
        if self.ard and self.ard.is_open:
            self.serial_stop_event.set()
            time.sleep(0.2)  # Give some time for the thread to stop
            self.ard.close()
            self.serial_thread.join()  # Wait for the thread to finish
            self.ard = None
            return "Disconnected from Arduino."
        return "Arduino is not connected."
    
    # send command
    def send_command(self, component, state):
        #command = COMMAND_MAP[component](state)
        print(COMMAND_MAP[component](state))
        self.write_utf(COMMAND_MAP[component](state))

    # write utf-8 encoded data to arduino
    def write_utf(self, data):
        if self.ard and self.ard.is_open:
            try:
                self.ard.write((data).encode('utf-8'))  # Send command to Arduino
                return "Command sent."
            except serial.SerialException as e:
                return f"Error sending command: {e}"
        return "Arduino is not connected."
    
    # requests arduino to return all relevent parameters currently loaded
    def get_loaded_params(self):
        # get session parameters, will be updated in _handle_data function
        # value in python are different from value loaded on arduino 
        for param in self.session_params: 
            if param in GET_PARAM_MAP:
                self.write_utf(GET_PARAM_MAP[param])

        # get stimulation parameters, will be updated in _handle_data function
        # value in python are different from value loaded on arduino 
        for param in self.stim_params:
            if param in GET_PARAM_MAP:
                self.write_utf(GET_PARAM_MAP[param])
            #print("[Arduino] " + param + ": " + GET_PARAM_MAP[param])

    # update parameter(s) using a dictionary "params"
    def update_params(self, params):
        for param, val in params.items():
            #print(param + ": " + val)
            #print("Command: " + SET_PARAM_MAP[param](val))
            #print(val != self.session_params[param])
            #self.send_command(SET_PARAM_MAP[param](val))
            update_val = False
            if (param in self.session_params) and (val != self.session_params[param]):
                update_val = True
                self.session_params[param] = val
                #print("Session Parameter Updated: " + param)
                #print("Session" + param)
            elif (param in self.stim_params) and (val != self.stim_params[param]):
                update_val = True
                self.stim_params[param] = val
                #print("Stim Parameter Updated: " + param)
            if update_val:
                self.write_utf(SET_PARAM_MAP[param](val))
                update_val = False
            
                #print("Stim" + param)
            #if val != self.session_params[param]:
            #    self.send_command(SET_PARAM_MAP[param](val))


    def get_queue(self):
        return self.serial_queue
    
    def is_connected(self):
        return self.ard and self.ard.is_open
    
    # sets the experiment handler function (found in experiment_handlers.py)
    def assign_handler(self, handler_fnc):
        self._handle_data = handler_fnc.__get__(self, ArduinoManager)
        


    



     
