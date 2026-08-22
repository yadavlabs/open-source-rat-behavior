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
    tone_duration: string; // Stimulus amplitude (uA)
    forced: string; // Whether current trial is forced (1) or unforced (0)
    trial_res: string; // Current trial response (1 = left port, 2 = right port, 5 = no response)
    per_cor: string; // Percent correct over session
}

export interface CurrentTrialDataVibration {
    sess_time: string; // Duration of the session (min)
    trial_n: string; // Current trial number (n)
    trial_type: string; // Left port (1) vs. Right port (2)
    vibration_level: string; // Vibration level (PWM value)
    vibration_length: string; // Vibration length (ms)
    forced: string; // Whether current trial is forced (1) or unforced (0)
    trial_res: string; // Current trial response (1 = left port, 2 = right port, 5 = no response)
    per_cor: string; // Percent correct over session
}

export interface CurrentTrialDataSpatialSCS2 {
    sess_time: string; // Duration of the session (min)
    trial_n: string; // Current trial number (n)
    trial_type: string; // Left port (1) vs. Right port (2)
    amplitude: string; // Stimulus amplitude (uA)
    cathode: string; // Stimulus frequency (Hz)
    anode: string; // Session CV (0, 0.2, 0.4, 0.6, 0.8, 1)
    forced: string; // Whether current trial is forced (1) or unforced (0)
    trial_res: string; // Current trial response (1 = left port, 2 = right port, 5 = no response)
    per_cor: string; // Percent correct over session

}

export const TRIAL_TABLE_FIELDS_SPATIAL_SCS = [
    { key: 'sess_time', label: 'Time (min)' },
    { key: 'trial_n', label: 'Trial #' },
    { key: 'trial_type', label: 'Type' },
    { key: 'forced', label: 'Forced' },
    { key: 'amplitude', label: 'Amplitude (uA)' },
    { key: 'cathode', label: 'Cathode' },
    { key: 'anode', label: 'Anode' },
    { key: 'trial_res', label: 'Response' },
    { key: 'per_cor', label: 'Correct (%)' }
] as const;

export type CurrentTrialDataSpatialSCS = Record<typeof TRIAL_TABLE_FIELDS_SPATIAL_SCS[number]['key'], string>;

export function createDefualtTrialDataSpatialSCS(): CurrentTrialDataSpatialSCS {
    const defaultObj = {} as any;
    TRIAL_TABLE_FIELDS_SPATIAL_SCS.forEach(field => {
        defaultObj[field.key] = 'N/A';
    });
    return defaultObj
}
// export const DEFUALT_TRIAL_DATA_SPATIAL_SCS = {
//    sess_time: 'N/A', // Duration of the session (min)
//    trial_n: 'N/A', // Current trial number (n)
//    trial_type: 'N/A', // Left port (1) vs. Right port (2)
//    amplitude: 'N/A', // Stimulus amplitude (uA)
//    cathode: 'N/A', // Stimulus frequency (Hz)
//    anode: 'N/A', // Session CV (0, 0.2, 0.4, 0.6, 0.8, 1)
//    forced: 'N/A', // Whether current trial is forced (1) or unforced (0)
//    trial_res: 'N/A', // Current trial response (1 = left port, 2 = right port, 5 = no response)
//    per_cor: 'N/A', // Percent correct over session
// } as const;

//export type CurrentTrialDataSpatialSCS = {
//    -readonly [K in keyof typeof DEFUALT_TRIAL_DATA_SPATIAL_SCS]: string;
//};