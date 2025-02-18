// Import components
import { DeviceStartupComponent } from './device-startup.component';

// Import modules
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';


@Injectable({
  providedIn: 'root'
})

export class SSEService {
  constructor() { }

  URL3 = "http://127.0.0.1:5000/stream"; // RESTful URL for SSE

  // Declaring the observable that is used later in the function
  ev_source!: EventSource;
  subj = new BehaviorSubject([]);

  startCOMS() {
    let subject = this.subj;

    if (typeof (EventSource) !== 'undefined') {
      this.ev_source = new EventSource(this.URL3); // creates the event source that the observable monitors

      // a function called upon the opening of the observable
      this.ev_source.onopen = function (e) {
        console.log("Opening Connection... Ready State is " + this.readyState); // partial indication that the observable's been opened
      }

      // onmessage allows for the BehaviorSubject to display a value only when it's no longer receiving any (when stopped)
      this.ev_source.onmessage = function (e) {
        subject.next(JSON.parse(e.data)); // appends the data to the BehaviorSubject observable object
        
        const elemToAdd = JSON.parse(e.data)["item1"]; // parses the print statements from devices
        DeviceStartupComponent.prototype.scrollToBot(elemToAdd) // passes the newly printed statement to append in the view-port

        const incSessData = JSON.parse(e.data)["item2"]; // parses the current trial data
        DeviceStartupComponent.parentCurTrial = incSessData; // redefines the current trial data with the newly parsed data
        }

      // EventListener allows for in-real-time updates to the BehaviorSubject
      this.ev_source.addEventListener("message", function (e) { })

      // Error handling for if the backend disconnects, the observable attempts to reconnect to the event source
      this.ev_source.onerror = function (e) {
        if (this.readyState == 0) {
          console.log("Reconnecting..."); // partial indication that the observable is trying to reconnect
        }
      }
    }

    return subject; // returns the observable
  }

  stopCOMS() {
    console.log("Observable closed"); // partial indication that the observable is closed
    this.ev_source.close(); // closes the observable
  }
}
