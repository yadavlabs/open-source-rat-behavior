# helper functions
# currently only contains function for exporting session data

import pandas as pd
import os
import sys
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
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
    

def saveSessionData(session_data, column_names):
    print("[Flask] Saving session data...")
    file_name = get_save_path_via_dialog_window()
    if not file_name:
        print("[Flask] File save cancelled.")
        return "File save cancelled"
    print("ehrer")
    print(file_name)
    df = pd.DataFrame(session_data)
    df.columns = column_names

    if (".xlsx" in str(file_name)):
        df.to_excel(file_name, index=False)

    elif (".csv" in str(file_name)):
        df.to_csv(file_name)

    return "Session data saved: " + file_name



def get_save_path_via_dialog_window(default_name=('Rat_' + datetime.now().strftime("%m-%d-%y")), default_path=r'C:/'):
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    root.update()
    root.iconify()

    file_type = [('Excel (*.xlsx)','*.xlsx'), ('CSV (*.csv)', '*.csv')]
    file_name = filedialog.asksaveasfilename(
        title='Save Session Data',
        initialfile=default_name,
        initialdir=default_path,
        filetypes=file_type,
        defaultextension=file_type
    ) #generate asksaveasfile window

    root.destroy()

    return file_name if file_name else None
