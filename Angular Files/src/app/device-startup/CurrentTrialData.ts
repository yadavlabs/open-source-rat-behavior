/*
  This is an interface to receive the current trial data from the backend (Flask),
    which is then displayed in the table on the client-end.
*/

export interface CurrentTrialDataEle {
    sess_time: string; // Duration of the session (min)
    trial_n: string; // Current trial number (n)
    trial_type: string; // Left port (1) vs. Right port (2)
    stim_A: string; // Stimulus amplitude (uA)
    stim_fre: string; // Stimulus frequency (Hz)
    CV: string; // Session CV (0, 0.2, 0.4, 0.6, 0.8, 1)
    forced: string; // Whether current trial is forced (1) or unforced (0)
    trial_res: string; // Current trial response (1 = left port, 2 = right port, 5 = no response)
    per_cor: string; // Percent correct over session
}

export interface CurrentTrialDataAuditory {
    sess_time: string; // Duration of the session (min)
    trial_n: string; // Current trial number (n)
    trial_type: string; // Left port (1) vs. Right port (2)
    stim_duration: string; // Stimulus amplitude (uA)
    tone_freq: string; // Session CV (0, 0.2, 0.4, 0.6, 0.8, 1)
    forced: string; // Whether current trial is forced (1) or unforced (0)
    trial_res: string; // Current trial response (1 = left port, 2 = right port, 5 = no response)
    per_cor: string; // Percent correct over session
}
