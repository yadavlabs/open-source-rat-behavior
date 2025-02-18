// Import modules
import { Component, Input } from '@angular/core';
import { MatSlideToggleChange } from '@angular/material/slide-toggle';

// Import services
import { FlaskService } from '../total.service';


@Component({
  selector: 'app-run-trial',
  templateUrl: './run-trial.component.html',
  styleUrls: ['./run-trial.component.css','../app.component.css']
})


export class RunTrialComponent {
  constructor(private flaskService: FlaskService) { }
  
  post_res: any; // records responses from the POST requests
  pause_label: string = "Pause"; // text to display for the print toggle slider
  @Input() childFlags: any; // the inherited flags to coordinate button enabling/disabling
  @Input() childCurTrial: any; // the inherited current trial data to display in the table
  man_flag: boolean = false; // flag to determine whether the manual control buttons/toggle sliders are enabled/disabled

  // Tooltips for select buttons and form fields
  ExpDataToolTip = "Exports the entire session's trial data to an external file.";


  SessionButtonsPressed(butString: string, device: string) {
    /*
      This function is responsible for any of the session buttons being pressed. The same information is sent
        to the RESTful API, so the function is used for that. Extra logic exists only to change the manual
        control flag (man_flag) depending on whether the start/stop button was pressed. The destination device
        (device) and a string to indicate which button was clicked (butString) are sent, but since these buttons
        don't need their state sent for processing in the RESTful API the string "N/A" is sent.
    */

    // The POST request, where the return from the RESTful API is captured
    this.flaskService.writeToCOMport(butString, device, "N/A").subscribe(data => { this.post_res = data });

    // Changing of the manual control flag depending on the button pressed.
    if (butString == "start") {
      this.man_flag = true;
    }
    if (butString == "stop") {
      this.man_flag = false;
    }
  }


  onSlideChange(butString: string, device: string, $event: MatSlideToggleChange) {
    /*
      This function is responsible for the change events of the slide toggles. The device state
        ($event.checked) is sent as an argument, alongside the destination device (device), and
        a string to indicate which slider was changed (butString).
    */

    // The POST request, where the return from the RESTful API is captured
    this.flaskService.writeToCOMport(butString, device, $event.checked).subscribe(data => { this.post_res = data });

    // Changing of the label for the pause slider depending on the state of the slider, alongside the manual control flag
    if (butString == "pause" && $event.checked == true) {
      this.pause_label = "Unpause";
      this.man_flag = false;
    }
    if (butString == "pause" && $event.checked == false) {
      this.pause_label = "Pause";
      this.man_flag = true;
    }
  }
}
