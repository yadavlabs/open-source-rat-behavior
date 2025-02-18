// Importing modules
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';

// Importing services
import { SSEService } from './device-startup/sse.service';

// Importing interfaces
import { postDic } from './postDic';


@Injectable({
  providedIn: 'root'
})

export class FlaskService {
  constructor(private http: HttpClient, private sseService: SSEService) { }

  URL1 = "http://127.0.0.1:5000/device_setup"; // URL to RESTful API for setup
  URL2 = "http://127.0.0.1:5000/to_dev"; // URL to RESTful API for serial communication


  // THE FOLLOWING FUNCTIONS ARE USED ONLY BY THE device-startup COMPONENT

  refreshPortList(device: string) {
    /*
      This function is responsible for returning a list of COM ports that either device is
        connected to. Processing is handled on the backend, but identifying information
        is sent through the variable "body" to help with backend logic. The returned
        list of ports is displayed in selection fields.
    */

    let body = new HttpParams(); // declares a useful HTTP property
    body = body.set("task", "findPorts"); // adds a dictionary key (task) with a value (findPorts)
    body = body.set("device", device); // adds a dictionary key (device) with a value (Arduino or Gibson)

    return this.http.post<postDic>(this.URL1, body); // returns the list received from the RESTful API
  }

  openCOMs(baudRate: number, selectedPort: string, device: string) {
    /*
      This function is responsible for sending relevant information to the RESTful API to
        open a serial port connection with the respective device. Processing is handled
        on the backend, but the variable "body" helps with backend logic.
      To open a serial port with the backend, a baudrate and port have to be specified, which
        is streamlined through the client-end UI to select. The device identifier just helps
        with logic to better address processes relevant to the different devices (Arduino or
        Gibson).
    */

    let body = new HttpParams(); // declares a useful HTTP property
    body = body.set("task", "openCOMs"); // adds a dictionary key (task) with a value (openCOMs)
    body = body.set("device", device); // ...
    body = body.set("baudRate", baudRate); // ...
    body = body.set("port", selectedPort); // ...

    return this.http.post<postDic>(this.URL1, body); // returns a status message
  }

  closeCOMs(device: string) {
    /*
      This function is responsible for sending relevant information to the RESTful API
        to close a serial port connection with the respective device.
    */

    let body = new HttpParams(); // ...
    body = body.set("task", "closeCOMs"); // ...
    body = body.set("device", device); // ...

    return this.http.post<postDic>(this.URL1, body); // returns a status message
  }

  checkConnect(res_message: string) {
    /*
      This function is responsible for checking whether the respective device
        successfully connected or not to change the flags relevant to button
        enabling/disabling. Processing is handled through a few if statements
        on the client-end.
    */

    if (res_message == "success") {
      return true // changes button state, as the connection was successful
    }
    else {
      return false // button state doens't change, since the connection was unsuccessful
    }
  }

  checkDisconnect(res_message: string) {
    /*
      This function is responsible for checking whether the respective device
        successfully disconnected or not to change the flags relevant to
        button enabling/disabling. Processing is handled through a few if
        statements on the client-end.
    */

    if (res_message == "success") {
      return false // changes button state, as the connection was successful
    }
    else {
      return true // button state doesn't change, since the connection was unsuccessful
    }
  }

  closeObservable(flags: any) {
    /*
      This function is responsible for closing the observable monitoring the
        RESTful API when appropriate.
    */

    if (flags[0] == false && flags[1] == false) {
      // This condition is met when both devices are disconnected
      this.sseService.stopCOMS(); // the observable is no longer needed
      return false // changes the flag so the observable can open again in the future
    }
    else {
      console.log("Observable not closed yet"); // partial indicator that the observable wasn't closed
      return true // doesn't change the flag, so no new observable will be created if a device connects
    }
  }

  enterLoop(device: string) {
    /*
      This function is responsible for putting the respective device in a state to
        read/write to the serial port. A previous version used a forever loop, but
        a different function was used instead - so this function can likely be changed
        in a future version.
    */

    let body = new HttpParams(); // ...
    body = body.set("task", "enterLoop"); // ...
    body = body.set("device", device); // ...

    return this.http.post<postDic>(this.URL1, body); // returns a status message
  }

  updateParams(params: any, paramType: string) {
    /*
      This function is responsible for updating session/stimulator parameters, which
        are each destined for a different device.
    */
    
    let body = new HttpParams(); // ...
    body = body.set("task", "updateParams"); // ...
    body = body.set("params", params); // ...
    body = body.set("paramType", paramType); // ...

    return this.http.post<postDic>(this.URL1, body); // returns a status message
  }

  paramsImportExport(paramType: string) {
    /*
      This function is responsible for handling the importing and exporting of
        parameters necessary for multi-session experiments. This is the exception
        POST request that doesn't use the postDic interface.
    */

    let body = new HttpParams(); // ...
    body = body.set("task", "paramsImpExp"); // ...
    body = body.set("paramType", paramType); // ...

    return this.http.post(this.URL1, body); // returns a status message
  }

  // THE FOLLOWING FUNCTIONS ARE USED ONLY BY THE run-trial COMPONENT

  writeToCOMport(string: any, device: string, state: any) {
    /*
      This function is responsible for sending commands to the RESTful API
        to coordinate writing appropriate strings to the serial port of the
        respective device. Button states are sometimes important to consider
        for select function, so that is included as a dictionary entry to help
        in backend logic.
    */

    let body = new HttpParams(); // ...
    body = body.set("task", "writeCOM"); // ...
    body = body.set("string", string); // ...
    body = body.set("device", device); // ...
    body = body.set("butState", state); // ...

    return this.http.post<postDic>(this.URL2, body); // returns a status message
  }

}
