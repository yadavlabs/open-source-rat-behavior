export interface FormFieldConfig {
    key: string;
    label: string;
    value: string;

    isDiscrimination?: boolean;
}

export const FormFieldsSCS: FormFieldConfig[] = [
    {key: 'anode', label: 'Anode', value: '16'},
    {key: 'cathode', label: 'Cathode', value: '1'},
    {key: 'frequency', label: 'Frequency (Hz)', value: '50'},
    {key: 'duration', label: 'Pulse Width (us)', value: '200'},
    {key: 'amplitude', label: 'Amplitude (uA)', value: '100'},
    {key: 'train_length', label: 'Train Length (sec)', value: '1'},
    {key: 'cathodeL', label: 'Left Port Cathode', value: '1', isDiscrimination: true},
    {key: 'cathodeR', label: 'Right Port Cathode', value: '14', isDiscrimination: true},
];

export type ExperimentModeSCS = "Initial Training" | "Discrimination" | "Detection";