/*
  This is an interface to contain the response to all but one POST request.
    Each POST request indicates a task used in backend logic, which gets
    returned, as well as a status message depending on the processing
    that occurs in the backend. The output is useful for if there is any data
    to return to the front-end.
  The one exception is that way purely because it was the final POST request
    added late into the project and at the time was declared as type 'any'
    as opposed to using this interface.
*/

export interface postDic {
  task: string; // The indicated task (openCOMs, findPorts, etc.)
  message: string; // The status message returned from the RESTful API
  output: any; // A space for data to come back to the client-end, although it's mostly empty
}
