

''' General parameter defaults for 2AFC Tasks (consistent regardless of stimulus type)'''

# Main session parameters that govern the experiment
session_params = {
    "session_type": "Initial Training",
	"experiment_type": "Detection",
    "session_length": "60",
    "response_time": "10",
    "forced_trials": "Yes",
    "consecutive_error": "3"
}

# holds current trial data of a given trial. This is what appears in the trial table of the GUI.
current_trial_data = { #uses strings to populate dict (why? because I don't want to change the typescript that handles the json dump)
    "sess_time":"-",
    "trial_n":"-",
    "trial_type":"-",
    "forced":"-",
    #"vibration_level":"-",
    #"vibration_length":"-",
    "trial_res":"-",
    "per_cor":"-"
}

# holds data for the entire session, to be exported/saved
session_data = { #uses integers and/or floats (not strings) to populate dict
    "trial_time":[],
    "trial_number":[],
    "trial_type":[],
    "forced":[],
    #"vibration_level":[],
    #"vibration_length":[],
    "randomized":[],
    "response":[],
    "response_time":[],
    "correct":[],
    "percent":[]
}

column_names = {
    "trial_time": 'Time (sec)',
    "trial_number": 'Trial',
    "trial_type": 'Type',
    "forced": 'Forced',
    "randomized": 'Randomized',
    "response": 'Response',
    "response_time": 'Response Time (sec)',
    "correct": 'Correct',
    "percent": 'Percent (%)'
}

''' stimulation parameters for SCS '''

''' 
stim_params_scs = { #uses integers and floats (not strings) to populate dict
        "frequency":[],  #frequency in Hz
        "amplitude":[],  #running amplitude in uA
        #"CV":[],         #coefficient of variation of stimulation (0-1 with steps of 0.1)
        #"pulse_width":[],#pulse-width in us
        #"ipi":[],        #inter-pulse interval in us
        "pulse_num":[],  #number of pulses (only used in periodic case (i.e. CV = 0)
        "stim_enable":1, #indicates if experiment involves stimulation
        "periodic":0,    #indicates if stimulation is periodic (CV = 0) or aperiodic (CV > 0)
        "randomize":0,   #indicates if stimulation parameter should be randomized
        "base_amp":[],   #base/default amplitude set at beginning of session (if randomize=0, this amplitude is used for stimulation trials)
        "task_amps":list(range(25,275,25)), #amplitudes to be randomized and tested (this variable can be changed depending on the experiment)
        "shuffled_amps":[], #randomized amplitudes based on task_amps
        "amp_indx":0,     #index to track which amplitudes have been tested in shuffled_amps
		"tone_duration": [], #duration of the tone in seconds
		"tone_durationL": [],
		"tone_durationR": [],
		"discrimination": 1
}
'''
stim_params_scs = {
    "anode": [], # anode electrode
    "cathode": [], # cathode electrode
    #"sequential": False,
    "frequency": [], # frequency in Hz
    "duration": [], # pulse width in us
    "amplitude": [], # amplitude in uA
    "train_length": [], # length of pulse train in sec
    #"step": [],
    #"amplitude_cathode": [],
    #"amplitude_anode": [],
    "randomize": 0 # indicates if stimulation parameters should be randomized
}

stim_task_params_scs = {
    "task_param_name": "amplitude", # name of stim parameter to be randomized
    "task_array": list(range(25,250,25)), # stim parameters to be randomized
    "task_array_shuffled": [], # randomized permutation of task_array
    "task_idx": 0, # counter for indexing through task_array_shuffled
    "shuffle_idx": 0, # counter for tracking number of times task_array has been re-shuffled -> when task_idx == len(task_array)
    "all_param_names": ["amplitude","cathode", "anode", "frequency", "duration", "train_length"], # list of all stim parameters
    "table_param_names": ["amplitude", "cathode", "anode"]
}

current_trial_data_scs = current_trial_data.copy()
current_trial_data_scs.update({"amplitude": "-", "cathode": "-", "anode": "-"})

session_data_scs = session_data.copy()
session_data_scs.update({"amplitude": [], "cathode": [], "anode": [], "frequency": [], "duration": [], "train_length": []})
column_names_scs = column_names.copy()
column_names_scs.update({
    "amplitude": "Amplitude (uA)", 
    "cathode": "Cathode", 
    "anode": "Anode", 
    "frequency": "Frequency (Hz)", 
    "duration": "Pulse Width (us)", 
    "train_length": "Train Length (sec)"
    }
)




#def get_stim_task_params():
