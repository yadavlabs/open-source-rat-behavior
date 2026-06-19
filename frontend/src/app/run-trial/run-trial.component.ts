// Import modules
import { Component, Input, SimpleChanges } from '@angular/core';
import { MatSlideToggleChange } from '@angular/material/slide-toggle';

// Import services
import { FlaskService } from '../total.service';


@Component({
  selector: 'app-run-trial',
  templateUrl: './run-trial.component.html',
  styleUrls: ['./run-trial.component.css','../app.component.css']
})


export class RunTrialComponent {

  toggleStates: { [key: string]: boolean } = {
    'left-door': false
  }

  constructor(private flaskService: FlaskService) {}
  
  post_res: any; // records responses from the POST requests
  pause_label: string = "Pause"; // text to display for the print toggle slider
  @Input() childFlags: any; // the inherited flags to coordinate button enabling/disabling
  @Input() childCurTrial: any; // the inherited current trial data to display in the table
  @Input() childTrialTable: any;
  man_flag: boolean = false; // flag to determine whether the manual control buttons/toggle sliders are enabled/disabled

  // Tracking flag to prevent double clicks during file translation
  isExporting: boolean = false;
  
  // Tooltips for select buttons and form fields
  ExpDataToolTip = "Exports the entire session's trial data to an external file.";

  handleDataExport(chosenFormat: 'xlsx' | 'csv' = 'xlsx') {
    if (this.isExporting) return;
    this.isExporting = true;

    console.log("[Angular] Requesting behavior spreadsheet generation via Docker bridge...");

    this.flaskService.downloadSessionFile(chosenFormat).subscribe({
      next: (incomingFileBlob: Blob) => {
        // 1. Build a local memory object URL out of the binary network data array
        const localDownloadUrl = window.URL.createObjectURL(incomingFileBlob);
        
        // 2. Build a temporary link hidden inside the DOM
        const hiddenAnchor = document.createElement('a');
        hiddenAnchor.href = localDownloadUrl;
        
        // Match the extension accurately for the browser file manager allocation window
        hiddenAnchor.download = `rat_behavior_session.${chosenFormat}`;
        
        // 3. Fire a programmatic mouse click event to trigger the native browser download prompt box
        document.body.appendChild(hiddenAnchor);
        hiddenAnchor.click();
        
        // 4. Delete tracking pointers instantly to guarantee no memory leak tracks survive
        document.body.removeChild(hiddenAnchor);
        window.URL.revokeObjectURL(localDownloadUrl);
        
        console.log("[Angular] Export successfully handled by the browser engine.");
        this.isExporting = false;
      },
      error: (err) => {
        console.error("Export pipeline encountered a transmission fault:", err);
        this.isExporting = false;
      }
    });
  }

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
    //console.log(this.childTrialTable)
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
