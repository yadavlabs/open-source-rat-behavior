# helper functions
# currently only contains function for exporting session data

import pandas as pd
import os
import sys
import tkinter as tk
from tkinter import filedialog
from datetime import date
import time

def saveSessionDataUI(sessionData, y):

    print("Saving session data...")
    y.append("Saving session data...")
    root = tk.Tk()
    root.attributes('-topmost', True)
    root.iconify()
    #root.withdraw()
    
    column_names = [
        'Time (sec)',
        'Trial',
        'Type',
        'Forced',
        'Response',
        'Response  Time (sec)',
        'Correct',
        'Percent (%)',
        'Tone Duration (sec)',
        'Randomized',
        'Amplitude (uA)',
        'Frequency (Hz)',
        'CV'
    ] #column names for spreadsheet
    file_type = [('Excel (*.xlsx)','*.xlsx'), ('CSV (*.csv)', '*.csv')] #specify .xlsx file
    
    file_info = filedialog.asksaveasfile(
        title='Save Session Data',
        initialdir=r'C:\Most Recent Design Files\Data',
        filetypes=file_type,
        defaultextension=file_type
    ) #generate asksaveasfile window
    st = time.time()
    root.destroy()
    if not file_info: # on cancel or window closed
        print("Saving aborted.")
        y.append("Saving aborted.")
        
    else: # on save press
        df = pd.DataFrame(sessionData)
        df.columns = column_names

        print(file_info.name)
        if (".xlsx" in str(file_info.name)):
            df.to_excel(file_info.name, index=False)

        elif(".csv" in str(file_info.name)):
            df.to_csv(file_info.name)
            
        print("File saved: " + file_info.name)
        y.append("File saved: " + file_info.name)
    
    et = time.time()
    el = et - st
    print('Execution time: ', el, 'seconds')
    root.mainloop()
    
