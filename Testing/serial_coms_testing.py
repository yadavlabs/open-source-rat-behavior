
import serial_coms_testing_functions as sp




ardParams = ['9600', 'COM6']

try:
        global ard
        global y

        ard = sp.openCOMS(ardParams)
        
except:
        print("Failed to connected.")
