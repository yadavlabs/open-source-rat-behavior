

#include <Arduino.h>
//#include <stdint.h>
#include "VIBRATION_MOTOR.h"

// main difference from previous version is that the trigPin 
const long baudrate = 115200;
const int trigPin = 2;
const int vbmPin = 3;
const int recPin = 4;
VIBRATION_MOTOR vibration_stimulus(vbmPin);


const int readDelay = 10;
int bufferDelay = 100; // delay for Fetch call to contain rising edge of trigPin

// default vibration stimulus parameters
int vibration_level = 75;    // value between 0 and 255 for level of vibration
int vibration_time = 2000;    // length of vibration stimulus (msec)


void setup() {
  
  vibration_stimulus.setUp(vibration_level,vibration_time);
  //vibration_stimulus.setTrigPin(trigPin);
  pinMode(trigPin, OUTPUT);
  pinMode(recPin, OUTPUT);
  digitalWrite(recPin, LOW);
  Serial.begin(baudrate);
  delay(readDelay);
  Serial.print("Connected,");
  Serial.println("Wating for input...");

  //USER_COMMANDS();

}

void loop() {
  //USER_COMMANDS();
  if(Serial.available() > 0){
      byte comByte = Serial.read();
      switch(comByte){
        //case 'C':
        //  USER_COMMANDS();
        //  break;
        case 'V': //vibration motor controls 
          int vbmCom; 
          vbmCom = Serial.parseInt();
          delay(readDelay);
          if(vbmCom == 0){ //turn off stimulus
              vibration_stimulus.OFF();
              //Serial.println("Stimulus vibration test off.");

          }
          else if(vbmCom == 1){ //turns on stimulus based on vibration_level until off command is read
            vibration_stimulus.ON();
            //Serial.println("Stimulus vibration test...");

          }
          else if(vbmCom == 2){ //delivers stimulus based on vibration_level and vibration_time
            vibration_stimulus.RUN();
            

          }
          else if(vbmCom == 3){ //set vibration_level (0-255)
            vibration_level = Serial.parseInt();
            vibration_stimulus.setPWM(vibration_level);

          }
          else if(vbmCom == 4){ //set vibration_time in msec
            vibration_time = Serial.parseInt();
            vibration_stimulus.setDelay(vibration_time);
      
          }
          break;

        case 'D':
          bufferDelay = Serial.parseInt();
          Serial.print("Buffer delay set: ");
          Serial.print(bufferDelay);
          Serial.println("ms");
          break;
          
        case 'S':
          delay(bufferDelay);
          Serial.println("Writing trig pin high...");
          digitalWrite(trigPin, HIGH);
          serial_flush_buffer();
          break;
      }
      
  }


  if(digitalRead(trigPin) == HIGH){
    vibration_stimulus.RUN();
    digitalWrite(trigPin, LOW);
    Serial.println("Trig pin set low.");
  }
}

// flush serial buffer
void serial_flush_buffer(){
  while(Serial.available()){
    Serial.read(); 
  }
}

// general commands
/*void USER_COMMANDS(){
  int ch = 0;
  while(ch == 0){
    if(Serial.available() > 0){
      byte comByte = Serial.read();

      switch(comByte){
        
        case 'b': //exit setup loop
          Serial.println("Initialized");
          serial_flush_buffer();
          ch = 1;
          break;

        case 'R': //start ('R1') and stop ('R0') recording
          int rCom;
          rCom = Serial.parseInt();
          if(rCom == 0){
            digitalWrite(recPin, LOW);
          }
          else if(rCom == 1){
            digitalWrite(recPin, HIGH);
          }
          break;
          
        case 'T':
          int tCom;
          tCom = Serial.parseInt();
          delay(readDelay);
          Serial.print("Time");
          Serial.print(tCom);
          Serial.print(",");
          Serial.println(millis()-readDelay);
          break;
          
        case 'V': //vibration motor controls 
          int vbmCom; 
          vbmCom = Serial.parseInt();
          delay(readDelay);
          if(vbmCom == 0){ //turn off stimulus
              vibration_stimulus.OFF();
              //Serial.println("Stimulus vibration test off.");

          }
          else if(vbmCom == 1){ //turns on stimulus based on vibration_level until off command is read
            vibration_stimulus.ON();
            //Serial.println("Stimulus vibration test...");

          }
          else if(vbmCom == 2){ //delivers stimulus based on vibration_level and vibration_time
            vibration_stimulus.RUN();
            

          }
          else if(vbmCom == 3){ //set vibration_level (0-255)
            vibration_level = Serial.parseInt();
            vibration_stimulus.setPWM(vibration_level);

          }
          else if(vbmCom == 4){ //set vibration_time in msec
            vibration_time = Serial.parseInt();
            vibration_stimulus.setDelay(vibration_time);
      
          }
          break;
      }
    }
  }
}
*/

