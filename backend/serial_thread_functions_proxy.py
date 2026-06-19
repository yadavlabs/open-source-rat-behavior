#import serial
#import serial.tools.list_ports as port_list
import socket
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
    "start": lambda state: "b",
    "test-stim": lambda state: "S"
}

# dictionary of "GET" commands for returning parameters currently set on the Arduino
GET_PARAM_MAP = {
    "session_length": "G1",
    "response_time": "G2",
    "consecutive_error": "G3",
    "session_type": "G4",
    "forced_trials": "G5",
    "experiment_type": "G6",
    "vibration_levelL": "G7",
    "vibration_levelR": "G8",
    "vibration_length": "G9"
}

# dictionary of "SET" commands for setting/changing parameters on the Arduino
SET_PARAM_MAP = {
    "session_length": lambda new_val: f"P1{new_val}",
    "response_time": lambda new_val: f"P2{new_val}",
    "consecutive_error": lambda new_val: f"P3{new_val}",
    "session_type": lambda new_val: f"P4{int(new_val == 'Initial Training')+1}",
    "forced_trials": lambda new_val: f"P5{int(new_val == 'Yes')}",
    "experiment_type": lambda new_val: f"P6{int(new_val == 'Discrimination')}",
    "vibration_levelL": lambda new_val: f"P7{new_val}",
    "vibration_levelR": lambda new_val: f"P8{new_val}",
    "vibration_length": lambda new_val: f"P9{new_val}"
}

#finds and returns devices ocnnected to serial port
def findPorts(): 
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("host.docker.internal", 8888))
        s.sendall(b"LIST_PORTS")
        response = s.recv(1024).decode('utf-8').strip()
        #ports = data.split(',')
        s.close()
        if response:

            return [f"{port_name}" for port_name in response.split(",")]
    except Exception as e:
        print(f"[Docker Engine] Could not reach Windows Host Proxy: {e}")
        return []
	
	


class ArduinoManager:
    def __init__(self):
        #self.ard = None # serial port object
        self.socket_connection = None
        self.host_ip = "host.docker.internal"
        self.serial_thread = None # thread for serial communication
        self.serial_queue = Queue() # queue for serial data to be placed
        self.serial_stop_event = threading.Event() # event to stop serial thread
        self.serial_connected_event = threading.Event() # event to signal that the arduino is connected
        self._handle_data = lambda line: None # default, function for handling received data from the arduino 
        self.session_params = {} # dictionary of session parameters
        self.stim_params = {} # dictionary of stimulation parameters
        self.task_params = {} # dictionary for controlling stimulation parameter randomization
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
    def initialize_experiment(self, session_params, stim_params, task_params, current_trial_data, session_data, column_names):
        self.session_params = session_params
        self.stim_params = stim_params
        self.task_params = task_params
        self.current_trial_data = current_trial_data
        self.session_data = session_data
        self.column_names = column_names
        if "task_array" in self.task_params: #might just remove this but trying to manage backwards compatibility. 
            #I already have immediately made this not backwards compatible by isolating randomization params to a new dictionary
            # but oh well
            self.setup_task_randomization()

    # listener thread for reading incoming serial port data
    def _serial_listener(self):
        print("[THREAD] Serial listener started.")
        while not self.serial_stop_event.is_set():
            try:
                if self.socket_connection:#self.ard.is_open and self.ard.in_waiting:
                    data = self.socket_connection.recv(2048).decode('utf-8', errors='ignore')
                    if data:
                        buffer += data
                        while "\n" in buffer:
                            line, buffer = buffer.split("\n", 1)
                            line = line.strip()
                            if line:
                                self._handle_data(line)
                    #line = self.ard.read_until(expected=b'\r\n').decode("utf").rstrip() #readline().decode('utf-8').strip()
                    #print(line)
                    #if line:
                    #    self._handle_data(line)
                    #    #self.serial_queue.put(line)

            except Exception as e:
                    print(f"Serial error: {e}")
                    #self.serial_stop_event.set()
            time.sleep(0.1)  # Sleep to prevent busy waiting
        print("[THREAD] Serial listener stopped.")

    # connect to arduino and start listener
    def connect(self, port="COM6", baudrate=9600):
        if self.socket_connection:
            return "Arduino already connected."
        try:
            # Clean string name if extracted containing our proxy string tag
            clean_com_port = port.split(" ")[0].strip()
            
            # 1. Instruct proxy to start bridging the COM port
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host_ip, 8888))
            s.sendall(f"CONNECT:{clean_com_port}:{baudrate}\n".encode('utf-8'))
            status = s.recv(1024).decode('utf-8').strip()
            s.close()

            if status != "SUCCESS":
                return f"Windows host failed to unlock COM port {clean_com_port}"

            # 2. Derive matching target port layout
            digits = ''.join(filter(str.isdigit, clean_com_port))
            tcp_port = 9000 + (int(digits) if digits else 0)
            time.sleep(0.5)
            
            # 3. Secure network streaming connection
            self.socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_connection.connect((self.host_ip, tcp_port))

            self.serial_stop_event.clear()  # Clear the stop event
            self.serial_connected_event.clear()
            self.serial_thread = threading.Thread(target=self._serial_listener, daemon=True)  # Create a thread for serial communication
            self.serial_thread.start()  # Start the serial thread
            return "Establishing connection"
        except Exception as e:
            return f"Error connecting to Arduino: {e}"
    
    # disconnect from arduino and stop listener
    def disconnect(self):
        if self.socket_connection:
            self.serial_stop_event.set()
            time.sleep(0.2)  # Give some time for the thread to stop
            self.socket_connection.close()
            self.serial_thread.join()  # Wait for the thread to finish
            self.socket_connection = None
            self.serial_connected_event.clear()
            return "Disconnected from Arduino."
        return "Arduino is not connected."
    
    # send command
    def send_command(self, component, state):
        #command = COMMAND_MAP[component](state)
        print(COMMAND_MAP[component](state))
        self.write_utf(COMMAND_MAP[component](state))

    # write utf-8 encoded data to arduino
    def write_utf(self, data):
        if self.socket_connection:
            try:
                self.socket_connection.sendall(f"{data}\n".encode('utf-8'))  # Send command to Arduino
                return "Command sent."
            except Exception as e:
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

    def setup_task_randomization(self, seed=42):
        random.seed(seed)
        if not self.task_params["task_array_shuffled"]: # will do this on startup. Overwritten by loading experiment file
            self.task_params["task_idx"] = 0
            self.task_params["task_array_shuffled"] = random.sample(self.task_params["task_array"], len(self.task_params["task_array"]))
            self.task_params["shuffle_idx"] = self.task_params["shuffle_idx"] + 1 # first shuffle

        
    def randomize_task_parameter(self):

        if self.task_params["task_idx"] == len(self.task_params["task_array"]): # re-shuffled task_array
            self.task_params["task_idx"] = 0
            self.task_params["task_array_shuffled"] = random.sample(self.task_params["task_array"], len(self.task_params["task_array"]))
            self.task_params["shuffle_idx"] = self.task_params["shuffle_idx"] + 1
        
        # format next value as dictionary and send for updates
        # task_param_name specifies the target parameter for updating
        next_param = {self.task_params["task_param_name"] : str(self.task_params["task_array_shuffled"][self.task_params["shuffle_idx"]])}
        self.update_params(next_param)
        self.task_params["task_idx"] = self.task_params["task_idx"] + 1 #incriment task_idx


    def get_queue(self):
        return self.serial_queue
    
    def is_connected(self):
        #return self.ard and self.ard.is_open
        return self.socket_connection is not None
    
    # sets the experiment handler function (found in experiment_handlers.py)
    def assign_handler(self, handler_fnc):
        self._handle_data = handler_fnc.__get__(self, ArduinoManager)
        


    



     
