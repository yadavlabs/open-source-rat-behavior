/*
    This code is made for the Ardunio Mega.

    This was copied from "Custom_ManualApp_v1_1" from my work in the Fall, and has since been modified.

*/
const int nInputs = 8;
const int nOutputs = 16;

const int OutputPins[nOutputs] = {22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52}; // Array of output pins
const int InputPins[nInputs] = {3,4,5,6,7,8,9,10}; // Array of input pins

int InputStates[nInputs];

void setup() {
  Serial.begin(9600); // baud rate

  // set the pins
  // https://docs.arduino.cc/built-in-examples/control-structures/ForLoopIteration
  for (int i=0; i<nOutputs; i++){
    pinMode(OutputPins[i], OUTPUT);
  }
  for (int i=0; i<nInputs; i++) {
    pinMode(InputPins[i], INPUT);
  }

  for (int i=0; i<nInputs; i++) {
    InputStates[i] = digitalRead(InputPins[i]);
    printInputState(i,InputStates[i]);
  }

  Serial.println("Arduino Set-up is complete!");
}

void loop() {
  // this is the code that repeats itself, which just calls both functions each iteration
  readOutputStates();
  //printInputStates(); // Seeing if this is what is jamming the speed of the Angular app // it was...

  InputStates[0] = checkInputPinChange(InputPins[0], InputStates[0], InputStates);
  InputStates[1] = checkInputPinChange(InputPins[1], InputStates[1], InputStates);
  InputStates[2] = checkInputPinChange(InputPins[2], InputStates[2], InputStates);
  InputStates[3] = checkInputPinChange(InputPins[3], InputStates[3], InputStates);
  InputStates[4] = checkInputPinChange(InputPins[4], InputStates[4], InputStates);
  InputStates[5] = checkInputPinChange(InputPins[5], InputStates[5], InputStates);
  InputStates[6] = checkInputPinChange(InputPins[6], InputStates[6], InputStates);
  InputStates[7] = checkInputPinChange(InputPins[7], InputStates[7], InputStates);

}




// -=-=-=-=- FUNCTIONS -=-=-=-=-
void readOutputStates(){
  if (Serial.available() > 0) { // triggers if User Input sends anything
    byte fbyte = Serial.read(); // reads what User Input sent

    switch(fbyte){
      case 'a': // if User input is "a", then do this
        toggleOutput(OutputPins[0]); // switch the state of the pin
        break;
      case 'b': // ...
        toggleOutput(OutputPins[1]); // ...
        break;
      case 'c':
        toggleOutput(OutputPins[2]); // ...
        break;
      case 'd':
        toggleOutput(OutputPins[3]); // ...
        break;
      case 'e':
        toggleOutput(OutputPins[4]); // ...
        break;
      case 'f':
        toggleOutput(OutputPins[5]); // ...
        break;
      case 'g':
        toggleOutput(OutputPins[6]); // ...
        break;
      case 'h':
        toggleOutput(OutputPins[7]); // ...
        break;
      case 'i':
        toggleOutput(OutputPins[8]); // ...
        break;
      case 'j':
        toggleOutput(OutputPins[9]); // ...
        break;
      case 'k':
        toggleOutput(OutputPins[10]); // ...
        break;
      case 'l':
        toggleOutput(OutputPins[11]); // ...
        break;
      case 'm':
        toggleOutput(OutputPins[12]); // ...
        break;
      case 'n':
        toggleOutput(OutputPins[13]); // ...
        break;
      case 'o':
        toggleOutput(OutputPins[14]); // ...
        break;
      case 'p':
        toggleOutput(OutputPins[15]); // ...
        break;
    }
  }
}



void printInputState(int pin, int state){
  Serial.print(pin);
  Serial.print(",");
  Serial.println(state);
}



void toggleOutput(int pin) {
  int pinState = digitalRead(pin); // read the current pin state...
  
  if (pinState == HIGH) { // ...if the pin is high...
    digitalWrite(pin, LOW); // ...set the pin to low...
  }
  else { // ...if the pin is low...
    digitalWrite(pin, HIGH); // ...set the pin to high
  }
}



int checkInputPinChange(int pin, int lastState, int inputStates[]) {
  // https://www.programmingelectronics.com/tutorial-18-state-change-detection-and-the-modulo-operator-old-version/
  // https://docs.arduino.cc/learn/programming/functions
  int currentState = digitalRead(pin);

  if (currentState != lastState) {
    printInputState(pin,currentState); // to change

    return currentState;
  }
  else {
    return lastState;
  }
}
