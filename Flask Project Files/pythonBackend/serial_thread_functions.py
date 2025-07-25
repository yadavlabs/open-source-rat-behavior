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

COMMAND_MAP = {
    "left-door": lambda state: f"D{int(state == 'true')}",
    "right-door": lambda state: f"d{int(state == 'true')}",
}

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


def findPorts(): #finds and returns devices ocnnected to serial port
	ports = list(port_list.comports())
	
	return ports


class ArduinoManager:
    def __init__(self):
        self.ard = None
        self.serial_thread = None
        self.serial_queue = Queue()
        self.serial_stop_event = threading.Event()
        self.serial_connected_event = threading.Event()

    def serial_listener(self):
        print("[THREAD] Serial listener started.")
        while not self.serial_stop_event.is_set():
            try:
                if self.ard.is_open and self.ard.in_wating:
                    line = self.ard.read_until(expected=b'\r\n').decode("utf").rstrip() #readline().decode('utf-8').strip()
                    if line:
                        self.serial_queue.put(line)
            except serial.SerialException as e:
                    print(f"Serial error: {e}")
                    #self.serial_stop_event.set()
            time.sleep(0.1)  # Sleep to prevent busy waiting
        print("[THREAD] Serial listener stopped.")

    def connect(self, port="COM6", baudrate=9600):
        if self.ard and self.ard.is_open:
            return "Arduino already connected."
        try:
            self.ard = serial.Serial(port, baudrate, timeout=2)  # Initialize the serial port object
            self.serial_stop_event.clear()  # Clear the stop event
            self.serial_thread = threading.Thread(target=self.serial_listener, daemon=True)  # Create a thread for serial communication
            self.serial_thread.start()  # Start the serial thread
            return "Establishing connection"
        except Exception as e:
            return f"Error connecting to Arduino: {e}"
        
    def disconnect(self):
        if self.ard and self.ard.is_open:
            self.serial_stop_event.set()
            time.sleep(0.1)  # Give some time for the thread to stop
            self.ard.close()
            self.serial_thread.join()  # Wait for the thread to finish
            self.ard = None
            return "Disconnected from Arduino."
        return "Arduino is not connected."
    
    def send_command(self, command):
        if self.ard and self.ard.is_open:
            try:
                self.ard.write((command + '\r\n').encode('utf-8'))  # Send command to Arduino
                return "Command sent."
            except serial.SerialException as e:
                return f"Error sending command: {e}"
        return "Arduino is not connected."
    



     
