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
  @Input() childStimSource: string; // the inherited stimulator source to send to the backend for stimulation
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

  async handleDataExportFD(chosenFormat: 'xlsx' | 'csv' = 'xlsx') {
  if (this.isExporting) return;
  this.isExporting = true;

  console.log("[Angular] Requesting behavior spreadsheet generation via Docker bridge...");

  this.flaskService.downloadSessionFile(chosenFormat).subscribe({
    next: async (incomingFileBlob: Blob) => {
      
      // 1. Check if the browser supports the modern File System Access API
      if ('showSaveFilePicker' in window) {
        try {
          // Define file options and format restrictions for the native popup
          const options = {
            suggestedName: `rat_behavior_session.${chosenFormat}`,
            types: chosenFormat === 'xlsx' ? [
              {
                description: 'Excel Spreadsheet',
                accept: { 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'] }
              }
            ] : [
              {
                description: 'CSV File',
                accept: { 'text/csv': ['.csv'] }
              }
            ]
          };

          // 2. Open the Native File Explorer "Save As" Prompt Box
          const fileHandle = await (window as any).showSaveFilePicker(options);

          // 3. Stream the file binary directly into the user-selected folder path
          const writableStream = await fileHandle.createWritable();
          await writableStream.write(incomingFileBlob);
          await writableStream.close();

          console.log("[Angular] Native save location successfully processed by the system.");
        } catch (err) {
          // Handle cases where the user clicks "Cancel" inside the dialog
          console.warn("User aborted the save dialog or picker failed:", err);
        }
      } else {
        // 4. FALLBACK: Use your exact original hidden anchor link strategy for unsupported browsers
        console.log("[Angular] showSaveFilePicker unsupported. Using anchor tag fallback.");
        const localDownloadUrl = window.URL.createObjectURL(incomingFileBlob);
        const hiddenAnchor = document.createElement('a');
        hiddenAnchor.href = localDownloadUrl;
        hiddenAnchor.download = `rat_behavior_session.${chosenFormat}`;
        
        document.body.appendChild(hiddenAnchor);
        hiddenAnchor.click();
        
        document.body.removeChild(hiddenAnchor);
        window.URL.revokeObjectURL(localDownloadUrl);
      }

      this.isExporting = false;
    },
    error: (err) => {
      console.error("Export pipeline encountered a transmission fault:", err);
      this.isExporting = false;
    }
  });
}

async handleDataExportFD2(chosenFormat: 'xlsx' | 'csv' = 'xlsx') {
  if (this.isExporting) return;
  this.isExporting = true;

  this.flaskService.downloadSessionFile2(chosenFormat).subscribe({
    next: async (response: any) => {
      // 1. Extract the binary file array body
      const incomingFileBlob = response.body; 

      // 2. Parse the python-defined filename out of the Content-Disposition header
      let finalFilename = `rat_behavior_session.${chosenFormat}`; // Local fallback name

      const contentDisposition = response.headers.get('content-disposition');
      if (contentDisposition) {
        const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition);
        if (matches != null && matches[1]) { 
          finalFilename = matches[1].replace(/['"]/g, ''); // Strip quotes out
        }
      }

      // 3. Launch native Save Picker using the Python-defined filename
      if ('showSaveFilePicker' in window) {
        try {
          const options = {
            suggestedName: finalFilename, // <--- Dynamic filename passed from Python!
            types: chosenFormat === 'xlsx' ? [
              {
                description: 'Excel Spreadsheet',
                accept: { 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'] }
              }
            ] : [
              {
                description: 'CSV File',
                accept: { 'text/csv': ['.csv'] }
              }
            ]
          };

          const fileHandle = await (window as any).showSaveFilePicker(options);
          const writableStream = await fileHandle.createWritable();
          await writableStream.write(incomingFileBlob);
          await writableStream.close();
        } catch (err) {
          console.warn("User aborted save window context:", err);
        }
      } else {
        // Fallback Anchor handling
        const localDownloadUrl = window.URL.createObjectURL(incomingFileBlob);
        const hiddenAnchor = document.createElement('a');
        hiddenAnchor.href = localDownloadUrl;
        hiddenAnchor.download = finalFilename;
        document.body.appendChild(hiddenAnchor);
        hiddenAnchor.click();
        document.body.removeChild(hiddenAnchor);
        window.URL.revokeObjectURL(localDownloadUrl);
      }

      this.isExporting = false;
    },
    error: (err) => {
      console.error("Export pipeline transmission fault:", err);
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
