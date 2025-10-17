// Importing modules
import { Component } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';

// Importing services
import { FlaskService } from '../total.service';
import { SSEService } from './sse.service';
import { Subscription } from 'rxjs';

// Importing interfaces
import { postDic } from '../postDic';
import { DropDownInfo } from './DropDownInfo';
import { CurrentTrialDataEle, CurrentTrialDataAuditory } from './CurrentTrialData';

@Component({
  selector: 'app-device-startup',
  templateUrl: './device-startup.component.html',
  styleUrls: ['./device-startup.component.css','../app.component.css']
})


export class DeviceStartupComponent {
  private sseSub!: Subscription;
  ngOnInit(){
    this.sseSub = this.sseService.paramUpdates$.subscribe(({ name, value }) => {
      this.updateParamFromArduino(name, value); // subsribe incoming data from sse.service.ts
    });
  }
  //paramMap: { [key: string]: (v: string) => void } = {};
  constructor(private flaskService: FlaskService, public sseService: SSEService) {
    // The following methods are used for initialization of selection values, which are defined below
    //this.paramMap = {
    //  "session_length": (v: string) => this.sess_len.setValue(v),
    //  "response_time": (v: string) => this.sess_res_t.setValue(v),
    //  "consecutive_error": (v: string) => this.sess_conerr.setValue(v),
    //  "session_type": (v: string) => this.sess_type2 = v,
    //  "experiment_type": (v: string) => this.sess_type1 = v,
    //  "forced_trials": (v: string) => this.forced_type = v,
    //};
    //console.log(typeof this.tableFields)
    //console.log(CurrentTrialTable)

    
    if(this.isStimulatorVisible == false) {
      

      DeviceStartupComponent.parentCurTrial = DeviceStartupComponent.parentCurTrialAuditory;
      //console.log(this.connectFlags)
      //console.log(this.tableFields)
      //console.log(DeviceStartupComponent.parentCurTrial[this.tableFields[1].key])
      //console.log(this.tableFields[0].key)
      this.stim_label_1_name = "Enter Tone Duration (ms)";
      this.stim_label_2_name = "Tone Duration";
      this.stim_val_1_name = "tone_duration";
      this.stim_val_2_name = "tone_durationL";
      this.stim_val_3_name = "tone_durationR";
      //console.log(this.stim_val_1_name)
      this.exp_type2 = ["Initial Training", "Auditory Experiment"];
      //this.stim_form = this.stim_form_auditory;
      this.stim_form.get('stim_A')?.setValue('500');
      this.stim_form.get('sess_cv')?.setValue(this.stim_form.get('tone_duration').value);
      this.onSessChange = this.onSessChangeAud;
      this.onSessTypeChange = this.onSessTypeChangeAud;
      this.UpdateParamsButtonPressed = this.UpdateParamsButtonPressedAuditory;
    } else {
      //this.stim_form = this.stim_form_ele;
      DeviceStartupComponent.parentCurTrial = DeviceStartupComponent.parentCurTrialEle;
      this.onSessChange = this.onSessChangeStim;
      this.onSessTypeChange = this.onSessTypeChangeStim;
      this.UpdateParamsButtonPressed = this.UpdateParamsButtonPressedEle;
    }
    this.onSessChange(this.sess_type2)
    this.onSessTypeChange(this.sess_type1)
  }

  // Tooltips for select buttons and form fields
  FindPortToolTip = "Scans for connected Arduino boards and Gibson stimulators.";
  ImportToolTip = "Imports previous session progress. Use if performing a multi-session experiment."
  ExportToolTip = "Exports current session progress. Use if performing a multi-session experiment."
  ExpTypeToolTip = "Detection experiments feature one port with a CV, and Discrimination experiments feature each port with a unique CV."

  // Functionality variables
  inc_data: any; // Used with the SSEService BehaviorSubject observable subscription
  
  static parentCurTrial: object = {}; // This will be the dictionary of current trial data, initialized as an empty object
  static parentCurTrialEle: CurrentTrialDataEle = {
      sess_time: 'N/A',
      trial_n: 'N/A',
      trial_type: 'N/A',
      stim_A: 'N/A',
      stim_fre: 'N/A',
      CV: 'N/A',
      forced: 'N/A',
      trial_res: 'N/A',
      per_cor: 'N/A'
  }; // This will be the dictionary of current trial data

  static parentCurTrialAuditory: CurrentTrialDataAuditory = {
      sess_time: 'N/A',
      trial_n: 'N/A',
      trial_type: 'N/A',
      tone_duration: 'N/A',
      forced: 'N/A',
      trial_res: 'N/A',
      per_cor: 'N/A'
  }; // This will be the dictionary of current trial data for auditory experiments

  
  //static tableFields: object = {};//Object.keys(DevicparentCurTrialAuditory)
  /*[
      { key: 'sess_time', label: 'Time (min)'},
      { key: 'trial_n', label: 'Number' },
      { key: 'trial_type', label: 'Type' },
      { key: 'tone_duration', label: 'Tone Duration' },
      { key: 'forced', label: 'Forced' },
      { key: 'trial_res', label: 'Response' },
      { key: 'per_cor', label: 'Correct (%)' }
  ];*/
  // Flags
  connectFlags = [
    false, // Arduino Connect Flag (true when connected, false when disconnected)
    false, // Gibson Connect Flag ("...")
    false, // Initial Training Flag (true when selected, false when not selected)
    true // override flag for auditory experiment where arduino controls stim and not gibson
  ];
  tableFields = [
    { key: 'sess_time', label: 'Time (min)'},
    { key: 'trial_n', label: 'Number' },
    { key: 'trial_type', label: 'Type' },
    { key: 'forced', label: 'Forced' },
    { key: 'tone_duration', label: 'Tone Duration' },
    { key: 'trial_res', label: 'Response' },
    { key: 'per_cor', label: 'Correct (%)' }
  ];
  observeOpenFlag = false; // flag for when the observable is opened
  isStimulatorVisible = false; // flag for visibility of the Gibson stimulator parameters, set to false for auditory experiment

  // POST Responses
  COM_res: postDic = { task: "initalize", message: "initialize", output: "initialize" };
  loop_res: postDic = { task: "initalize", message: "initialize", output: "initialize" };
  SESS_res: postDic = { task: "initalize", message: "initialize", output: "initialize" };
  STIM_res: postDic = { task: "initalize", message: "initialize", output: "initialize" };
  paramsImpExp_res: any; 

  // Serial Port Connection variables
  gibPortList: postDic | undefined;
  gibPorts: DropDownInfo[] = [];
  gibSelectedPort: string | undefined;
  gibBaudRate = 115200; // Gibson stimulator baud rate (it won't change)
  ardPortList: postDic | undefined;
  ardPorts: DropDownInfo[] = [];
  ardSelectedPort: string | undefined;
  ardBaudRate = 9600; // Arduino baud rate (it also won't change)

  // Session variables

  exp_type2 = ["Initial Training", "CV Experiment"];
  sess_type2: string = "Initial Training";
  exp_type1 = ["Discrimination", "Detection"];
  sess_type1: string = "Detection";
  sess_len = new FormControl('60');
  sess_res_t = new FormControl('10');
  forced_q = ["Yes", "No"];
  forced_type: string = "Yes";
  sess_conerr = new FormControl('3');
  SESS_params: any;

  

  

  // Stimulator variables
  stim_label_1_name = "Enter Stimulus Amplitude (uA)";
  stim_label_2_name = "CV";
  stim_val_1_name = "stim_A";
  stim_val_2_name = "sess_cvL";
  stim_val_3_name = "sess_cvR";

  //stim_form: FormGroup;
  stim_form = new FormGroup({
    stim_A: new FormControl({ value: '200', disabled: false }),
    stim_fre: new FormControl({ value: '50', disabled: false }),
    sess_cv: new FormControl({ value: '0.8', disabled: false }),
    sess_cvL: new FormControl({ value: '', disabled: false }),
    sess_cvR: new FormControl({ value: '', disabled: false }),
    stim_width: new FormControl({ value: '200', disabled: false }),
    stim_interval: new FormControl({ value: '50', disabled: false }),
    stim_pulNum: new FormControl({ value: '100', disabled: false }),
    tone_duration: new FormControl({ value: '500', disabled: false }),
    tone_durationL: new FormControl({ value: '500', disabled: false }),
    tone_durationR: new FormControl({ value: '100', disabled: false })
  });

  //stim_form_auditory = new FormGroup({
  //      stim_duration: new FormControl({ value: '500', disabled: false }),
  //      sess_toneL: new FormControl({ value: '', disabled: false }),
  //      sess_toneR: new FormControl({ value: '', disabled: false })
  //});
  STIM_params: any;



  
  RefreshPortListButtonPress() {
    /*
      This function is called when the "Refresh Port List" is pressed. It executes a POST request that returns each device's
        port list. The port list is determined by the RESTful API to be displayed by variables local to the client-end UI.
    */

    this.flaskService.refreshPortList("Arduino").subscribe(data => { this.ardPorts = data.output["Arduino"] }); // returns the Arduino port list
    this.flaskService.refreshPortList("Gibson").subscribe(data => { this.gibPorts = data.output["Gibson"] }); // returns the Gibson port list
  }


  ConnectDeviceButtonPress(baudRate: number, selectedPort: string, device: string, flag: number) {
    /*
      This function is called when either "Connect <device>" button is pressed. It executes a POST request that opens a COM
        port of the specified device, with other functions completed once the backend returns a value. An observable is
        created when the first device (either device) is connected to monitor the SSE data stream. 
    */

    // Initiates the POST request to open the serial port
   
    this.flaskService.openCOMs(baudRate, selectedPort, device).subscribe(data => {
      this.COM_res = data, // captures return response
      this.connectFlags[flag] = this.flaskService.checkConnect(data["message"]), // changes button flags based on response
      this.flaskService.enterLoop(device).subscribe(nested_data => { this.loop_res = nested_data }) // enters a state to read serial port
    });

    // Checks whether an observable is created, and opens one if it's not created yet
    if (this.observeOpenFlag == false) {
      this.sseService.startCOMS().subscribe(x => { this.inc_data = x });
      this.observeOpenFlag = true;
    }
    //console.log(this.observeOpenFlag)
    //console.log(this.connectFlags[flag])
  }


  DisconnectDeviceButtonPressed(device: string, flag: number) {
    /*
      This function is called when either "Disconnect <device>" button is pressed. It executes a POST request that
        closes the COM port of the specified device, with other functions completed once the backend returns a
        value. The opened observable is closed only when the final connected device disconnects.
    */

    this.flaskService.closeCOMs(device).subscribe(data => {
      this.COM_res = data, // captures return response
      this.connectFlags[flag] = this.flaskService.checkDisconnect(data["message"]), // changes button flags based on response
      this.observeOpenFlag = this.flaskService.closeObservable(this.connectFlags) // closes the observable if appropriate
    });
  }

  UpdateParamsButtonPressed: (paramType: string) => void;

  UpdateParamsButtonPressedEle(paramType: string) {
    /*
      This function is called when either "Update <type> Parameters" or "Export/Import Parameters" button is pressed.
        It executes a POST request that sends the respective parameters to the Arduino (session) or Gibson (stimulator),
        which the RESTful API processes.
    */
    if (paramType == "Session") {

      // Updates the values of the SESS_params, based on user inputs that have changed since initialization
      this.SESS_params = [
        this.sess_type2, // Discrimination/Detection
        this.sess_type1, // Initial Training/CV Experiment
        this.sess_len.value, // Session Length (min)
        this.sess_res_t.value, // Rodent Response Time (s)
        this.forced_type, // Forced/Unforced
        this.sess_conerr.value // Rodent Consecutive Error (n)
      ];

      // The POST request itself, which captures the return response
      this.flaskService.updateParams(this.SESS_params, paramType).subscribe(x => { this.SESS_res = x });
    }
    if (paramType == "Stimulator") {

      // Updates the values of the STIM_params, based on user inputs that have changed since initialization
      if (this.isStimulatorVisible) {
        this.STIM_params = [
          this.stim_form.get('stim_A').value, // Stimulus Amplitude (uA)
          this.stim_form.get('stim_fre').value, // Stimulus Frequency (Hz)
          this.stim_form.get('stim_width').value, // Stimulus Pulse Width (us)
          this.stim_form.get('stim_interval').value, // Stimulus Inter-Phase Interval (us)
          this.stim_form.get('stim_pulNum').value, // Stimulus Number of Pulses (n)
          this.stim_form.get('sess_cv').value, // Detection CV
          this.stim_form.get('sess_cvL').value, // Discrimination CV - Left Port
          this.stim_form.get('sess_cvR').value // Discrimination CV - Right Port
        ];
      }
      else {
        this.STIM_params = [
          this.stim_form.get('stim_duration').value, // Stimulus Duration (ms)
          this.stim_form.get('sess_toneL').value, // Detection Tone - Left Port
          this.stim_form.get('sess_toneR').value // Detection Tone - Right Port
        ];
      }

      // The POST request itself, which captures the return response
      this.flaskService.updateParams(this.STIM_params, paramType).subscribe(x => { this.STIM_res = x });
    }
    else {

      // The POST request, which captures the return response
      this.flaskService.paramsImportExport(paramType).subscribe(x => { this.paramsImpExp_res = x });
    }
  }
  UpdateParamsButtonPressedAuditory(paramType: string) {
    /*
      This function is called when either "Update <type> Parameters" or "Export/Import Parameters" button is pressed.
        It executes a POST request that sends the respective parameters to the Arduino (session) or Gibson (stimulator),
        which the RESTful API processes.
    */
    if (paramType == "Session") {

      // Updates the values of the SESS_params, based on user inputs that have changed since initialization
      this.SESS_params = {
        session_type: this.sess_type2, // Initial Training/CV Experiment
        experiment_type: this.sess_type1, // Discrimination/Detection
        session_length: this.sess_len.value, // Session Length (min)
        response_time: this.sess_res_t.value, // Rodent Response Time (s)
        forced_trials: this.forced_type, // Forced/Unforced
        consecutive_error: this.sess_conerr.value, // Rodent Consecutive Error (n)
      };
      // The POST request itself, which captures the return response
      this.flaskService.updateParams(this.SESS_params, paramType).subscribe(x => { this.SESS_res = x });
      if (this.sess_type1 == "Detection"){
        this.stim_form.get('tone_durationL')?.setValue(this.stim_form.get('tone_duration').value)
        //this.stim_form.get('sess_cv')?.setValue(this.stim_form.get('tone_duration').value);
      }
      else if (this.sess_type1 == "Discrimination"){
        this.stim_form.get('tone_duration')?.setValue(this.stim_form.get('tone_durationL').value)
      }
      this.STIM_params = {
        //tone_duration: this.stim_form.get('tone_duration').value, // Detection tone duration (ms)
        tone_durationL: this.stim_form.get('tone_durationL').value, // Same as above, but used if discrimination is selected
        tone_durationR: this.stim_form.get('tone_durationR').value
      }
      
      this.flaskService.updateParams(this.STIM_params, "Stimulator").subscribe(x => { this.STIM_res = x });
    }
    else {

      // The POST request, which captures the return response
      this.flaskService.paramsImportExport(paramType).subscribe(x => { this.paramsImpExp_res = x });
    }
  }


  scrollToBot(incData: any) {
    /*
      This function is responsible for autoscrolling the content of the view-port unless the user
        has scrolled away from the bottom. A quality of life implementation for the amount of
        prints that both devices will do during an experimental session.
    */

    const vp = document.getElementById("viewPort") // an object of the div that contains the view-port

    // checks if the div is null or undefined, as error handling for observable initializing as such, and skips if so
    if (vp != null) {
      const isAtBottom = vp.scrollHeight - vp.clientHeight <= vp.scrollTop + 1; // boolean of whether the user is at the bottom
      const newElement = document.createElement("div"); // creates a new div object

      newElement.textContent = incData; // sets the text of the div object to be the observable's emitted value
      vp.append(newElement); // appends the div object to the view-port div object

      if (isAtBottom) {
        vp.scrollTop = vp.scrollHeight - vp.clientHeight; // if the user is at the bottom, it auto scrolls to the bottom if changed
      }
    }

  }


  get staticSessData() {
    /*
      This function is responsible for getting the values of parentCurTrial. This method has to be used
        since the variable is declared as static, which is being done to access the variable in other files.
    */
    return DeviceStartupComponent.parentCurTrial;
  }
  
  onSessChange: (selValue: any) => void;

  onSessChangeStim(selValue: any) {
    /*
      This function is responsible for handling a change event of the Session Type selection.
        Conditions are checked as to the value selected, which determines which fields are
        enabled or disabled through flags or directly changing properties of the form fields.
    */
    if (selValue == "Initial Training") {
      this.connectFlags[2] = true; // changes the Initial Training flag for buttons/sliders

      // changes the properties of select form fields
      this.stim_form.get('stim_A')?.disable();
      this.stim_form.get('stim_fre')?.disable();
      this.stim_form.get('sess_cv')?.disable();
      this.stim_form.get('sess_cvL')?.disable();
      this.stim_form.get('sess_cvR')?.disable();
      this.stim_form.get('stim_width')?.disable();
      this.stim_form.get('stim_interval')?.disable();
      this.stim_form.get('stim_pulNum')?.disable();

      // Handling on disconnecting the Gibson if it was connected previously
      if (this.connectFlags[1] == true) {
        this.flaskService.closeCOMs("Gibson").subscribe(x => {
          this.COM_res = x,
          this.connectFlags[1] = false
        });
      }
    }
    else {
      this.connectFlags[2] = false; // changes the Initial Training flag for buttons/sliders

      // changes the properties of select form fields
      this.stim_form.get('stim_A')?.enable();
      this.stim_form.get('stim_fre')?.enable();
      this.stim_form.get('stim_width')?.enable();
      this.stim_form.get('stim_interval')?.enable();
      this.stim_form.get('stim_pulNum')?.enable();

      // checks which experiment type is selected, if any, to enable/disable correctly
      if (this.sess_type1 != "Initialize") {
        this.onSessTypeChange(this.sess_type1);
      }
      else {
        this.stim_form.get('sess_cv')?.enable();
        this.stim_form.get('sess_cvL')?.enable();
        this.stim_form.get('sess_cvR')?.enable();
      }
    }
  }

  onSessChangeAud(selValue: any) {
    if (selValue == "Initial Training") {
      this.connectFlags[2] = true; // changes the Initial Training flag for buttons/sliders
      console.log("Initial Training selected");
      // changes the properties of select form fields
      this.stim_form.get('tone_duration')?.disable();
      //this.stim_form.get('stim_fre')?.disable();
      this.stim_form.get('tone_durationL')?.disable();
      this.stim_form.get('tone_durationR')?.disable();
      //this.stim_form.get('stim_width')?.disable();
      //this.stim_form.get('stim_interval')?.disable();
      //this.stim_form.get('stim_pulNum')?.disable();
      if (this.connectFlags[1] == true) {
        this.flaskService.closeCOMs("Gibson").subscribe(x => {
          this.COM_res = x,
          this.connectFlags[1] = false
        });
      }
    }
    else {
      this.connectFlags[2] = false; // changes the Initial Training flag for buttons/sliders

      // changes the properties of select form fields
      this.stim_form.get('tone_duration')?.enable();
      //this.stim_form.get('stim_fre')?.enable();
      //this.stim_form.get('stim_width')?.enable();
      //this.stim_form.get('stim_interval')?.enable();
      //this.stim_form.get('stim_pulNum')?.enable();

      // checks which experiment type is selected, if any, to enable/disable correctly
      if (this.sess_type1 != "Initialize") {
        this.onSessTypeChange(this.sess_type1);
      }
      else {
        this.stim_form.get('tone_duration')?.enable();
        this.stim_form.get('sess_toneL')?.enable();
        this.stim_form.get('sess_toneR')?.enable();
      }
    }


  }
  onSessTypeChange: (selValue: any) => void;

  onSessTypeChangeStim(selValue: any) {
    /*
      This function is responsible for handling a change event of the Experiment Type selection.
        Conditions are checked as to the value selected, which determines which fields are enabled
        or disabled through directly changing properties of the form fields.
    */

    if (selValue == "Detection" && this.connectFlags[2] == false) {
      this.stim_form.get('sess_cv')?.enable();
      this.stim_form.get('sess_cvL')?.disable();
      this.stim_form.get('sess_cvR')?.disable();
    }
    if (selValue == "Discrimination" && this.connectFlags[2] == false) {
      this.stim_form.get('sess_cv')?.disable();
      this.stim_form.get('sess_cvL')?.enable();
      this.stim_form.get('sess_cvR')?.enable();
    }
  }

  onSessTypeChangeAud(selValue: any) {
    /*
      This function is responsible for handling a change event of the Experiment Type selection.
        Conditions are checked as to the value selected, which determines which fields are enabled
        or disabled through directly changing properties of the form fields.
    */

    if (selValue == "Detection" && this.connectFlags[2] == false) {
      this.stim_form.get('tone_duration')?.enable();
      this.stim_form.get('tone_durationL')?.disable();
      this.stim_form.get('tone_durationR')?.disable();
    }
    if (selValue == "Discrimination" && this.connectFlags[2] == false) {
      this.stim_form.get('tone_duration')?.disable();
      this.stim_form.get('tone_durationL')?.enable();
      this.stim_form.get('tone_durationR')?.enable();
    }
  }

  updateParamFromArduino(name: string, value: string) {
    // updates UI elements based if parameters loaded on Arduino differ from default UI values
    const handlers: { [key: string]: (v: string) => void } = {
      "session_length": (v) => this.sess_len.setValue(v),
      "response_time": (v) => this.sess_res_t.setValue(v),
      "consecutive_error": (v) => this.sess_conerr.setValue(v),
      "session_type": (v) => this.sess_type2 = v,
      "experiment_type": (v) => this.sess_type1 = v,
      "forced_trials": (v) => this.forced_type = v,
    };
    const handler = handlers[name];
    if (handler) {
      handler(value);
    } else {
      console.warn('Unhandled parameter: ', name);
    }
    //const formFields = document.querySelectorAll('.cus-card mat-form-field');
    //console.log(formFields)
    //const cards = document.querySelectorAll('.cus-card');
    //cards.forEach((card) => {
    //  const header = card.querySelector('.cus-card-header, .card-title'); // your header classes
    //  if (header && header.textContent?.trim() === 'Session Parameters') {
    //    const formFields = card.querySelectorAll('mat-form-field');
    //    formFields.forEach((field) => {
    //    console.log('Found field');
        
      // Do whatever you need with each field here
    //    });
    //  }
    //});
    

    
    //console.log(this.sess_conerr)
    //console.log(handlers[name](value))
    //if (this.paramMap[name]) {
    //  this.paramMap[name](value);
    //} else {
    //  console.warn("Unknown parameter from Arduino:", name);
    //}
    }
    ngOnDestroy() {
      this.sseSub?.unsubscribe();
    }
}


