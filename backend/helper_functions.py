# helper functions
# currently only contains function for exporting session data

import pandas as pd
import os
import sys
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import time
import json
import io

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

    print(file_name)
    df = pd.DataFrame(session_data)
    df.columns = column_names

    if (".xlsx" in str(file_name)):
        df.to_excel(file_name, index=False)

    elif (".csv" in str(file_name)):
        df.to_csv(file_name)

    return "Session data saved: " + file_name

def saveSessionDataD(session_data, column_names, file_format="xlsx"):
    """
    Refactored saveSessionData: Bypasses Tkinter completely.
    Converts session_data matrices into an in-memory binary tracking buffer
    to stream down the web pipeline directly into the user's browser.
    """
    print("[Docker Helper] Flask is structuring an in-memory session export stream...")
    
    # 1. Map your row arrays directly to a pandas DataFrame and apply your structural headers
    df = pd.DataFrame(session_data)
    df.columns = column_names
    
    # 2. Allocate an isolated memory byte block to capture file data
    file_stream = io.BytesIO()
    
    # 3. Compile the file structure into memory depending on the format requested
    if file_format == "xlsx":
        with pd.ExcelWriter(file_stream, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = "experiment_behavior_log.xlsx"
        
    else:  # Fallback seamlessly to standard CSV format 
        text_stream = io.StringIO()
        df.to_csv(text_stream, index=False)
        file_stream.write(text_stream.getvalue().encode('utf-8'))
        mimetype = "text/csv"
        filename = 'Rat_' + datetime.now().strftime("%m-%d-%y")
        
    # 4. Rewind the stream memory pointer back to index zero so Flask reads from the beginning
    file_stream.seek(0)
    return file_stream, mimetype, filename

def saveSessionTaskParams(task_params):
    print("[Flask] Saving task parameters...")
    file_name = get_save_path_via_dialog_window(file_type=[('JSON (*.json)','*.json')], title='Save Task Parameters')
    if not file_name:
        print("[Flask] File save cancelled.")
        return "File save cancelled"
    
    print(file_name)
    with open(file_name, 'w') as f:
        json.dump(task_params, f, indent=4)


    return "Task parameters saved: " + file_name

def loadSessionTaskParams():
    print("[Flask] Loading task parameters...")
    file_name = get_load_path_via_dialog_window()
    if not file_name:
        print("[Flask] File load cancelled.")
        return None
    
    with open(file_name, 'r') as f:
        task_params = json.load(f)

    return task_params


def get_save_path_via_dialog_window(default_name=('Rat_' + datetime.now().strftime("%m-%d-%y")), default_path=r'C:/', 
                                    file_type=[('Excel (*.xlsx)','*.xlsx'), ('CSV (*.csv)', '*.csv')], 
                                    title='Save Session Data'):
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    root.update()
    root.iconify()

    #file_type = [('Excel (*.xlsx)','*.xlsx'), ('CSV (*.csv)', '*.csv')]
    file_name = filedialog.asksaveasfilename(
        title=title,
        initialfile=default_name,
        initialdir=default_path,
        filetypes=file_type,
        defaultextension=file_type
    ) #generate asksaveasfile window

    root.destroy()

    return file_name if file_name else None


def get_load_path_via_dialog_window(default_path=r'C:/'):
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    root.update()
    root.iconify()
    print('here')
    file_type = [('JSON (*.json)','*.json')]#, ('CSV (*.csv)', '*.csv')]
    file_name = filedialog.askopenfilename(
        title='Load Experiment File',
        initialdir=default_path,
        filetypes=file_type,
    ) #generate asksaveasfile window

    root.destroy()

    return file_name if file_name else None

def get_session_summary(session_data):
    """
    Generate a summary of the session data.
    """
    if not session_data:
        return "No session data available."

    total_trials = len(session_data)
    correct_trials = sum(1 for trial in session_data if trial['Correct'])
    percent_correct = (correct_trials / total_trials) * 100 if total_trials > 0 else 0

    summary = {
        'Total Trials': total_trials,
        'Correct Trials': correct_trials,
        'Percent Correct': percent_correct
    }

    return summary
